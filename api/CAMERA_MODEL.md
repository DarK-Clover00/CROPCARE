# Live AI Camera model integration

Only the Live AI Camera capture/analysis workflow uses the new trained CROPCARE model.
The upload workflow, legacy model, samples, Flutter application, notification routes,
existing report generation, page design, tracking reticles, auto-capture and ROI controls
retain their original implementations. The README's selected camera bullet is updated.

## Run on this computer

Open PowerShell:

```powershell
cd "D:\plant disease\Plant_Disease_Detector\Plant_Disease_Detector\api\src"
..\.venv\Scripts\python.exe main.py
```

Open http://127.0.0.1:8080, choose **Live AI Camera**, allow camera access, then
choose **Capture & Analyze Leaf** (or use the existing auto-capture switch).
Camera model support: **potato and tomato**, healthy / early blight / late blight.
The live reticle remains a framing/stability aid; diagnosis runs on a captured frame,
with CPU/server latency. It is not zero-latency CNN inference on every video frame.

The camera has its own result view in the existing results card. It shows only accepted
diagnoses with confidence, explains uncertain/invalid captures, and displays original
images and labeled Grad-CAM attention where available. Severity and affected area stay
unavailable. Reference symptoms are not independent image observations. Camera reports
can be downloaded as JSON or PDF (using the existing PDF library); the existing upload report/history data is not overwritten.

## Dependencies on another machine

From the api directory, use Python 3.12 in a virtual environment:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
.venv\Scripts\python.exe -m pip install -r requirements-camera.txt
cd src
..\.venv\Scripts\python.exe main.py
```

Original requirements files remain untouched. The camera dependencies supersede their
old PyTorch/Flask pins for this runtime. On the existing machine the integration was
tested with Python 3.12.10, torch 2.14.0+cpu, torchvision 0.29.0+cpu, and Flask 3.1.3.
No retraining or external model download is needed to run the bundled checkpoint.

## Implementation and scope

- POST /api/camera/diagnose accepts JSON image data URLs or multipart image files.
- src/camera_model contains the actual trained checkpoint and copied inference runtime.
- src/camera_diagnosis.py isolates camera uploads, model loading and temporary artifacts.
- Concurrent CNN/Grad-CAM requests are serialized. Temporary images/reports are removed
  after their image bytes are included in the response; server filesystem paths are hidden.
- Empty, malformed and oversized requests return explicit errors. Missing model/dependency
  errors do not fall back to the old model. Browser requests cancel on stop, tab change,
  or camera flip, and duplicate manual/automatic capture requests are suppressed.
- Unaccepted responses expose no diagnosis confidence. The raw classifier_score is
  available in JSON for debugging but is not presented as an accepted diagnosis.
- Inference is local to your Flask server; frames are sent only when captured.

The copied model card describes the original training run. Its full evaluation artifacts
and reproducible training scripts remain in the previously delivered CROPCARE project.
Checkpoint SHA-256: caa0fac869f8d5734948abb72184931fe20fcb76c030e8a77e799d2435347d1e.
Unknown-image rejection is imperfect, field validation remains outstanding, and Grad-CAM
is attention rather than exact lesion segmentation. No chemical doses are invented.

## Tests

From the project root:

```powershell
api\.venv\Scripts\python.exe -m unittest discover -s api/tests -p "test_camera*.py" -v
node --test api/tests/camera_frontend.test.cjs
```

Real-image fixtures originate from the held-out PlantVillage subset supplied with CROPCARE.
Physical browser camera capture should also be checked on your actual device.
