// Everything OHUET says, and the few numbers it has. Kept in one place so the
// product can be tuned without reading the rest of the code.

// The state. Three soft tints on a pale, warm ground — paper, stone, a memory
// of moss, something mineral underneath. Nothing pure, nothing bright, and
// the ground is light: the glass over it is milk, not smoke.
//
// `base` is given twice — night and day — and the field crosses between them
// with the hour. The same object is pale stone at three in the afternoon and a
// dimmer, warmer paper at three in the morning.
export const STATE = {
  base: { night: [206, 198, 186], day: [237, 232, 223] },
  blobs: [
    { rgb: [255, 248, 234], peak: 0.9 }, // light on paper
    { rgb: [170, 186, 158], peak: 0.7 }, // the moss, almost gone
    { rgb: [178, 160, 148], peak: 0.6 }, // mineral, underneath
  ],
};

// Occasional minimal language. One line surfaces after the state has been open
// for a while, then rarely. It never explains. Nothing here names the brand or
// the word: that reaction has to be the visitor's own.
export const LINES = [
  "It's here.",
  "Nothing to do.",
  "Stay.",
  "You can leave it on.",
  "Still here.",
];

// The T-shirt is the only thing OHUET sells, and it is sold outside — the
// storefront is not this app. The price is the working concept from the canon
// (100) and is not validated; leave `url` empty until the storefront exists,
// and the line stays a line rather than a link.
export const SHIRT = {
  before: "There is a",
  struck: "store", // crossed out: the one joke OHUET tells, and it is true
  after: "T-shirt.",
  price: "100",
  url: "",
};

// The wordmark, as it arrives: stacked, in thick glass, then let go.
export const WORD = ["OH", "UET"];
export const WORD_SETTLE_MS = 1600; // liquid → glass
export const WORD_STAY_MS = 5600; // then it dissolves on its own

// Presence is the material. How long the state must be open before the first
// line surfaces, and how long between lines after that.
export const FIRST_LINE_AFTER_MS = 3 * 60 * 1000;
export const LINE_EVERY_MS = 9 * 60 * 1000;
