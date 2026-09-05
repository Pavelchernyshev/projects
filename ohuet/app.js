// OHUET, carried.
//
// One screen. The state is there when the app opens — nothing to enter, accept
// or buy. A touch brings the voice; a hold presses the skin; the small mark in
// the corner opens the one door with words behind it. That is the whole
// interface, and everything else is discovered.

import {
  STATE, LINES, SHIRT, WORD, WORD_SETTLE_MS, WORD_STAY_MS, FIRST_LINE_AFTER_MS, LINE_EVERY_MS,
} from "./data.js";
import { mountObject } from "./object.js";
import { mountGlass } from "./glass.js";
import * as voice from "./sound.js";

const KEY = "ohuet.v1";

/* ---------------------------------------------------------------- memory */

// The only thing remembered: when the state first arrived on this device.
// Private mode in Safari can throw on write; the state must not care.
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
const door = document.querySelector(".door");

let busy = false;
let wordStage = true; // the wordmark is up; taps and lines wait

// A touch on the field brings the voice, or lets it go. A hold is the skin and
// is handled inside the field itself.
async function toggleVoice() {
  if (busy || wordStage) return;
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

// Glass when the device can do it, the canvas field when it cannot.
const glass = mountGlass(field, STATE, { onTap: toggleVoice });
if (!glass) mountObject(field, STATE, { onTap: toggleVoice });

// The slab sits exactly behind the door's words; the wordmark exactly in its
// stage; the horizon's edge crosses at 82% of the height, so the mark sits on
// the stone. All measured from the DOM so glass and text never drift.
const stage = document.querySelector(".word-stage");
const hint = document.querySelector(".hint");
function place() {
  if (!glass) return;
  glass.setHorizon(innerHeight * 0.82, innerWidth);
  glass.setWord(stage.getBoundingClientRect(), WORD);
  const body = document.querySelector(".door-body");
  const wasHidden = door.hidden;
  if (wasHidden) door.hidden = false; // measure the box even while the door is shut
  glass.setSlab(body.getBoundingClientRect());
  if (wasHidden) door.hidden = true;
}
addEventListener("resize", place);

/* ------------------------------------------------------------- arrival */

// The wordmark arrives liquid, settles into glass, and then is let go — by a
// swipe up, or by itself after a while. Nothing is asked; the state is
// already there behind the letters.
let wordTimer = 0;
function letGo(speed = 0.08) {
  if (!wordStage) return;
  wordStage = false;
  clearTimeout(wordTimer);
  hint.classList.remove("shown");
  if (glass) glass.setWordState({ a: 0, liquid: 1, dy: -140, speed });
}

function arrive() {
  place();
  if (!glass) {
    wordStage = false;
    return;
  }
  glass.setWordState({ a: 1, liquid: 1, dy: 0 });
  setTimeout(() => glass.setWordState({ liquid: 0 }), WORD_SETTLE_MS);
  setTimeout(() => { if (wordStage) hint.classList.add("shown"); }, WORD_SETTLE_MS + 900);
  wordTimer = setTimeout(() => letGo(0.05), WORD_STAY_MS);
}

// The swipe: the letters ride the finger 1:1 and grow liquid as they go; on
// release a flick or enough distance lets them go with the finger's speed,
// anything less springs them back.
const swipe = { on: false, y0: 0, dy: 0, vy: 0, t: 0 };
field.addEventListener("pointerdown", (e) => {
  if (!wordStage || !glass) return;
  swipe.on = true;
  swipe.y0 = e.clientY;
  swipe.dy = 0;
  swipe.vy = 0;
  swipe.t = performance.now();
});
field.addEventListener("pointermove", (e) => {
  if (!swipe.on) return;
  const now = performance.now();
  const dy = Math.min(0, e.clientY - swipe.y0);
  swipe.vy = ((dy - swipe.dy) / Math.max(1, now - swipe.t)) * 1000;
  swipe.dy = dy;
  swipe.t = now;
  glass.carryWord(dy * 0.9);
  glass.setWordState({ liquid: Math.min(1, -dy / 160) });
}, { passive: true });
const endSwipe = () => {
  if (!swipe.on) return;
  swipe.on = false;
  if (swipe.dy < -80 || swipe.vy < -700) {
    letGo(Math.min(0.3, 0.1 + Math.abs(swipe.vy) / 6000));
  } else if (wordStage) {
    glass.setWordState({ dy: 0, liquid: 0, speed: 0.1 });
  }
};
field.addEventListener("pointerup", endSwipe);
field.addEventListener("pointercancel", endSwipe);

// Presence. After a while, how long the state has been with you; later still,
// a line. The first minutes are for nothing at all.
setTimeout(() => {
  sinceEl.textContent = withYou(since);
  sinceEl.classList.add("shown");
}, 20000);

let lineAt = 0;
function speak() {
  const text = LINES[lineAt % LINES.length];
  lineAt += 1 + Math.floor(Math.random() * (LINES.length - 1));
  line.textContent = text;
  line.classList.add("shown");
  setTimeout(() => line.classList.remove("shown"), 9000);
}
setTimeout(() => {
  if (!wordStage) speak();
  setInterval(() => { if (!wordStage) speak(); }, LINE_EVERY_MS);
}, FIRST_LINE_AFTER_MS);

/* ----------------------------------------------------------------- door */

const shirt = document.querySelector(".shirt");
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
  shirt.appendChild(host);
}

const keep = document.querySelector(".keep");
const keepHow = document.querySelector(".keep-how");
let installPrompt = null;

addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  installPrompt = e;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "keep-install";
  btn.textContent = "Keep";
  btn.addEventListener("click", async () => {
    const p = installPrompt;
    installPrompt = null;
    btn.remove();
    if (p) await p.prompt();
  });
  keepHow.replaceWith(btn);
});

const standalone =
  typeof matchMedia === "function" && matchMedia("(display-mode: standalone)").matches;
if (standalone || navigator.standalone) keep.hidden = true;

function setDoor(open) {
  if (open && wordStage) letGo(0.12);
  if (open) {
    door.hidden = false;
    place();
    // Two frames so the entrance transition has a "from" to leave.
    requestAnimationFrame(() => requestAnimationFrame(() => door.classList.add("open")));
  } else {
    door.classList.remove("open");
    // Match the glass: the words leave in 200 ms, then the section hides.
    setTimeout(() => { if (!door.classList.contains("open")) door.hidden = true; }, 220);
  }
  if (glass) glass.setDoor(open);
  mark.setAttribute("aria-expanded", String(open));
  document.body.classList.toggle("door-open", open);
}

mark.addEventListener("click", () => setDoor(door.hidden));
// A touch anywhere that isn't a link or a button closes the door again.
door.addEventListener("click", (e) => {
  if (!e.target.closest("a, button")) setDoor(false);
});
addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !door.hidden) setDoor(false);
});

/* -------------------------------------------------------------- arrival */

// The state arrives from black over three seconds, the letters with it. It is
// given before anything is asked.
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
