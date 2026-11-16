import json
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
import torch
from .data import read_image, transform
from .model import load_model

UNCERTAIN = 'Unable to identify the crop accurately. Please capture another clear image.'
VERIFY = 'Treatment recommendation requires verification by an agricultural expert.'

def decision(logits, features, checkpoint):
    classes, cal = checkpoint['classes'], checkpoint['calibration']
    p = torch.softmax(logits.detach().cpu() / cal['temperature'], dim=-1).flatten()
    crops = sorted({name.split('___')[0] for name in classes})
    masses = {c: float(sum(p[i] for i, name in enumerate(classes) if name.split('___')[0] == c)) for c in crops}
    crop = max(masses, key=masses.get)
    candidates = [i for i, name in enumerate(classes) if name.split('___')[0] == crop]
    idx = max(candidates, key=lambda i: float(p[i]))
    confidence = float(p[idx]); conditional = confidence / max(masses[crop], 1e-8)
    z = torch.nn.functional.normalize(features.detach().cpu().reshape(1, -1), dim=1)
    distance = float(1 - (z @ cal['centers'][idx].reshape(-1, 1)).item())
    crop_ok = masses[crop] >= cal['crop_threshold']
    accepted = crop_ok and conditional >= cal['disease_threshold'] and confidence >= cal['joint_threshold'] and distance <= cal['radii'][idx]
    scope_probability = None
    if 'scope_gate' in checkpoint:
        gate = checkpoint['scope_gate']
        raw = features.detach().cpu().flatten()
        scope_probability = float(torch.sigmoid(((raw - gate['mean']) / gate['scale'] * gate['coef']).sum() + gate['intercept']))
        accepted = accepted and scope_probability >= gate['threshold']
    return {'accepted': accepted, 'crop_accepted': crop_ok, 'index': idx, 'crop': crop,
            'disease': classes[idx].split('___', 1)[1], 'confidence': confidence,
            'crop_confidence': masses[crop], 'disease_conditional_confidence': conditional,
            'embedding_distance': distance, 'distance_limit': cal['radii'][idx], 'scope_probability': scope_probability}

def quality(image):
    a = np.array(image)
    if min(image.size) < 100:
        return 'Image must be at least 100 pixels on each side.'
    gray = cv2.cvtColor(cv2.resize(a, (256, 256)), cv2.COLOR_RGB2GRAY)
    if gray.mean() < 20 or gray.mean() > 240:
        return 'Image is too dark or overexposed.'
    if cv2.Laplacian(gray, cv2.CV_64F).var() < 35:
        return 'Image is too blurry or lacks visible detail.'
    return None

def gradcam(model, x, index, image, output):
    # Direct feature gradients avoid stale hooks and work with a frozen backbone.
    model.zero_grad(set_to_none=True)
    f = model.features(x.requires_grad_(True))
    score = model.net.fc(model.net.avgpool(f).flatten(1))[0, index]
    g = torch.autograd.grad(score, f)[0]
    cam = torch.relu((g.mean((2, 3), keepdim=True) * f).sum(1))[0].detach().cpu().numpy()
    if not np.isfinite(cam).all() or cam.max() <= 0:
        return None
    cam = cv2.resize(cam / cam.max(), image.size)
    original = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    heat = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(original, .6, heat, .4, 0)
    result = np.concatenate([original, overlay], axis=1)
    # A visible legend travels with the exported image.
    banner = np.zeros((45, result.shape[1], 3), dtype=np.uint8)
    cv2.putText(banner, 'Original | Grad-CAM attention (not segmentation)', (5, 28), cv2.FONT_HERSHEY_SIMPLEX, min(.55, result.shape[1] / 1000), (255, 255, 255), 1)
    if not cv2.imwrite(str(output), np.concatenate([banner, result], axis=0)):
        raise OSError(f'Could not save {output}')
    return str(output.resolve())

