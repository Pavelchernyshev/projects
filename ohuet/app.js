// OHUET, carried.
//
// One screen. The state is there when the app opens — nothing to enter, accept
// or buy. A touch brings the voice; a hold presses the skin; the small mark in
// the corner opens the one door with words behind it. That is the whole
// interface, and everything else is discovered.

import { STATE, LINES, SHIRT, FIRST_LINE_AFTER_MS, LINE_EVERY_MS } from "./data.js";
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

// A touch on the field brings the voice, or lets it go. A hold is the skin and
// is handled inside the field itself.
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

// Glass when the device can do it, the canvas field when it cannot.
const glass = mountGlass(field, STATE, { onTap: toggleVoice });
if (!glass) mountObject(field, STATE, { onTap: toggleVoice });

// The slab sits exactly behind the door's words; the pebble exactly under the
// mark. Both are measured from the DOM so the glass and the text never drift.
function place() {
  if (!glass) return;
  glass.setPebble(mark.getBoundingClientRect());
  const body = document.querySelector(".door-body");
  const wasHidden = door.hidden;
  if (wasHidden) door.hidden = false; // measure the box even while the door is shut
  glass.setSlab(body.getBoundingClientRect());
  if (wasHidden) door.hidden = true;
}
addEventListener("resize", place);
requestAnimationFrame(place);

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
  speak();
  setInterval(speak, LINE_EVERY_MS);
}, FIRST_LINE_AFTER_MS);

/* ----------------------------------------------------------------- door */

const shirt = document.querySelector(".shirt");
if (SHIRT.url) {
  const a = document.createElement("a");
  a.href = SHIRT.url;
  a.rel = "noopener";
  a.target = "_blank";
  a.textContent = `${SHIRT.line} ${SHIRT.price}.`;
  shirt.appendChild(a);
} else {
  shirt.textContent = `${SHIRT.line} ${SHIRT.price}.`;
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

// The state arrives from black over three seconds. It is given before anything
// is asked.
requestAnimationFrame(() => {
  requestAnimationFrame(() => document.body.classList.remove("arriving"));
});

if ("serviceWorker" in navigator) {
  addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      /* offline or not — the state is already here */
    });
  });
}
