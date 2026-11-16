# 🌿 CropCare v3.0 — AI-Powered Live Leaf Detection & Crop Disease Management Platform

> **Detect Early. Protect Crops. Grow Better.**

CropCare v3.0 is an automated precision-agriculture diagnostic platform engineered to detect and diagnose plant illnesses directly from foliar photography and **live camera video feeds**. Utilizing PyTorch deep convolutional neural networks and OpenCV multi-spectral vegetation verification, CropCare tracks and recognizes crop leaves through a real-time camera viewfinder, isolates necrotic lesion areas, identifies botanical species and leaf morphology, determines pathogen severity, prescribes registered chemical and bio-fungicides with exact application rates, and generates comprehensive clinical agricultural PDF reports.

---

## 👥 Project Owners & Engineering Team
* **Subarno Priyo Pandit** — Project Owner & Lead System Architect
* **Sufal Podder** — Project Owner & Machine Learning Engineer
* **Suchorita Ghosh** — Project Owner & Agronomic Data Specialist
* **Ayushman Paul** — Project Owner & Frontend Engineer
* **Shannidhya Guha** — Project Owner & Systems Analyst

---

## 🚀 Key Features

- **NEW: Discrete Area-Wise Disease Detection**: Highlights distinct suspected infected regions using dynamic red bounding boxes labelled `Area 1`, `Area 2`, `Area 3`, etc., matching clinical diagnostic standards. Each lesion cluster receives individual confidence scoring and Non-Maximum Suppression (NMS) with $\text{IoU} \le 0.30$.
- **NEW: True Pixel Segmentation Affected Area**: Computes affected leaf area strictly via the true foliar mask formula: $(\sum M_{\text{infected}} / \sum M_{\text{leaf}}) \times 100$. Healthy leaves are verified with 0 infected regions and 0.0% affected area.
- **NEW: Two-Stage Crop-Gated AI Pipeline**: 
  - *Stage 1*: Botanical crop recognition across **100+ distinct agricultural plant varieties**.
  - *Stage 2*: Crop-gated disease classification that strictly bounds predictions to biologically valid pathogens, eliminating cross-crop misclassifications. Unsupported crops are recognized and guided to extension experts without false disease triggers.
- **NEW: Standalone OpenCV Camera Tool (`capture_camera.py`)**: Real-time webcam capture tool with foliar targeting reticle, key-triggered capture (<kbd>c</kbd> or <kbd>SPACE</kbd>), on-screen bounding boxes, and terminal diagnostic table.
- **NEW: Live In-Browser AI Camera**: Live HTML5 MediaDevices & Canvas viewfinder with emerald targeting reticles, laser scanning beam, front/rear camera switching (`facingMode: { ideal: "environment" }`), and instant Area-Wise breakdown table.
- **NEW: Model Validation & Evaluation Suite (`evaluate_models.py`)**: Comprehensive test runner measuring crop recognition accuracy, disjoint class gating, IoU suppression, and non-plant image rejection.
- **Genuine AI Deep Learning**: Softmax probability distributions across 19+ crop-pathogen classes (Potato, Tomato, Bell Pepper, Corn, Apple, Grape, Peach, Strawberry, Papaya).
- **Multi-Spectral Foliar Verification**: OpenCV HSV and L\*a\*b\* color-space analysis detects authentic vegetation and rejects non-plant images.
- **Botanical Leaf Profiling**: Identifies specific leaf names, compound leaf morphology, and taxonomic botanical species (e.g. *Solanum tuberosum*).
- **Evidence-Based Prescriptions**: Recommends chemical and biological active ingredients with field dosages, spray frequencies, PPE safety precautions, and restricted-entry intervals (REI).
- **Direct PDF Export**: One-click client-side PDF rendering (`html2pdf.js`) generates clean clinical reports featuring original and annotated images with the complete Area-Wise detection breakdown table.
- **Dual-View User Interface**: Single-Page Application with smooth transitions between the Home Page and the Diagnostic Dashboard.
- **Vibrant Animated Background**: High-resolution, zero-latency looping agricultural video background.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Flask, Flask-CORS, Werkzeug
- **Deep Learning**: PyTorch (`torch`, `torchvision`), NumPy, SymPy
- **Computer Vision**: OpenCV (`opencv-python`), PIL / Pillow
- **Frontend**: HTML5, Modern Vanilla CSS3 (Glassmorphism & CSS Grid), Vanilla ES6+ JavaScript
- **PDF Engine**: `html2pdf.js` (`html2canvas` + `jsPDF`)
- **Mobile Client**: Flutter / Dart

---

## 💻 Quick Start & Running Locally

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/DarK-Clover00/CROPCARE.git
cd CROPCARE
```

### 2. Set Up Virtual Environment & Dependencies
```bash
cd api
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

### 3. Run the CropCare Web Server
```bash
cd src
python main.py
```

Open your browser and navigate to:
```
http://127.0.0.1:8080/
```

---

## 📑 Technical Documentation

Detailed architecture, mathematical formulation, training methodology, and system design are documented in:
- [CROPCARE_TECHNOLOGY_AND_METHODOLOGY.txt](CROPCARE_TECHNOLOGY_AND_METHODOLOGY.txt)
- [PROJECT_DOCUMENTATION.txt](api/src/PROJECT_DOCUMENTATION.txt)

---

## 📄 License
This project is developed for agricultural intelligence and precision crop health management.
