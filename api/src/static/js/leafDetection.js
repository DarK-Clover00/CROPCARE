/**
 * CropCare v3.0 — Real-Time Leaf Detection Engine (leafDetection.js)
 * High-speed, zero-latency client-side computer vision engine.
 * Continuously analyzes camera video frames via HTML5 Canvas, transforms to
 * HSV & LAB color spaces, groups foliar vegetation clusters, evaluates shape
 * and texture metrics, tracks temporal stability, and powers auto-capture.
 */

class CropCareLeafDetector {
  constructor(videoElement, overlayCanvas, options = {}) {
    this.video = videoElement;
    this.overlayCanvas = overlayCanvas;
    this.overlayCtx = overlayCanvas ? overlayCanvas.getContext('2d') : null;

    // Downscaled offscreen canvas for high-speed analysis
    this.procCanvas = document.createElement('canvas');
    this.procWidth = 240;
    this.procHeight = 160;
    this.procCanvas.width = this.procWidth;
    this.procCanvas.height = this.procHeight;
    this.procCtx = this.procCanvas.getContext('2d', { willReadFrequently: true });

    this.isRunning = false;
    this.animationFrameId = null;
    this.lastProcessTime = 0;
    this.targetFps = options.fps || 15; // 15 FPS provides optimal balance of smoothness and low battery/CPU drain
    this.frameInterval = 1000 / this.targetFps;

    // Detection status states: 'SEARCHING', 'LEAF_DETECTED', 'POSITION_LOCKED'
    this.status = 'SEARCHING';
    this.currentBox = null;      // raw detection box {x, y, width, height, area_pct}
    this.smoothBox = null;       // exponentially smoothed box for jitter-free rendering
    this.foliageRatio = 0.0;
    this.confidence = 0.0;

    // Stability tracking
    this.stabilityHistory = [];
    this.stableStartTime = null;
    this.isPositionLocked = false;
    this.lockRequiredDurationMs = options.lockDurationMs || 1000;

    // Auto-capture configuration
    this.autoCaptureEnabled = false;
    this.autoCaptureDelayMs = options.autoCaptureDelayMs || 1500;
    this.autoCaptureStartTime = null;
    this.autoCaptureTriggered = false;

    // Callbacks
    this.onDetectionUpdate = options.onDetectionUpdate || (() => {});
    this.onAutoCapture = options.onAutoCapture || (() => {});

    // Scanning beam animation angle
    this.scanBeamPhase = 0;
  }

  /**
   * Start live analysis loop.
   */
  start() {
    if (this.isRunning) return;
    this.isRunning = true;
    this.stabilityHistory = [];
    this.stableStartTime = null;
    this.isPositionLocked = false;
    this.autoCaptureStartTime = null;
    this.autoCaptureTriggered = false;
    this._loop(0);
  }

  /**
   * Stop analysis loop and clear canvas.
   */
  stop() {
    this.isRunning = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
    if (this.overlayCtx && this.overlayCanvas) {
      this.overlayCtx.clearRect(0, 0, this.overlayCanvas.width, this.overlayCanvas.height);
    }
    this.status = 'SEARCHING';
    this.currentBox = null;
    this.smoothBox = null;
    this.isPositionLocked = false;
    this.autoCaptureStartTime = null;
    this.autoCaptureTriggered = false;
  }

  setAutoCapture(enabled, delayMs = 1500) {
    this.autoCaptureEnabled = !!enabled;
    this.autoCaptureDelayMs = delayMs;
    this.autoCaptureStartTime = null;
    this.autoCaptureTriggered = false;
  }

  /**
   * Main requestAnimationFrame loop.
   */
  _loop(timestamp) {
    if (!this.isRunning) return;

    this.animationFrameId = requestAnimationFrame((ts) => this._loop(ts));

    // Throttle frame processing frequency
    const elapsed = timestamp - this.lastProcessTime;
    if (elapsed < this.frameInterval) {
      // Still update overlay animations (scan beam & smooth interpolation) even when skipping a CV step
      this._renderOverlay(timestamp);
      return;
    }

    this.lastProcessTime = timestamp;

    if (this.video && this.video.readyState >= 2 && !this.video.paused && !this.video.ended) {
      this._processFrame(timestamp);
    }

    this._renderOverlay(timestamp);
  }

