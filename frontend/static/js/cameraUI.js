/**
 * CropCare v3.0 — Camera UI & Workflow Coordinator (cameraUI.js)
 * Coordinates the live camera scanner interface, mode switching, UI HUD feedback,
 * auto-capture triggers, camera permissions, device flipping, and diagnostic integration.
 */

class CropCareCameraUI {
  constructor() {
    this.camera = null;
    this.detector = null;
    this.currentMode = 'upload'; // 'upload' or 'camera'
    this.isCameraActive = false;
    this.intelligentCropEnabled = true;
    this.latestDetection = null;
    this.cameraRequest = null;
    this.cameraResult = null;
    this.savedResultVisibility = null;

    // Elements
    this.elements = {};
  }

  /**
   * Bind DOM elements and attach listeners.
   */
  init() {
    this.elements = {
      // Mode tabs
      tabUpload: document.getElementById('tabUpload'),
      tabCamera: document.getElementById('tabCamera'),
      panelUpload: document.getElementById('panelUpload'),
      panelCamera: document.getElementById('panelCamera'),

      // Live Camera panel elements
      liveVideo: document.getElementById('liveCameraVideo'),
      liveCanvas: document.getElementById('liveCameraOverlay'),
      cameraContainer: document.getElementById('liveCameraContainer'),
      cameraStatusDot: document.getElementById('cameraStatusDot'),
      cameraStatusText: document.getElementById('cameraStatusText'),
      detectionBadge: document.getElementById('detectionBadge'),
      btnStartStopCamera: document.getElementById('btnStartStopCamera'),
      btnSwitchCamera: document.getElementById('btnSwitchCamera'),
      btnCaptureAnalyze: document.getElementById('btnCaptureAnalyze'),
      chkAutoCapture: document.getElementById('chkAutoCapture'),
      chkIntelligentCrop: document.getElementById('chkIntelligentCrop'),
      autoCaptureTimerBadge: document.getElementById('autoCaptureTimerBadge'),
      cameraErrorBanner: document.getElementById('cameraErrorBanner'),
      cameraErrorMsg: document.getElementById('cameraErrorMsg'),

      // Progress & Results elements
      progressCard: document.getElementById('progressCard'),
      progressText: document.getElementById('progressStepText'),
      progressBar: document.getElementById('progressBarFill'),
      diagnoseBtn: document.getElementById('diagnoseBtn'),
      previewWrapper: document.getElementById('previewWrapper'),
      previewImg: document.getElementById('previewImg')
    };

    if (!this.elements.liveVideo || !this.elements.liveCanvas) {
      console.warn('[CropCareCameraUI] Live camera elements not found in DOM.');
      return;
    }

    // Initialize Camera Controller
    this.camera = new CropCareCamera(this.elements.liveVideo, {
      onStateChange: (state, message) => this.onCameraStateChange(state, message),
      onError: (err, title, message) => this.onCameraError(err, title, message)
    });

    // Initialize Leaf Detector
    this.detector = new CropCareLeafDetector(this.elements.liveVideo, this.elements.liveCanvas, {
      fps: 15,
      lockDurationMs: 1100,
      autoCaptureDelayMs: 1600,
      onDetectionUpdate: (det) => this.onDetectionUpdate(det),
      onAutoCapture: (det) => this.onAutoCaptureTriggered(det)
    });

    this.initCameraResults();
    document.querySelectorAll('[onclick="openReportModal()"]')?.forEach(button => {
      button.addEventListener('click', event => {
        if (this.currentMode !== 'camera') return;
        event.preventDefault(); event.stopImmediatePropagation();
        this.showToast('Use the camera report download buttons in Live camera result.');
      }, true);
    });
    window.addEventListener('pagehide', () => this.stopCamera());
    this.bindEvents();
    this.syncCanvasDimensions();
    window.addEventListener('resize', () => this.syncCanvasDimensions());
  }

