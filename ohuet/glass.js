// The state, in glass.
//
// Two passes. The first paints the field — three lights, the breath, the hour,
// the finger's pull, the rare ring — into a half-resolution texture. The second
// puts glass over it: a lens that forms under a finger, a slab behind the door,
// a pebble under the mark. Each is a signed-distance shape; the field is
// sampled through it with the offset bent hardest at the rim, the way light
// bends through the edge of a thick glass.
//
// Wabi is in the imperfections: edges wobble by a few pixels of noise, the
// glass is not evenly thick so the picture through it is not evenly bent, the
// slab holds three small bubbles, the tint is that of old bottle glass — a
// little smoke, a little amber — and grain sits over everything. Nothing is
// straight, nothing is perfectly clear, nothing hurries.
//
// Falls back to the canvas renderer in object.js when WebGL is not there.

const FPS_IDLE = 30;
const FPS_LIVE = 60;

const reduceMotion =
  typeof matchMedia === "function" &&
  matchMedia("(prefers-reduced-motion: reduce)").matches;

const VERT = `
attribute vec2 a;
varying vec2 v;
void main() { v = a * 0.5 + 0.5; gl_Position = vec4(a, 0.0, 1.0); }
`;

// Pass one: the field.
const FIELD = `
precision highp float;
varying vec2 v;
uniform vec2 u_res;
uniform float u_time;
uniform vec3 u_base;
uniform vec3 u_tint;
uniform float u_gain;
uniform vec3 u_light[3];   // x, y, radius (in field units, y up)
uniform vec4 u_colour[3];  // rgb, peak
uniform vec4 u_ring;       // x, y, radius, alpha

void main() {
  float aspect = u_res.x / u_res.y;
  vec2 p = vec2((v.x - 0.5) * aspect, v.y - 0.5);
  vec3 col = u_base;
  for (int i = 0; i < 3; i++) {
    vec2 c = vec2((u_light[i].x - 0.5) * aspect, u_light[i].y - 0.5);
    float d = length(p - c) / u_light[i].z;
    float a = u_colour[i].w * u_gain * pow(max(0.0, 1.0 - d), 1.7);
    vec3 rgb = mix(u_colour[i].rgb, u_tint, 0.18);
    col += rgb * a;
  }
  // The unexplained thing, when it is there: a thin soft ring.
  if (u_ring.w > 0.0) {
    vec2 c = vec2((u_ring.x - 0.5) * aspect, u_ring.y - 0.5);
    float d = abs(length(p - c) - u_ring.z);
    col += vec3(0.9, 0.87, 0.81) * u_ring.w * smoothstep(0.03, 0.0, d);
  }
  // Vignette: the edge darker than the middle, always.
  float e = length(p) / (0.72 * max(aspect, 1.0));
  col *= 1.0 - 0.72 * smoothstep(0.25, 1.0, e);
  gl_FragColor = vec4(col, 1.0);
}
`;

