// ACUYETE — магазин, в котором вещь нельзя купить.
//
// Один экран за раз, никаких переходов «назад в списки»: это не каталог, это
// помещение. Роутинг на хэше, чтобы всё работало из файла и с любого статического
// хостинга, и чтобы установленное приложение открывалось ровно там, где вы вышли.

import { OBJECTS, objectBySlug, CODEX } from "./data.js";
import { mountObject } from "./object.js";

const KEY = "acuyete.v1";
const HOLD_MS = 3500; // столько держать палец, чтобы состояние перешло к вам

const app = document.getElementById("app");
let teardown = []; // всё, что надо погасить при уходе с экрана
let installPrompt = null;

/* ------------------------------------------------------------------ хранение */

// Приватный режим Safari умеет бросать на записи в localStorage. Магазин от
// этого не должен падать — просто состояние не переживёт закрытие вкладки.
function load() {
  try {
    const raw = localStorage.getItem(KEY);
    const data = raw ? JSON.parse(raw) : null;
    if (data && typeof data === "object") {
      return { entered: !!data.entered, owned: data.owned || {} };
    }
  } catch (e) {
    /* пусто */
  }
  return { entered: false, owned: {} };
}

function save(state) {
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch (e) {
    /* пусто */
  }
}

let state = load();

function acquire(obj) {
  if (state.owned[obj.slug]) return state.owned[obj.slug];
  // Номер в тираже назначается здесь же, на устройстве: у концепта нет сервера,
  // который вёл бы книгу тиража. В настоящем магазине номер выдаёт касса.
  const record = {
    edition: 1 + Math.floor(Math.random() * obj.edition),
    at: Date.now(),
  };
  state.owned[obj.slug] = record;
  save(state);
  return record;
}

/* -------------------------------------------------------------------- утилиты */

function plural(n, one, few, many) {
  const a = Math.abs(n) % 100;
  const b = a % 10;
  if (a > 10 && a < 20) return many;
  if (b > 1 && b < 5) return few;
  if (b === 1) return one;
  return many;
}

function withYou(since) {
  const ms = Date.now() - since;
  const days = Math.floor(ms / 86400000);
  if (days >= 1) return `${days} ${plural(days, "день", "дня", "дней")} с вами`;
  const hours = Math.floor(ms / 3600000);
  if (hours >= 1) return `${hours} ${plural(hours, "час", "часа", "часов")} с вами`;
  const min = Math.floor(ms / 60000);
  if (min >= 1) return `${min} ${plural(min, "минута", "минуты", "минут")} с вами`;
  return "только что";
}

function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

function go(hash) {
  if (location.hash === hash) render();
  else location.hash = hash;
}

function ownedCount() {
  return Object.keys(state.owned).length;
}

/* --------------------------------------------------------------------- экраны */

function chrome(active) {
  const nav = el(`
    <nav class="chrome">
      <a class="mark" href="#/store" aria-label="ACUYETE">ACUYETE</a>
      <div class="chrome-links">
        <a href="#/store"${active === "store" ? ' aria-current="page"' : ""}>витрина</a>
        <a href="#/state"${active === "state" ? ' aria-current="page"' : ""}>состояние${
          ownedCount() ? ` <i>${ownedCount()}</i>` : ""
        }</a>
        <a href="#/codex"${active === "codex" ? ' aria-current="page"' : ""}>кодекс</a>
      </div>
    </nav>
  `);
  return nav;
}

function viewThreshold() {
  const node = el(`
    <main class="screen threshold">
      <canvas class="field" aria-hidden="true"></canvas>
      <div class="threshold-body">
        <p class="eyebrow">MMXXVI</p>
        <h1 class="wordmark">ACUYETE</h1>
        <p class="lede">Вещи, которые нельзя купить.<br>И состояние, которое можно.</p>
        <button class="enter" type="button">Войти</button>
      </div>
    </main>
  `);
  const o = mountObject(node.querySelector(".field"), OBJECTS[0].palette, {
    intensity: 0.75,
  });
  teardown.push(o.destroy);
  node.querySelector(".enter").addEventListener("click", () => {
    state.entered = true;
    save(state);
    go("#/store");
  });
  return node;
}

function viewStore() {
  const node = el(`
    <main class="screen store">
      <header class="store-head">
        <p class="eyebrow">Витрина · три объекта · MMXXVI</p>
        <h2 class="title">Всё, что здесь висит, существует. Ничего из этого нельзя унести.</h2>
      </header>
      <div class="shelf"></div>
      <footer class="store-foot">
        <a href="#/install">Поставить магазин на телефон</a>
      </footer>
    </main>
  `);
  const shelf = node.querySelector(".shelf");

  OBJECTS.forEach((obj) => {
    const owned = state.owned[obj.slug];
    const card = el(`
      <a class="card" href="#/object/${obj.slug}">
        <span class="card-field"><canvas aria-hidden="true"></canvas></span>
        <span class="card-body">
          <span class="eyebrow">${obj.index}</span>
          <span class="card-name">${obj.name}</span>
          <span class="card-thing">${obj.thing}</span>
          <span class="card-prices">
            <span class="struck">${obj.thingPrice}</span>
            <span class="not-for-sale">не продаётся</span>
          </span>
          <span class="card-state">${
            owned ? `ваше · № ${owned.edition}` : `состояние — ${obj.statePrice}`
          }</span>
        </span>
      </a>
    `);
    shelf.appendChild(card);
    const o = mountObject(card.querySelector("canvas"), obj.palette, {
      intensity: 0.8,
    });
    teardown.push(o.destroy);
  });

  return node;
}

