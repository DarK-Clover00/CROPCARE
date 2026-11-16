"""Numbered visual lesion candidates; NOT validated disease segmentation.

This conservative single-leaf heuristic excludes the image background using a
green/yellow leaf-hull estimate, then finds interior brown/dark color anomalies.
It cannot establish pathogen identity or an affected-leaf-area percentage.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps


def leaf_mask(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    # Seed from green/yellow tissue only; brown objects outside the leaf do not
    # extend the silhouette. This assumes one prominent leaf on a plain background.
    seed = cv2.inRange(hsv, np.array([23, 35, 40]), np.array([95, 255, 255]))
    seed = cv2.morphologyEx(seed, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(seed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = np.zeros(rgb.shape[:2], np.uint8)
    if not contours:
        return result
    main = max(contours, key=cv2.contourArea)
    if cv2.contourArea(main) < rgb.shape[0] * rgb.shape[1] * .05:
        return result
    cv2.drawContours(result, [cv2.convexHull(main)], -1, 255, -1)
    return result


def find_regions(image):
    original = ImageOps.exif_transpose(image).convert('RGB')
    working = original.copy()
    working.thumbnail((768, 768))
    rgb = np.asarray(working)
    h, w = rgb.shape[:2]
    mask = leaf_mask(rgb)
    leaf_pixels = int(np.count_nonzero(mask))
    if leaf_pixels == 0:
        return [], False
    inner = cv2.erode(mask, np.ones((5, 5), np.uint8))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    local = cv2.GaussianBlur(gray, (0, 0), max(3., min(h, w) / 35))
    hue, sat, val = cv2.split(hsv)
    red, green, blue = [rgb[:, :, i].astype(float) for i in range(3)]
    brown = (hue >= 3) & (hue <= 25) & (sat >= 50) & (val >= 35) & (val <= 215) & (red >= green * .95) & (red > blue * 1.15)
    # Local contrast finds discrete dark spots, not entire uniform shadows.
    dark = (gray < 75) & (sat > 30) & (val > 25) & (local.astype(float) - gray > 18)
    candidate = ((brown | dark) & (inner > 0)).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(candidate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    selected = []
    minimum = max(4, leaf_pixels * .0008)
    for contour in sorted(contours, key=cv2.contourArea, reverse=True):
        area = cv2.contourArea(contour)
        if area < minimum or area > leaf_pixels * .30:
            continue
        x, y, width, height = cv2.boundingRect(contour)
        # Ignore edge-connected anomalies where background/shadow separation is weakest.
        boundary = cv2.subtract(mask, inner)
        if np.any(boundary[y:y+height, x:x+width]):
            continue
        sx, sy = original.width / w, original.height / h
        px, py = int(x * sx), int(y * sy)
        pw, ph = min(original.width - px, max(1, int(np.ceil(width * sx)))), min(original.height - py, max(1, int(np.ceil(height * sy))))
        selected.append({'id': len(selected) + 1, 'label': f'Area {len(selected) + 1}',
                         'x': px, 'y': py, 'width': pw, 'height': ph,
                         'normalized_box': {'x': px / original.width, 'y': py / original.height,
                                            'width': pw / original.width, 'height': ph / original.height},
                         'finding': 'Suspected visual lesion; not a confirmed infected region'})
        if len(selected) == 12:
            break
    return selected, True


def annotate_regions(image, regions):
    rgb = np.array(ImageOps.exif_transpose(image).convert('RGB'))
    h, w = rgb.shape[:2]
    thickness = max(1, round(min(h, w) / 180))
    font = max(.36, min(1.0, min(h, w) / 600))
    for region in regions:
        x, y, bw, bh = (region[k] for k in ('x', 'y', 'width', 'height'))
        color = (238, 55, 63)
        cv2.rectangle(rgb, (x, y), (x + bw - 1, y + bh - 1), color, thickness)
        label = region['label']
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font, 1)
        lx = max(0, min(x, w - tw - 8))
        ly = max(th + 6, y - 3)
        cv2.rectangle(rgb, (lx, ly - th - 5), (min(w - 1, lx + tw + 7), min(h - 1, ly + baseline)), color, -1)
        cv2.putText(rgb, label, (lx + 3, ly - 2), cv2.FONT_HERSHEY_SIMPLEX, font, (255, 255, 255), 1, cv2.LINE_AA)
    return Image.fromarray(rgb)


def localize_capture(path, output):
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert('RGB')
    regions, has_leaf = find_regions(image)
    annotated = None
    if regions:
        annotate_regions(image, regions).save(output, quality=95)
        annotated = str(Path(output))
    return {'regions': regions, 'annotated_image': annotated,
            'image_size': {'width': image.width, 'height': image.height},
            'region_method': 'Leaf-masked color and local-contrast candidates (unvalidated)',
            'region_notice': 'Numbered areas are suspected visual lesions, not confirmed infected pixels. Shadows, aging and other damage can look similar. No affected-area percentage is estimated.',
            'leaf_mask_detected': has_leaf, 'segmentation_validated': False}
