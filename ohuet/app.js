// OHUET, carried.
//
// One screen, one gesture. The state is there when the app opens — nothing to
// enter, accept or buy. A stone of glass sits on the bottom edge; a swipe up
// carries it to the middle of the screen, where it lands as a pebble and the
// one place with words comes in. Drag it back down and the words go. A touch
// brings the voice; a still finger presses the skin. That is the whole
// interface, and everything else is discovered.

import {
  STATE, LINES, SHIRT, WORD, WORD_SETTLE_MS, WORD_STAY_MS, FIRST_LINE_AFTER_MS, LINE_EVERY_MS,
} from "./data.js";
import { mountObject } from "./object.js";
import { mountGlass } from "./glass.js";
import * as voice from "./sound.js";

const KEY = "ohuet.v1";
const reduceMotion =
  typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ---------------------------------------------------------------- memory */

function firstOpened() {
  try {
    const raw = localStorage.getItem(KEY);
    const data = raw ? JSON.parse(raw) : null;
    if (data && typeof data.since === "number") return data.since;
    const since = Date.now();
    localStorage.setItem(KEY, JSON.stringify({ since }));
    return since;
  } catch (e) {
    return Date.now();
  }
}

function withYou(since) {
  const days = Math.floor((Date.now() - since) / 86400000);
  if (days < 1) return "today";
  if (days === 1) return "one day";
  if (days < 30) return `${days} days`;
  const months = Math.floor(days / 30);
  if (months < 12) return months === 1 ? "one month" : `${months} months`;
  const years = Math.floor(days / 365);
  return years === 1 ? "one year" : `${years} years`;
}

/* ---------------------------------------------------------------- state */

const since = firstOpened();
const field = document.querySelector(".field");
const line = document.querySelector(".line");
const sinceEl = document.querySelector(".since");
const dot = document.querySelector(".voice");
const mark = document.querySelector(".mark");
const stage = document.querySelector(".word-stage");
const hint = document.querySelector(".hint");
const open = document.querySelector(".open");
const headline = document.querySelector(".headline");
const third = document.querySelector(".third");
const keep = document.querySelector(".keep");

let busy = false;
let wordStage = true;
let isOpen = false;

async function toggleVoice() {
  if (busy) return;
  busy = true;
  try {
    if (voice.isOn()) {
      voice.stop();
      dot.hidden = true;
    } else if (await voice.start()) {
      dot.hidden = false;
    }
  } finally {
    busy = false;
  }
}

/* ------------------------------------------------- the copy, with the stone */

// Blur is the reference's language for copy coming and going: nothing
// travels, it goes soft where it stands. The study's intensities map to
// pixels here at roughly a quarter.
const BLUR_PX = 0.25;

let hintReady = false;
function onTravel(p, slosh, R) {
  // the gate: the hint goes soft and out within the first push, carried a
  // little with the liquid; the wordmark fades and goes liquid as the stone
  // rises
  if (hintReady) {
    const hintA = 1 - clamp01((p - 0.06) / 0.24);
    const hintB = 12 * clamp01((p - 0.04) / 0.24) * BLUR_PX;
    hint.style.transition = "none";
    hint.style.opacity = String(hintA);
    hint.style.filter = hintB > 0.05 ? `blur(${hintB.toFixed(2)}px)` : "";
    hint.style.transform = `translate(${(slosh.x * R * 0.04).toFixed(1)}px, ${(slosh.y * R * 0.04).toFixed(1)}px)`;
  }
  if (glass) {
    glass.setWordFade(1 - clamp01((p - 0.08) / 0.54));
    if (wordStage) glass.setWordState({ liquid: clamp01((p - 0.05) / 0.55) });
  }
}

let shown = 0;
let shownFrom = 0;
let shownTo = 0;
let shownStart = 0;
let shownDur = 0;
let shownRaf = 0;
const bezierIn = (x) => 1 - Math.pow(1 - x, 3.2);            // cubic-bezier(.23,1,.32,1), close
const easeOutQuad = (x) => 1 - (1 - x) * (1 - x);
const easeInQuad = (x) => x * x;