function viewObject(slug) {
  const obj = objectBySlug(slug);
  if (!obj) return viewStore();
  const owned = state.owned[obj.slug];

  const node = el(`
    <main class="screen object">
      <div class="object-field"><canvas aria-hidden="true"></canvas></div>
      <div class="object-body">
        <p class="eyebrow">${obj.index} · ${obj.year}</p>
        <h2 class="object-name">${obj.name}</h2>
        <p class="object-line">${obj.line}</p>

        <dl class="spec">
          <div><dt>Вещь</dt><dd>${obj.thing}</dd></div>
          <div><dt>Цена вещи</dt><dd><span class="struck">${obj.thingPrice}</span> <span class="not-for-sale">не продаётся</span></dd></div>
          <div><dt>Состояние</dt><dd>${obj.statePrice} · тираж ${obj.edition}</dd></div>
          <div><dt>Где живёт</dt><dd>На вашем телефоне. Без сети, без аккаунта, без ленты.</dd></div>
        </dl>

        <div class="object-act"></div>
        <p class="back"><a href="#/store">← в витрину</a></p>
      </div>
    </main>
  `);

  const o = mountObject(node.querySelector("canvas"), obj.palette);
  teardown.push(o.destroy);

  const act = node.querySelector(".object-act");
  if (owned) {
    act.appendChild(
      el(`<p class="owned-note">Состояние уже ваше · № ${owned.edition} из ${obj.edition} · <a href="#/state">открыть</a></p>`),
    );
  } else {
    const btn = el(`<a class="cta" href="#/take/${obj.slug}">Принять состояние — ${obj.statePrice}</a>`);
    act.appendChild(btn);
    act.appendChild(el(`<p class="fine">Оплата в этом концепте не подключена: состояние переходит к вам сразу после ритуала.</p>`));
  }
  return node;
}

// Ритуал вместо кнопки «купить». Три с половиной секунды пальцем — столько,
// сколько нужно, чтобы это перестало быть кликом.
function viewTake(slug) {
  const obj = objectBySlug(slug);
  if (!obj) return viewStore();
  if (state.owned[obj.slug]) return viewState();

  const node = el(`
    <main class="screen take">
      <canvas class="field" aria-hidden="true"></canvas>
      <div class="take-body">
        <p class="eyebrow">${obj.index} · ${obj.name}</p>
        <h2 class="title">Держите, пока не перейдёт</h2>
        <button class="hold" type="button" aria-describedby="hold-hint">
          <span class="hold-ring"></span>
          <span class="hold-label">держать</span>
        </button>
        <p class="fine" id="hold-hint">Отпустите — и всё вернётся как было. ${obj.statePrice} · № из тиража ${obj.edition}.</p>
        <p class="back"><a href="#/object/${obj.slug}">← назад</a></p>
      </div>
    </main>
  `);

  const o = mountObject(node.querySelector(".field"), obj.palette, { intensity: 0.9 });
  teardown.push(o.destroy);

  const btn = node.querySelector(".hold");
  const label = node.querySelector(".hold-label");
  let raf = 0;
  let start = 0;
  let done = false;

  const tick = (now) => {
    const p = Math.min(1, (now - start) / HOLD_MS);
    btn.style.setProperty("--p", p.toFixed(4));
    if (p >= 1) {
      done = true;
      acquire(obj);
      go("#/state");
      return;
    }
    raf = requestAnimationFrame(tick);
  };

  const begin = (e) => {
    if (done) return;
    e.preventDefault();
    btn.classList.add("holding");
    label.textContent = "тише";
    start = performance.now();
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(tick);
  };

  const end = () => {
    if (done) return;
    cancelAnimationFrame(raf);
    raf = 0;
    btn.classList.remove("holding");
    btn.style.setProperty("--p", "0");
    label.textContent = "держать";
  };

  btn.addEventListener("pointerdown", begin);
  btn.addEventListener("pointerup", end);
  btn.addEventListener("pointerleave", end);
  btn.addEventListener("pointercancel", end);
  // Клавиатура: пробел и Enter удерживают так же, как палец.
  btn.addEventListener("keydown", (e) => {
    if ((e.key === " " || e.key === "Enter") && !btn.classList.contains("holding")) begin(e);
  });
  btn.addEventListener("keyup", end);
  teardown.push(() => cancelAnimationFrame(raf));

  return node;
}

