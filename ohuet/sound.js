// The voice.
//
// Not background music: a low, continuous sound that changes without changing.
// Three layers — a sub drone, a filtered pad, a breath of air — each on its own
// slow stereo drift, so the source never sits still and is hard to place. Every
// minute or two a fifth swells above the pad for a while and dissolves:
// almost located → lost → rediscovered → resolved.
//
// Everything is synthesised on the device. There is no file to download and
// nothing to find elsewhere.

let ctx = null;
let master = null;
let running = false;
let resolveTimer = 0;
let layers = [];

const FADE_IN = 8;
const FADE_OUT = 6;

function osc(type, freq, detune = 0) {
  const o = ctx.createOscillator();
  o.type = type;
  o.frequency.value = freq;
  o.detune.value = detune;
  return o;
}

// A very slow LFO driving one AudioParam around a centre value.
function drift(param, centre, depth, period, phase = 0) {
  const lfo = osc("sine", 1 / period);
  const g = ctx.createGain();
  g.gain.value = depth;
  lfo.connect(g).connect(param);
  param.value = centre;
  lfo.start(ctx.currentTime + phase);
  return lfo;
}

function layer(gainValue, panPeriod, panPhase) {
  const g = ctx.createGain();
  g.gain.value = gainValue;
  const pan = ctx.createStereoPanner();
  drift(pan.pan, 0, 0.7, panPeriod, panPhase);
  g.connect(pan).connect(master);
  return g;
}

function build() {
  const t = ctx.currentTime;

  // Sub: two sines a hair apart. The beat between them is the slowest pulse.
  const sub = layer(0.22, 53, 0);
  [55, 55.35].forEach((f) => {
    const o = osc("sine", f);
    o.connect(sub);
    o.start(t);
    layers.push(o);
  });

  // Pad: a bare fifth an octave up, three detuned voices each, through a low
  // filter whose cutoff wanders. Density changes; the chord does not.
  const pad = layer(0.16, 37, 9);
  const lp = ctx.createBiquadFilter();
  lp.type = "lowpass";
  lp.Q.value = 0.4;
  drift(lp.frequency, 520, 260, 41, 3);
  lp.connect(pad);
  [110, 164.81].forEach((f, i) => {
    [-6, 0, 7].forEach((cents) => {
      const o = osc(i ? "sine" : "triangle", f, cents);
      const g = ctx.createGain();
      g.gain.value = 0.33;
      o.connect(g).connect(lp);
      o.start(t);
      layers.push(o);
    });
  });

  // Air: band-passed noise, barely there, breathing on its own long cycle.
  const air = layer(0.05, 23, 17);
  drift(air.gain, 0.05, 0.03, 29, 5);
  const bp = ctx.createBiquadFilter();
  bp.type = "bandpass";
  bp.frequency.value = 1200;
  bp.Q.value = 0.6;
  const seconds = 4;
  const buffer = ctx.createBuffer(1, ctx.sampleRate * seconds, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
  const noise = ctx.createBufferSource();
  noise.buffer = buffer;
  noise.loop = true;
  noise.connect(bp).connect(air);
  noise.start(t);
  layers.push(noise);

  // Resolution: the fifth above the pad (E4, then its octave) swelling for ten
  // seconds every minute or two, from a place of its own.
  const swell = layer(0, 19, 2);
  const s1 = osc("sine", 329.63);
  const s2 = osc("sine", 659.25, 4);
  const s2g = ctx.createGain();
  s2g.gain.value = 0.3;
  s1.connect(swell);
  s2.connect(s2g).connect(swell);
  s1.start(t);
  s2.start(t);
  layers.push(s1, s2);

  swellGain = swell.gain;
}

let swellGain = null;

function resolve() {
  if (!running) return;
  const now = ctx.currentTime;
  swellGain.cancelScheduledValues(now);
  swellGain.setValueAtTime(swellGain.value, now);
  swellGain.linearRampToValueAtTime(0.06, now + 6);
  swellGain.linearRampToValueAtTime(0, now + 14);
  resolveTimer = setTimeout(resolve, 70000 + Math.random() * 80000);
}

export function isOn() {
  return running;
}

/** Starts the voice, or brings it back. Must be called from a user gesture. */
export async function start() {
  if (!ctx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return false;
    ctx = new AC();
    master = ctx.createGain();
    master.gain.value = 0;
    master.connect(ctx.destination);
    build();
  }
  if (ctx.state === "suspended") await ctx.resume();
  running = true;
  const now = ctx.currentTime;
  master.gain.cancelScheduledValues(now);
  master.gain.setValueAtTime(master.gain.value, now);
  master.gain.linearRampToValueAtTime(0.9, now + FADE_IN);
  clearTimeout(resolveTimer);
  resolveTimer = setTimeout(resolve, 25000 + Math.random() * 30000);
  return true;
}

/** Lets the voice go — over six seconds, never cut. */
export function stop() {
  if (!ctx || !running) return;
  running = false;
  clearTimeout(resolveTimer);
  const now = ctx.currentTime;
  master.gain.cancelScheduledValues(now);
  master.gain.setValueAtTime(master.gain.value, now);
  master.gain.linearRampToValueAtTime(0, now + FADE_OUT);
}

// With the app hidden the voice pauses rather than plays to no one; it comes
// back where it was when the app returns.
addEventListener("visibilitychange", () => {
  if (!ctx || !running) return;
  if (document.hidden) ctx.suspend();
  else ctx.resume();
});