  /**
   * Process downscaled frame with multi-spectral color and morphological clustering.
   */
  _processFrame(timestamp) {
    const pw = this.procWidth;
    const ph = this.procHeight;

    this.procCtx.drawImage(this.video, 0, 0, pw, ph);
    const imgData = this.procCtx.getImageData(0, 0, pw, ph);
    const data = imgData.data;

    let foliageCount = 0;
    let minX = pw, maxX = 0, minY = ph, maxY = 0;
    let gradientSum = 0;
    let foliagePixels = [];

    // Step 1: Pixel classification using HSV and LAB color transformations
    for (let y = 0; y < ph; y++) {
      for (let x = 0; x < pw; x++) {
        const idx = (y * pw + x) * 4;
        const r = data[idx];
        const g = data[idx + 1];
        const b = data[idx + 2];

        // RGB -> HSV
        const rn = r / 255;
        const gn = g / 255;
        const bn = b / 255;
        const max = Math.max(rn, gn, bn);
        const min = Math.min(rn, gn, bn);
        const d = max - min;
        const v = max;
        const s = max === 0 ? 0 : d / max;
        let h = 0;

        if (d !== 0) {
          if (max === rn) {
            h = ((gn - bn) / d + (gn < bn ? 6 : 0)) * 60;
          } else if (max === gn) {
            h = ((bn - rn) / d + 2) * 60;
          } else {
            h = ((rn - gn) / d + 4) * 60;
          }
        }

        // Approximate LAB a* and b* components
        // a* reflects green (<128) vs magenta (>128)
        // b* reflects blue (<128) vs yellow (>128)
        const labA = 128 + (0.5 * rn - 0.418 * gn - 0.082 * bn) * 150;
        const labB = 128 + (-0.168 * rn - 0.331 * gn + 0.5 * bn) * -150;

        // Leaf Classifiers:
        // 1. Healthy Green: Hue 65 - 170, Sat > 0.16, Val > 0.16, labA <= 126
        const isGreen = (h >= 62 && h <= 175) && (s >= 0.15) && (v >= 0.15) && (labA <= 127);
        // 2. Chlorotic Yellow: Hue 35 - 62, Sat > 0.22, Val > 0.22, labB >= 130
        const isYellow = (h >= 34 && h < 62) && (s >= 0.20) && (v >= 0.20) && (labB >= 128);
        // 3. Necrotic Brown / Diseased: Hue 14 - 34, Sat > 0.22, Val in [0.14, 0.75], r > b
        const isBrown = (h >= 14 && h < 34) && (s >= 0.22) && (v >= 0.14 && v <= 0.75) && (rn > bn);
        // Reject Human Skin tones (h < 25 or h > 335 with high red to green ratio)
        const isSkin = ((h < 22 || h > 340) && rn > 1.25 * gn && labA > 136);

        if ((isGreen || isYellow || isBrown) && !isSkin) {
          foliageCount++;
          if (x < minX) minX = x;
          if (x > maxX) maxX = x;
          if (y < minY) minY = y;
          if (y > maxY) maxY = y;

          // Sample texture gradients (difference with adjacent pixel)
          if (x > 0) {
            const prevIdx = (y * pw + (x - 1)) * 4;
            gradientSum += Math.abs(g - data[prevIdx + 1]);
          }
        }
      }
    }

    const totalPixels = pw * ph;
    this.foliageRatio = (foliageCount / totalPixels) * 100;

    // Check if enough leaf foliage exists (at least 3.5% of frame)
    if (this.foliageRatio < 3.5 || minX >= maxX || minY >= maxY) {
      this._updateStatus('SEARCHING', null, 0.0);
      return;
    }

    // Step 2: Bounding Box & Shape Validation
    const boxW = maxX - minX;
    const boxH = maxY - minY;
    const boxArea = boxW * boxH;
    const solidity = foliageCount / Math.max(1, boxArea);
    const aspectRatio = boxW / Math.max(1, boxH);
    const avgGradient = gradientSum / Math.max(1, foliageCount);

    // Leaves have characteristic aspect ratios (0.25 to 4.5) and solidity (0.18 to 0.95)
    // Flat artificial green paper or walls lack texture variation (avgGradient < 3)
    const isValidLeaf = (aspectRatio >= 0.22 && aspectRatio <= 4.5) &&
                        (solidity >= 0.18) &&
                        (avgGradient >= 3.0);

    if (!isValidLeaf) {
      this._updateStatus('SEARCHING', null, 0.15);
      return;
    }

    // Calculate Normalized Bounding Box [0% - 100%]
    const normBox = {
      x: (minX / pw) * 100,
      y: (minY / ph) * 100,
      width: (boxW / pw) * 100,
      height: (boxH / ph) * 100,
      area_pct: (boxArea / totalPixels) * 100
    };

    // Calculate Confidence Score
    const confComponents = [
      Math.min(1.0, this.foliageRatio / 30.0) * 0.35,
      Math.min(1.0, normBox.area_pct / 25.0) * 0.25,
      (solidity >= 0.25 ? 1.0 : 0.4) * 0.20,
      Math.min(1.0, avgGradient / 25.0) * 0.20
    ];
    this.confidence = Math.min(0.99, Math.max(0.20, confComponents.reduce((a, b) => a + b, 0)));

    // Step 3: Temporal Stability & Position Lock Verification
    this._trackStability(normBox, timestamp);
  }