// Pass two: the glass.
const GLASS = `
precision highp float;
varying vec2 v;
uniform sampler2D u_field;
uniform vec2 u_res;        // canvas, device px
uniform float u_time;
uniform float u_seed;
uniform vec3 u_lens;       // x, y (device px, y up), radius
uniform float u_lensA;     // 0..1
uniform vec4 u_slab;       // centre x, y, half-width, half-height (device px)
uniform float u_slabA;     // 0..1
uniform float u_slabR;     // corner radius
uniform vec3 u_pebble;     // x, y, radius
uniform float u_still;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x),
             mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

// A rounded box, with a wobbling edge.
float sdSlab(vec2 p) {
  vec2 q = abs(p - u_slab.xy) - u_slab.zw + u_slabR;
  float d = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - u_slabR;
  return d + (noise(p * 0.02 + u_seed) - 0.5) * 6.0;
}

// A pebble: a circle whose radius varies with the angle.
float sdPebble(vec2 p) {
  vec2 q = p - u_pebble.xy;
  float ang = atan(q.y, q.x);
  float r = u_pebble.z * (1.0 + 0.14 * sin(ang * 3.0 + u_seed * 7.0) + 0.07 * sin(ang * 5.0 - u_seed * 3.0));
  return length(q) - r;
}

float sdLens(vec2 p) { return length(p - u_lens.xy) - u_lens.z; }

vec2 grad(float d0, vec2 p, int which) {
  float e = 1.5;
  float dx, dy;
  if (which == 0) { dx = sdSlab(p + vec2(e, 0.0)); dy = sdSlab(p + vec2(0.0, e)); }
  else if (which == 1) { dx = sdPebble(p + vec2(e, 0.0)); dy = sdPebble(p + vec2(0.0, e)); }
  else { dx = sdLens(p + vec2(e, 0.0)); dy = sdLens(p + vec2(0.0, e)); }
  vec2 g = vec2(dx - d0, dy - d0);
  float l = length(g);
  return l > 0.0001 ? g / l : vec2(0.0);
}

void main() {
  vec2 p = v * u_res;          // device px, y up
  vec2 px = 1.0 / u_res;
  vec2 off = vec2(0.0);
  float frost = 0.0;
  float spec = 0.0;
  float tintA = 0.0;
  float smoke = 0.0;
  float mask = 0.0;

  // The slab, behind the door.
  if (u_slabA > 0.0) {
    float d = sdSlab(p);
    float m = (1.0 - smoothstep(0.0, 1.5, d)) * u_slabA;
    if (m > 0.0) {
      vec2 n = grad(d, p, 0);
      float rim = 1.0 - smoothstep(0.0, 26.0, -d);
      float thick = noise(p * 0.008 + u_seed * 3.0) - 0.5;   // uneven thickness
      off += n * rim * rim * 22.0 * m + vec2(thick, -thick) * 9.0 * m;
      // Three bubbles, caught in the glass.
      for (int k = 0; k < 3; k++) {
        float fk = float(k);
        vec2 bp = u_slab.xy + vec2(
          (hash(vec2(fk, u_seed)) - 0.5) * 1.5 * u_slab.z,
          (hash(vec2(u_seed, fk)) - 0.5) * 1.4 * u_slab.w);
        float bd = length(p - bp) - (3.0 + fk * 1.5);
        float bm = 1.0 - smoothstep(0.0, 1.0, bd);
        float brim = 1.0 - smoothstep(0.0, 4.0, -bd);
        vec2 bn = (p - bp) / max(length(p - bp), 0.001);
        off += bn * brim * 10.0 * bm * m;
        spec += brim * bm * 0.35 * m;
      }
      spec += (pow(max(0.0, dot(n, normalize(vec2(-0.55, 0.83)))), 6.0) * 0.42 + 0.06) * rim * m;
      smoke = max(smoke, m);
      frost = max(frost, m);
      tintA = max(tintA, m);
      mask = max(mask, m);
    }
  }

  // The pebble, under the mark.
  {
    float d = sdPebble(p);
    float m = 1.0 - smoothstep(0.0, 1.5, d);
    if (m > 0.0) {
      vec2 n = grad(d, p, 1);
      float rim = 1.0 - smoothstep(0.0, 10.0, -d);
      off += n * rim * rim * 12.0 * m;
      spec += (pow(max(0.0, dot(n, normalize(vec2(-0.55, 0.83)))), 5.0) * 0.5 + 0.05) * rim * m;
      tintA = max(tintA, m);
      mask = max(mask, m);
    }
  }

  // The lens, under the finger: liquid.
  if (u_lensA > 0.0 && u_lens.z > 1.0) {
    float d = sdLens(p);
    float m = (1.0 - smoothstep(0.0, 2.0, d)) * u_lensA;
    if (m > 0.0) {
      vec2 n = grad(d, p, 2);
      float rim = 1.0 - smoothstep(0.0, u_lens.z * 0.3, -d);
      float ripple = u_still > 0.5 ? 0.0 : sin(-d * 0.22 - u_time * 3.2) * 1.6;
      // A convex lens: the middle magnifies (sample nearer the centre), the rim
      // bends the other way, hard.
      off += (-(p - u_lens.xy) * 0.24 * (1.0 - rim) + n * (rim * rim * 26.0 + ripple)) * m;
      spec += (pow(max(0.0, dot(n, normalize(vec2(-0.55, 0.83)))), 8.0) * 0.5 + 0.07) * rim * m;
      tintA = max(tintA, m * 0.2);
      mask = max(mask, m);
    }
  }

  vec2 uv = v + off * px;
  vec3 col = texture2D(u_field, uv).rgb;
  if (frost > 0.0) {
    // A soft frost: a few taps around the bent sample, only inside the slab.
    float r = 2.5 * frost;
    vec3 acc = col;
    acc += texture2D(u_field, uv + vec2(r, 0.0) * px).rgb;
    acc += texture2D(u_field, uv - vec2(r, 0.0) * px).rgb;
    acc += texture2D(u_field, uv + vec2(0.0, r) * px).rgb;
    acc += texture2D(u_field, uv - vec2(0.0, r) * px).rgb;
    col = mix(col, acc / 5.0, frost);
  }
  // Old glass: a little smoke, a little amber, a faint lift.
  col = mix(col, col * vec3(1.03, 0.985, 0.93) + vec3(0.045, 0.04, 0.032), tintA);
  col *= 1.0 - 0.28 * smoke;
  col += vec3(0.93, 0.89, 0.82) * spec;

  // Grain over everything: one value per device pixel, changing 24 times a second.
  float g = fract(sin(dot(floor(p) + (u_still > 0.5 ? 0.0 : floor(u_time * 24.0)) * 0.37, vec2(12.9898, 78.233))) * 43758.5453);
  col += (g - 0.5) * 0.045;

  gl_FragColor = vec4(col, 1.0);
}
`;