def recommendation(crop, disease):
    if disease == 'healthy':
        return {'treatment': ['No disease treatment indicated by this image. Continue regular crop monitoring.'],
                'medicine_recommendations': [], 'reference_symptoms': [], 'possible_causes': [],
                'prevention': ['Maintain appropriate irrigation and crop hygiene.'], 'safety_precautions': [], 'sources': []}
    db = json.loads(Path(__file__).with_name('disease_database.json').read_text())
    return db.get(f'{crop}___{disease}', {'treatment': [VERIFY], 'medicine_recommendations': [], 'reference_symptoms': [], 'sources': []})

class Diagnoser:
    def __init__(self, checkpoint='models/cropcare.pt', device='cpu'):
        if not Path(checkpoint).is_file():
            raise FileNotFoundError(f'Trained model missing: {checkpoint}. Run cropcare.train; no dummy predictions are available.')
        self.model, self.ck = load_model(checkpoint, device)
        if 'scope_gate' not in self.ck:
            raise ValueError('Scope rejection model missing. Run python -m cropcare.rejection after CNN training.')
        self.device = device
        torch.set_num_threads(4)
    def diagnose(self, path, output='output'):
        out = Path(output)
        for sub in ('captured_images', 'analyzed_images', 'reports'):
            (out / sub).mkdir(parents=True, exist_ok=True)
        identifier = uuid4().hex
        result = {'id': identifier, 'crop_name': None, 'health_status': 'Uncertain', 'disease_name': None,
                  'confidence': None, 'severity': None, 'symptoms_detected': [], 'reference_symptoms': [],
                  'symptom_note': 'Classification does not independently detect individual symptoms.',
                  'damaged_region_detection': {'available': False, 'method': None, 'visualization': None, 'affected_area_percentage': None, 'exact_infected_regions_available': False},
                  'treatment': [VERIFY], 'medicine_recommendations': [], 'safety_precautions': [], 'prevention': []}
        try:
            im = read_image(path)
            error = quality(im)
        except (OSError, ValueError, ImageError) as e:
            im, error = None, f'Cannot decode image: {e}'
        if im is not None:
            original = out / 'captured_images' / f'{identifier}.jpg'
            im.save(original, quality=95)
            result['original_image'] = str(original.resolve())
        if error:
            result.update(health_status='Invalid image', message=error)
        else:
            x = transform()(im).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits, features = self.model(x, embeddings=True)
            d = decision(logits, features, self.ck)
            result['confidence'] = d['confidence']
            result['confidence_note'] = 'Temperature-scaled class probability; not a guarantee of correctness.'
            result['confidence_checks'] = {k: v for k, v in d.items() if k not in ('index', 'crop', 'disease')}
            if not d['accepted']:
                result['message'] = UNCERTAIN
            else:
                result.update(crop_name=d['crop'], disease_name=None if d['disease'] == 'healthy' else d['disease'].replace('_', ' '), health_status='Healthy' if d['disease'] == 'healthy' else 'Diseased')
                result.update(recommendation(d['crop'], d['disease']))
                result['message'] = 'No obvious disease detected.' if d['disease'] == 'healthy' else 'Visual pattern is consistent with the predicted class; confirm in the field.'
                if d['disease'] != 'healthy':
                    visual = gradcam(self.model, x, d['index'], im, out / 'analyzed_images' / f'{identifier}.jpg')
                    result['damaged_region_detection'].update(available=visual is not None, method='Grad-CAM attention, not pixel-level disease segmentation', visualization=visual)
        result['limitations'] = ['Supported: potato and tomato, healthy/early blight/late blight only.', 'Unknown plants and non-leaf images can evade rejection; field and open-set reliability is not established.', 'Severity and affected area are unavailable without validated segmentation.']
        report = out / 'reports' / f'{identifier}.json'
        result['report_path'] = str(report.resolve())
        report.write_text(json.dumps(result, indent=2), encoding='utf-8')
        return result

# PIL decompression errors are distinct from ordinary decode errors.
from PIL.Image import DecompressionBombError as ImageError