  /**
   * Bind event listeners.
   */
  bindEvents() {
    // Mode Switching
    if (this.elements.tabUpload) {
      this.elements.tabUpload.addEventListener('click', () => this.setMode('upload'));
    }
    if (this.elements.tabCamera) {
      this.elements.tabCamera.addEventListener('click', () => this.setMode('camera'));
    }

    // Start / Stop Camera Button
    if (this.elements.btnStartStopCamera) {
      this.elements.btnStartStopCamera.addEventListener('click', () => {
        if (this.isCameraActive) {
          this.stopCamera();
        } else {
          this.startCamera();
        }
      });
    }

    // Switch Camera Button
    if (this.elements.btnSwitchCamera) {
      this.elements.btnSwitchCamera.addEventListener('click', async () => {
        if (!this.isCameraActive) return;
        try {
          this.cancelCameraAnalysis();
          this.detector.stop();
          await this.camera.switchCamera();
          this.detector.start();
          this.showToast('Switched camera');
        } catch (e) {
          console.warn('[CropCareCameraUI] Camera switch error:', e);
        }
      });
    }

    // Manual Capture & Analyze Button
    if (this.elements.btnCaptureAnalyze) {
      this.elements.btnCaptureAnalyze.addEventListener('click', () => {
        this.captureAndAnalyze();
      });
    }

    // Auto-Capture Checkbox
    if (this.elements.chkAutoCapture) {
      this.elements.chkAutoCapture.addEventListener('change', (e) => {
        const enabled = e.target.checked;
        this.detector.setAutoCapture(enabled);
        if (this.elements.autoCaptureTimerBadge) {
          this.elements.autoCaptureTimerBadge.style.display = enabled ? 'inline-flex' : 'none';
        }
        this.showToast(enabled ? 'Auto-capture enabled (captures when held steady)' : 'Auto-capture disabled');
      });
    }

    // Intelligent Crop Checkbox
    if (this.elements.chkIntelligentCrop) {
      this.elements.chkIntelligentCrop.addEventListener('change', (e) => {
        this.intelligentCropEnabled = e.target.checked;
      });
    }
  }

  /**
   * Set active input mode: 'upload' or 'camera'.
   */
  setMode(mode) {
    if (mode !== this.currentMode) this.showCameraResults(mode === 'camera');
    if (mode === 'upload') this.cancelCameraAnalysis();
    this.currentMode = mode;

    if (mode === 'upload') {
      if (this.elements.tabUpload) this.elements.tabUpload.classList.add('active');
      if (this.elements.tabCamera) this.elements.tabCamera.classList.remove('active');
      if (this.elements.panelUpload) this.elements.panelUpload.style.display = 'block';
      if (this.elements.panelCamera) this.elements.panelCamera.style.display = 'none';
      // Automatically pause camera when leaving to save resources
      if (this.isCameraActive) {
        this.stopCamera();
      }
    } else {
      if (this.elements.tabCamera) this.elements.tabCamera.classList.add('active');
      if (this.elements.tabUpload) this.elements.tabUpload.classList.remove('active');
      if (this.elements.panelCamera) this.elements.panelCamera.style.display = 'block';
      if (this.elements.panelUpload) this.elements.panelUpload.style.display = 'none';
      this.syncCanvasDimensions();

      // Automatically activate camera when user opens the Live AI Camera tab
      if (!this.isCameraActive) {
        this.startCamera();
      }
    }
  }

  /**
   * Start camera and leaf detection.
   */
  async startCamera() {
    this.hideErrorBanner();
    try {
      await this.camera.start();
      this.isCameraActive = true;
      this.syncCanvasDimensions();
      this.detector.start();

      if (this.elements.btnStartStopCamera) {
        this.elements.btnStartStopCamera.innerHTML = '<span>⏹️</span> Stop Camera';
        this.elements.btnStartStopCamera.classList.remove('btn-primary');
        this.elements.btnStartStopCamera.classList.add('btn-secondary');
      }
      if (this.elements.btnCaptureAnalyze) {
        this.elements.btnCaptureAnalyze.disabled = false;
      }
    } catch (err) {
      console.warn('[CropCareCameraUI] Start camera failed:', err);
    }
  }

