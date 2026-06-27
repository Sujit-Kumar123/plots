// Read an accent/foreground CSS variable and return as a Three.js hex integer.
// We use background-color (not color) to force the browser to fully resolve the
// value into a computed rgb() form even for oklch/color-mix expressions.
export function cssColorToInt(expr: string): number {
  if (typeof document === "undefined") return 0x888888;
  const el = document.createElement("div");
  el.style.cssText = `background-color:${expr};position:absolute;visibility:hidden;width:1px;height:1px`;
  document.body.appendChild(el);
  const raw = getComputedStyle(el).backgroundColor;
  document.body.removeChild(el);
  // getComputedStyle always returns rgb() / rgba() for background-color
  const m = raw.match(/\d+(?:\.\d+)?/g);
  if (!m || m.length < 3) return 0x888888;
  return (Math.round(+m[0]) << 16) | (Math.round(+m[1]) << 8) | Math.round(+m[2]);
}

export function cssColorToStr(expr: string): string {
  return "#" + cssColorToInt(expr).toString(16).padStart(6, "0");
}

// Scene background — always neutral white/dark regardless of accent theme color.
// Reading --background via a CSS property can misparse oklch in some browsers;
// checking the dark-mode class directly is simpler and 100% reliable.
export function getSceneBg(): number {
  if (typeof document === "undefined") return 0xfafafa;
  return document.documentElement.classList.contains("dark") ? 0x2d2d2d : 0xffffff;
}
