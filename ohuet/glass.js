// The state, in glass.
//
// Two passes. The first paints the field — three tints, the breath, the hour,
// the finger's pull, the rare ring — into a half-resolution texture. The
// second puts glass over it:
//
//   the stone   — a dome of glass on the bottom edge that a swipe carries up
//                 the screen; it shrinks as it climbs until it is a pebble,
//                 and its size is a straight function of where it is, so it
//                 follows the finger both ways. Its light gathers at the crown
//                 and answers the force of the hand, not its speed. The one
//                 gesture in the product.
//   the wordmark — thick glass letters, on arrival, fading as the stone rises;
//   the lens    — liquid glass that forms under a still finger (the skin);
//   the bubbles — a few that surface through the pebble once it has landed
//                 and breathe above it, and dip away when it is sent back.
//
// Geometry, thresholds and springs follow the measured welcome-screen study
// (a 402 × 874 reference, scaled by width and height separately). The
// material is OHUET's: milk rather than clear, one warm grey family, light as
// the only accent — no colour in the caustic, no dispersion of the channels —
// and every edge wobbled by a few pixels of noise.
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
    col = mix(col, rgb, clamp(a, 0.0, 1.0));
  }
  if (u_ring.w > 0.0) {
    vec2 c = vec2((u_ring.x - 0.5) * aspect, u_ring.y - 0.5);
    float d = abs(length(p - c) - u_ring.z);
    col = mix(col, vec3(1.0, 0.99, 0.97), u_ring.w * 2.0 * (1.0 - smoothstep(0.0, 0.03, d)));
  }
  float e = length(p) / (0.72 * max(aspect, 1.0));
  col *= 1.0 - 0.2 * smoothstep(0.25, 1.0, e);
  gl_FragColor = vec4(col, 1.0);
}
`;

// Pass two: the glass.
const GLASS = `
precision highp float;
varying vec2 v;
uniform sampler2D u_field;
uniform sampler2D u_word;  // the wordmark as a soft height map
uniform vec2 u_res;        // canvas, device px
uniform float u_time;
uniform float u_seed;
uniform float u_still;

uniform vec3 u_stone;      // centre x, y (device px, y up), radius
uniform float u_amount;    // lens thickness: 0.42 at the dome, 0.62 at the pebble
uniform float u_bezel;     // share of the radius that is bevel: 0.25 → 0.42
uniform vec2 u_slosh;      // device px: the liquid inside dragged along with the motion
uniform float u_glow;      // 0..1, how hard the stone is being pushed
uniform vec2 u_dir;        // unit vector toward the leading edge
uniform float u_small;     // 0 = the dome, 1 = the pebble
uniform float u_caus;      // how much of the caustic this size of stone shows

uniform vec3 u_lens;       // the finger's lens: x, y, radius
uniform float u_lensA;

uniform vec4 u_wordRect;   // centre x, y, half-width, half-height
uniform float u_wordA;
uniform float u_wordLiquid;

uniform vec4 u_bub[6];     // bubbles: x, y, radius, alpha

const vec2 LIGHT = vec2(-0.55, 0.83);

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x),
             mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}

// The wordmark's height at a point, with the edge wobbled and, while liquid,
// the whole thing still moving.
float wordH(vec2 p) {
  vec2 uv = (p - u_wordRect.xy) / (u_wordRect.zw * 2.0) + 0.5;
  uv += (vec2(noise(p * 0.03 + u_seed), noise(p * 0.03 - u_seed)) - 0.5) * 0.006;
  if (u_wordLiquid > 0.0 && u_still < 0.5) {
    uv += vec2(sin(p.y * 0.02 + u_time * 1.7), cos(p.x * 0.02 - u_time * 1.3)) * 0.03 * u_wordLiquid;
  }
  if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) return 0.0;
  return texture2D(u_word, vec2(uv.x, 1.0 - uv.y)).r;
}

