// The state itself.
//
// Three lights drift through each other on a warm, near-dark field. The whole
// thing breathes on a six-second cycle — slower than a person, so a person
// slows down next to it. Grain on top, or the gradient reads as a screensaver
// instead of a surface.
//
// Drawn into a small buffer (LOW×LOW) and stretched to the canvas: the softness
// comes from the scaling, not from a blur filter, and it costs almost nothing on
// a weak phone.
//
// Skin: press the field and the nearest light leans toward the finger and the
// breath deepens — the surface yields, slightly, and returns when let go.

const LOW = 160; // buffer side, px
const FPS = 30; // nothing here moves fast enough to need more
const GRAIN = 128; // grain tile side

const reduceMotion =
  typeof matchMedia === "function" &&
  matchMedia("(prefers-reduced-motion: reduce)").matches;

function makeGrain() {
  const c = document.createElement("canvas");
  c.width = c.height = GRAIN;
  const ctx = c.getContext("2d");
  const img = ctx.createImageData(GRAIN, GRAIN);
  for (let i = 0; i < img.data.length; i += 4) {
    const v = 128 + (Math.random() * 2 - 1) * 90;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
    img.data[i + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  return c;
}

let grainTile = null;

/**
 * The hour moves the field: by night it darkens and cools, by day it warms and
 * lifts. This is the one thing the state knows about the visitor's life.
 *
 * @param {number} hour 0–24 (fractional)
 * @returns {{day: number, gain: number, tint: number[]}}
 */
export function daylight(hour) {
  // 0 — deep night, 1 — early afternoon
  const day = Math.max(0, Math.cos(((hour - 13) / 24) * Math.PI * 2)) ** 0.7;
  return {
    day,
    gain: 0.72 + day * 0.28,
    tint: day > 0.5 ? [255, 250, 240] : [186, 198, 224],
  };
}

function mix(a, b, t) {
  return [
    a[0] + (b[0] - a[0]) * t,
    a[1] + (b[1] - a[1]) * t,
    a[2] + (b[2] - a[2]) * t,
  ];
}

function rgba(c, a) {
  return `rgba(${c[0] | 0}, ${c[1] | 0}, ${c[2] | 0}, ${a})`;
}

/**
 * Mounts the state on a <canvas>. Returns a handle; the state must be put out
 * when its screen goes, or it keeps turning in the background and eats battery.
 *
 * @param {HTMLCanvasElement} canvas
 * @param {{base: {night: number[], day: number[]}, blobs: {rgb: number[], peak: number}[]}} state
 * @param {{still?: boolean, onTap?: () => void}} [opts]
 *   onTap fires on a short press with little movement — a touch, not a hold.
 */
export function mountObject(canvas, state, opts = {}) {
  const still = opts.still || reduceMotion;

  const buf = document.createElement("canvas");
  buf.width = buf.height = LOW;
  const bctx = buf.getContext("2d");
  const ctx = canvas.getContext("2d");
  if (!grainTile) grainTile = makeGrain();
  const grain = ctx.createPattern(grainTile, "repeat");

  let w = 0;
  let h = 0;
  let raf = 0;
  let last = 0;
  let alive = true;
  let born = performance.now();

  // Touch. `press` eases toward 1 while a finger is down and back to 0 after.
  const touch = { x: 0.5, y: 0.5, press: 0, down: false, at: 0, sx: 0, sy: 0 };

  // Something unexplained. On a rare opening a faint ring crosses the field,
  // once, slowly, and is not mentioned anywhere. Most visitors never see it;
  // that is the point. Nothing in the interface points at it.
  const now = new Date();
  const rare =
    !still &&
    (Math.random() < 1 / 40 || (now.getHours() === 4 && now.getMinutes() === 4));
  const rareStart = 20 + Math.random() * 40; // seconds after opening
  const RARE_LEN = 40;

  function resize() {
    const r = canvas.getBoundingClientRect();
    const dpr = Math.min(devicePixelRatio || 1, 2);
    w = Math.max(1, Math.round(r.width * dpr));
    h = Math.max(1, Math.round(r.height * dpr));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
  }

  function paint(now) {
    const t = still ? 8000 : (now - born) / 1000;
    const d = new Date();
    const light = daylight(d.getHours() + d.getMinutes() / 60);
    const breath = still
      ? 1
      : 1 + Math.sin((t * (Math.PI * 2)) / 6) * (0.035 + touch.press * 0.03);

    // Field
    bctx.globalCompositeOperation = "source-over";
    bctx.fillStyle = rgba(mix(state.base.night, state.base.day, light.day), 1);
    bctx.fillRect(0, 0, LOW, LOW);
    bctx.globalCompositeOperation = "lighter";

    state.blobs.forEach((blob, i) => {
      const s = i + 1;
      // Three incommensurable periods — the picture never literally repeats.
      let x = 0.5 + Math.sin(t / (17 + s * 6) + s) * 0.26;
      let y = 0.5 + Math.cos(t / (23 + s * 5) + s * 2) * 0.24;
      // Skin: the nearest light leans toward the finger. Weighted by distance so
      // one light answers and the others barely notice.
      if (touch.press > 0) {
        const dist = Math.hypot(touch.x - x, touch.y - y);
        const pull = touch.press * Math.max(0, 1 - dist / 0.9) * 0.62;
        x += (touch.x - x) * pull;
        y += (touch.y - y) * pull;
      }
      const r = (0.34 + Math.sin(t / (13 + s * 3)) * 0.07) * breath * LOW;
      const colour = mix(blob.rgb, light.tint, 0.18);
      const peak = 0.5 * light.gain * blob.peak * (1 + touch.press * 0.22);

      const g = bctx.createRadialGradient(x * LOW, y * LOW, 0, x * LOW, y * LOW, r);
      g.addColorStop(0, rgba(colour, peak));
      g.addColorStop(0.45, rgba(colour, peak * 0.35));
      g.addColorStop(1, rgba(colour, 0));
      bctx.fillStyle = g;
      bctx.fillRect(0, 0, LOW, LOW);
    });

    // The unexplained thing: a thin soft ring, crossing once.
    if (rare && t > rareStart && t < rareStart + RARE_LEN) {
      const p = (t - rareStart) / RARE_LEN;
      const a = Math.sin(p * Math.PI) * 0.09 * light.gain;
      const x = (0.15 + p * 0.7) * LOW;
      const y = (0.62 - Math.sin(p * Math.PI) * 0.22) * LOW;
      const rr = 0.2 * LOW;
      const g = bctx.createRadialGradient(x, y, rr * 0.82, x, y, rr);
      g.addColorStop(0, "rgba(230, 222, 206, 0)");
      g.addColorStop(0.5, rgba([230, 222, 206], a));
      g.addColorStop(1, "rgba(230, 222, 206, 0)");
      bctx.fillStyle = g;
      bctx.fillRect(0, 0, LOW, LOW);
    }

    // Stretch the buffer: all the softness comes from here.
    ctx.globalCompositeOperation = "source-over";
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.clearRect(0, 0, w, h);
    ctx.drawImage(buf, 0, 0, w, h);

    // Vignette: the edge is always darker than the middle, or it looks like a
    // screen rather than a surface.
    const v = ctx.createRadialGradient(
      w / 2, h / 2, Math.min(w, h) * 0.18,
      w / 2, h / 2, Math.max(w, h) * 0.72,
    );
    v.addColorStop(0, "rgba(0,0,0,0)");
    v.addColorStop(1, "rgba(0,0,0,0.72)");
    ctx.fillStyle = v;
    ctx.fillRect(0, 0, w, h);

    // Grain
    if (grain) {
      ctx.save();
      ctx.globalAlpha = 0.055;
      ctx.globalCompositeOperation = "overlay";
      ctx.translate(
        still ? 0 : -((t * 60) % GRAIN),
        still ? 0 : -((t * 37) % GRAIN),
      );
      ctx.fillStyle = grain;
      ctx.fillRect(0, 0, w + GRAIN, h + GRAIN);
      ctx.restore();
    }
  }

  function frame(now) {
    if (!alive) return;
    raf = requestAnimationFrame(frame);
    if (now - last < 1000 / FPS) return;
    last = now;
    // The skin yields slowly and returns slowly. Never a snap.
    const target = touch.down ? 1 : 0;
    touch.press += (target - touch.press) * (touch.down ? 0.06 : 0.035);
    paint(now);
  }

  function place(e) {
    const r = canvas.getBoundingClientRect();
    touch.x = (e.clientX - r.left) / r.width;
    touch.y = (e.clientY - r.top) / r.height;
  }

  function onDown(e) {
    if (e.button && e.button !== 0) return;
    place(e);
    touch.down = true;
    touch.at = performance.now();
    touch.sx = e.clientX;
    touch.sy = e.clientY;
    try {
      canvas.setPointerCapture(e.pointerId);
    } catch (err) {
      /* nothing */
    }
  }

  function onMove(e) {
    if (touch.down) place(e);
  }

  function onUp(e) {
    if (!touch.down) return;
    touch.down = false;
    const held = performance.now() - touch.at;
    const moved = Math.hypot(e.clientX - touch.sx, e.clientY - touch.sy);
    // A touch, not a hold: short and still.
    if (held < 320 && moved < 12 && opts.onTap) opts.onTap();
  }

  function onCancel() {
    touch.down = false;
  }

  function onVisibility() {
    if (document.hidden) {
      cancelAnimationFrame(raf);
      raf = 0;
    } else if (alive && !still && !raf) {
      // The state doesn't rewind the time it missed — it just continues.
      born = performance.now() - (last - born);
      last = 0;
      raf = requestAnimationFrame(frame);
    }
  }

  const ro = typeof ResizeObserver === "function"
    ? new ResizeObserver(() => {
        resize();
        paint(performance.now());
      })
    : null;

  resize();
  if (ro) ro.observe(canvas);
  else addEventListener("resize", resize);
  addEventListener("visibilitychange", onVisibility);
  canvas.addEventListener("pointerdown", onDown);
  canvas.addEventListener("pointermove", onMove, { passive: true });
  canvas.addEventListener("pointerup", onUp);
  canvas.addEventListener("pointercancel", onCancel);
  if (!still) raf = requestAnimationFrame(frame);
  paint(performance.now());

  return {
    destroy() {
      alive = false;
      cancelAnimationFrame(raf);
      if (ro) ro.disconnect();
      else removeEventListener("resize", resize);
      removeEventListener("visibilitychange", onVisibility);
      canvas.removeEventListener("pointerdown", onDown);
      canvas.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("pointerup", onUp);
      canvas.removeEventListener("pointercancel", onCancel);
    },
  };
}