function viewState() {
  const owned = OBJECTS.filter((o) => state.owned[o.slug]);

  if (!owned.length) {
    return el(`
      <main class="screen empty">
        <p class="eyebrow">Состояние</p>
        <h2 class="title">Здесь пока пусто.</h2>
        <p class="lede">Состояние появляется здесь, когда вы его принимаете, и остаётся, пока стоит приложение.</p>
        <p class="back"><a href="#/store">← в витрину</a></p>
      </main>
    `);
  }

  const node = el(`<main class="screen vault"></main>`);

  owned.forEach((obj) => {
    const rec = state.owned[obj.slug];
    const card = el(`
      <section class="held">
        <canvas class="field" aria-hidden="true"></canvas>
        <div class="held-body">
          <p class="eyebrow">${obj.index} · № ${rec.edition} из ${obj.edition}</p>
          <h2 class="held-name">${obj.name}</h2>
          <p class="whisper" aria-live="polite"></p>
          <p class="held-since">${withYou(rec.at)}</p>
        </div>
      </section>
    `);
    node.appendChild(card);

    const o = mountObject(card.querySelector(".field"), obj.palette, { intensity: 1 });
    teardown.push(o.destroy);

    // Одна фраза за раз, смена раз в двенадцать секунд, через прозрачность.
    const whisper = card.querySelector(".whisper");
    let i = Math.floor(Math.random() * obj.whispers.length);
    whisper.textContent = obj.whispers[i];
    const timer = setInterval(() => {
      whisper.classList.add("fading");
      setTimeout(() => {
        i = (i + 1) % obj.whispers.length;
        whisper.textContent = obj.whispers[i];
        whisper.classList.remove("fading");
      }, 1200);
    }, 12000);
    teardown.push(() => clearInterval(timer));
  });

  node.appendChild(
    el(`<p class="back vault-back"><a href="#/store">← в витрину</a> · <a href="#/install">поставить на телефон</a></p>`),
  );
  return node;
}

function viewCodex() {
  const node = el(`
    <main class="screen codex">
      <p class="eyebrow">Кодекс</p>
      <div class="codex-body"></div>
      <p class="back"><a href="#/store">← в витрину</a></p>
    </main>
  `);
  const body = node.querySelector(".codex-body");
  CODEX.forEach((line, i) => {
    const p = el(`<p class="codex-line">${line}</p>`);
    p.style.setProperty("--i", String(i));
    body.appendChild(p);
  });
  return node;
}

function viewInstall() {
  const node = el(`
    <main class="screen install">
      <p class="eyebrow">Установка</p>
      <h2 class="title">Состояние должно жить на телефоне, а не во вкладке.</h2>
      <div class="install-act"></div>
      <ol class="steps">
        <li><b>iPhone.</b> Safari → «Поделиться» → «На экран «Домой»».</li>
        <li><b>Android.</b> Chrome → меню → «Установить приложение».</li>
        <li><b>Компьютер.</b> Значок установки в адресной строке.</li>
      </ol>
      <p class="lede">После установки магазин работает без сети: состояние уже у вас, ему ничего не нужно.</p>
      <p class="back"><a href="#/store">← в витрину</a></p>
    </main>
  `);

  const act = node.querySelector(".install-act");
  if (installPrompt) {
    const btn = el(`<button class="cta" type="button">Установить</button>`);
    btn.addEventListener("click", async () => {
      const p = installPrompt;
      installPrompt = null;
      btn.remove();
      await p.prompt();
    });
    act.appendChild(btn);
  } else if (matchMedia("(display-mode: standalone)").matches) {
    act.appendChild(el(`<p class="owned-note">Приложение уже стоит на этом устройстве.</p>`));
  }
  return node;
}

/* -------------------------------------------------------------------- роутинг */

function render() {
  teardown.forEach((fn) => {
    try {
      fn();
    } catch (e) {
      /* пусто */
    }
  });
  teardown = [];
  app.textContent = "";

  const hash = location.hash.replace(/^#/, "") || "/";
  const [, head, arg] = hash.split("/");

  let view;
  let active = "";
  if (!state.entered && head !== "codex") {
    view = viewThreshold();
  } else if (head === "object" && arg) {
    view = viewObject(arg);
    active = "store";
  } else if (head === "take" && arg) {
    view = viewTake(arg);
    active = "store";
  } else if (head === "state") {
    view = viewState();
    active = "state";
  } else if (head === "codex") {
    view = viewCodex();
    active = "codex";
  } else if (head === "install") {
    view = viewInstall();
  } else {
    view = viewStore();
    active = "store";
  }

  if (state.entered) app.appendChild(chrome(active));
  app.appendChild(view);
  view.classList.add("entering");
  requestAnimationFrame(() => view.classList.remove("entering"));
  scrollTo(0, 0);
}

// Установленное приложение открывается на вашем состоянии, а не в витрине:
// вы уже купили, вам больше нечего смотреть.
if (
  !location.hash &&
  ownedCount() &&
  typeof matchMedia === "function" &&
  matchMedia("(display-mode: standalone)").matches
) {
  history.replaceState(null, "", "#/state");
}

addEventListener("hashchange", render);
addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  installPrompt = e;
});

render();

if ("serviceWorker" in navigator) {
  addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      /* без сети предмет всё равно уже на устройстве */
    });
  });
}
