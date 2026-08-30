// Сам предмет.
//
// Три пятна света ходят друг сквозь друга на почти чёрном поле, всё это
// дышит с периодом примерно в шесть секунд — медленнее, чем дыхание человека,
// поэтому рядом с ним замедляешься сам. Поверх — зерно, иначе градиент читается
// как заставка, а не как вещь.
//
// Рисуется в маленький буфер (LOW×LOW) и растягивается на весь холст: мягкость
// здесь берётся не из blur-фильтра, а из самого масштабирования, и стоит это
// почти ничего даже на слабом телефоне.

const LOW = 160; // сторона буфера, в пикселях
const FPS = 30; // больше не нужно: всё движется очень медленно
const GRAIN = 128; // сторона тайла зерна

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
 * Время суток сдвигает состояние: к ночи оно темнеет и уходит в синеву,
 * днём — светлеет. Один и тот же объект в три часа дня и в три часа ночи
 * выглядит по-разному, и это единственное, чем он «знает» о вашей жизни.
 *
 * @param {number} hour 0–24
 * @returns {{gain: number, tint: number[]}}
 */
export function daylight(hour) {
  // 0 — глухая ночь, 1 — полдень
  const day = Math.max(0, Math.cos(((hour - 13) / 24) * Math.PI * 2)) ** 0.7;
  return {
    gain: 0.62 + day * 0.38,
    tint: day > 0.5 ? [255, 250, 242] : [186, 198, 224],
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
 * Вешает живой предмет на <canvas>. Возвращает ручку: предмет надо гасить,
 * когда экран уходит, иначе он продолжает крутиться в фоне и жрёт батарею.
 *
 * @param {HTMLCanvasElement} canvas
 * @param {{base: number[], blobs: number[][]}} palette
 * @param {{still?: boolean, intensity?: number}} [opts]
 */
export function mountObject(canvas, palette, opts = {}) {
  const still = opts.still || reduceMotion;
  const intensity = opts.intensity ?? 1;

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
  const pointer = { x: 0, y: 0, tx: 0, ty: 0 };

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
    const light = daylight(new Date().getHours());
    const breath = still ? 1 : 1 + Math.sin(t * (Math.PI * 2) / 6) * 0.035;

    // Поле
    bctx.globalCompositeOperation = "source-over";
    bctx.fillStyle = rgba(palette.base, 1);
    bctx.fillRect(0, 0, LOW, LOW);
    bctx.globalCompositeOperation = "lighter";

    palette.blobs.forEach((rgb, i) => {
      const s = i + 1;
      // Три несоизмеримых периода — рисунок никогда не повторяется буквально.
      const x = 0.5 + Math.sin(t / (17 + s * 6) + s) * 0.26 + pointer.x * 0.05 * s;
      const y = 0.5 + Math.cos(t / (23 + s * 5) + s * 2) * 0.24 + pointer.y * 0.05 * s;
      const r = (0.34 + Math.sin(t / (13 + s * 3)) * 0.07) * breath * LOW;
      const colour = mix(rgb, light.tint, 0.18);
      const peak = 0.5 * light.gain * intensity * (1 - i * 0.18);

      const g = bctx.createRadialGradient(x * LOW, y * LOW, 0, x * LOW, y * LOW, r);
      g.addColorStop(0, rgba(colour, peak));
      g.addColorStop(0.45, rgba(colour, peak * 0.35));
      g.addColorStop(1, rgba(colour, 0));
      bctx.fillStyle = g;
      bctx.fillRect(0, 0, LOW, LOW);
    });

    // Растягиваем буфер: вся мягкость отсюда.
    ctx.globalCompositeOperation = "source-over";
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.clearRect(0, 0, w, h);
    ctx.drawImage(buf, 0, 0, w, h);

    // Виньетка: край всегда темнее центра, иначе предмет выглядит как экран.
    const v = ctx.createRadialGradient(
      w / 2, h / 2, Math.min(w, h) * 0.18,
      w / 2, h / 2, Math.max(w, h) * 0.72,
    );
    v.addColorStop(0, "rgba(0,0,0,0)");
    v.addColorStop(1, "rgba(0,0,0,0.72)");
    ctx.fillStyle = v;
    ctx.fillRect(0, 0, w, h);

    // Зерно
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
    pointer.x += (pointer.tx - pointer.x) * 0.04;
    pointer.y += (pointer.ty - pointer.y) * 0.04;
    paint(now);
  }

  function onPointer(e) {
    const r = canvas.getBoundingClientRect();
    pointer.tx = ((e.clientX - r.left) / r.width - 0.5) * 2;
    pointer.ty = ((e.clientY - r.top) / r.height - 0.5) * 2;
  }

  function onVisibility() {
    if (document.hidden) {
      cancelAnimationFrame(raf);
      raf = 0;
    } else if (alive && !still && !raf) {
      // Предмет не отматывает пропущенное время назад — он просто продолжает.
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
  if (!still) {
    canvas.addEventListener("pointermove", onPointer, { passive: true });
    raf = requestAnimationFrame(frame);
  }
  paint(performance.now());

  return {
    destroy() {
      alive = false;
      cancelAnimationFrame(raf);
      if (ro) ro.disconnect();
      else removeEventListener("resize", resize);
      removeEventListener("visibilitychange", onVisibility);
      canvas.removeEventListener("pointermove", onPointer);
    },
  };
}
