"""
CropCare v3.0 - Leaf Localization and Computer Vision Module
Provides OpenCV-based real-time and server-side leaf detection,
vegetation verification, contour extraction, and bounding box localization.
"""

import cv2
import numpy as np


def detect_leaf_contours(cv_img_rgb):
    """
    Analyzes an RGB image to detect foliar plant matter using multi-spectral
    color analysis (HSV + LAB + Excess Green), morphological contour segmentation,
    and texture gradient verification.

    Returns:
        dict containing:
            - leaf_detected (bool): Whether a valid plant leaf is detected.
            - confidence (float): Localization confidence score [0.0 - 1.0].
            - bounding_box (dict): Normalized coords {x, y, width, height, area_pct}.
            - pixel_box (dict): Pixel coords {x, y, width, height}.
            - foliage_ratio (float): Percentage of image containing leaf tissue.
            - message (str): Human-readable diagnostic message.
            - stability_score (float): Quality score based on contour solidity & texture.
    """
    if cv_img_rgb is None or cv_img_rgb.size == 0:
        return {
            "leaf_detected": False,
            "confidence": 0.0,
            "bounding_box": None,
            "pixel_box": None,
            "foliage_ratio": 0.0,
            "message": "Empty or invalid image frame.",
            "stability_score": 0.0
        }

    h, w = cv_img_rgb.shape[:2]
    total_pixels = h * w

    # 1. Multi-spectral Color Space Transformations
    hsv = cv2.cvtColor(cv_img_rgb, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(cv_img_rgb, cv2.COLOR_RGB2LAB)
    lab_l, lab_a, lab_b = cv2.split(lab)

    r = cv_img_rgb[:, :, 0].astype(np.float32)
    g = cv_img_rgb[:, :, 1].astype(np.float32)
    b = cv_img_rgb[:, :, 2].astype(np.float32)

    # 2. Vegetation Color Masks (Healthy Green, Chlorotic Yellow, Necrotic Brown)
    # Healthy Green foliage: HSV Hue 24-95, Sat > 25, Val > 25
    mask_hsv_green = cv2.inRange(hsv, np.array([24, 25, 25]), np.array([95, 255, 255]))
    mask_lab_green = cv2.inRange(lab_a, 0, 126)
    mask_green = cv2.bitwise_and(mask_hsv_green, mask_lab_green)

    # Chlorotic Yellow / Pale Foliage: HSV Hue 16-24, Sat > 30, Val > 30, LAB b* >= 130
    mask_hsv_yellow = cv2.inRange(hsv, np.array([16, 30, 30]), np.array([24, 255, 255]))
    mask_lab_yellow = cv2.inRange(lab_b, 130, 255)
    mask_yellow = cv2.bitwise_and(mask_hsv_yellow, mask_lab_yellow)

    # Necrotic Brown / Diseased Foliage: HSV Hue 8-16, Sat > 25, Val in [20, 210]
    mask_hsv_brown = cv2.inRange(hsv, np.array([8, 25, 20]), np.array([16, 255, 210]))
    mask_brown = cv2.bitwise_and(mask_hsv_brown, mask_lab_yellow)

    # Combine color channels
    mask_foliage = cv2.bitwise_or(mask_green, mask_yellow)
    mask_foliage = cv2.bitwise_or(mask_foliage, mask_brown)

    # Reject non-plant skin tones (Skin typically has a* > 136 and r > 1.2*g)
    mask_skin = (lab_a > 136) & (r > (1.2 * g))
    mask_foliage[mask_skin] = 0

    # 3. Morphological Filtering: OPEN first to eliminate isolated noise speckles, then CLOSE to unite lamina
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask_clean = cv2.morphologyEx(mask_foliage, cv2.MORPH_OPEN, kernel_open)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel_close)

    foliage_pixels = np.sum(mask_clean > 0)
    foliage_ratio = round(float(foliage_pixels / max(1, total_pixels)) * 100, 1)

    # Check minimum foliar presence
    if foliage_ratio < 4.0:
        return {
            "leaf_detected": False,
            "confidence": round(float(foliage_ratio / 15.0), 2),
            "bounding_box": None,
            "pixel_box": None,
            "foliage_ratio": foliage_ratio,
            "message": "Searching for plant leaves. Position a leaf inside the frame.",
            "stability_score": 0.0
        }

    # 4. Contour Extraction & Shape Analysis
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return {
            "leaf_detected": False,
            "confidence": 0.0,
            "bounding_box": None,
            "pixel_box": None,
            "foliage_ratio": foliage_ratio,
            "message": "No defined leaf contour detected.",
            "stability_score": 0.0
        }

    min_leaf_area = total_pixels * 0.02
    valid_contours = [c for c in contours if cv2.contourArea(c) >= min_leaf_area]

    if not valid_contours:
        return {
            "leaf_detected": False,
            "confidence": 0.25,
            "bounding_box": None,
            "pixel_box": None,
            "foliage_ratio": foliage_ratio,
            "message": "Leaf candidate is too small or distant. Bring camera closer.",
            "stability_score": 0.1
        }

    dominant_contour = max(valid_contours, key=cv2.contourArea)
    c_area = cv2.contourArea(dominant_contour)
    bx, by, bw, bh = cv2.boundingRect(dominant_contour)

    # 5. Texture & Gradient Analysis
    gray = cv2.cvtColor(cv_img_rgb, cv2.COLOR_RGB2GRAY)
    roi_gray = gray[by:by+bh, bx:bx+bw]
    laplacian_var = float(cv2.Laplacian(roi_gray, cv2.CV_64F).var()) if roi_gray.size > 0 else 0.0

    hull = cv2.convexHull(dominant_contour)
    hull_area = cv2.contourArea(hull)
    solidity = float(c_area / max(1.0, hull_area))
    aspect_ratio = float(bw) / max(1.0, float(bh))

    is_valid_shape = 0.20 <= aspect_ratio <= 4.5 and solidity >= 0.22
    has_realistic_texture = laplacian_var >= 8.0  # rejects perfectly flat synthetic solids

    confidence_components = [
        min(1.0, foliage_ratio / 30.0) * 0.35,
        min(1.0, c_area / (total_pixels * 0.25)) * 0.25,
        (1.0 if is_valid_shape else 0.3) * 0.20,
        (1.0 if has_realistic_texture else 0.2) * 0.20
    ]
    confidence = round(float(sum(confidence_components)), 2)
    confidence = min(0.99, max(0.10, confidence))

    leaf_detected = is_valid_shape and has_realistic_texture and (confidence >= 0.40 or foliage_ratio >= 8.0)

    norm_box = {
        "x": round(float(bx / w) * 100, 1),
        "y": round(float(by / h) * 100, 1),
        "width": round(float(bw / w) * 100, 1),
        "height": round(float(bh / h) * 100, 1),
        "area_pct": round(float(c_area / total_pixels) * 100, 1)
    }

    pixel_box = {
        "x": int(bx),
        "y": int(by),
        "width": int(bw),
        "height": int(bh)
    }

    if leaf_detected:
        if confidence >= 0.75:
            msg = "Leaf Detected Successfully — Position Locked."
        else:
            msg = "Leaf Detected — Hold camera steady."
    else:
        msg = "Adjust position or lighting to frame the leaf clearly."

    return {
        "leaf_detected": bool(leaf_detected),
        "confidence": confidence,
        "bounding_box": norm_box,
        "pixel_box": pixel_box,
        "foliage_ratio": foliage_ratio,
        "solidity": round(solidity, 2),
        "laplacian_var": round(laplacian_var, 1),
        "aspect_ratio": round(aspect_ratio, 2),
        "message": msg,
        "stability_score": round(solidity * min(1.0, laplacian_var / 50.0), 2)
    }


def crop_leaf_roi(cv_img_rgb, bounding_box_norm, padding=0.20):
    """
    Extracts the leaf region from an image with context padding,
    ensuring surrounding leaf edges are fully preserved for PyTorch inference.
    """
    h, w = cv_img_rgb.shape[:2]
    bx = int((bounding_box_norm["x"] / 100.0) * w)
    by = int((bounding_box_norm["y"] / 100.0) * h)
    bw = int((bounding_box_norm["width"] / 100.0) * w)
    bh = int((bounding_box_norm["height"] / 100.0) * h)

    pad_w = int(bw * padding)
    pad_h = int(bh * padding)

    x1 = max(0, bx - pad_w)
    y1 = max(0, by - pad_h)
    x2 = min(w, bx + bw + pad_w)
    y2 = min(h, by + bh + pad_h)

    crop = cv_img_rgb[y1:y2, x1:x2]
    return crop if crop.size > 0 else cv_img_rgb
