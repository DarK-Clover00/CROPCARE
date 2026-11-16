import base64
import io
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from PIL import Image

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
os.chdir(SRC)  # Match the documented existing server startup directory.
import main
import camera_diagnosis


class CameraApiTests(unittest.TestCase):
    def setUp(self):
        self.client = main.app.test_client()

    def send(self, filename):
        raw = (Path(__file__).parent / 'camera_fixtures' / filename).read_bytes()
        return self.client.post('/api/camera/diagnose', json={'image': 'data:image/jpeg;base64,' + base64.b64encode(raw).decode()})

    def test_real_diseased_capture_and_attention(self):
        response = self.send('Potato___Early_blight.jpg')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['accepted'])
        self.assertEqual(data['crop_name'], 'Potato')
        self.assertEqual(data['disease_name'], 'Early blight')
        self.assertGreater(data['confidence'], .7)
        self.assertTrue(data['original_image'].startswith('data:image/jpeg;base64,'))
        region = data['damaged_region_detection']
        self.assertTrue(region['visualization'].startswith('data:image/jpeg;base64,'))
        self.assertIsNone(region['affected_area_percentage'])
        self.assertFalse(region['exact_infected_regions_available'])
        self.assertNotIn('report_path', data)
        self.assertNotIn('cropcare_camera_', response.get_data(as_text=True))

    def test_real_healthy_capture_without_treatment_or_attention(self):
        data = self.send('Tomato___healthy.jpg').get_json()
        self.assertTrue(data['accepted'])
        self.assertEqual(data['health_status'], 'Healthy')
        self.assertEqual(data['medicine_recommendations'], [])
        self.assertIsNone(data['damaged_region_detection']['visualization'])

    def test_blank_image_rejected_and_multipart_supported(self):
        buf = io.BytesIO()
        Image.new('RGB', (256, 256), (110, 110, 110)).save(buf, format='PNG')
        buf.seek(0)
        response = self.client.post('/api/camera/diagnose', data={'image': (buf, 'frame.png')})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['accepted'])
        self.assertIsNone(data['confidence'])
        self.assertIsNone(data['crop_name'])

    def test_high_classifier_score_is_not_accepted_confidence(self):
        class Runner:
            def diagnose(self, *args):
                return dict(confidence=.999, confidence_checks={'accepted': False}, original_image=None,
                            damaged_region_detection={'visualization': None}, crop_name=None,
                            health_status='Uncertain', report_path='private-path')
        with patch.object(camera_diagnosis, '_get_runner', return_value=Runner()):
            data = self.send('Tomato___healthy.jpg').get_json()
        self.assertIsNone(data['confidence'])
        self.assertEqual(data['classifier_score'], .999)
        self.assertEqual(data['status'], 'uncertain')

    def test_malformed_requests(self):
        for payload in [{}, {'image': '%%%%'}, {'image': 123}, {'image': 'bm90LWltYWdl'}, []]:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post('/api/camera/diagnose', json=payload).status_code, 400)

    def test_oversized_request(self):
        response = self.client.post('/api/camera/diagnose', json={'image': 'A' * (camera_diagnosis.MAX_BYTES + 1)})
        self.assertEqual(response.status_code, 413)

    def test_missing_model_has_no_legacy_fallback(self):
        with patch.object(camera_diagnosis, 'MODEL_PATH', SRC/'missing.pt'), patch.object(main, 'analyze_crop_image') as old:
            self.assertEqual(self.send('Tomato___healthy.jpg').status_code, 503)
            old.assert_not_called()

    def test_legacy_diagnosis_routes_keep_original_handler(self):
        for route in ['/', '/api/diagnose']:
            with patch.object(main, 'analyze_crop_image', return_value={'legacy': True}) as old, patch.object(camera_diagnosis, '_get_runner') as new:
                response = self.client.post(route, json={'image': base64.b64encode(b'old-payload').decode()})
                self.assertEqual(response.get_json(), {'legacy': True})
                old.assert_called_once_with(b'old-payload')
                new.assert_not_called()

    def test_existing_page_and_samples_still_served(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/api/samples').status_code, 200)


if __name__ == '__main__':
    unittest.main()
