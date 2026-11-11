/* Regresiones del controlador, sin navegador ni dependencias: node --test scripts/check_video_runtime.cjs */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const { runInNewContext } = require('node:vm');
const source = readFileSync(resolve(__dirname, '../site.js'), 'utf8');
const flush = async () => { for (let i = 0; i < 6; i++) await Promise.resolve(); };
class Events {
  listeners = new Map();
  addEventListener(name, callback) {
    if (!this.listeners.has(name)) this.listeners.set(name, []);
    this.listeners.get(name).push(callback);
  }
  emit(name, event = {}) { for (const fn of this.listeners.get(name) || []) fn(event); }
}
function setup({ reduced = false } = {}) {
  let clock = 0, nextId = 0;
  const timers = new Map();
  const schedule = (fn, delay, repeat) => {
    const id = ++nextId;
    timers.set(id, { fn, time: clock + delay, repeat });
    return id;
  };
  const win = new Events();
  const doc = new Events();
  const motion = Object.assign(new Events(), { matches: reduced });
  const fallback = { hidden: true };
  const sources = [new Events(), new Events()];
  const video = Object.assign(new Events(), {
    paused: true, currentTime: 0, hidden: false, playCalls: 0, loadCalls: 0,
    parentElement: { querySelector: () => fallback },
    querySelectorAll: () => sources,
    play() {
      this.playCalls++;
      if (this.playResult) return this.playResult();
      this.paused = false;
      this.emit('playing');
      return Promise.resolve();
    },
    pause() { const changed = !this.paused; this.paused = true; if (changed) this.emit('pause'); },
    load() { this.loadCalls++; this.pause(); this.currentTime = 0; },
  });
  const observers = [];
  class Observer {
    constructor(callback, options) { this.callback = callback; this.options = options; observers.push(this); }
    observe() {} disconnect() {} unobserve() {}
    send(ratio) { this.callback([{ isIntersecting: ratio > 0, intersectionRatio: ratio }]); }
  }
  Object.assign(win, {
    matchMedia: () => motion, IntersectionObserver: Observer, scrollY: 0, innerWidth: 390,
    setTimeout: (fn, ms) => schedule(fn, ms, 0), clearTimeout: id => timers.delete(id),
    setInterval: (fn, ms) => schedule(fn, ms, ms), clearInterval: id => timers.delete(id),
  });
  Object.assign(doc, {
    hidden: false,
    querySelectorAll: query => query === 'video[data-video-ambiental]' ? [video] : [],
    querySelector: () => null,
  });
  const navigator = { onLine: true };
  runInNewContext(source, {
    window: win, document: doc, navigator, IntersectionObserver: Observer,
    Element: class {}, performance: { now: () => clock },
    requestAnimationFrame: fn => fn(),
  });
  return {
    video, fallback, sources, win, doc, motion, navigator,
    nearby: ratio => observers[0].send(ratio),
    visible: ratio => observers[1].send(ratio),
    async advance(ms) {
      const target = clock + ms;
      while (true) {
        const entry = [...timers].filter(([, t]) => t.time <= target).sort((a, b) => a[1].time - b[1].time)[0];
        if (!entry) break;
        const [id, timer] = entry;
        clock = timer.time;
        if (timer.repeat) timer.time += timer.repeat; else timers.delete(id);
        timer.fn();
        await flush();
      }
      clock = target;
      await flush();
    },
  };
}
test('precarga cercana y reproducción mientras cualquier parte siga visible', async () => {
  const s = setup();
  assert.equal(s.video.loadCalls, 0);
  s.nearby(1);
  assert.equal(s.video.loadCalls, 1);
  assert.equal(s.video.playCalls, 0);
  s.visible(1); await flush();
  assert.equal(s.video.paused, false);
  assert.ok(s.video.loop && s.video.muted && s.video.playsInline);
  s.visible(0.05);
  assert.equal(s.video.paused, false);
  s.visible(0);
  assert.equal(s.video.paused, true);
  s.visible(0.05); await flush();
  assert.equal(s.video.paused, false);
  assert.equal(s.video.loadCalls, 1);
});
test('una promesa vieja abortada no bloquea el regreso a pantalla', async () => {
  const s = setup();
  let reject;
  s.video.playResult = () => new Promise((_, r) => { reject = r; });
  s.visible(1);
  s.visible(0);
  delete s.video.playResult;
  s.visible(1);
  reject({ name: 'AbortError' }); await flush();
  assert.equal(s.video.paused, false);
  assert.equal(s.fallback.hidden, true);
});
test('autoplay denegado muestra respaldo y reintenta dentro del toque', async () => {
  const s = setup();
  s.video.playResult = () => Promise.reject({ name: 'NotAllowedError' });
  s.visible(1); await flush();
  assert.equal(s.video.hidden, true);
  assert.equal(s.fallback.hidden, false);
  await s.advance(30000);
  assert.equal(s.video.playCalls, 1);
  delete s.video.playResult;
  s.doc.emit('touchend'); await flush();
  assert.equal(s.video.hidden, false);
  assert.equal(s.video.paused, false);
});
test('una descarga atascada se reinicia una vez y después muestra respaldo', async () => {
  const s = setup(); s.visible(1); await flush();
  await s.advance(10000);
  assert.equal(s.video.loadCalls, 2);
  await s.advance(10000);
  assert.equal(s.fallback.hidden, false);
  await s.advance(30000);
  assert.equal(s.video.loadCalls, 2);
});
test('progreso normal y vuelta al inicio no recargan el archivo', async () => {
  const s = setup(); s.visible(1); await flush();
  for (let i = 1; i < 20; i++) { s.video.currentTime = (i * 2) % 10; await s.advance(2000); }
  assert.equal(s.video.loadCalls, 1);
  assert.equal(s.video.paused, false);
});
test('ocultar pestaña, salir de página y movimiento reducido cancelan reproducción y recuperación', async () => {
  const s = setup(); s.visible(1); await flush();
  s.doc.hidden = true; s.doc.emit('visibilitychange');
  await s.advance(30000);
  assert.equal(s.video.paused, true);
  assert.equal(s.video.loadCalls, 1);
  s.doc.hidden = false; s.doc.emit('visibilitychange'); await flush();
  assert.equal(s.video.paused, false);
  s.win.emit('pagehide'); await s.advance(30000);
  assert.equal(s.video.paused, true);
  s.win.emit('pageshow'); await flush();
  assert.equal(s.video.paused, false);
  s.motion.matches = true; s.motion.emit('change'); await s.advance(30000);
  assert.equal(s.video.paused, true);
  assert.equal(s.fallback.hidden, false);
  assert.equal(s.video.loadCalls, 1);
});
test('movimiento reducido desde el inicio evita descargar videos', async () => {
  const s = setup({ reduced: true }); s.nearby(1); s.visible(1); await s.advance(30000);
  assert.equal(s.video.loadCalls, 0);
  assert.equal(s.video.playCalls, 0);
  assert.equal(s.fallback.hidden, false);
});
test('fallo móvil permite probar escritorio; fallo final se recupera al volver la conexión', async () => {
  const s = setup(); s.visible(1); await flush();
  s.sources[0].emit('error');
  assert.equal(s.fallback.hidden, true);
  s.sources[1].emit('error');
  assert.equal(s.fallback.hidden, false);
  s.win.emit('online'); await flush();
  assert.equal(s.video.paused, false);
  assert.equal(s.video.loadCalls, 2);
});
test('pausa inesperada se reanuda, pausa fuera de pantalla permanece', async () => {
  const s = setup(); s.visible(1); await flush();
  s.video.pause(); await s.advance(0);
  assert.equal(s.video.paused, false);
  s.visible(0); await s.advance(30000);
  assert.equal(s.video.paused, true);
  assert.equal(s.video.loadCalls, 1);
});
