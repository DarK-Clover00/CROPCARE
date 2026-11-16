/**
 * CropCare v3.0 — Camera Module (camera.js)
 * Manages HTML5 MediaDevices camera lifecycle, permissions, stream acquisition,
 * multi-camera enumeration, front/rear camera switching, and graceful error handling.
 */

class CropCareCamera {
  constructor(videoElement, options = {}) {
    this.video = videoElement;
    this.stream = null;
    this.facingMode = options.facingMode || 'environment'; // prioritize rear camera on mobile
    this.availableCameras = [];
    this.currentCameraIndex = 0;
    this.isActive = false;
    this.onStateChange = options.onStateChange || (() => {});
    this.onError = options.onError || (() => {});
  }

  /**
   * Enumerate available video input devices.
   */
  async enumerateDevices() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
      return [];
    }
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      this.availableCameras = devices.filter(d => d.kind === 'videoinput');
      return this.availableCameras;
    } catch (e) {
      console.warn('[CropCareCamera] Could not enumerate devices:', e);
      return [];
    }
  }

  /**
   * Request permission and start camera stream.
   */
  async start() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      const err = new Error('Camera access is not supported by your browser.');
      this.onError(err, 'Unsupported Browser');
      throw err;
    }

    // Stop existing stream if active
    this.stop();

    this.onStateChange('INITIALIZING', 'Initializing Camera...');

    const constraintsList = [
      // Primary: High resolution with ideal facingMode
      {
        video: {
          facingMode: { ideal: this.facingMode },
          width: { ideal: 1920, min: 640 },
          height: { ideal: 1080, min: 480 }
        },
        audio: false
      },
      // Fallback 1: Standard facingMode without resolution constraint
      {
        video: { facingMode: this.facingMode },
        audio: false
      },
      // Fallback 2: Generic video input (works on desktop webcams)
      {
        video: true,
        audio: false
      }
    ];

    let lastError = null;

    for (const constraints of constraintsList) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        this.stream = stream;
        this.video.srcObject = stream;
        this.video.setAttribute('playsinline', 'true');
        this.video.setAttribute('webkit-playsinline', 'true');
        this.video.muted = true;

        await new Promise((resolve) => {
          if (this.video.readyState >= 2) {
            resolve();
          } else {
            this.video.onloadedmetadata = () => resolve();
          }
        });

        await this.video.play();
        this.isActive = true;

        await this.enumerateDevices();

        this.onStateChange('ACTIVE', 'Camera Ready');
        return stream;
      } catch (err) {
        lastError = err;
        console.warn('[CropCareCamera] Constraint attempt failed:', constraints, err);
      }
    }

    // If all attempts failed, translate error for human readability
    const translated = this._translateError(lastError);
    this.onStateChange('ERROR', translated.message);
    this.onError(lastError, translated.title, translated.message);
    throw lastError;
  }

  /**
   * Stop active camera stream and release hardware locks.
   */
  stop() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => {
        try {
          track.stop();
        } catch (e) {
          console.warn('[CropCareCamera] Error stopping track:', e);
        }
      });
      this.stream = null;
    }
    if (this.video) {
      this.video.srcObject = null;
    }
    this.isActive = false;
    this.onStateChange('INACTIVE', 'Camera Inactive');
  }

  /**
   * Toggle between front and rear cameras (or cycle available video inputs).
   */
  async switchCamera() {
    if (this.availableCameras.length > 1) {
      this.currentCameraIndex = (this.currentCameraIndex + 1) % this.availableCameras.length;
      this.facingMode = (this.facingMode === 'environment') ? 'user' : 'environment';
    } else {
      this.facingMode = (this.facingMode === 'environment') ? 'user' : 'environment';
    }
    return this.start();
  }

  /**
   * Translate WebRTC exceptions into understandable user messages.
   */
  _translateError(err) {
    if (!err) {
      return {
        title: 'Camera Error',
        message: 'Could not access device camera.'
      };
    }
    const name = err.name || '';
    if (name === 'NotAllowedError' || name === 'PermissionDeniedError') {
      return {
        title: 'Permission Denied',
        message: 'Camera permission was denied. Please allow camera access in your browser settings or use the Upload Image option.'
      };
    }
    if (name === 'NotFoundError' || name === 'DevicesNotFoundError') {
      return {
        title: 'No Camera Found',
        message: 'No camera was detected on this device. Please connect a webcam or use the Upload Image option.'
      };
    }
    if (name === 'NotReadableError' || name === 'TrackStartError') {
      return {
        title: 'Camera In Use',
        message: 'Your camera is already in use by another tab or application. Please close other camera apps and try again.'
      };
    }
    if (name === 'OverconstrainedError') {
      return {
        title: 'Hardware Limitation',
        message: 'Camera settings could not be satisfied by your device.'
      };
    }
    return {
      title: 'Camera Initialization Failed',
      message: err.message || 'Unable to open camera.'
    };
  }
}

window.CropCareCamera = CropCareCamera;

