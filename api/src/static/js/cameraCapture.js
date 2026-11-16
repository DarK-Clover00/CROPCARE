/**
 * CropCare v3.0 — Camera Capture & AI Diagnostic Dispatcher (cameraCapture.js)
 * Captures native high-resolution camera frames, performs intelligent leaf
 * region extraction with surrounding margin preservation, serializes image payloads,
 * and submits frames to the dedicated trained CROPCARE camera diagnosis pipeline.
 */

class CropCareCapture {
  /**
   * Captures the current camera video frame at maximum native sensor resolution.
   * If leafBox is provided and cropLeaf is enabled, extracts the leaf ROI
   * with contextual margin padding to preserve lesion and leaf edge symptoms.
   *
   * @param {HTMLVideoElement} video
   * @param {Object} options { cropLeaf: boolean, leafBox: Object, quality: number }
   * @returns {string} base64 DataURL (image/jpeg)
   */
  static captureFrame(video, options = {}) {
    if (!video || !video.videoWidth || !video.videoHeight) {
      throw new Error('Video stream is not ready for capture.');
    }

    const vw = video.videoWidth;
    const vh = video.videoHeight;
    const quality = options.quality || 0.94;

    // Full frame canvas
    const canvas = document.createElement('canvas');
    canvas.width = vw;
    canvas.height = vh;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, vw, vh);

    // Intelligent leaf crop if requested and valid bounding box is provided
    if (options.cropLeaf && options.leafBox && options.leafBox.width > 5 && options.leafBox.height > 5) {
      const b = options.leafBox;
      const padding = options.padding !== undefined ? options.padding : 0.22; // 22% context padding

      const bx = (b.x / 100) * vw;
      const by = (b.y / 100) * vh;
      const bw = (b.width / 100) * vw;
      const bh = (b.height / 100) * vh;

      const padW = bw * padding;
      const padH = bh * padding;

      const x1 = Math.max(0, Math.floor(bx - padW));
      const y1 = Math.max(0, Math.floor(by - padH));
      const x2 = Math.min(vw, Math.ceil(bx + bw + padW));
      const y2 = Math.min(vh, Math.ceil(by + bh + padH));

      const cropW = x2 - x1;
      const cropH = y2 - y1;

      // Extract ROI only if it is well-formed
      if (cropW >= 120 && cropH >= 120) {
        const cropCanvas = document.createElement('canvas');
        cropCanvas.width = cropW;
        cropCanvas.height = cropH;
        const cropCtx = cropCanvas.getContext('2d');
        cropCtx.drawImage(canvas, x1, y1, cropW, cropH, 0, 0, cropW, cropH);
        return cropCanvas.toDataURL('image/jpeg', quality);
      }
    }

    return canvas.toDataURL('image/jpeg', quality);
  }

  /** Analyze camera frames only; upload routes remain unchanged. */
  static async diagnoseImage(dataUrl, callbacks = {}) {
    const controller = new AbortController();
    const external = callbacks.signal;
    const cancel = () => controller.abort();
    if (external) {
      external.addEventListener('abort', cancel, { once: true });
      if (external.aborted) cancel();
    }
    let timedOut = false;
    const timer = setTimeout(() => { timedOut = true; controller.abort(); }, 90000);
    try {
      callbacks.onProgress?.(25, 'Analyzing captured leaf with the trained CROPCARE model…');
      const response = await fetch('/api/camera/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ image: dataUrl }),
        signal: controller.signal
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || `Camera analysis failed (HTTP ${response.status}).`);
      if (controller.signal.aborted) throw new DOMException('Cancelled', 'AbortError');
      callbacks.onProgress?.(100, result.accepted ? 'Camera diagnosis complete' : 'Image requires another capture');
      callbacks.onSuccess?.(result, dataUrl);
      return result;
    } catch (error) {
      const failure = timedOut ? new Error('Camera analysis timed out. Please try again.') : error;
      callbacks.onError?.(failure);
      throw failure;
    } finally {
      clearTimeout(timer);
      external?.removeEventListener('abort', cancel);
    }
  }
}

window.CropCareCapture = CropCareCapture;
