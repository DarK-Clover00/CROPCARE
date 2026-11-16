"""
CROPCARE v3.0 - Standalone OpenCV Camera Real-Time Foliar Capture & Diagnostic Tool
===================================================================================
1. Accesses device camera through OpenCV (cv2.VideoCapture).
2. Displays live camera feed with real-time targeting reticle and agricultural HUD.
3. Allows user to position leaf in front of camera.
4. On 'c' or SPACE: Captures frame, saves 'captured_leaf.jpg'.
5. Passes image to TwoStageCropPipeline:
   - Stage 1: Crop Identification across 100+ botanical taxonomy categories
   - Stage 2: Crop-Gated Deep Disease Identification
   - Stage 3: Area-Wise Infected-Region Detection with Red Bounding Boxes (Area 1, Area 2...)
6. Calculates true affected leaf area: (Infected Pixels / Total Leaf Pixels) * 100
7. Displays annotated result window and terminal breakdown table.
8. Saves 'analyzed_leaf_areas.jpg'.
"""

import os
import sys
import time
import io
import cv2
import numpy as np

# Ensure src directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from model_files.ml_predict import analyze_crop_image


def print_banner():
    print("=" * 78)
    print("  CROPCARE v3.0 - REAL-TIME LIVE CAMERA LEAF SCANNER & AREA-WISE AI")
    print("=" * 78)
    print("  Controls:")
    print("    [c] or [SPACE] : Capture leaf frame and run Area-Wise AI Diagnosis")
    print("    [q] or [ESC]   : Quit live camera scanner")
    print("=" * 78)


def print_diagnostic_table(results):
    print("\n" + "=" * 78)
    print("  CROPCARE AI DIAGNOSTIC REPORT (CAMERA CAPTURE)")
    print("=" * 78)
    crop = results.get("crop", "Unknown")
    species = results.get("botanical_species", "")
    disease = results.get("disease", "Unknown")
    health_status = results.get("health_status", "UNKNOWN")
    overall_conf = results.get("confidence_percent", results.get("confidence", 0) * 100)
    num_regions = results.get("num_detected_regions", 0)
    affected_pct = results.get("affected_area_percentage", 0.0)

    print(f"  Crop / Leaf Variety         : {crop} ({species})")
    print(f"  Primary Disease Diagnosis   : {disease}")
    print(f"  Health Status               : {health_status}")
    print(f"  Overall Disease Confidence  : {overall_conf:.1f}%")
    print(f"  Number of Detected Regions  : {num_regions}")
    print(f"  Estimated Affected Leaf Area: {affected_pct:.1f}%")
    print("-" * 78)
    print(f"  {'Region':<10} | {'Detection':<28} | {'Confidence':<12} | {'Leaf Area %':<12}")
    print("-" * 78)

    regions = results.get("detected_regions", [])
    if len(regions) == 0:
        if results.get("is_healthy", False):
            print("  No infected regions detected. Foliar lamina is uniform and healthy.")
        else:
            print("  No discrete lesion boundaries isolated above threshold.")
    else:
        for r in regions:
            rid = r.get("id", f"Area {r.get('region_number', 1)}")
            label = r.get("label", "Suspected infected region")
            conf = f"{r.get('confidence_percent', r.get('confidence', 0)*100):.1f}%"
            area = f"{r.get('area_percentage_of_leaf', 0.0):.2f}%"
            print(f"  {rid:<10} | {label:<28} | {conf:<12} | {area:<12}")

    print("-" * 78)
    if results.get("treatment"):
        print("  Recommended Actions:")
        for t in results["treatment"][:3]:
            print(f"    - {t}")
    print("=" * 78 + "\n")