void main() {
  vec2 p = v * u_res;          // device px, y up
  vec2 px = 1.0 / u_res;
  vec2 off = vec2(0.0);
  float spec = 0.0;   // light, the one accent
  float milk = 0.0;   // how much the glass whitens what is behind it
  float shade = 0.0;  // the dark side of an edge, so the form reads
  float warm = 0.0;   // a faint amber, where old glass goes thick

  // ── the wordmark ──────────────────────────────────────────────────────────
  if (u_wordA > 0.0) {
    float h = wordH(p);
    if (h > 0.02) {
      float e = 2.0;
      vec2 g = vec2(wordH(p + vec2(e, 0.0)) - wordH(p - vec2(e, 0.0)),
                    wordH(p + vec2(0.0, e)) - wordH(p - vec2(0.0, e)));
      float slope = length(g);
      vec2 n = slope > 0.0001 ? g / slope : vec2(0.0);
      float body = smoothstep(0.25, 0.6, h);
      float bevel = smoothstep(0.02, 0.35, slope * 6.0) * body;
      float thick = noise(p * 0.01 + u_seed * 2.0) - 0.5;
      float bend = 34.0 + 60.0 * u_wordLiquid;
      off += (-n * bevel * bend + vec2(thick, -thick) * 10.0 * body) * u_wordA;
      float sh = pow(max(0.0, dot(n, normalize(LIGHT))), 5.0);
      float back = pow(max(0.0, dot(-n, normalize(LIGHT))), 3.0);
      spec += (sh * 0.9 + 0.06) * bevel * u_wordA;
      shade += back * bevel * 0.55 * u_wordA;
      milk = max(milk, body * 0.3 * u_wordA);
    }
  }

  // ── the stone ─────────────────────────────────────────────────────────────
  {
    vec2 d = (p - u_stone.xy) / u_stone.z;
    float ang = atan(d.y, d.x);
    // the edge wanders: a little more at the dome, less on the pebble
    float wob = 1.0 + (0.006 * sin(ang * 5.0 + u_seed * 5.0) + 0.0025 * sin(ang * 13.0 - u_seed)) * (1.0 - 0.5 * u_small);
    float rr = length(d) / wob;
    float aa = 1.4 / u_stone.z;
    float inside = 1.0 - smoothstep(1.0 - aa, 1.0 + aa, rr);
    vec2 nd = d / max(length(d), 1e-4);

    if (rr < 1.34) {
      // the lens: a thick glass that magnifies toward the centre and shears
      // hard at the bevelled rim; the liquid inside lags the glass
      if (rr < 1.0) {
        float bev = smoothstep(1.0 - u_bezel, 1.0, rr);
        float k = u_amount * (0.42 + 0.58 * bev * bev);
        vec2 back = (p - u_stone.xy) * k + u_slosh * (1.0 - rr * rr);
        off -= back * inside;
      }

      // halo outside the rim: a soft shade, heavier below, that sets the stone
      // in front of the page
      float haloW = mix(0.075, 0.20, u_small);
      float halo = (1.0 - smoothstep(1.0, 1.0 + haloW, rr)) * (1.0 - inside);
      shade += halo * (0.075 + 0.11 * (1.0 - smoothstep(-1.0, 0.4, d.y))) * mix(1.0, 1.5, u_small) * 0.9;

      // the body: milk, a little more at the crown of the dome
      float dome = 1.0 - smoothstep(0.0, 1.0, rr);
      float a = mix(0.05 + 0.05 * dome, 0.16 + 0.06 * dome, u_small);
      milk = max(milk, a * inside);
      warm = max(warm, (0.14 + 0.10 * (1.0 - dome)) * inside);
      // the glass is thick at its edge: a shadow inside the rim on the side
      // away from the light, so the body reads on a pale page
      float away = pow(max(0.0, dot(-nd, normalize(LIGHT))), 1.5);
      shade += smoothstep(0.70, 0.985, rr) * (1.0 - smoothstep(0.985, 1.0, rr)) * (0.06 + 0.20 * away) * inside;

      // rim and sheen: one hairline at the edge, a broad sheen toward the
      // light, a fainter one on the low rim
      float rim   = smoothstep(0.958, 0.990, rr) * (1.0 - smoothstep(0.990, 1.0, rr));
      float inner = smoothstep(0.90, 0.975, rr) * (1.0 - smoothstep(0.975, 1.0, rr));
      float up    = clamp(dot(nd, normalize(LIGHT)), 0.0, 1.0);
      float sheen = smoothstep(0.86, 0.945, rr) * (1.0 - smoothstep(0.965, 0.995, rr)) * pow(up, 1.3)
                  + smoothstep(0.62, 0.90, rr) * (1.0 - smoothstep(0.90, 0.97, rr)) * pow(up, 2.2) * 0.35;
      float lowRim = smoothstep(0.86, 0.975, rr) * (1.0 - smoothstep(0.975, 1.0, rr))
                   * pow(clamp(dot(nd, normalize(vec2(0.42, -0.90))), 0.0, 1.0), 2.4);
      spec += (rim * mix(0.36, 0.62, u_small) + sheen * mix(0.22, 0.30, u_small) + lowRim * mix(0.08, 0.30, u_small)) * inside;
      shade += inner * 0.16 * inside;

      // the light gathering at the crown: it answers force, and focuses from
      // a soft bloom into a bowl. In OHUET it is light, not colour.
      float g = u_glow * u_caus;
      if (g > 0.002) {
        spec += g * 0.06 * (1.0 - smoothstep(0.80, 1.0, rr)) * inside;
        vec2 ax = u_dir;
        vec2 pxa = vec2(-ax.y, ax.x);
        float uu = dot(d, pxa);
        float vv = dot(d, ax);
        float focus = smoothstep(0.10, 0.80, g);
        float holeR = mix(0.06, 0.245, focus);
        float soft  = mix(0.55, 0.0, focus);
        float eo = length(vec2(uu / 0.52, (vv - 0.639) / 0.361));
        float eh = length(vec2(uu, vv - 0.750)) / holeR;
        float band = (1.0 - smoothstep(0.86 - soft, 1.06 + soft * 0.5, eo))
                   * smoothstep(0.80 - soft * 0.6, 1.18 + soft, eh);
        band *= 1.0 - smoothstep(0.955, 1.0, rr);
        float grade = 0.28 + 0.72 * smoothstep(0.42, 0.80, eo);
        float ba = band * grade * mix(0.55, 0.92, focus) * g;
        spec += ba * 0.34 * inside;
        // deeper in the bowl the glass goes thick, and thick old glass is warm
        warm += band * smoothstep(0.42, 0.80, eo) * g * 0.6 * inside;
        // the light that gets through the hole
        spec += (1.0 - smoothstep(0.10, 1.06, eh)) * g * 0.18 * focus * (1.0 - smoothstep(0.94, 1.0, rr)) * inside;
        // and a trace along the rim, strongest where the bowl meets it
        float lobe = 0.45 + 0.55 * (1.0 - smoothstep(0.55, 1.25, eo));
        spec += rim * lobe * g * 0.5 * inside;
      }

      // the pebble's edge: a fine dark line, so it sits on the page
      if (u_small > 0.01) {
        float line = smoothstep(0.985, 0.995, rr) * (1.0 - smoothstep(0.995, 1.0, rr));
        shade += line * 0.30 * u_small;
      }
    }
  }

  // ── the bubbles ───────────────────────────────────────────────────────────
  for (int k = 0; k < 6; k++) {
    vec4 b = u_bub[k];
    if (b.w > 0.001 && b.z > 0.5) {
      float d = length(p - b.xy) - b.z;
      float m = (1.0 - smoothstep(0.0, 1.0, d)) * b.w;
      if (m > 0.0) {
        vec2 n = (p - b.xy) / max(length(p - b.xy), 0.001);
        float rim = 1.0 - smoothstep(0.0, b.z * 0.55, -d);
        off += n * rim * b.z * 0.9 * m;
        float sh = pow(max(0.0, dot(n, normalize(LIGHT))), 4.0);
        spec += (rim * (0.35 + 0.45 * sh) + 0.05) * m;
        shade += pow(max(0.0, dot(-n, normalize(LIGHT))), 3.0) * rim * 0.12 * m;
        milk = max(milk, 0.2 * m);
      }
    }
  }

  // ── the lens under a still finger ─────────────────────────────────────────
  if (u_lensA > 0.0 && u_lens.z > 1.0) {
    float d = length(p - u_lens.xy) - u_lens.z;
    float m = (1.0 - smoothstep(0.0, 2.0, d)) * u_lensA;
    if (m > 0.0) {
      vec2 n = (p - u_lens.xy) / max(length(p - u_lens.xy), 0.001);
      float rim = 1.0 - smoothstep(0.0, u_lens.z * 0.3, -d);
      float ripple = u_still > 0.5 ? 0.0 : sin(-d * 0.22 - u_time * 3.2) * 1.6;
      off += (-(p - u_lens.xy) * 0.24 * (1.0 - rim) + n * (rim * rim * 26.0 + ripple)) * m;
      spec += (pow(max(0.0, dot(n, normalize(LIGHT))), 8.0) * 0.55 + 0.05) * rim * m;
      shade += pow(max(0.0, dot(-n, normalize(LIGHT))), 3.0) * rim * 0.12 * m;
      milk = max(milk, m * 0.14);
    }
  }

  vec2 uv = v + off * px;
  vec3 col = texture2D(u_field, uv).rgb;
  // Old glass, in a light room: milk rather than smoke, a warm cast where it
  // goes thick, the far side of every edge a little darker, the near side lit.
  col = mix(col, vec3(0.985, 0.978, 0.965), clamp(milk, 0.0, 1.0));
  col = mix(col, col * vec3(1.0, 0.975, 0.935), clamp(warm, 0.0, 1.0) * 0.7);
  col -= vec3(0.16, 0.15, 0.14) * shade;
  col += vec3(1.0, 0.995, 0.98) * spec;

  float g = fract(sin(dot(floor(p) + (u_still > 0.5 ? 0.0 : floor(u_time * 24.0)) * 0.37, vec2(12.9898, 78.233))) * 43758.5453);
  col += (g - 0.5) * 0.03;

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
 * Draws the wordmark as a soft height map: white letters on black, blurred
 * so the shader can take a normal from it. The blur width is the bevel.
 */
export function wordMask(lines, w, h) {
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  const ctx = c.getContext("2d");
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, w, h);
  const size = Math.min(w / (Math.max(...lines.map((l) => l.length)) * 0.68), h / (lines.length * 1.02));
  ctx.font = `900 ${size}px ui-sans-serif, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = "#fff";
  ctx.filter = `blur(${Math.round(size * 0.075)}px)`;
  const lh = size * 0.98;
  const top = h / 2 - ((lines.length - 1) * lh) / 2;
  lines.forEach((l, i) => ctx.fillText(l, w / 2, top + i * lh));
  return c;
}

const clamp01 = (x) => Math.max(0, Math.min(1, x));
const lerp = (a, b, t) => a + (b - a) * t;
const unlerp = (a, b, x) => clamp01((x - a) / (b - a));

/**
 * Mounts the glass renderer, which also owns the one gesture. Returns null
 * if WebGL is unavailable so the caller can fall back.
 *
 * @param {HTMLCanvasElement} canvas
 * @param {{base: {night: number[], day: number[]}, blobs: {rgb: number[], peak: number}[]}} state
 * @param {{
 *   onTap?: () => void,
 *   onTravel?: (p: number, slosh: {x: number, y: number}, R: number) => void,
 *   onLand?: (open: boolean) => void,
 *   still?: boolean,
 * }} [opts]
 *   onTravel fires every frame the stone moves, with p (0 gate → 1 open).
 *   onLand fires when the pebble has landed (true) and when it leaves (false).
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

  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);

  function texture() {
    const t = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return t;
  }

  const fbo = gl.createFramebuffer();
  const tex = texture();
  gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);

  const wordTex = texture();
  gl.bindTexture(gl.TEXTURE_2D, wordTex);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.LUMINANCE, 1, 1, 0, gl.LUMINANCE, gl.UNSIGNED_BYTE, new Uint8Array([0]));

  // ── geometry, from the reference (402 × 874), scaled by width and height ──
  let W = 1;   // CSS px
  let H = 1;
  let sx = 1;
  let sy = 1;
  let w = 0;   // device px
  let h = 0;
  let fw = 0;
  let fh = 0;
  let dpr = 1;
  const geo = { R0: 0, R1: 0, RF: 0, CY0: 0, CY1: 0, CX: 0, TRAVEL: 1 };

  function resize() {
    const rect = canvas.getBoundingClientRect();
    W = Math.max(1, rect.width);
    H = Math.max(1, rect.height);
    sx = W / 402;
    sy = H / 874;
    geo.R0 = 245 * sx;
    geo.R1 = 44 * sx;
    geo.RF = 32 * sx;
    geo.CY0 = H;
    geo.CY1 = 0.469 * H;
    geo.CX = W / 2;
    geo.TRAVEL = geo.CY0 - geo.CY1;
    dpr = Math.min(devicePixelRatio || 1, 2);
    w = Math.max(1, Math.round(W * dpr));
    h = Math.max(1, Math.round(H * dpr));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      fw = Math.max(1, Math.round(w / 2));
      fh = Math.max(1, Math.round(h / 2));
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, fw, fh, 0, gl.RGB, gl.UNSIGNED_BYTE, null);
    }
  }

  // ── the stone's state ─────────────────────────────────────────────────────
  // p: 0 at the gate, 1 landed as the pebble, past 1 thrown above its rest.
  const stone = {
    p: 0, v: 0, target: 0, springing: false,
    cx: 0, cxv: 0,               // sideways offset and its velocity
    glow: 0, dirX: 0, dirY: 1,   // the caustic (y up)
    sloshX: 0, sloshY: 0,
    prevCy: 0, prevCx: 0, prevV: 0, warm: 0,
    settled: false, landedAt: 0,
  };
  const SPRING = reduceMotion
    ? { damping: 30, stiffness: 160, mass: 1 }
    : { damping: 15, stiffness: 120, mass: 1.05 };

  function cyOf(p) {
    return geo.CY0 + (geo.CY1 - geo.CY0) * p;
  }
  function radiusOf(p) {
    if (p <= 1) return geo.R0 + (geo.R1 - geo.R0) * p;
    const up = (p - 1) * geo.TRAVEL;
    return geo.RF + (geo.R1 - geo.RF) * Math.exp(-up / (40 * sy));
  }

  // ── the finger ────────────────────────────────────────────────────────────
  const touch = {
    down: false, dragging: false, id: -1,
    x: 0.5, y: 0.5, press: 0,        // for the skin lens (0..1 of the canvas)
    sx: 0, sy: 0, at: 0,             // where it landed, when
    lx: 0, ly: 0, lt: 0,             // last position and time
    vx: 0, vy: 0,                    // CSS px / s
    p0: 0, cx0: 0,
  };
  const SLOP = 6;

  // ── the bubbles ───────────────────────────────────────────────────────────
  // Six at most, born through the pebble's glass once it has landed. They rise
  // and settle into a narrow plume above it and keep breathing there; sent
  // back, they dip and fade as the dome comes home.
  const SIZES = [6, 4, 5, 3, 4.5, 3.5];
  const bubbles = [];
  let bubbleMode = 0;   // 0 idle, 1 emit, 2 leave
  let emitted = 0;
  let nextEmit = 0;
  const bubUniform = new Float32Array(24);

  function spawnBubble(now) {
    const i = emitted;
    const R = radiusOf(stone.p);
    const cx = geo.CX + stone.cx;
    const cy = cyOf(stone.p);
    const ang = (-Math.PI / 2) + (Math.random() * 2 - 1) * (34 * Math.PI) / 180;
    const speed = (90 + Math.random() * 200) * sy * 0.35;
    const t = i / (SIZES.length - 1);
    bubbles.push({
      x: cx + (Math.random() * 2 - 1) * 8 * sx,
      y: cy + (Math.random() * 2 - 1) * 8 * sy,
      vx: Math.cos(ang) * speed,
      vy: Math.sin(ang) * speed,
      r: SIZES[i] * sx,
      scale: 0.34,
      a: 1,
      hx: cx + (Math.random() * 2 - 1) * (14 + 78 * t) * sx,
      hy: cy - R - (18 + 150 * t + Math.random() * 30) * sy,
      phase: Math.random() * Math.PI * 2,
      born: now,
    });
    emitted += 1;
  }

  function stepBubbles(now, dtIn) {
    const dt = Math.min(0.05, dtIn);
    if (bubbleMode === 1 && emitted < SIZES.length && now >= nextEmit) {
      spawnBubble(now);
      nextEmit = now + 30;
    }
    const leaving = bubbleMode === 2;
    const home = stone.p <= 0.02;
    for (const b of bubbles) {
      b.scale = Math.min(1, b.scale + 3.6 * dt);
      if (leaving && !home) {
        // the dip: gravity while the dome is returning
        b.vy += 1500 * sy * dt * 0.5;
        b.vx += Math.sin(now / 400 + b.phase) * 30 * sx * dt;
        const drag = Math.pow(0.55, dt);
        b.vx *= drag;
        b.vy *= drag;
      } else {
        // buoyancy, a wander, and a spring toward home in the plume
        b.vy -= 16 * sy * dt;
        b.vx += Math.sin(now / 900 + b.phase) * 11 * sx * dt;
        b.vy += Math.cos(now / 1300 + b.phase * 1.7) * 7 * sy * dt;
        b.vx += (b.hx - b.x) * 2.0 * dt;
        b.vy += (b.hy - b.y) * 2.0 * dt;
        const drag = Math.pow(0.07, dt);
        b.vx *= drag;
        b.vy *= drag;
        if (leaving && home) b.a = Math.max(0, b.a - 0.65 * dt);
      }
      b.x += b.vx * dt;
      b.y += b.vy * dt;
    }
    for (let i = bubbles.length - 1; i >= 0; i--) {
      if (bubbles[i].a <= 0 || bubbles[i].y > H + 40) bubbles.splice(i, 1);
    }
    if (bubbleMode === 2 && bubbles.length === 0) bubbleMode = 0;
    bubUniform.fill(0);
    bubbles.slice(0, 6).forEach((b, i) => {
      bubUniform[i * 4] = b.x * dpr;
      bubUniform[i * 4 + 1] = h - b.y * dpr;
      bubUniform[i * 4 + 2] = b.r * b.scale * dpr;
      bubUniform[i * 4 + 3] = b.a;
    });
  }

  // ── the wordmark ──────────────────────────────────────────────────────────
  let word = { x: 0, y: 0, hw: 0, hh: 0, a: 0, liquid: 1, dy: 0 };
  const wordTo = { a: 0, liquid: 1, dy: 0 };
  let wordSpring = 0.08;
  let wordFade = 1;

  // The unexplained thing — see object.js.
  const nowD = new Date();
  const rare =
    !still &&
    (Math.random() < 1 / 40 || (nowD.getHours() === 4 && nowD.getMinutes() === 4));
  const rareStart = 20 + Math.random() * 40;
  const RARE_LEN = 40;

  let raf = 0;
  let last = 0;
  let lastFrame = 0;
  let alive = true;
  let born = performance.now();

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

    for (let i = 0; i < 3; i++) {
      const s = i + 1;
      let x = 0.5 + Math.sin(t / (17 + s * 6) + s) * 0.26;
      let y = 0.5 - Math.cos(t / (23 + s * 5) + s * 2) * 0.24;
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

    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, w, h);
    gl.useProgram(glass.p);
    const aG = gl.getAttribLocation(glass.p, "a");
    gl.enableVertexAttribArray(aG);
    gl.vertexAttribPointer(aG, 2, gl.FLOAT, false, 0, 0);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.uniform1i(glass.u.u_field, 0);
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, wordTex);
    gl.uniform1i(glass.u.u_word, 1);
    gl.uniform2f(glass.u.u_res, w, h);
    gl.uniform1f(glass.u.u_time, t);
    gl.uniform1f(glass.u.u_seed, seed);
    gl.uniform1f(glass.u.u_still, still ? 1 : 0);

    // the stone
    const R = radiusOf(stone.p);
    const scx = geo.CX + stone.cx;
    const scy = cyOf(stone.p);
    gl.uniform3f(glass.u.u_stone, scx * dpr, h - scy * dpr, R * dpr);
    gl.uniform1f(glass.u.u_amount, lerp(0.62, 0.42, unlerp(geo.R1, geo.R0, R)));
    gl.uniform1f(glass.u.u_bezel, lerp(0.42, 0.25, unlerp(geo.R1, geo.R0, R)));
    gl.uniform2f(glass.u.u_slosh, stone.sloshX * R * 0.10 * dpr, -stone.sloshY * R * 0.10 * dpr);
    gl.uniform1f(glass.u.u_glow, stone.glow);
    const dn = Math.max(1e-4, Math.hypot(stone.dirX, stone.dirY));
    gl.uniform2f(glass.u.u_dir, stone.dirX / dn, stone.dirY / dn);
    gl.uniform1f(glass.u.u_small, 1 - unlerp(geo.R1 * 1.05, geo.R1 * 1.7, R));
    gl.uniform1f(glass.u.u_caus, unlerp(100 * sx, 190 * sx, R));

    // the finger's lens, only while the finger is still
    gl.uniform3f(glass.u.u_lens, touch.x * w, (1 - touch.y) * h, 72 * dpr * touch.press);
    gl.uniform1f(glass.u.u_lensA, Math.min(1, touch.press * 1.4));

    // the wordmark
    gl.uniform4f(glass.u.u_wordRect, word.x * dpr, h - (word.y + word.dy) * dpr, word.hw * dpr, word.hh * dpr);
    gl.uniform1f(glass.u.u_wordA, word.a * wordFade);
    gl.uniform1f(glass.u.u_wordLiquid, word.liquid);

    gl.uniform4fv(glass.u.u_bub, bubUniform);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  function stepStone(now, dt) {
    // the spring, when the finger has let go
    if (stone.springing) {
      const k = SPRING.stiffness;
      const c = SPRING.damping;
      const m = SPRING.mass;
      // fixed substeps: a slow frame must not slow the stone down
      let left = Math.min(0.25, dt);
      while (left > 0) {
        const h = Math.min(1 / 120, left);
        left -= h;
        const acc = (-k * (stone.p - stone.target) - c * stone.v) / m;
        stone.v += acc * h;
        stone.p += stone.v * h;
        const cacc = (-k * stone.cx - c * stone.cxv) / m;
        stone.cxv += cacc * h;
        stone.cx += stone.cxv * h;
      }
      if (Math.abs(stone.p - stone.target) < 0.0008 && Math.abs(stone.v) < 0.004 && Math.abs(stone.cx) < 0.3) {
        stone.p = stone.target;
        stone.v = 0;
        stone.cx = 0;
        stone.cxv = 0;
        stone.springing = false;
      }
    }

    // ── where the stone is decides the page ─────────────────────────────────
    if (stone.p > 0.97 && !stone.settled && !touch.down) {
      stone.settled = true;
      stone.landedAt = now;
      bubbles.length = 0;
      bubbleMode = 1;
      emitted = 0;
      nextEmit = now + 350;
      if (opts.onLand) opts.onLand(true);
    } else if (stone.p < 0.8 && stone.settled) {
      stone.settled = false;
      if (opts.onLand) opts.onLand(false);
    }
    if (stone.p < 0.35 && bubbleMode === 1) bubbleMode = 2;

    // ── motion → the light ──────────────────────────────────────────────────
    const cy = cyOf(stone.p);
    if (stone.warm < 4) {
      stone.warm += 1;
      stone.prevCy = cy;
      stone.prevCx = stone.cx;
      return;
    }
    const orbVy = (cy - stone.prevCy) / dt;      // CSS px/s, y down
    const orbVx = (stone.cx - stone.prevCx) / dt;
    stone.prevCy = cy;
    stone.prevCx = stone.cx;
    const orbA = (orbVy - stone.prevV) / dt;
    stone.prevV = orbVy;

    const mx = touch.vx + (touch.down ? 0 : orbVx);
    const my = orbVy + touch.vy * 0.7;
    const sp = Math.hypot(mx, my);
    let target = 0;
    if (touch.down && touch.dragging) {
      target = Math.min(1, sp / 430);
      if (sp > 45) {
        // the light gathers at the crown; a sideways shove tilts it, and it
        // only drops to the bottom when pulled straight down
        const tx = (mx / sp) * 0.42;
        const ty = (my / sp > 0.55 ? -1 : 1) * Math.sqrt(1 - tx * tx);   // y up
        stone.dirX += (tx - stone.dirX) * 0.16;
        stone.dirY += (ty - stone.dirY) * 0.16;
      }
    } else {
      const slowing = orbVy * orbA < 0 ? Math.abs(orbA) : 0;
      target = Math.min(1, slowing / 12000);
      if (target > 0.05) {
        stone.dirX += (0 - stone.dirX) * 0.2;
        stone.dirY += (1 - stone.dirY) * 0.2;
      }
    }
    stone.glow += (target - stone.glow) * (target > stone.glow ? 0.22 : 0.12);
    if (stone.glow < 0.002) stone.glow = 0;

    stone.sloshX += (Math.max(-1, Math.min(1, mx / 430)) - stone.sloshX) * 0.12;
    stone.sloshY += (Math.max(-1, Math.min(1, my / 430)) - stone.sloshY) * 0.12;

    const decay = Math.pow(0.02, dt);
    touch.vx *= decay;
    touch.vy *= decay;
  }

  function frame(now) {
    if (!alive) return;
    raf = requestAnimationFrame(frame);
    const wordMoving =
      Math.abs(word.a - wordTo.a) > 0.002 ||
      Math.abs(word.liquid - wordTo.liquid) > 0.002 ||
      Math.abs(word.dy - wordTo.dy) > 0.3;
    const live =
      touch.down || touch.press > 0.01 || stone.springing || stone.glow > 0.01 ||
      Math.abs(stone.sloshX) > 0.01 || Math.abs(stone.sloshY) > 0.01 ||
      bubbleMode !== 0 || bubbles.length > 0 || wordMoving;
    if (now - last < 1000 / (live ? FPS_LIVE : FPS_IDLE)) return;
    const dt = Math.min(0.25, Math.max(0.001, (now - (lastFrame || now)) / 1000));
    lastFrame = now;
    last = now;

    // the skin's lens forms under a still finger and dissolves when it drags
    const pressTarget = touch.down && !touch.dragging ? 1 : 0;
    touch.press += (pressTarget - touch.press) * (pressTarget ? 0.12 : 0.07);
    if (Math.abs(touch.press - pressTarget) < 0.002) touch.press = pressTarget;

    if (wordMoving) {
      word.a += (wordTo.a - word.a) * Math.max(0.06, wordSpring * 0.9);
      word.liquid += (wordTo.liquid - word.liquid) * 0.05;
      word.dy += (wordTo.dy - word.dy) * wordSpring;
    }

    const pBefore = stone.p;
    stepStone(now, dt);
    stepBubbles(now, dt);
    if (opts.onTravel && (stone.p !== pBefore || touch.dragging || stone.springing || Math.abs(stone.sloshX) > 0.01)) {
      opts.onTravel(stone.p, { x: stone.sloshX, y: stone.sloshY }, radiusOf(stone.p));
    }
    paint(now);
  }

  // ── pointer ───────────────────────────────────────────────────────────────
  function locate(e) {
    const r = canvas.getBoundingClientRect();
    touch.x = (e.clientX - r.left) / r.width;
    touch.y = (e.clientY - r.top) / r.height;
  }
  function onDown(e) {
    if (e.button && e.button !== 0) return;
    if (touch.down) return;
    locate(e);
    touch.down = true;
    touch.dragging = false;
    touch.id = e.pointerId;
    touch.at = performance.now();
    touch.sx = touch.lx = e.clientX;
    touch.sy = touch.ly = e.clientY;
    touch.lt = touch.at;
    touch.vx = 0;
    touch.vy = 0;
    touch.p0 = stone.p;
    touch.cx0 = stone.cx;
    try {
      canvas.setPointerCapture(e.pointerId);
    } catch (err) {
      /* nothing */
    }
  }
  function onMove(e) {
    if (!touch.down || e.pointerId !== touch.id) return;
    const now = performance.now();
    const dtm = Math.max(1, now - touch.lt);
    touch.vx = ((e.clientX - touch.lx) / dtm) * 1000;
    touch.vy = ((e.clientY - touch.ly) / dtm) * 1000;
    touch.lx = e.clientX;
    touch.ly = e.clientY;
    touch.lt = now;
    if (!touch.dragging) {
      if (Math.abs(e.clientX - touch.sx) > SLOP || Math.abs(e.clientY - touch.sy) > SLOP) {
        touch.dragging = true;
        stone.springing = false;
        touch.p0 = stone.p;
        touch.cx0 = stone.cx;
        touch.sx = e.clientX;
        touch.sy = e.clientY;
      } else {
        locate(e);
        return;
      }
    }
    // the stone rides the finger 1:1, rubber-banded past either end, and
    // sideways on a soft leash
    const raw = touch.p0 - (e.clientY - touch.sy) / geo.TRAVEL;
    stone.p = raw < 0 ? raw * 0.25 : raw > 1 ? 1 + (raw - 1) * 0.25 : raw;
    const lim = 150 * sx;
    stone.cx = lim * Math.tanh((touch.cx0 + (e.clientX - touch.sx)) / lim);
  }
  function release(e) {
    if (!touch.down || (e && e.pointerId !== touch.id)) return;
    touch.down = false;
    if (touch.dragging) {
      // a flick or enough distance lands it, anything less brings it back;
      // the spring is handed the finger's speed
      const vhat = -touch.vy / geo.TRAVEL;
      const now = performance.now();
      const stale = now - touch.lt > 80;   // the finger stopped before it lifted
      const vel = stale ? 0 : vhat;
      stone.target = stone.p + vel * 0.18 > 0.5 ? 1 : 0;
      stone.v = vel;
      stone.cxv = stale ? 0 : touch.vx;
      stone.springing = true;
      touch.dragging = false;
      return;
    }
    const held = performance.now() - touch.at;
    const moved = e ? Math.hypot(e.clientX - touch.sx, e.clientY - touch.sy) : 0;
    if (held < 320 && moved < 12 && opts.onTap) opts.onTap();
  }
  function onUp(e) {
    release(e);
  }
  function onCancel(e) {
    release(e);
  }
  function onVisibility() {
    if (document.hidden) {
      cancelAnimationFrame(raf);
      raf = 0;
    } else if (alive && !still && !raf) {
      born = performance.now() - (last - born);
      last = 0;
      lastFrame = 0;
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
  raf = requestAnimationFrame(frame);
  paint(performance.now());

  return {
    /** Sends the stone up (open) or home, on its spring. */
    setOpen(open) {
      stone.target = open ? 1 : 0;
      stone.springing = true;
      if (still) {
        stone.p = stone.target;
        stone.v = 0;
        stone.springing = false;
        if (open && !stone.settled) {
          stone.settled = true;
          bubbles.length = 0;
          bubbleMode = 1;
          emitted = 0;
          nextEmit = performance.now() + 350;
          if (opts.onLand) opts.onLand(true);
        } else if (!open && stone.settled) {
          stone.settled = false;
          bubbleMode = 2;
          if (opts.onLand) opts.onLand(false);
        }
        paint(performance.now());
      }
    },
    /** Where the stone is now: 0 at the gate, 1 open. */
    travel() {
      return stone.p;
    },
    /** The wordmark's box in CSS px and its lines; draws the height map. */
    setWord(rect, lines) {
      word.x = rect.left + rect.width / 2;
      word.y = rect.top + rect.height / 2;
      word.hw = rect.width / 2;
      word.hh = rect.height / 2;
      const mask = wordMask(lines, Math.round(rect.width * dpr), Math.round(rect.height * dpr));
      gl.bindTexture(gl.TEXTURE_2D, wordTex);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 0);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.LUMINANCE, gl.LUMINANCE, gl.UNSIGNED_BYTE, mask);
      if (still) paint(performance.now());
    },
    /** Where the wordmark is going: how present, how liquid, how far carried. */
    setWordState({ a, liquid, dy, speed }) {
      if (a !== undefined) wordTo.a = a;
      if (liquid !== undefined) wordTo.liquid = liquid;
      if (dy !== undefined) wordTo.dy = dy;
      wordSpring = speed ?? 0.08;
      if (still) {
        Object.assign(word, wordTo);
        paint(performance.now());
      }
    },
    /** A multiplier on the wordmark's presence, driven by the stone's travel. */
    setWordFade(f) {
      wordFade = clamp01(f);
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