function paintShown() {
  headline.style.opacity = String(shown);
  headline.style.filter = shown < 0.995 ? `blur(${((1 - shown) * 14 * BLUR_PX).toFixed(2)}px)` : "";
  keep.style.opacity = String(shown);
  keep.style.transform = `translateY(${((1 - shown) * 10).toFixed(1)}px)`;
  keep.style.pointerEvents = shown > 0.9 ? "auto" : "none";
}

function animateShown(now) {
  const k = shownDur ? Math.min(1, (now - shownStart) / shownDur) : 1;
  const e = shownTo > shownFrom ? bezierIn(k) : easeOutQuad(k);
  shown = shownFrom + (shownTo - shownFrom) * e;
  paintShown();
  if (k < 1) shownRaf = requestAnimationFrame(animateShown);
  else if (shownTo === 0) open.hidden = true;
}

function setShown(to) {
  cancelAnimationFrame(shownRaf);
  shownFrom = shown;
  shownTo = to;
  shownStart = performance.now();
  shownDur = reduceMotion ? 0 : to ? 520 : 240;
  if (to) open.hidden = false;
  shownRaf = requestAnimationFrame(animateShown);
}

// ── the third line: a positional blur wipe, left to right ────────────────────
const IN_MS = 560;
const HOLD_MS = 1950;
const OUT_MS = 400;
const GAP_MS = 460;
const RAMP = 0.34;
const SOFT = 26;
let thirdIndex = 0;
let thirdTimer = 0;
let thirdRaf = 0;
let thirdLive = false;

function layThird(text) {
  third.textContent = "";
  const words = text.split(" ");
  const total = text.length;
  let start = 0;
  words.forEach((wd, i) => {
    if (i) third.appendChild(document.createTextNode(" "));
    const span = document.createElement("span");
    span.textContent = wd;
    span.dataset.at = String((start + wd.length * 0.5) / total);
    third.appendChild(span);
    start += wd.length + 1;
  });
}

function paintWipe(wipe, soften) {
  for (const span of third.children) {
    const at = Number(span.dataset.at);
    const front = -RAMP + wipe * (1 + RAMP * 2);
    const t = clamp01((front - at) / RAMP + 0.5);
    const blur = ((1 - t) * SOFT + soften) * BLUR_PX;
    span.style.opacity = String(t);
    span.style.filter = blur > 0.05 ? `blur(${blur.toFixed(2)}px)` : "";
  }
}

const wipeEase = (x) => {
  // cubic-bezier(0.16, 0.42, 0.40, 1): near-linear, so the front travels at a
  // steady rate instead of dumping the sweep into a couple of frames
  const t = x;
  return 3 * (1 - t) * (1 - t) * t * 0.42 + 3 * (1 - t) * t * t * 1.0 + t * t * t;
};

function revealThird() {
  if (!thirdLive) return;
  layThird(LINES[thirdIndex % LINES.length]);
  third.style.opacity = "1";
  if (reduceMotion) {
    paintWipe(1, 0);
  } else {
    const t0 = performance.now();
    const step = (now) => {
      const k = Math.min(1, (now - t0) / IN_MS);
      paintWipe(wipeEase(k), 0);
      if (k < 1 && thirdLive) thirdRaf = requestAnimationFrame(step);
    };
    thirdRaf = requestAnimationFrame(step);
  }
  thirdTimer = setTimeout(cycleThird, HOLD_MS + IN_MS);
}

function cycleThird() {
  if (!thirdLive) return;
  // out: it goes soft where it stands — the blur leads, the opacity follows
  const t0 = performance.now();
  const step = (now) => {
    const k = Math.min(1, (now - t0) / (reduceMotion ? 1 : OUT_MS));
    paintWipe(1, 19 * easeOutQuad(k));
    third.style.opacity = String(1 - easeInQuad(k));
    if (k < 1 && thirdLive) thirdRaf = requestAnimationFrame(step);
  };
  thirdRaf = requestAnimationFrame(step);
  thirdTimer = setTimeout(() => {
    if (!thirdLive) return;
    thirdIndex += 1;
    thirdTimer = setTimeout(revealThird, GAP_MS);
  }, OUT_MS);
}

function setThirdLive(live) {
  if (live === thirdLive) return;
  thirdLive = live;
  clearTimeout(thirdTimer);
  cancelAnimationFrame(thirdRaf);
  if (live) revealThird();
  else third.style.opacity = "0";
}