  /**
   * Evaluates whether the leaf is held steady inside the camera frame.
   */
  _trackStability(newBox, timestamp) {
    this.currentBox = newBox;

    // Initialize or smooth the display box
    if (!this.smoothBox) {
      this.smoothBox = { ...newBox };
    } else {
      const alpha = 0.35; // Exponential smoothing factor
      this.smoothBox.x = this.smoothBox.x * (1 - alpha) + newBox.x * alpha;
      this.smoothBox.y = this.smoothBox.y * (1 - alpha) + newBox.y * alpha;
      this.smoothBox.width = this.smoothBox.width * (1 - alpha) + newBox.width * alpha;
      this.smoothBox.height = this.smoothBox.height * (1 - alpha) + newBox.height * alpha;
    }

    this.stabilityHistory.push({
      x: newBox.x + newBox.width / 2,
      y: newBox.y + newBox.height / 2,
      w: newBox.width,
      h: newBox.height,
      t: timestamp
    });

    if (this.stabilityHistory.length > 10) {
      this.stabilityHistory.shift();
    }

    // Check jitter over stability history
    let isStable = false;
    if (this.stabilityHistory.length >= 5) {
      const first = this.stabilityHistory[0];
      const last = this.stabilityHistory[this.stabilityHistory.length - 1];
      const dist = Math.hypot(last.x - first.x, last.y - first.y);
      const sizeDiff = Math.abs(last.w - first.w) + Math.abs(last.h - first.h);

      // Stable if center drifted less than 4.5% and size varied less than 6%
      isStable = dist < 4.5 && sizeDiff < 6.0;
    }

    if (isStable) {
      if (!this.stableStartTime) {
        this.stableStartTime = timestamp;
      }
      const stableDuration = timestamp - this.stableStartTime;

      if (stableDuration >= this.lockRequiredDurationMs) {
        this._updateStatus('POSITION_LOCKED', newBox, this.confidence, timestamp);
      } else {
        this._updateStatus('LEAF_DETECTED', newBox, this.confidence, timestamp);
      }
    } else {
      this.stableStartTime = null;
      this._updateStatus('LEAF_DETECTED', newBox, this.confidence, timestamp);
    }
  }

  /**
   * Updates internal state and notifies subscribers.
   */
  _updateStatus(newStatus, box, confidence, timestamp = performance.now()) {
    const prevStatus = this.status;
    this.status = newStatus;

    if (newStatus === 'SEARCHING') {
      this.smoothBox = null;
      this.stableStartTime = null;
      this.isPositionLocked = false;
      this.autoCaptureStartTime = null;
      this.autoCaptureTriggered = false;
    } else if (newStatus === 'POSITION_LOCKED') {
      this.isPositionLocked = true;

      // Handle Auto-Capture countdown
      if (this.autoCaptureEnabled && !this.autoCaptureTriggered) {
        if (!this.autoCaptureStartTime) {
          this.autoCaptureStartTime = timestamp;
        }
        const autoElapsed = timestamp - this.autoCaptureStartTime;
        if (autoElapsed >= this.autoCaptureDelayMs) {
          this.autoCaptureTriggered = true;
          this.onAutoCapture({
            box: this.smoothBox || this.currentBox,
            confidence: this.confidence
          });
        }
      }
    } else {
      this.isPositionLocked = false;
      this.autoCaptureStartTime = null;
      this.autoCaptureTriggered = false;
    }

    let autoCountdownRemaining = null;
    if (this.autoCaptureEnabled && this.autoCaptureStartTime && !this.autoCaptureTriggered) {
      const elapsed = timestamp - this.autoCaptureStartTime;
      autoCountdownRemaining = Math.max(0, ((this.autoCaptureDelayMs - elapsed) / 1000).toFixed(1));
    }

    this.onDetectionUpdate({
      status: this.status,
      confidence: this.confidence,
      foliageRatio: this.foliageRatio,
      box: this.smoothBox || this.currentBox,
      isPositionLocked: this.isPositionLocked,
      autoCaptureCountdown: autoCountdownRemaining,
      autoCaptureEnabled: this.autoCaptureEnabled
    });
  }