  /**
   * Stop camera and detection engine.
   */
  stopCamera() {
    this.cancelCameraAnalysis();
    if (this.detector) {
      this.detector.stop();
    }
    if (this.camera) {
      this.camera.stop();
    }
    this.isCameraActive = false;

    if (this.elements.btnStartStopCamera) {
      this.elements.btnStartStopCamera.innerHTML = '<span>📷</span> Open Live Camera';
      this.elements.btnStartStopCamera.classList.remove('btn-secondary');
      this.elements.btnStartStopCamera.classList.add('btn-primary');
    }
    if (this.elements.btnCaptureAnalyze) {
      this.elements.btnCaptureAnalyze.disabled = true;
    }
    if (this.elements.cameraStatusDot) {
      this.elements.cameraStatusDot.className = 'status-dot dot-inactive';
    }
    if (this.elements.cameraStatusText) {
      this.elements.cameraStatusText.textContent = 'Camera Inactive';
    }
    if (this.elements.detectionBadge) {
      this.elements.detectionBadge.className = 'status-pill pill-idle';
      this.elements.detectionBadge.innerHTML = '<span>🔍</span> Ready to Start';
    }
  }

  /**
   * Callback on camera state transitions.
   */
  onCameraStateChange(state, message) {
    if (this.elements.cameraStatusText) {
      this.elements.cameraStatusText.textContent = message;
    }
    if (this.elements.cameraStatusDot) {
      if (state === 'ACTIVE') {
        this.elements.cameraStatusDot.className = 'status-dot dot-active';
      } else if (state === 'INITIALIZING') {
        this.elements.cameraStatusDot.className = 'status-dot dot-pending';
      } else {
        this.elements.cameraStatusDot.className = 'status-dot dot-inactive';
      }
    }
  }

  /**
   * Callback on camera permission or hardware errors.
   */
  onCameraError(err, title, message) {
    this.showErrorBanner(message || err.message);
    this.stopCamera();
    this.showToast(message || err.message);
  }

  /**
   * Callback on real-time leaf detection updates.
   */
  onDetectionUpdate(det) {
    this.latestDetection = det;
    if (this.cameraRequest) return;
    const badge = this.elements.detectionBadge;
    if (!badge) return;

    if (det.status === 'SEARCHING') {
      badge.className = 'status-pill pill-searching';
      badge.innerHTML = '<span>🔍</span> Searching for Plant Leaves...';
      if (this.elements.btnCaptureAnalyze) {
        this.elements.btnCaptureAnalyze.classList.remove('btn-pulse-ready');
      }
    } else if (det.status === 'LEAF_DETECTED') {
      const confPct = Math.round(det.confidence * 100);
      badge.className = 'status-pill pill-detected';
      badge.innerHTML = `<span>🌿</span> Leaf Candidate — Hold Steady`;
      if (this.elements.btnCaptureAnalyze) {
        this.elements.btnCaptureAnalyze.classList.remove('btn-pulse-ready');
      }
    } else if (det.status === 'POSITION_LOCKED') {
      const confPct = Math.round(det.confidence * 100);
      badge.className = 'status-pill pill-locked';
      if (det.autoCaptureCountdown !== null) {
        badge.innerHTML = `<span>⏱️</span> Auto-Capturing in ${det.autoCaptureCountdown}s...`;
      } else {
        badge.innerHTML = `<span>🔒</span> Leaf Position Locked — Ready to Analyze`;
      }
      if (this.elements.btnCaptureAnalyze) {
        this.elements.btnCaptureAnalyze.classList.add('btn-pulse-ready');
      }
    }
  }

  /**
   * Callback when auto-capture countdown finishes.
   */
  onAutoCaptureTriggered(det) {
    this.showToast('📸 Leaf position locked — Auto-capturing!');
    this.captureAndAnalyze();
  }

