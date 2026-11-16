# CROPCARE model card

Built and evaluated on 16 November 2026. Real trained weights are included in models/cropcare.pt.

## Supported scope

Potato and tomato only; healthy, early blight, and late blight for each crop (six joint classes).
ResNet18 initialized from ImageNet; final residual block and classifier fine-tuned for 15 epochs on CPU.
Best checkpoint: epoch 13, selected by validation loss. Training split: 1,057; validation: 341; test: 254.
PlantVillage revision: 7f7ecc7e1eaca78107e3affe7cb5abd9427e139a. Original dataset subset: 1,652 images.
Leaf identity plus exact/perceptual duplicate components stay within a split. Official leaf-map coverage: 83.23%; remaining identities use filename fallbacks and perceptual grouping.

## Measured results

| Measurement | Result |
|---|---:|
| Six-class classification accuracy, before abstention | 247/254 (97.24%) |
| Crop identification accuracy, before abstention | 98.43% |
| Macro precision / recall / F1 | 97.65% / 97.16% / 97.34% |
| Accepted diagnoses | 224/254 (88.19%) |
| Correct among accepted diagnoses | 223/224 (99.55%) |
| Uncertain diagnoses withheld | 30/254 |
| Unsupported apple leaves rejected | 49/50 |
| Unsupported corn leaves rejected | 50/50 |
| Blurred leaves rejected | 20/20 |
| Non-leaf scene photographs rejected | 2/2 |
| Automated software tests | 12 passed |

One unsupported apple leaf was incorrectly accepted. One accepted supported leaf was misclassified.
Do not interpret the accepted-only accuracy as accuracy on all submitted images. The two non-leaf photographs are far too few for a reliable non-leaf performance estimate.

The scope gate is L2 logistic regression on frozen CNN features, trained using known leaves and 803 negative images. Another 263 negative images set/check its threshold. Negative sources include six unsupported crop classes and PyTorch tutorial insect photographs. 31 leaf/perceptual neighbors of the original probe set were excluded from training and validation. Gate validation accepted 98.24% of known leaves and rejected 99.24% of negatives. Apple and corn are represented as negative classes during gate training: their probe results measure new images of known negative categories, not unseen-species generalization.

The baseline gate rejected only 62/100 unsupported leaves and one of two non-leaf photographs. Those observed failures motivated adding the learned gate. The final repeated benchmark is therefore a development evaluation. No test images train either model or set thresholds, but fresh independent evaluation is needed after this development cycle. Baseline measurements are retained in evaluation/baseline_evaluation.json.

## What is and is not verified

- Real image-file inference, healthy and diseased outputs, corrupt/blurred image handling, saved JSON, and Grad-CAM generation were exercised.
- Camera capture and cleanup were tested with a mock device. A physical camera session was not performed.
- No field deployment, independent farm dataset, mixed-infection evaluation, or universal unknown-image validation was performed.
- Grad-CAM is a coarse attention map, not lesion segmentation. Severity and affected percentage are unavailable.
- Symptoms are class-reference information, not independently detected image findings.
- Management advice is sourced. Chemical recommendations and doses are intentionally absent pending verified local crop/product labels.

## Reproduction and evidence

See README.md for Windows commands and requirements-tested.txt for tested direct dependencies.
See evaluation/evaluation.json, test_predictions.json, probe_results.json, confusion_matrix.png, training_curves.png, and software_tests.txt.
The examples folder contains one correctly accepted held-out image per class, selected only to illustrate outputs; those examples are not the evaluation sample.

Checkpoint SHA-256: caa0fac869f8d5734948abb72184931fe20fcb76c030e8a77e799d2435347d1e.
