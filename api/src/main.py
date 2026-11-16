import base64
import os
import cv2
import numpy as np
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from model_files.ml_predict import analyze_crop_image
from model_files.leaf_localization import detect_leaf_contours, crop_leaf_roi

try:
    from pyfcm import FCMNotification
    from decouple import config
    push_service = FCMNotification(api_key=config('API_KEY', default=''))
except Exception as e:
    push_service = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask("CropCare", 
            template_folder=os.path.join(BASE_DIR, 'templates'), 
            static_folder=os.path.join(BASE_DIR, 'static'))
CORS(app)

# Isolated trained-model pipeline for the Live AI Camera feature only.
from camera_diagnosis import camera_api
app.register_blueprint(camera_api)

TEST_DIR = os.path.join(os.path.dirname(__file__), 'model_files', 'test')
VIDEO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'video'))
VIDEO_FILENAME = 'make_the_picture_moving_like_a (1).mp4'


@app.route('/video/background', methods=['GET'])
def serve_background_video():
    target = os.path.join(VIDEO_DIR, VIDEO_FILENAME)
    if os.path.exists(target):
        return send_from_directory(VIDEO_DIR, VIDEO_FILENAME, mimetype='video/mp4')
    if os.path.exists(VIDEO_DIR):
        for f in os.listdir(VIDEO_DIR):
            if f.lower().endswith('.mp4'):
                return send_from_directory(VIDEO_DIR, f, mimetype='video/mp4')
    return "Background video not found", 404


@app.route('/', methods=['GET', 'POST'])
def index_or_predict():
    if request.method == 'GET':
        return render_template('index.html')

    return handle_diagnosis()


@app.route('/api/diagnose', methods=['POST'])
def api_diagnose():
    return handle_diagnosis()


@app.route('/api/detect-leaf', methods=['POST'])
def api_detect_leaf():
    """
    Dedicated endpoint for real-time OpenCV-based foliar verification and leaf localization.
    Accepts JSON { 'image': base64 } or multipart file upload.
    """
    try:
        if request.is_json:
            data = request.get_json()
            if not data or 'image' not in data:
                return jsonify({"status": "error", "message": "Missing 'image' base64 payload"}), 400
            raw_base64 = data['image']
            if ',' in raw_base64:
                raw_base64 = raw_base64.split(',', 1)[1]
            img_bytes = base64.b64decode(raw_base64)
        elif 'image' in request.files:
            file = request.files['image']
            img_bytes = file.read()
        else:
            return jsonify({"status": "error", "message": "No image data provided"}), 400

        nparr = np.frombuffer(img_bytes, np.uint8)
        cv_img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if cv_img_bgr is None:
            return jsonify({"status": "error", "message": "Failed to decode image data."}), 400

        cv_img_rgb = cv2.cvtColor(cv_img_bgr, cv2.COLOR_BGR2RGB)
        result = detect_leaf_contours(cv_img_rgb)
        result["status"] = "success"
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Leaf localization error: {str(e)}"}), 500


def handle_diagnosis():
    try:
        # Check if json with base64 image or multipart file upload
        if request.is_json:
            data = request.get_json()
            if not data or 'image' not in data:
                return jsonify({
                    "status": "error",
                    "is_plant": False,
                    "message": "Missing 'image' base64 payload in request body."
                }), 400
            
            raw_base64 = data['image']
            if ',' in raw_base64:
                raw_base64 = raw_base64.split(',', 1)[1]
            img_bytes = base64.b64decode(raw_base64)
        elif 'image' in request.files:
            file = request.files['image']
            img_bytes = file.read()
        else:
            return jsonify({
                "status": "error",
                "is_plant": False,
                "message": "No image data provided. Send base64 JSON or multipart form."
            }), 400

        result = analyze_crop_image(img_bytes)

        # Include leaf localization metadata if valid image
        try:
            nparr = np.frombuffer(img_bytes, np.uint8)
            cv_img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if cv_img_bgr is not None:
                cv_img_rgb = cv2.cvtColor(cv_img_bgr, cv2.COLOR_BGR2RGB)
                loc = detect_leaf_contours(cv_img_rgb)
                result["leaf_localization"] = {
                    "leaf_detected": loc.get("leaf_detected", False),
                    "bounding_box": loc.get("bounding_box"),
                    "confidence": loc.get("confidence", 0.0),
                    "stability_score": loc.get("stability_score", 0.0)
                }
        except Exception:
            pass

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "is_plant": False,
            "message": f"Server processing error: {str(e)}"
        }), 500


@app.route('/api/samples', methods=['GET'])
def get_sample_images():
    samples = []
    if os.path.exists(TEST_DIR):
        files = [f for f in os.listdir(TEST_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        for f in sorted(files):
            name_no_ext = os.path.splitext(f)[0]
            # Replace 'Potato' with 'Leaf' as requested
            label = name_no_ext.replace('Potato', 'Leaf ')
            if 'EarlyBlight' in label:
                label = label.replace('EarlyBlight', ' Early Blight ')
            elif 'Healthy' in label:
                label = label.replace('Healthy', ' Healthy ')
            elif 'YellowCurlVirus' in label:
                label = label.replace('YellowCurlVirus', ' Yellow Curl ')

            clean_label = " ".join(label.split())
            samples.append({
                'name': f,
                'label': clean_label,
                'url': f'/api/sample-image/{f}'
            })
    return jsonify(samples)


@app.route('/api/sample-image/<path:filename>', methods=['GET'])
def serve_sample_image(filename):
    return send_from_directory(TEST_DIR, filename)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "service": "CropCare v3.0",
        "tagline": "Detect Early. Protect Crops. Grow Better.",
        "model": "PyTorch CNN Deep Classifier (19 classes)",
        "features": [
            "Live AI camera leaf detection and localization",
            "Real-time leaf bounding boxes and stability lock",
            "Leaf verification",
            "Computer vision lesion segmentation",
            "Affected area percentage",
            "Visual disease overlays",
            "Multi-stage diagnostic pipeline",
            "Agronomic prescription & safety guide",
            "Downloadable PDF report"
        ]
    })


@app.route('/notification', methods=['POST'])
def send_notification():
    if push_service is None:
        return jsonify({"status": "notice", "message": "FCM notification service not configured."}), 200
    try:
        key_dict = request.get_json()
        plant = key_dict.get('plant', 'Crop')
        disease = key_dict.get('disease', 'Condition')
        user = key_dict.get('user', 'Farmer')

        message = f"Plant {plant} diagnosed with {disease} recently by {user}"
        data_message = {
            "title": "AgriVision Alert",
            "body": message,
        }

        result = push_service.notify_topic_subscribers(
            data_message=data_message, topic_name="cropcare")
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
