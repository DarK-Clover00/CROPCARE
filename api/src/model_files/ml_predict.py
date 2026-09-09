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

LEAF_METADATA = {
    "Potato": {
        "leaf_name": "Potato Leaf",
        "leaf_type": "Compound Pinnate Foliage Leaf",
        "botanical_species": "Solanum tuberosum"
    },
    "Tomato": {
        "leaf_name": "Tomato Leaf",
        "leaf_type": "Odd-Pinnately Compound Leaf",
        "botanical_species": "Solanum lycopersicum"
    },
    "Pepper": {
        "leaf_name": "Pepper Leaf",
        "leaf_type": "Simple Smooth-Edged Foliar Leaf",
        "botanical_species": "Capsicum annuum"
    },
    "Cherry": {
        "leaf_name": "Cherry Tree Leaf",
        "leaf_type": "Simple Ovate Serrated Leaf",
        "botanical_species": "Prunus avium"
    },
    "Papaya": {
        "leaf_name": "Papaya Leaf",
        "leaf_type": "Large Palmate Deeply-Lobed Leaf",
        "botanical_species": "Carica papaya"
    }
}

_MODEL_INSTANCE = None
_LABELS_DICT = None
_IDX_TO_LABEL = None


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
    Returns (affected_area_percentage, bounding_boxes).
    """
    if is_healthy:
        return 0.0, []

    h, w = cv_img_rgb.shape[:2]
    hsv = cv2.cvtColor(cv_img_rgb, cv2.COLOR_RGB2HSV)

    # Total leaf foliage mask
    mask_foliage = cv2.inRange(hsv, np.array([10, 20, 20]), np.array([98, 255, 255]))
    leaf_pixels = max(1, np.sum(mask_foliage > 0))

    # Mask for necrotic brown spots, chlorotic halos, and lesions
    mask_lesion = cv2.inRange(hsv, np.array([10, 32, 25]), np.array([33, 255, 220]))
    mask_lesion = cv2.bitwise_and(mask_lesion, mask_foliage)

    # Morphological filtering to clean noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_lesion_clean = cv2.morphologyEx(mask_lesion, cv2.MORPH_OPEN, kernel)

    lesion_pixels = np.sum(mask_lesion_clean > 0)
    affected_pct = round(float((lesion_pixels / leaf_pixels) * 100), 1)

    # Find lesion contour bounding boxes
    contours, _ = cv2.findContours(mask_lesion_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = []

    # Sort contours by area descending and take top significant boxes
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
    min_box_area = (w * h) * 0.002  # filter out tiny noise

    for c in sorted_contours:
        area = cv2.contourArea(c)
        if area > min_box_area:
            bx, by, bw, bh = cv2.boundingRect(c)
            bounding_boxes.append({
                "x": round(float(bx / w) * 100, 1),
                "y": round(float(by / h) * 100, 1),
                "width": round(float(bw / w) * 100, 1),
                "height": round(float(bh / h) * 100, 1),
                "area_pct": round(float(area / (w * h)) * 100, 2)
            })
            if len(bounding_boxes) >= 8:
                break

    # Cap affected percentage within sensible realistic bounds
    affected_pct = min(affected_pct, 95.0)

    # If lesions detected but affected_pct calculated near 0, provide baseline minimum
    if len(bounding_boxes) > 0 and affected_pct < 2.0:
        affected_pct = 5.0

    return affected_pct, bounding_boxes


@torch.no_grad()
def analyze_crop_image(img_bytes):
    """
    Complete dynamic AI analysis pipeline for an uploaded crop image:
    1. Image decoding & format validation
    2. Plant / Leaf verification
    3. PyTorch Deep CNN prediction with Softmax probabilities
    4. Computer vision lesion segmentation & affected area estimation
    5. Dynamic severity calculation
    6. Extraction of disease-specific symptoms, treatments, active ingredients, precautions, prevention
    7. Formats structured JSON response
    """
    try:
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        return {
            "status": "error",
            "is_plant": False,
            "message": f"Invalid image file: {str(e)}"
        }

    # Convert to OpenCV RGB numpy array for computer vision analysis
    cv_img = np.array(pil_img)

    # Step 1: Detect whether the image contains a plant/leaf
    is_plant, foliage_ratio = check_plant_image(cv_img)
    if not is_plant:
        return {
            "status": "rejected",
            "is_plant": False,
            "message": "No plant or leaf detected in the uploaded image. Please upload a clear, focused photo of a crop or plant leaf.",
            "foliage_ratio": foliage_ratio,
            "confidence": 0.0
        }

    # Step 2: PyTorch Model Inference
    model = get_model()
    labels, idx_to_label = get_labels()

    preprocess = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor()
    ])
    tensor = preprocess(pil_img).unsqueeze(0)

    logits = model(tensor)
    probs = torch.softmax(logits, dim=1)[0]

    # Top-K predictions
    k = min(3, len(labels))
    top_probs, top_indices = torch.topk(probs, k)

    top_idx = top_indices[0].item()
    top_prob = round(float(top_probs[0].item()), 3)
    predicted_key = idx_to_label[top_idx]

    # Alternative diagnoses
    alternatives = []
    for i in range(1, k):
        alt_idx = top_indices[i].item()
        alt_prob = round(float(top_probs[i].item()), 3)
        alt_key = idx_to_label[alt_idx]
        alt_info = get_disease_info(alt_key)
        condition_name = f"{alt_info['disease']} ({alt_info['crop']})"
        alternatives.append({
            "condition": condition_name,
            "confidence": alt_prob,
            "confidence_percent": round(alt_prob * 100, 1)
        })

    # Retrieve comprehensive agronomic knowledge for the top class
    disease_info = get_disease_info(predicted_key)
    is_healthy = disease_info["is_healthy"]

    # Step 3: Computer Vision Lesion Segmentation & Highlighting
    affected_area_pct, bounding_boxes = segment_lesions(cv_img, is_healthy=is_healthy)

    # Step 4: Confidence Check (Uncertainty threshold)
    is_uncertain = top_prob < 0.42
    if is_uncertain:
        detection_status = "Uncertain Diagnosis"
        severity = "Uncertain"
        status_code = "uncertain"
        uncertain_msg = "Unable to confidently identify the disease. The AI confidence is below the diagnostic threshold. Please upload a clearer, well-lit photo of the leaf symptoms."
    elif is_healthy:
        detection_status = "No Obvious Disease Detected"
        severity = "None (Healthy)"
        status_code = "success"
        uncertain_msg = ""
    else:
        detection_status = "Disease Detected"
        status_code = "success"
        uncertain_msg = ""
        # Dynamic severity based on affected area percentage
        if affected_area_pct < 8.0:
            severity = "Mild"
        elif affected_area_pct <= 25.0:
            severity = "Moderate"
        else:
            severity = "Severe"

    # Step 5: Dynamic symptoms tailored from CV analysis
    dynamic_symptoms = list(disease_info["symptoms"])
    if not is_healthy and len(bounding_boxes) > 0:
        dynamic_symptoms.insert(0, f"Computer-vision analysis detected {len(bounding_boxes)} suspected symptom clusters covering approximately {affected_area_pct}% of the leaf lamina")

    base_crop = disease_info["crop"]
    leaf_meta = LEAF_METADATA.get(base_crop, {
        "leaf_name": f"{base_crop} Leaf",
        "leaf_type": "Compound Foliar Leaf",
        "botanical_species": disease_info.get("scientific_name", "Plantae")
    })

    # Construct complete structured response
    response = {
        "status": status_code,
        "is_plant": True,
        "is_uncertain": is_uncertain,
        "message": uncertain_msg,
        "crop": leaf_meta["leaf_name"],
        "crop_base": base_crop,
        "leaf_name": leaf_meta["leaf_name"],
        "leaf_type": leaf_meta["leaf_type"],
        "botanical_species": leaf_meta["botanical_species"],
        "disease": disease_info["disease"],
        "scientific_name": leaf_meta["botanical_species"],
        "pathogen_name": disease_info.get("scientific_name", "N/A"),
        "is_healthy": is_healthy,
        "confidence": top_prob,
        "confidence_percent": round(top_prob * 100, 1),
        "severity": severity,
        "detection_status": detection_status,
        "affected_area_percentage": affected_area_pct,
        "bounding_boxes": bounding_boxes,
        "summary": disease_info["summary"],
        "symptoms": dynamic_symptoms,
        "immediate_actions": disease_info["immediate_actions"],
        "treatment": disease_info["treatment"],
        "medicines": disease_info["medicines"],
        "safety_precautions": disease_info["safety_precautions"],
        "prevention": disease_info["prevention"],
        "alternatives": alternatives,
        "disclaimer": "AI-assisted diagnosis. For severe or uncertain cases, consult an agricultural expert or certified crop advisor before chemical application."
    }

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