  /**
   * Capture high-res frame and dispatch to existing diagnosis engine.
   */
  async captureAndAnalyze() {
    if (this.cameraRequest) return;
    if (!this.elements.liveVideo || !this.isCameraActive) {
      this.showToast('Camera is not active.');
      return;
    }
    const request = new AbortController();
    this.cameraRequest = request;
    this.triggerShutterFlash();
    this.elements.btnCaptureAnalyze.disabled = true;
    try {
      const hasLeaf = this.latestDetection && ['LEAF_DETECTED', 'POSITION_LOCKED'].includes(this.latestDetection.status);
      const dataUrl = CropCareCapture.captureFrame(this.elements.liveVideo, {
        cropLeaf: this.intelligentCropEnabled && hasLeaf,
        leafBox: hasLeaf ? this.latestDetection.box : null,
        padding: 0.24,
        quality: 0.94
      });
      // Camera-only feedback: never write into the upload report or its progress state.
      this.elements.detectionBadge.className = 'status-pill pill-analyzing';
      this.elements.detectionBadge.textContent = 'Analyzing captured leaf…';
      this.cameraResult.textContent = 'Analyzing this capture. Please wait…';
      const result = await CropCareCapture.diagnoseImage(dataUrl, { signal: request.signal });
      if (this.cameraRequest !== request || request.signal.aborted || this.currentMode !== 'camera') return;
      this.renderCameraResult(result);
      this.elements.detectionBadge.textContent = result.accepted ? 'Diagnosis completed' : 'Uncertain — capture again';
      this.showToast(result.accepted ? 'Camera diagnosis complete.' : result.message);
      if (window.innerWidth < 1024) this.cameraResult.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
      if (this.cameraRequest === request && !request.signal.aborted) {
        this.cameraResult.textContent = error.message;
        this.showToast('Camera analysis failed: ' + error.message);
      }
    } finally {
      if (this.cameraRequest === request) {
        this.cameraRequest = null;
        this.elements.btnCaptureAnalyze.disabled = !this.isCameraActive;
      }
    }
  }

  cancelCameraAnalysis() {
    if (this.cameraRequest) {
      this.cameraRequest.abort();
      this.cameraRequest = null;
      if (this.cameraResult) this.cameraResult.textContent = 'Analysis cancelled. Capture a clear leaf to try again.';
    }
    if (this.elements.btnCaptureAnalyze) this.elements.btnCaptureAnalyze.disabled = !this.isCameraActive;
  }

  initCameraResults() {
    const legacy = document.getElementById('diagnosticPanel');
    if (!legacy) return;
    this.cameraResult = document.createElement('section');
    this.cameraResult.id = 'cameraDiagnosticResult';
    this.cameraResult.setAttribute('aria-live', 'polite');
    this.cameraResult.style.cssText = 'display:none;padding:20px;line-height:1.6;overflow-wrap:anywhere';
    legacy.parentNode.appendChild(this.cameraResult);
    this.cameraResult.textContent = 'Live camera model: potato and tomato — healthy, early blight and late blight. Capture a clear leaf to analyze. The moving reticle is a framing aid, not a disease diagnosis.';
  }

  showCameraResults(show) {
    if (!this.cameraResult) return;
    const legacy = ['emptyState', 'diagnosticPanel', 'extendedAgronomicSection'].map(id => document.getElementById(id)).filter(Boolean);
    if (show) {
      this.savedResultVisibility = legacy.map(element => [element, element.style.display]);
      legacy.forEach(element => { element.style.display = 'none'; });
    } else if (this.savedResultVisibility) {
      this.savedResultVisibility.forEach(([element, display]) => { element.style.display = display; });
      this.savedResultVisibility = null;
    }
    this.cameraResult.style.display = show ? 'block' : 'none';
  }

