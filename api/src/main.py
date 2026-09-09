import base64
import os
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from model_files.ml_predict import analyze_crop_image

try:
    from pyfcm import FCMNotification
    from decouple import config
    push_service = FCMNotification(api_key=config('API_KEY', default=''))
except Exception as e:
    push_service = None

app = Flask("CropCare", template_folder='templates')
CORS(app)

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
        "service": "CropCare",
        "model": "PyTorch CNN Deep Classifier (19 classes)",
        "features": [
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
