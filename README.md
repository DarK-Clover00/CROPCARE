# 🌿 CropCare — Intelligent Crop Disease Detection & Agricultural Management

CropCare is an automated precision-agriculture diagnostic platform engineered to detect and diagnose plant illnesses directly from foliar photography. Utilizing PyTorch deep convolutional neural networks and OpenCV computer-vision vegetation verification, CropCare analyzes uploaded crop leaves in real time, isolates necrotic lesion areas, identifies botanical species and leaf morphology, determines pathogen severity, prescribes registered chemical and bio-fungicides with exact application rates, and generates comprehensive, downloadable clinical agricultural PDF reports.

---

## 👥 Project Owners & Engineering Team
* **Subarno Priyo Pandit** — Project Owner & Lead System Architect
* **Sufal Podder** — Project Owner & Machine Learning Engineer
* **Suchorita Ghosh** — Project Owner & Agronomic Data Specialist
* **Ayushman Paul** — Project Owner & Frontend Engineer
* **Shannidhya Guha** — Project Owner & Systems Analyst

---

## 🚀 Key Features

- **Genuine AI Computer Vision**: Softmax probability distributions across 19+ crop-pathogen classes (Potato, Tomato, Bell Pepper, Corn, Apple, Grape, Peach, Strawberry, Papaya).
- **Automated Foliar Verification**: OpenCV HSV and L\*a\*b\* color-space analysis detects authentic vegetation and rejects non-plant images.
- **Lesion Contour Segmentation**: Isolates chlorotic halos and necrotic spots, calculating the percentage of affected leaf surface area.
- **Botanical Leaf Profiling**: Identifies specific leaf names, compound leaf morphology, and taxonomic botanical species (e.g. *Solanum tuberosum*).
- **Evidence-Based Prescriptions**: Recommends chemical and biological active ingredients with field dosages, spray frequencies, PPE safety precautions, and restricted-entry intervals (REI).
- **Direct PDF Export**: One-click client-side PDF rendering (`html2pdf.js`) generates clean, clinical letterhead reports ready for print or download.
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