  renderCameraResult(data) {
    const host = this.cameraResult;
    host.replaceChildren();
    const add = (tag, text, parent = host) => {
      const element = document.createElement(tag);
      element.textContent = text;
      parent.appendChild(element);
      return element;
    };
    add('h3', 'Live camera result');
    add('p', 'Model support: potato and tomato • healthy, early blight and late blight.');
    add('strong', data.health_status || 'Uncertain');
    add('p', data.message || '');
    if (data.accepted) {
      add('p', `Crop: ${data.crop_name}`);
      add('p', `Disease: ${data.disease_name || 'No obvious disease detected'}`);
      add('p', `Model confidence: ${(data.confidence * 100).toFixed(2)}%`);
      const numRegions = data.num_detected_regions !== undefined 
        ? data.num_detected_regions 
        : (data.damaged_region_detection?.regions?.length || 0);
      const affectedArea = data.affected_area_percentage !== undefined 
        ? `${data.affected_area_percentage}%` 
        : (data.estimated_affected_leaf_area || (data.health_status === 'Healthy' ? '0.0%' : 'Unavailable'));
      add('p', `Number of Detected Regions: ${numRegions}`);
      add('p', `Estimated Affected Leaf Area: ${affectedArea}`);
    } else {
      add('p', 'No diagnosis accepted. Confidence: unavailable.');
      add('p', 'Severity: unavailable • Affected leaf area: unavailable');
    }
    const section = (title, entries) => {
      if (!entries?.length) return;
      add('h4', title);
      const list = add('ul', '');
      entries.forEach(text => add('li', text, list));
    };
    section('Reference symptoms (not individually detected)', data.reference_symptoms);
    section('Management guidance', data.treatment);
    section('Prevention', data.prevention);
    section('Precautions', data.safety_precautions);
    if (data.health_status === 'Healthy') {
      add('p', 'No disease treatment is indicated by this image. Continue regular monitoring.');
    } else if (data.accepted) {
      add('p', 'Chemical recommendations require a verified local crop/product label; no dosage is prescribed.');
    }
    const picture = (url, label) => {
      if (typeof url !== 'string' || !url.startsWith('data:image/jpeg;base64,')) return;
      const figure = add('figure', '');
      figure.style.margin = '16px 0';
      const image = add('img', '', figure);
      image.src = url; image.alt = label;
      image.style.cssText = 'width:100%;height:auto;border-radius:12px';
      add('figcaption', label, figure);
    };
    const regions = data.damaged_region_detection || {};
    const imageDownload = (url, label, filename) => {
      if (typeof url !== 'string' || !url.startsWith('data:image/jpeg;base64,')) return;
      const link = add('a', label);
      link.className = 'btn-secondary'; link.href = url; link.download = filename;
      link.style.display = 'inline-block'; link.style.margin = '6px 6px 6px 0';
      link.setAttribute('data-html2canvas-ignore', 'true');
    };
    if (regions.annotated_image && regions.regions?.length) {
      add('h4', `Suspected disease areas (${regions.regions.length})`);
      const figure = add('figure', ''); figure.style.margin = '16px 0';
      const image = add('img', '', figure);
      image.src = regions.annotated_image;
      image.alt = 'Numbered suspected lesion regions in the captured leaf';
      image.style.cssText = 'width:100%;height:auto;border-radius:12px';
      const caption = add('figcaption', 'Numbered areas are visual candidates, not confirmed infected pixels.', figure);
      const toggle = add('button', 'Hide detection areas');
      toggle.type = 'button'; toggle.className = 'btn-secondary';
      toggle.setAttribute('data-html2canvas-ignore', 'true');
      let visible = true;
      toggle.addEventListener('click', () => {
        visible = !visible;
        image.src = visible ? regions.annotated_image : data.original_image;
        image.alt = visible ? 'Numbered suspected lesion regions in the captured leaf' : 'Original captured leaf';
        toggle.textContent = visible ? 'Hide detection areas' : 'View AI Detection Areas';
        caption.textContent = visible ? 'Numbered areas are visual candidates, not confirmed infected pixels.' : 'Original captured leaf image';
      });
      add('p', regions.region_notice);
      imageDownload(regions.annotated_image, 'Save image with numbered areas', `cropcare-areas-${data.id}.jpg`);

      // Area-Wise Breakdown Table
      const table = add('table', '');
      table.className = 'rep-table';
      table.style.cssText = 'width:100%;margin:12px 0;border-collapse:collapse;font-size:0.85rem;';
      const areaList = data.detected_regions || regions.regions || [];
      table.innerHTML = `
        <thead>
          <tr style="background:#fee2e2;">
            <th style="padding:8px 10px;border:1px solid #cbd5e1;color:#991b1b;text-align:left;">Region</th>
            <th style="padding:8px 10px;border:1px solid #cbd5e1;color:#991b1b;text-align:left;">Detection</th>
            <th style="padding:8px 10px;border:1px solid #cbd5e1;color:#991b1b;text-align:left;">Confidence</th>
            <th style="padding:8px 10px;border:1px solid #cbd5e1;color:#991b1b;text-align:left;">Affected Area %</th>
          </tr>
        </thead>
        <tbody>
          ${areaList.map((r, i) => `
            <tr>
              <td style="padding:8px 10px;border:1px solid #cbd5e1;"><strong style="color:#b91c1c;">${r.id || r.label || ('Area ' + (i + 1))}</strong></td>
              <td style="padding:8px 10px;border:1px solid #cbd5e1;">${r.label && r.label.includes('Suspected') ? r.label : (r.finding || 'Suspected infected region')}</td>
              <td style="padding:8px 10px;border:1px solid #cbd5e1;"><span style="font-family:monospace;font-weight:700;">${r.confidence_percent ? r.confidence_percent + '%' : (r.confidence ? (r.confidence * 100).toFixed(1) + '%' : ((data.confidence || 0.9)*100).toFixed(1) + '%')}</span></td>
              <td style="padding:8px 10px;border:1px solid #cbd5e1;"><span style="font-family:monospace;font-weight:700;">${r.area_percentage_of_leaf !== undefined ? r.area_percentage_of_leaf + '%' : '—'}</span></td>
            </tr>
          `).join('')}
        </tbody>
      `;
    } else {
      picture(data.original_image, 'Captured leaf image');
      if (data.accepted && data.health_status === 'Diseased') {
        add('p', 'No reliable individual visual regions were found in this capture. This does not rule out disease.');
      }
    }
    imageDownload(data.original_image, 'Save captured image', `cropcare-capture-${data.id}.jpg`);
    picture(data.damaged_region_detection?.visualization, 'Original and Grad-CAM attention — not infected-pixel segmentation');
    section('Limitations', data.limitations);
    if (data.sources?.length) {
      add('h4', 'Agricultural references');
      data.sources.forEach(url => {
        if (!url.startsWith('https://')) return;
        const link = add('a', url);
        link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer';
        link.style.display = 'block';
      });
    }
    const pdf = add('button', 'Download camera PDF report');
    pdf.className = 'btn-secondary'; pdf.type = 'button';
    pdf.setAttribute('data-html2canvas-ignore', 'true');
    pdf.addEventListener('click', async () => {
      if (typeof window.html2pdf !== 'function') {
        this.showToast('PDF library unavailable. Download the camera JSON report instead.'); return;
      }
      try {
        await window.html2pdf().set({ filename: `cropcare-camera-${data.id}.pdf`, margin: 10,
          html2canvas: { scale: 2 }, jsPDF: { unit: 'mm', format: 'a4' } }).from(host).save();
      } catch (error) { this.showToast('Camera PDF could not be generated: ' + error.message); }
    });
    const button = add('button', 'Download camera JSON report');
    button.setAttribute('data-html2canvas-ignore', 'true');
    button.className = 'btn-secondary'; button.type = 'button';
    button.addEventListener('click', () => {
      const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
      const link = document.createElement('a');
      link.href = url; link.download = `cropcare-camera-${data.id}.json`;
      document.body.appendChild(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  }

  /**
   * Shutter flash visual effect.
   */
  triggerShutterFlash() {
    const flash = document.createElement('div');
    flash.className = 'camera-shutter-flash';
    if (this.elements.cameraContainer) {
      this.elements.cameraContainer.appendChild(flash);
      setTimeout(() => {
        if (flash.parentNode) flash.parentNode.removeChild(flash);
      }, 350);
    }
  }

  /**
   * Sync overlay canvas dimensions to video element client dimensions.
   */
  syncCanvasDimensions() {
    if (!this.elements.liveCanvas || !this.elements.liveVideo) return;
    const v = this.elements.liveVideo;
    const c = this.elements.liveCanvas;
    const rect = v.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
      c.width = rect.width;
      c.height = rect.height;
    }
  }

  showErrorBanner(msg) {
    if (this.elements.cameraErrorBanner && this.elements.cameraErrorMsg) {
      this.elements.cameraErrorMsg.textContent = msg;
      this.elements.cameraErrorBanner.style.display = 'flex';
    }
  }

  hideErrorBanner() {
    if (this.elements.cameraErrorBanner) {
      this.elements.cameraErrorBanner.style.display = 'none';
    }
  }

  showToast(msg) {
    if (window.showToast) {
      window.showToast(msg);
    } else {
      console.log('[Toast]', msg);
    }
  }
}

window.CropCareCameraUI = CropCareCameraUI;