function compile(gl, type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src);
  gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
    throw new Error(gl.getShaderInfoLog(s) || "shader");
  }
  return s;
}

function program(gl, frag) {
  const p = gl.createProgram();
  gl.attachShader(p, compile(gl, gl.VERTEX_SHADER, VERT));
  gl.attachShader(p, compile(gl, gl.FRAGMENT_SHADER, frag));
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) {
    throw new Error(gl.getProgramInfoLog(p) || "link");
  }
  const u = {};
  const n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
  for (let i = 0; i < n; i++) {
    const info = gl.getActiveUniform(p, i);
    const name = info.name.replace(/\[0\]$/, "");
    u[name] = gl.getUniformLocation(p, info.name);
  }
  return { p, u };
}

/** Same curve as object.js: the hour lifts and warms the field. */
export function daylight(hour) {
  const day = Math.max(0, Math.cos(((hour - 13) / 24) * Math.PI * 2)) ** 0.7;
  return {
    day,
    gain: 0.72 + day * 0.28,
    tint: day > 0.5 ? [255, 250, 240] : [186, 198, 224],
  };
}

/**
 * Mounts the glass renderer. Returns null if WebGL is unavailable so the
 * caller can fall back. The handle exposes the same `destroy()` as object.js
 * plus `setDoor(0..1)`, `setSlab(rect)` and `setPebble(rect)` in CSS px.
 *
 * @param {HTMLCanvasElement} canvas
 * @param {{base: {night: number[], day: number[]}, blobs: {rgb: number[], peak: number}[]}} state
 * @param {{onTap?: () => void, still?: boolean}} [opts]
 */
