import io
import os
import json
import pickle
import numpy as np
from PIL import Image
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms

from model_files.disease_knowledge import get_disease_info
from model_files.crop_taxonomy import CROP_TAXONOMY_100, get_crop_profile
from model_files.area_detection import (
    segment_leaf_lamina,
    segment_infected_areas,
    detect_leaf_infected_regions,
    draw_area_detection_overlay,
    encode_cv_image_base64
)
from model_files.two_stage_pipeline import TwoStageCropPipeline


# PyTorch Model Architecture (matches pretrained weights)
class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=6, kernel_size=5)
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=12, kernel_size=5)
        self.conv3 = nn.Conv2d(in_channels=12, out_channels=24, kernel_size=5)
        self.conv4 = nn.Conv2d(in_channels=24, out_channels=48, kernel_size=5)

        self.fc1 = nn.Linear(in_features=48 * 12 * 12, out_features=240)
        self.fc2 = nn.Linear(in_features=240, out_features=120)
        self.out = nn.Linear(in_features=120, out_features=19)

    def forward(self, t):
        t = self.conv1(t)
        t = F.relu(t)
        t = F.max_pool2d(t, kernel_size=2, stride=2)

        t = self.conv2(t)
        t = F.relu(t)
        t = F.max_pool2d(t, kernel_size=2, stride=2)

        t = self.conv3(t)
        t = F.relu(t)
        t = F.max_pool2d(t, kernel_size=2, stride=2)

        t = self.conv4(t)
        t = F.relu(t)
        t = F.max_pool2d(t, kernel_size=2, stride=2)

        t = t.reshape(-1, 48 * 12 * 12)
        t = self.fc1(t)
        t = F.relu(t)

        t = self.fc2(t)
        t = F.relu(t)

        t = self.out(t)
        return t


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_MODEL_INSTANCE = None
_LABELS_DICT = None
_IDX_TO_LABEL = None
_PIPELINE_INSTANCE = None


def get_model():
    """Singleton getter for the PyTorch model."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        model = Network()
        model_path = os.path.join(BASE_DIR, "model.pth")
        try:
            state_dict = torch.load(model_path, map_location=torch.device("cpu"), weights_only=False)
        except TypeError:
            state_dict = torch.load(model_path, map_location=torch.device("cpu"))
        model.load_state_dict(state_dict)
        model.eval()
        _MODEL_INSTANCE = model
    return _MODEL_INSTANCE


def get_labels():
    """Singleton getter for labels dictionary."""
    global _LABELS_DICT, _IDX_TO_LABEL
    if _LABELS_DICT is None:
        labels_path = os.path.join(BASE_DIR, "labels.json")
        with open(labels_path, "rb") as f:
            _LABELS_DICT = pickle.load(f)
        _IDX_TO_LABEL = {v: k for k, v in _LABELS_DICT.items()}
    return _LABELS_DICT, _IDX_TO_LABEL


def get_pipeline():
    """Singleton getter for TwoStageCropPipeline."""
    global _PIPELINE_INSTANCE
    if _PIPELINE_INSTANCE is None:
        model = get_model()
        labels, idx_to_label = get_labels()
        _PIPELINE_INSTANCE = TwoStageCropPipeline(model, labels, idx_to_label)
    return _PIPELINE_INSTANCE


def check_plant_image(cv_img_rgb):
    """
    Validates whether the image contains a plant, crop, or leaf.
    Uses HSV and LAB vegetation color masks.
    """
    hsv = cv2.cvtColor(cv_img_rgb, cv2.COLOR_RGB2HSV)

    # Green foliage: Hue 24-95, Sat > 25, Val > 25
    mask_green = cv2.inRange(hsv, np.array([24, 25, 25]), np.array([95, 255, 255]))

    # Yellowish/brownish diseased foliage: Hue 10-24, Sat > 25, Val > 25
    mask_yellow_brown = cv2.inRange(hsv, np.array([10, 25, 25]), np.array([24, 255, 255]))

    combined = cv2.bitwise_or(mask_green, mask_yellow_brown)
    total_pixels = cv_img_rgb.shape[0] * cv_img_rgb.shape[1]
    foliage_pixels = np.sum(combined > 0)
    foliage_ratio = foliage_pixels / max(1, total_pixels)

    # Threshold for real plant/leaf content
    is_plant = foliage_ratio >= 0.08
    return is_plant, round(float(foliage_ratio) * 100, 1)


def segment_lesions(cv_img_rgb, is_healthy=False):
    """
    Segment diseased/necrotic/chlorotic regions on the leaf using OpenCV.
    Delegates to the advanced area-wise detection engine.
    Returns (affected_area_percentage, bounding_boxes).
    """
    res = detect_leaf_infected_regions(cv_img_rgb, is_healthy=is_healthy)
    return res["affected_area_percentage"], res["bounding_boxes"]


@torch.no_grad()
def analyze_crop_image(img_bytes):
    """
    Complete dynamic AI analysis pipeline for an uploaded or camera-captured crop image:
    1. Image decoding & format validation
    2. Plant / Leaf verification
    3. Stage 1: Plant & Crop Identification (100+ botanical taxonomy categories)
    4. Stage 2: Crop-Gated Deep Disease Identification
    5. Stage 3: Advanced Area-Wise Lesion & Disease Detection (red bounding boxes, Area-N labels, NMS)
    6. Pixel-level Affected Area Percentage calculation
    7. Agronomic prescription & medicine guidance
    8. Formats structured JSON response including base64 annotated image
    """
    try:
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        return {
            "status": "error",
            "is_plant": False,
            "message": f"Invalid image file: {str(e)}"
        }

    cv_img = np.array(pil_img)

    # Step 1: Detect whether the image contains a plant/leaf
    is_plant, foliage_ratio = check_plant_image(cv_img)
    if not is_plant:
        return {
            "status": "rejected",
            "is_plant": False,
            "message": "No plant or leaf detected in the uploaded image. Please upload a clear, focused photo of a crop or plant leaf.",
            "foliage_ratio": foliage_ratio,
            "confidence": 0.0,
            "num_detected_regions": 0,
            "detected_regions": [],
            "affected_area_percentage": 0.0
        }

    # Step 2: Run Two-Stage Crop & Disease Recognition Pipeline
    pipeline = get_pipeline()
    response = pipeline.predict_crop_and_disease(pil_img, cv_img)
    response["foliage_ratio"] = foliage_ratio
    return response


# Backwards-compatible function for old scripts
def predict_plant(model, imgdata):
    analysis = analyze_crop_image(imgdata)
    if not analysis.get("is_plant", False):
        return "Non_Plant___Image", "Please upload a clear picture of a plant leaf."
    plant = analysis["crop"]
    disease = analysis["disease"].replace(" ", "_")
    remedy = "\n".join(analysis.get("treatment", []))
    return f"{plant}___{disease}", remedy