  /**
   * Render modern futuristic agricultural AI reticle HUD on the overlay canvas.
   */
  _renderOverlay(timestamp) {
    if (!this.overlayCtx || !this.overlayCanvas) return;

    const canvas = this.overlayCanvas;
    const ctx = this.overlayCtx;
    const cw = canvas.width;
    const ch = canvas.height;

    ctx.clearRect(0, 0, cw, ch);

    // If searching or no box, render subtle viewfinder target reticle in center
    if (!this.smoothBox || this.status === 'SEARCHING') {
      this._drawCenterViewfinder(ctx, cw, ch, timestamp);
      return;
    }

    // Convert normalized box to overlay canvas pixel coordinates
    const b = this.smoothBox;
    const bx = (b.x / 100) * cw;
    const by = (b.y / 100) * ch;
    const bw = (b.width / 100) * cw;
    const bh = (b.height / 100) * ch;

    const isLocked = this.status === 'POSITION_LOCKED';
    const primaryColor = isLocked ? '#22c55e' : '#10b981'; // vibrant emerald
    const accentColor = isLocked ? '#4ade80' : '#34d399';

    // 1. Draw Corner Reticles / Brackets [  ]
    ctx.save();
    ctx.lineWidth = isLocked ? 3.5 : 2.5;
    ctx.strokeStyle = primaryColor;
    ctx.shadowColor = isLocked ? 'rgba(34, 197, 94, 0.75)' : 'rgba(16, 185, 129, 0.45)';
    ctx.shadowBlur = isLocked ? 14 : 8;

    const armLen = Math.min(bw, bh) * 0.22;

    // Top-Left
    ctx.beginPath();
    ctx.moveTo(bx, by + armLen);
    ctx.lineTo(bx, by);
    ctx.lineTo(bx + armLen, by);
    ctx.stroke();

    // Top-Right
    ctx.beginPath();
    ctx.moveTo(bx + bw - armLen, by);
    ctx.lineTo(bx + bw, by);
    ctx.lineTo(bx + bw, by + armLen);
    ctx.stroke();

    // Bottom-Left
    ctx.beginPath();
    ctx.moveTo(bx, by + bh - armLen);
    ctx.lineTo(bx, by + bh);
    ctx.lineTo(bx + armLen, by + bh);
    ctx.stroke();

    // Bottom-Right
    ctx.beginPath();
    ctx.moveTo(bx + bw - armLen, by + bh);
    ctx.lineTo(bx + bw, by + bh);
    ctx.lineTo(bx + bw, by + bh - armLen);
    ctx.stroke();

    // 2. Draw Soft Bounding Box Outline
    ctx.fillStyle = isLocked ? 'rgba(34, 197, 94, 0.08)' : 'rgba(16, 185, 129, 0.04)';
    ctx.fillRect(bx, by, bw, bh);

    ctx.strokeStyle = isLocked ? 'rgba(34, 197, 94, 0.4)' : 'rgba(16, 185, 129, 0.25)';
    ctx.lineWidth = 1;
    ctx.strokeRect(bx, by, bw, bh);

    // 3. Animated Laser Scanning Beam across the leaf bounding box
    this.scanBeamPhase = (this.scanBeamPhase + 0.025) % 1.0;
    const beamY = by + (bh * this.scanBeamPhase);

    const grad = ctx.createLinearGradient(bx, beamY, bx + bw, beamY);
    grad.addColorStop(0, 'rgba(34, 197, 94, 0.0)');
    grad.addColorStop(0.5, isLocked ? 'rgba(74, 222, 128, 0.85)' : 'rgba(52, 211, 153, 0.65)');
    grad.addColorStop(1, 'rgba(34, 197, 94, 0.0)');

    ctx.strokeStyle = grad;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(bx, beamY);
    ctx.lineTo(bx + bw, beamY);
    ctx.stroke();

    // 4. Floating Identification Pill Tag Above Bounding Box
    const pillY = Math.max(26, by - 12);
    const confPct = Math.round(this.confidence * 100);
    const tagText = isLocked ? `🌿 Plant Leaf Locked • ${confPct}%` : `🌿 Leaf Detected • ${confPct}%`;

    ctx.font = '600 12px "Plus Jakarta Sans", sans-serif';
    const textWidth = ctx.measureText(tagText).width;
    const pillW = textWidth + 24;
    const pillH = 22;
    const pillX = Math.max(8, Math.min(cw - pillW - 8, bx));

    ctx.fillStyle = isLocked ? 'rgba(21, 128, 61, 0.92)' : 'rgba(18, 55, 42, 0.88)';
    ctx.beginPath();
    ctx.roundRect(pillX, pillY - pillH, pillW, pillH, 6);
    ctx.fill();

    ctx.strokeStyle = isLocked ? '#4ade80' : '#10b981';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = '#ffffff';
    ctx.fillText(tagText, pillX + 12, pillY - 7);

    // 5. Auto-Capture Countdown Ring (if actively counting down)
    if (this.autoCaptureEnabled && this.autoCaptureStartTime && !this.autoCaptureTriggered) {
      const elapsed = timestamp - this.autoCaptureStartTime;
      const progress = Math.min(1.0, elapsed / this.autoCaptureDelayMs);
      const remainingSec = Math.max(0, ((this.autoCaptureDelayMs - elapsed) / 1000).toFixed(1));

      const ringCenterX = bx + bw / 2;
      const ringCenterY = by + bh / 2;
      const ringRadius = Math.min(bw, bh) * 0.28;

      ctx.beginPath();
      ctx.arc(ringCenterX, ringCenterY, ringRadius, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
      ctx.lineWidth = 4;
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(ringCenterX, ringCenterY, ringRadius, -Math.PI / 2, (-Math.PI / 2) + (Math.PI * 2 * progress));
      ctx.strokeStyle = '#22c55e';
      ctx.lineWidth = 5;
      ctx.stroke();

      ctx.fillStyle = '#ffffff';
      ctx.font = '700 16px "Plus Jakarta Sans", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`${remainingSec}s`, ringCenterX, ringCenterY);
      ctx.textAlign = 'left';
      ctx.textBaseline = 'alphabetic';
    }

    ctx.restore();
  }

  /**
   * Draw center viewfinder targeting brackets when searching for leaves.
   */
  _drawCenterViewfinder(ctx, cw, ch, timestamp) {
    const vfSize = Math.min(cw, ch) * 0.55;
    const cx = cw / 2;
    const cy = ch / 2;
    const half = vfSize / 2;
    const arm = vfSize * 0.18;

    // Subtle breathing pulse for guide reticles
    const pulse = 0.5 + 0.5 * Math.sin(timestamp * 0.003);
    const alpha = 0.45 + 0.35 * pulse;

    ctx.save();
    ctx.strokeStyle = `rgba(16, 185, 129, ${alpha})`;
    ctx.lineWidth = 2;
    ctx.shadowColor = 'rgba(16, 185, 129, 0.4)';
    ctx.shadowBlur = 6;

    // Reticles around center guide area
    // Top-Left
    ctx.beginPath();
    ctx.moveTo(cx - half, cy - half + arm);
    ctx.lineTo(cx - half, cy - half);
    ctx.lineTo(cx - half + arm, cy - half);
    ctx.stroke();

    // Top-Right
    ctx.beginPath();
    ctx.moveTo(cx + half - arm, cy - half);
    ctx.lineTo(cx + half, cy - half);
    ctx.lineTo(cx + half, cy - half + arm);
    ctx.stroke();

    // Bottom-Left
    ctx.beginPath();
    ctx.moveTo(cx - half, cy + half - arm);
    ctx.lineTo(cx - half, cy + half);
    ctx.lineTo(cx - half + arm, cy + half);
    ctx.stroke();

    // Bottom-Right
    ctx.beginPath();
    ctx.moveTo(cx + half - arm, cy + half);
    ctx.lineTo(cx + half, cy + half);
    ctx.lineTo(cx + half, cy + half - arm);
    ctx.stroke();

    // Center Crosshairs
    const crossSize = 10;
    ctx.beginPath();
    ctx.moveTo(cx - crossSize, cy);
    ctx.lineTo(cx + crossSize, cy);
    ctx.moveTo(cx, cy - crossSize);
    ctx.lineTo(cx, cy + crossSize);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.stroke();

    ctx.restore();
  }
}

window.CropCareLeafDetector = CropCareLeafDetector;