def draw_hud(frame, status_text="Awaiting Leaf Positioning..."):
    h, w = frame.shape[:2]
    # Reticle / target box in center
    cx, cy = w // 2, h // 2
    rw, rh = int(w * 0.65), int(h * 0.70)
    x1, y1 = cx - rw // 2, cy - rh // 2
    x2, y2 = cx + rw // 2, cy + rh // 2

    # Draw darkened outer vignette
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, y1), (0, 0, 0), -1)
    cv2.rectangle(overlay, (0, y2), (w, h), (0, 0, 0), -1)
    cv2.rectangle(overlay, (0, y1), (x1, y2), (0, 0, 0), -1)
    cv2.rectangle(overlay, (x2, y1), (w, y2), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

    # Draw corner brackets for target box
    corner_len = 28
    color_reticle = (34, 197, 94)  # Emerald Green (BGR)
    thick = 2

    # Top-Left
    cv2.line(frame, (x1, y1), (x1 + corner_len, y1), color_reticle, thick)
    cv2.line(frame, (x1, y1), (x1, y1 + corner_len), color_reticle, thick)
    # Top-Right
    cv2.line(frame, (x2, y1), (x2 - corner_len, y1), color_reticle, thick)
    cv2.line(frame, (x2, y1), (x2, y1 + corner_len), color_reticle, thick)
    # Bottom-Left
    cv2.line(frame, (x1, y2), (x1 + corner_len, y2), color_reticle, thick)
    cv2.line(frame, (x1, y2), (x1, y2 - corner_len), color_reticle, thick)
    # Bottom-Right
    cv2.line(frame, (x2, y2), (x2 - corner_len, y2), color_reticle, thick)
    cv2.line(frame, (x2, y2), (x2, y2 - corner_len), color_reticle, thick)

    # Top banner bar
    cv2.rectangle(frame, (0, 0), (w, 42), (20, 20, 20), -1)
    cv2.putText(
        frame,
        "CROPCARE v3.0 - AI LIVE LEAF SCANNER",
        (16, 26),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        frame,
        "PRESS [SPACE]/[C] TO CAPTURE",
        (w - 280, 26),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (34, 197, 94),
        1,
        cv2.LINE_AA,
    )

    # Bottom status bar
    cv2.rectangle(frame, (0, h - 36), (w, h), (20, 20, 20), -1)
    cv2.putText(
        frame,
        status_text,
        (16, h - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )

    return frame


def run_camera_scanner(camera_index=0):
    print_banner()
    print(f"Initializing camera on index {camera_index}...")
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"[ERROR] Could not open camera device on index {camera_index}.")
        print("Please check webcam permissions and device connection.")
        return

    # Set desired resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    window_name = "CropCare v3.0 - Live Camera Foliar Scanner"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 960, 540)

    print("[SUCCESS] Camera activated. Position a leaf inside the reticle.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARNING] Failed to grab frame from camera.")
            time.sleep(0.05)
            continue

        display_frame = frame.copy()
        draw_hud(display_frame, "Position leaf in frame. Press [SPACE] or [C] to Diagnose.")
        cv2.imshow(window_name, display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key in [ord('q'), ord('Q'), 27]:  # 27 is ESC
            print("Exiting scanner...")
            break
        elif key in [ord('c'), ord('C'), 32]:  # 32 is SPACE
            # Capture frame
            print("\nCapturing frame for analysis...")
            captured_path = os.path.join(CURRENT_DIR, "captured_leaf.jpg")
            cv2.imwrite(captured_path, frame)
            print(f"Saved raw captured frame to: {captured_path}")

            # Show analyzing HUD
            analyzing_frame = frame.copy()
            draw_hud(analyzing_frame, "Analyzing Leaf Image with AI Neural Pipeline...")
            cv2.imshow(window_name, analyzing_frame)
            cv2.waitKey(20)

            # Convert frame to JPEG bytes
            success, encoded_img = cv2.imencode('.jpg', frame)
            if not success:
                print("[ERROR] Failed to encode frame to JPEG bytes.")
                continue

            # Run Two-Stage AI Pipeline
            t0 = time.time()
            results = analyze_crop_image(encoded_img.tobytes())
            elapsed = time.time() - t0

            print(f"Diagnosis completed in {elapsed:.2f} seconds.")
            print_diagnostic_table(results)

            # Build and display annotated result
            analyzed_path = os.path.join(CURRENT_DIR, "analyzed_leaf_areas.jpg")

            # Check if annotated image base64 exists or draw bounding boxes
            if results.get("annotated_image_base64"):
                import base64
                img_data = base64.b64decode(results["annotated_image_base64"])
                np_arr = np.frombuffer(img_data, np.uint8)
                result_display = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            else:
                result_display = frame.copy()

            # Add result header banner to display
            rh, rw = result_display.shape[:2]
            header = np.zeros((80, rw, 3), dtype=np.uint8)
            crop_name = results.get("crop", "Unknown")
            disease_name = results.get("disease", "Undetermined")
            conf = results.get("confidence_percent", 0.0)
            area_pct = results.get("affected_area_percentage", 0.0)
            num_reg = results.get("num_detected_regions", 0)

            cv2.putText(
                header,
                f"CROP: {crop_name} | DIAGNOSIS: {disease_name}",
                (14, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.72,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                header,
                f"Confidence: {conf:.1f}% | Affected Area: {area_pct:.1f}% | Detected Regions: {num_reg}",
                (14, 62),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.58,
                (34, 197, 94) if results.get("is_healthy") else (50, 50, 240),
                1,
                cv2.LINE_AA,
            )
            final_composite = np.vstack([header, result_display])

            # Save final composite
            cv2.imwrite(analyzed_path, final_composite)
            print(f"Saved analyzed diagnostic image to: {analyzed_path}")

            # Display results window
            cv2.imshow(window_name, final_composite)
            print("Press any key in the window to resume live scanning, or [q] to exit...")
            res_key = cv2.waitKey(0) & 0xFF
            if res_key in [ord('q'), ord('Q'), 27]:
                break

    cap.release()
    cv2.destroyAllWindows()
    print("Camera scanner session ended successfully.")


if __name__ == "__main__":
    cam_id = 0
    if len(sys.argv) > 1:
        try:
            cam_id = int(sys.argv[1])
        except ValueError:
            cam_id = 0
    run_camera_scanner(cam_id)
