const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = path.resolve(__dirname, '../src/static/js');

class Element {
  constructor(tag = 'div') {
    this.tag = tag; this.children = []; this.style = {}; this.listeners = {};
    this.classList = { add() {}, remove() {} }; this._text = '';
  }
  set textContent(value) { this._text = value; this.children = []; }
  get textContent() { return this._text + this.children.map(x => x.textContent).join(' '); }
  appendChild(child) { child.parentNode = this; this.children.push(child); return child; }
  replaceChildren() { this.children = []; this._text = ''; }
  setAttribute() {}
  addEventListener(name, fn) { this.listeners[name] = fn; }
  scrollIntoView() {}
}

function harness() {
  const nodes = {};
  const parent = new Element();
  for (const id of ['emptyState', 'diagnosticPanel', 'extendedAgronomicSection']) {
    nodes[id] = parent.appendChild(new Element());
    nodes[id].style.display = id === 'emptyState' ? 'none' : 'flex';
    nodes[id].textContent = 'Existing upload result';
  }
  const context = vm.createContext({
    window: { innerWidth: 1280, showToast() {} },
    document: { getElementById: id => nodes[id], createElement: tag => new Element(tag) },
    console, AbortController, DOMException, setTimeout, clearTimeout, URL, Blob
  });
  vm.runInContext(fs.readFileSync(path.join(source, 'cameraCapture.js'), 'utf8'), context);
  vm.runInContext(fs.readFileSync(path.join(source, 'cameraUI.js'), 'utf8'), context);
  const ui = new context.window.CropCareCameraUI();
  ui.initCameraResults();
  ui.elements = { btnCaptureAnalyze: new Element('button'), detectionBadge: new Element(), liveVideo: {} };
  ui.isCameraActive = true; ui.currentMode = 'camera';
  ui.triggerShutterFlash = () => {};
  return { context, ui, nodes };
}

test('camera dispatch uses only dedicated endpoint and real response', async () => {
  const { context } = harness();
  let called;
  context.fetch = async (url, options) => {
    called = { url, options }; return { ok: true, json: async () => ({ accepted: false, health_status: 'Uncertain' }) };
  };
  const result = await context.window.CropCareCapture.diagnoseImage('data:image/jpeg;base64,YQ==');
  assert.equal(called.url, '/api/camera/diagnose');
  assert.equal(JSON.parse(called.options.body).image, 'data:image/jpeg;base64,YQ==');
  assert.equal(result.accepted, false);
});

test('service errors remain explicit without legacy fallback', async () => {
  const { context } = harness();
  let calls = 0;
  context.fetch = async () => { calls++; return { ok: false, status: 503, json: async () => ({ message: 'Camera model unavailable' }) }; };
  await assert.rejects(context.window.CropCareCapture.diagnoseImage('abc'), /Camera model unavailable/);
  assert.equal(calls, 1);
});

test('external cancellation aborts camera fetch', async () => {
  const { context } = harness();
  context.fetch = (url, options) => new Promise((resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(new DOMException('Cancelled', 'AbortError')));
  });
  const controller = new AbortController();
  const pending = context.window.CropCareCapture.diagnoseImage('abc', { signal: controller.signal });
  controller.abort();
  await assert.rejects(pending, { name: 'AbortError' });
});

test('duplicate capture and stale result cannot overwrite results after stop', async () => {
  const { context, ui } = harness();
  let count = 0, complete;
  Object.assign(context.window.CropCareCapture, {
    captureFrame: () => 'frame',
    diagnoseImage: () => { count++; return new Promise(resolve => { complete = resolve; }); }
  });
  let renders = 0; ui.renderCameraResult = () => renders++;
  const first = ui.captureAndAnalyze();
  await ui.captureAndAnalyze();
  assert.equal(count, 1);
  ui.stopCamera();
  complete({ accepted: true });
  await first;
  assert.equal(renders, 0);
  assert.equal(ui.elements.btnCaptureAnalyze.disabled, true);
});

test('switching to upload cancels analysis and restores existing report visibility', async () => {
  const { context, ui, nodes } = harness();
  ui.currentMode = 'upload'; ui.setMode('camera');
  assert.equal(nodes.diagnosticPanel.style.display, 'none');
  let complete;
  Object.assign(context.window.CropCareCapture, { captureFrame: () => 'frame', diagnoseImage: () => new Promise(resolve => { complete = resolve; }) });
  let renders = 0; ui.renderCameraResult = () => renders++;
  const pending = ui.captureAndAnalyze();
  ui.setMode('upload');
  complete({ accepted: true }); await pending;
  assert.equal(renders, 0);
  assert.equal(nodes.diagnosticPanel.style.display, 'flex');
  assert.equal(nodes.extendedAgronomicSection.style.display, 'flex');
  assert.equal(nodes.emptyState.style.display, 'none');
  assert.equal(nodes.diagnosticPanel.textContent, 'Existing upload result');
});

test('uncertain result does not present 99.9% as diagnosis or fabricate severity', () => {
  const { ui } = harness();
  ui.renderCameraResult({ accepted: false, confidence: null, classifier_score: .999,
    health_status: 'Uncertain', message: 'Capture again', damaged_region_detection: {} });
  const text = ui.cameraResult.textContent;
  assert.match(text, /No diagnosis accepted/);
  assert.match(text, /Severity: unavailable/);
  assert.doesNotMatch(text, /99\.9|Moderate|Affected Area: 0/);
});

test('healthy result does not prescribe pesticide and labels attention honestly', () => {
  const { ui } = harness();
  ui.renderCameraResult({ accepted: true, confidence: .97, health_status: 'Healthy',
    crop_name: 'Tomato', disease_name: null, damaged_region_detection: {} });
  assert.match(ui.cameraResult.textContent, /No disease treatment is indicated/);
  assert.match(ui.cameraResult.textContent, /97\.00%/);
  assert.doesNotMatch(ui.cameraResult.textContent, /Chemical recommendations require/);
});