function onLand(landed) {
  isOpen = landed;
  if (landed && wordStage) letGo(0.12);
  setShown(landed ? 1 : 0);
  setThirdLive(landed);
  mark.setAttribute("aria-expanded", String(landed));
  document.body.classList.toggle("door-open", landed);
}

/* --------------------------------------------------------- the renderer */

const glass = mountGlass(field, STATE, { onTap: toggleVoice, onTravel, onLand });
if (!glass) mountObject(field, STATE, { onTap: toggleVoice });

function place() {
  if (!glass) return;
  glass.setWord(stage.getBoundingClientRect(), WORD);
}
addEventListener("resize", place);

/* ------------------------------------------------------------- arrival */

// The wordmark arrives liquid, settles into glass, and is let go — by the
// stone rising under it, or by itself after a while. Nothing is asked; the
// state is already there behind the letters.
let wordTimer = 0;
function letGo(speed = 0.08) {
  if (!wordStage) return;
  wordStage = false;
  clearTimeout(wordTimer);
  if (glass) glass.setWordState({ a: 0, liquid: 1, dy: -140, speed });
}

function arrive() {
  place();
  if (!glass) {
    wordStage = false;
    hint.style.opacity = "1";
    return;
  }
  glass.setWordState({ a: 1, liquid: 1, dy: 0 });
  setTimeout(() => glass.setWordState({ liquid: 0 }), WORD_SETTLE_MS);
  setTimeout(() => {
    hintReady = true;
    if (glass.travel() < 0.06) hint.style.opacity = "1";
  }, WORD_SETTLE_MS + 900);
  wordTimer = setTimeout(() => letGo(0.05), WORD_STAY_MS);
}

// Presence. After a while, how long the state has been with you; later still,
// a line. The first minutes are for nothing at all.
setTimeout(() => {
  sinceEl.textContent = withYou(since);
  sinceEl.classList.add("shown");
}, 20000);

let lineAt = 0;
function speak() {
  if (isOpen) return;
  const text = LINES[lineAt % LINES.length];
  lineAt += 1 + Math.floor(Math.random() * (LINES.length - 1));
  line.textContent = text;
  line.classList.add("shown");
  setTimeout(() => line.classList.remove("shown"), 9000);
}
setTimeout(() => {
  speak();
  setInterval(speak, LINE_EVERY_MS);
}, FIRST_LINE_AFTER_MS);

/* ------------------------------------------------------------ the words */

{
  const s = document.createElement("s");
  s.textContent = SHIRT.struck;
  const host = document.createElement(SHIRT.url ? "a" : "span");
  if (SHIRT.url) {
    host.href = SHIRT.url;
    host.rel = "noopener";
    host.target = "_blank";
  }
  host.append(`${SHIRT.before} `, s, ` ${SHIRT.after} ${SHIRT.price}.`);
  headline.appendChild(host);
}

const keepLine = document.querySelector(".keep-line");
const keepHow = document.querySelector(".keep-how");
let installPrompt = null;

addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  installPrompt = e;
  // the line itself becomes the one action
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "keep-line keep-action";
  btn.textContent = keepLine.textContent;
  btn.addEventListener("click", async () => {
    const p = installPrompt;
    installPrompt = null;
    if (p) await p.prompt();
  });
  keepLine.replaceWith(btn);
  keepHow.hidden = true;
});

const standalone =
  typeof matchMedia === "function" && matchMedia("(display-mode: standalone)").matches;
if (standalone || navigator.standalone) keep.hidden = true;

// The mark sends the stone up or home — the same door, for a hand that
// would rather tap, and for a keyboard.
mark.addEventListener("click", () => {
  if (!glass) {
    onLand(!isOpen);   // without glass there is no stone; the words still come
    return;
  }
  glass.setOpen(!(isOpen || glass.travel() > 0.5));
});
addEventListener("keydown", (e) => {
  if (e.key === "Escape" && glass && (isOpen || glass.travel() > 0.5)) glass.setOpen(false);
});

/* -------------------------------------------------------------- arrival */

requestAnimationFrame(() => {
  requestAnimationFrame(() => {
    document.body.classList.remove("arriving");
    arrive();
  });
});

if ("serviceWorker" in navigator) {
  addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      /* offline or not — the state is already here */
    });
  });
}

function clamp01(x) {
  return Math.max(0, Math.min(1, x));
}
