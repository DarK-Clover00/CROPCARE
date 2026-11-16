"""Isolated CROPCARE camera API. Existing upload/diagnosis routes are unchanged."""
import base64
import binascii
import io
from pathlib import Path
import tempfile
import threading

from flask import Blueprint, jsonify, request
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import RequestEntityTooLarge

camera_api = Blueprint('cropcare_camera', __name__)
MODEL_PATH = Path(__file__).parent / 'camera_model' / 'cropcare.pt'
MAX_BYTES = 12 * 1024 * 1024
_runner = None
_lock = threading.Lock()


def _read_frame():
    # Bound reads even for requests without a Content-Length header.
    request.max_content_length = MAX_BYTES
    if request.is_json:
        data = request.get_json(silent=True)
        encoded = data.get('image') if isinstance(data, dict) else None
        if not isinstance(encoded, str) or not encoded:
            raise ValueError('Provide a captured image in the image field.')
        if encoded.startswith('data:'):
            if not encoded.startswith(('data:image/jpeg;base64,', 'data:image/png;base64,', 'data:image/webp;base64,')):
                raise ValueError('Capture a JPEG, PNG or WebP image.')
            encoded = encoded.split(',', 1)[1]
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error):
            raise ValueError('The captured image contains invalid base64 data.') from None
    elif 'image' in request.files:
        raw = request.files['image'].read(MAX_BYTES + 1)
    else:
        raise ValueError('No captured image was supplied.')
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError('The captured image is empty or too large.')
    try:
        with Image.open(io.BytesIO(raw)) as image:
            if image.format not in ('JPEG', 'PNG', 'WEBP'):
                raise ValueError('Capture a JPEG, PNG or WebP image.')
            if image.width * image.height > 40_000_000:
                raise ValueError('Captured image exceeds 40 megapixels.')
            image.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ValueError('Cannot decode the captured image. Please capture again.') from None
    return raw


def _get_runner():
    global _runner
    if not MODEL_PATH.is_file():
        raise FileNotFoundError('Camera model is missing')
    if _runner is None:
        from camera_model.predict import Diagnoser
        _runner = Diagnoser(MODEL_PATH)
    return _runner


def _image_data_url(path):
    return 'data:image/jpeg;base64,' + base64.b64encode(Path(path).read_bytes()).decode('ascii') if path else None


@camera_api.post('/api/camera/diagnose')
def camera_diagnose():
    try:
        raw = _read_frame()
    except RequestEntityTooLarge:
        return jsonify(status='error', message='Captured image is too large (12 MB maximum request).'), 413
    except ValueError as error:
        return jsonify(status='error', message=str(error)), 400
    try:
        # Grad-CAM uses autograd; serialize access to the shared model.
        with _lock:
            runner = _get_runner()
            with tempfile.TemporaryDirectory(prefix='cropcare_camera_') as temp:
                folder = Path(temp)
                frame = folder / 'frame.jpg'
                frame.write_bytes(raw)
                result = runner.diagnose(frame, folder / 'result')
                if result.get('confidence_checks', {}).get('accepted') and result['health_status'] == 'Diseased':
                    from camera_model.regions import localize_capture
                    candidates = localize_capture(frame, folder / 'numbered-areas.jpg')
                    candidates['annotated_image'] = _image_data_url(candidates['annotated_image'])
                    result['damaged_region_detection'].update(candidates)

                    # Dynamic Area-Wise Segmentation & Affected Area % calculation
                    try:
                        import cv2
                        from model_files.area_detection import detect_leaf_infected_regions
                        cv_bgr = cv2.imread(str(frame))
                        if cv_bgr is not None:
                            cv_rgb = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2RGB)
                            area_res = detect_leaf_infected_regions(cv_rgb, is_healthy=False)
                            result['affected_area_percentage'] = area_res['affected_area_percentage']
                            result['estimated_affected_leaf_area'] = f"{area_res['affected_area_percentage']}%"
                            result['num_detected_regions'] = area_res['num_regions']
                            result['detected_regions'] = area_res['regions']
                    except Exception as e:
                        print("Area detection notice in camera_diagnosis:", e)
                elif result.get('confidence_checks', {}).get('accepted') and result['health_status'] == 'Healthy':
                    result['damaged_region_detection'].update(regions=[], annotated_image=None, segmentation_validated=False)
                    result['affected_area_percentage'] = 0.0
                    result['estimated_affected_leaf_area'] = "0.0%"
                    result['num_detected_regions'] = 0
                    result['detected_regions'] = []
                else:
                    result['damaged_region_detection'].update(regions=[], annotated_image=None, segmentation_validated=False)
                result['original_image'] = _image_data_url(result.get('original_image'))
                region = result['damaged_region_detection']
                region['visualization'] = _image_data_url(region.get('visualization'))
                result.pop('report_path', None)
        accepted = result.get('confidence_checks', {}).get('accepted', False)
        result['classifier_score'] = result['confidence']
        if not accepted:
            result['confidence'] = None
        result['accepted'] = accepted
        result['pipeline'] = 'cropcare_camera'
        result['status'] = 'success' if accepted else 'uncertain'
        result['confidence_note'] = 'Confidence is shown only for accepted diagnoses. A classifier score alone does not establish that an image is a supported leaf.'
        return jsonify(result)
    except (ImportError, FileNotFoundError):
        return jsonify(status='error', message='Camera model unavailable. Follow api/CAMERA_MODEL.md to install the camera dependencies and model.'), 503
    except Exception:
        return jsonify(status='error', message='Camera analysis failed. Please capture another clear leaf image.'), 500
