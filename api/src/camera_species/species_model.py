"""Official Pl@ntNet-300K v1 species-only inference, isolated from disease diagnosis.

Output scores are uncalibrated softmax values. An accepted candidate is not a
verified botanical identification and does not imply healthy or diseased status.
"""
import json
from pathlib import Path
import threading

import torch
from torchvision.models import resnet18
from torchvision import transforms
from PIL import Image, ImageOps

BASE_DIR = Path(__file__).resolve().parent
WEIGHTS_PATH = BASE_DIR / 'resnet18_weights_best_acc.tar'
PROBABILITY_THRESHOLD = 0.70
MARGIN_THRESHOLD = 0.20
SOURCE_URL = 'https://github.com/plantnet/PlantNet-300K/tree/main/legacy_v1'
_instance = None
_load_lock = threading.Lock()


class SpeciesClassifier:
    def __init__(self, root=BASE_DIR):
        root = Path(root)
        self.class_map = json.loads((root / 'class_idx_to_species_id.json').read_text(encoding='utf-8-sig'))
        names = json.loads((root / 'species_id_to_name.json').read_text(encoding='utf-8-sig'))
        self.count = len(self.class_map)
        if self.count != 1081 or set(self.class_map) != {str(i) for i in range(self.count)}:
            raise ValueError('Official species label mapping is incomplete or inconsistent.')
        self.names = [names[str(self.class_map[str(i)])] for i in range(self.count)]
        if len(set(self.class_map.values())) != self.count:
            raise ValueError('Species mapping contains duplicate species IDs.')
        checkpoint = torch.load(root / WEIGHTS_PATH.name, map_location='cpu', weights_only=True)
        self.model = resnet18(weights=None, num_classes=self.count)
        self.model.load_state_dict(checkpoint['model'], strict=True)
        self.model.eval()
        self.epoch = int(checkpoint.get('epoch', -1))
        self.transform = transforms.Compose([
            transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

    def identify(self, image):
        if not isinstance(image, Image.Image):
            raise TypeError('identify_species expects a decoded PIL image.')
        image = ImageOps.exif_transpose(image).convert('RGB')
        if min(image.size) < 100 or image.width * image.height > 40_000_000:
            raise ValueError('Use a clear image at least 100 pixels per side and at most 40 megapixels.')
        tensor = self.transform(image).unsqueeze(0)
        with torch.inference_mode():
            probabilities = self.model(tensor).softmax(dim=-1)[0]
        values, indexes = probabilities.topk(3)
        index = int(indexes[0])
        probability = float(values[0])
        margin = float(values[0] - values[1])
        accepted = probability >= PROBABILITY_THRESHOLD and margin >= MARGIN_THRESHOLD
        return {
            'available': True,
            'accepted': accepted,
            'candidate_only': True,
            'scientific_name': self.names[index],
            'species_id': str(self.class_map[str(index)]),
            'probability': probability,
            'runner_up_margin': margin,
            'supported_species': self.count,
            'thresholds': {'probability': PROBABILITY_THRESHOLD, 'runner_up_margin': MARGIN_THRESHOLD},
            'top_candidates': [
                {'scientific_name': self.names[int(i)], 'probability': float(p)}
                for p, i in zip(values, indexes)
            ],
            'disease_diagnosis_available': False,
            'health_status': 'Not assessed by the species model',
            'score_note': 'Uncalibrated species-classifier score; not disease confidence or a guarantee of identification.',
            'limitations': [
                'Training covers plant photographs, including flowers and whole plants, not exclusively camera leaf close-ups.',
                'This model has no disease or healthy/diseased labels.',
                'The score and margin thresholds are conservative heuristics, not validated open-set rejection.',
                'A species outside the 1,081 training labels may still resemble a supported species.',
            ],
            'model_source': SOURCE_URL,
        }


def get_classifier():
    global _instance
    if _instance is None:
        with _load_lock:
            if _instance is None:
                _instance = SpeciesClassifier()
    return _instance


def identify_species(image):
    return get_classifier().identify(image)


def supported_species():
    root = BASE_DIR
    mapping = json.loads((root / 'class_idx_to_species_id.json').read_text(encoding='utf-8-sig'))
    names = json.loads((root / 'species_id_to_name.json').read_text(encoding='utf-8-sig'))
    return [{'species_id': str(mapping[str(i)]), 'scientific_name': names[str(mapping[str(i)])]}
            for i in range(len(mapping))]