export function mountGlass(canvas, state, opts = {}) {
  const gl =
    canvas.getContext("webgl", { antialias: false, alpha: false, premultipliedAlpha: false }) ||
    canvas.getContext("experimental-webgl");
  if (!gl) return null;

  let field;
  let glass;
  try {
    field = program(gl, FIELD);
    glass = program(gl, GLASS);
  } catch (e) {
    return null;
  }

  const still = opts.still || reduceMotion;
  const seed = Math.random() * 10;

  // One triangle covers the screen.
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);

  // The field texture, half resolution.
  const fbo = gl.createFramebuffer();
  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);

  let w = 0;
  let h = 0;
  let fw = 0;
  let fh = 0;
  let dpr = 1;
  let raf = 0;
  let last = 0;
  let alive = true;
  let born = performance.now();

  const touch = { x: 0.5, y: 0.5, press: 0, down: false, at: 0, sx: 0, sy: 0 };
  let door = 0;
  let slab = { x: 0, y: 0, hw: 0, hh: 0, r: 28 };
  let pebble = { x: 0, y: 0, r: 0 };

  // The unexplained thing — see object.js.
  const nowD = new Date();
  const rare =
    !still &&
    (Math.random() < 1 / 40 || (nowD.getHours() === 4 && nowD.getMinutes() === 4));
  const rareStart = 20 + Math.random() * 40;
  const RARE_LEN = 40;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    dpr = Math.min(devicePixelRatio || 1, 2);
    w = Math.max(1, Math.round(rect.width * dpr));
    h = Math.max(1, Math.round(rect.height * dpr));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      fw = Math.max(1, Math.round(w / 2));
      fh = Math.max(1, Math.round(h / 2));
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, fw, fh, 0, gl.RGB, gl.UNSIGNED_BYTE, null);
    }
  }

  const lights = new Float32Array(9);
  const colours = new Float32Array(12);
  state.blobs.forEach((b, i) => {
    colours[i * 4] = b.rgb[0] / 255;
    colours[i * 4 + 1] = b.rgb[1] / 255;
    colours[i * 4 + 2] = b.rgb[2] / 255;
    colours[i * 4 + 3] = b.peak * 0.5;
  });

  function paint(now) {
    const t = still ? 8000 : (now - born) / 1000;
    const d = new Date();
    const light = daylight(d.getHours() + d.getMinutes() / 60);
    const breath = still ? 1 : 1 + Math.sin((t * Math.PI * 2) / 6) * (0.035 + touch.press * 0.03);

    // Lights, as in object.js, pulled toward the finger.
    for (let i = 0; i < 3; i++) {
      const s = i + 1;
      let x = 0.5 + Math.sin(t / (17 + s * 6) + s) * 0.26;
      let y = 0.5 - Math.cos(t / (23 + s * 5) + s * 2) * 0.24; // y up here
      if (touch.press > 0) {
        const ty = 1 - touch.y;
        const dist = Math.hypot(touch.x - x, ty - y);
        const pull = touch.press * Math.max(0, 1 - dist / 0.9) * 0.62;
        x += (touch.x - x) * pull;
        y += (ty - y) * pull;
      }
      lights[i * 3] = x;
      lights[i * 3 + 1] = y;
      lights[i * 3 + 2] = (0.34 + Math.sin(t / (13 + s * 3)) * 0.07) * breath;
      colours[i * 4 + 3] = state.blobs[i].peak * 0.5 * (1 + touch.press * 0.22);
    }

    const base = state.base.night.map((c, i) => (c + (state.base.day[i] - c) * light.day) / 255);

    // Pass one.
    gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
    gl.viewport(0, 0, fw, fh);
    gl.useProgram(field.p);
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    const aF = gl.getAttribLocation(field.p, "a");
    gl.enableVertexAttribArray(aF);
    gl.vertexAttribPointer(aF, 2, gl.FLOAT, false, 0, 0);
    gl.uniform2f(field.u.u_res, fw, fh);
    gl.uniform1f(field.u.u_time, t);
    gl.uniform3f(field.u.u_base, base[0], base[1], base[2]);
    gl.uniform3f(field.u.u_tint, light.tint[0] / 255, light.tint[1] / 255, light.tint[2] / 255);
    gl.uniform1f(field.u.u_gain, light.gain);
    gl.uniform3fv(field.u.u_light, lights);
    gl.uniform4fv(field.u.u_colour, colours);
    if (rare && t > rareStart && t < rareStart + RARE_LEN) {
      const p = (t - rareStart) / RARE_LEN;
      gl.uniform4f(field.u.u_ring, 0.15 + p * 0.7, 0.38 + Math.sin(p * Math.PI) * 0.22, 0.2, Math.sin(p * Math.PI) * 0.09 * light.gain);
    } else {
      gl.uniform4f(field.u.u_ring, 0, 0, 0, 0);
    }
    gl.drawArrays(gl.TRIANGLES, 0, 3);

    // Pass two.
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, w, h);
    gl.useProgram(glass.p);
    const aG = gl.getAttribLocation(glass.p, "a");
    gl.enableVertexAttribArray(aG);
    gl.vertexAttribPointer(aG, 2, gl.FLOAT, false, 0, 0);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.uniform1i(glass.u.u_field, 0);
    gl.uniform2f(glass.u.u_res, w, h);
    gl.uniform1f(glass.u.u_time, t);
    gl.uniform1f(glass.u.u_seed, seed);
    gl.uniform1f(glass.u.u_still, still ? 1 : 0);
    // The lens grows with the press and follows the finger.
    gl.uniform3f(glass.u.u_lens, touch.x * w, (1 - touch.y) * h, 72 * dpr * touch.press);
    gl.uniform1f(glass.u.u_lensA, Math.min(1, touch.press * 1.4));
    // The slab rises a little as the door opens.
    const lift = (1 - door) * 24 * dpr;
    gl.uniform4f(glass.u.u_slab, slab.x * dpr, h - (slab.y + lift / dpr) * dpr, slab.hw * dpr, slab.hh * dpr);
    gl.uniform1f(glass.u.u_slabA, door);
    gl.uniform1f(glass.u.u_slabR, slab.r * dpr);
    gl.uniform3f(glass.u.u_pebble, pebble.x * dpr, h - pebble.y * dpr, pebble.r * dpr);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  let doorFrom = 0;
  let doorTo = 0;
  let doorStart = 0;
  let doorDur = 0;
  const easeOut = (x) => 1 - Math.pow(1 - x, 3.2); // close to cubic-bezier(.23,1,.32,1)

  function frame(now) {
    if (!alive) return;
    raf = requestAnimationFrame(frame);
    const live = touch.down || touch.press > 0.01 || door !== doorTo;
    if (now - last < 1000 / (live ? FPS_LIVE : FPS_IDLE)) return;
    last = now;
    const target = touch.down ? 1 : 0;
    touch.press += (target - touch.press) * (touch.down ? 0.12 : 0.07);
    if (Math.abs(touch.press - target) < 0.002) touch.press = target;
    if (door !== doorTo) {
      const k = doorDur ? Math.min(1, (now - doorStart) / doorDur) : 1;
      door = doorFrom + (doorTo - doorFrom) * easeOut(k);
      if (k >= 1) door = doorTo;
    }
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
    /** Door 0..1. Opening takes 280 ms, closing 200 ms; still: at once. */
    setDoor(open) {
      doorFrom = door;
      doorTo = open ? 1 : 0;
      doorStart = performance.now();
      doorDur = still ? 0 : open ? 280 : 200;
      if (still) {
        door = doorTo;
        paint(performance.now());
      }
    },
    /** Where the slab sits, in CSS px: centre and half sizes. */
    setSlab(rect) {
      slab = {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2,
        hw: rect.width / 2,
        hh: rect.height / 2,
        r: 28,
      };
    },
    /** Where the pebble sits, in CSS px. */
    setPebble(rect) {
      pebble = {
        x: rect.left + rect.width / 2 + 4,
        y: rect.top + rect.height / 2 - 3,
        r: Math.max(rect.width, rect.height) * 0.46,
      };
      if (still) paint(performance.now());
    },
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
      gl.getExtension("WEBGL_lose_context")?.loseContext();
    },
  };
}
