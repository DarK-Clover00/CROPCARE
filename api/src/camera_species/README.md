# Local species recognition — Pl@ntNet-300K v1

This module uses the official already-trained ResNet18 checkpoint for **1,081 plant species**.
It does **not** recognize diseases for those species, does not infer healthy status,
and does not turn species probabilities into treatment recommendations. The original
CROPCARE disease classifier remains a separate model with its own supported classes.

## Source and inference

- Official project: https://github.com/plantnet/PlantNet-300K
- Exact legacy instructions: https://github.com/plantnet/PlantNet-300K/tree/main/legacy_v1
- Checkpoint: https://seafile.plantnet.org/d/01ab6658dad6447c95ae/files/?p=/resnet18_weights_best_acc.tar&dl=1
- Index mapping: https://seafile.plantnet.org/d/bed81bc15e8944969cf6/files/?p=/class_idx_to_species_id.json&dl=1
- Species names: https://seafile.plantnet.org/d/bed81bc15e8944969cf6/files/?p=/plantnet300K_species_id_2_name.json&dl=1

Architecture: torchvision ResNet18 with 1,081 outputs. The official checkpoint stores
weights under `model`; optimizer state is not used. Loading uses `weights_only=True`
and strict state-dictionary checking. No new model is trained by this module.

Preprocessing follows the official legacy pretrained configuration: EXIF-oriented RGB,
short-side resize to 256, center crop 224, ImageNet normalization. Candidate acceptance
requires probability >= 0.70 and top-two probability margin >= 0.20. These thresholds
are heuristics, not a calibrated confidence guarantee. Even an accepted result remains
a tentative species candidate and has `disease_diagnosis_available: false`.

Python call from api/src:

```python
from PIL import Image
from camera_species.species_model import identify_species
result = identify_species(Image.open('leaf.jpg'))
```

No additional runtime package is required beyond the camera pipeline's existing
PyTorch, torchvision and Pillow dependencies. Model loading is lazy and cached.
The caller should apply its image-quality and leaf-presence checks first.

## Limitations and terms

The original benchmark contains plant images, not only leaves. Species coverage is
not disease coverage and is not guaranteed coverage of the user's desired crop list.
Deployment performance on the user's webcam has not been established. Preserve the
upstream BSD-2-Clause software notice in LICENSE. The official dataset separately
tracks per-image licenses; those dataset images are not bundled here. The upstream
checkpoint download has no separate explicit model license attached in its file listing;
consult upstream terms before distributing it commercially.

See provenance.json for exact retrieved file hashes and primary sources. No 100-species
disease diagnosis claim is made.
