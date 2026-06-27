import type { Tool } from "./_types";

export const SHEET_PRESETS = [
  { label: "10×10",  w: 10, d: 10 },
  { label: "20×20",  w: 20, d: 20 },
  { label: "30×20",  w: 30, d: 20 },
  { label: "40×30",  w: 40, d: 30 },
  { label: "60×40",  w: 60, d: 40 },
] as const;

function mkCur(svg: string, hx: number, hy: number) {
  return `url("data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}") ${hx} ${hy}, auto`;
}

export const CURSORS: Record<string, string> = {
  none: "default",

  block: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><polygon points="16,3 28,10 28,22 16,29 4,22 4,10" fill="#dbeafe" stroke="#1d4ed8" stroke-width="1.5"/><polyline points="4,10 16,17 28,10" fill="none" stroke="#1d4ed8" stroke-width="1"/><line x1="16" y1="17" x2="16" y2="29" stroke="#1d4ed8" stroke-width="1"/><circle cx="16" cy="16" r="2" fill="#1d4ed8"/></svg>`,
    16, 16,
  ),

  pencil: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><g transform="rotate(45,16,16)"><rect x="12" y="4" width="8" height="18" rx="1" fill="#fde68a" stroke="#92400e" stroke-width="1.2"/><rect x="12" y="4" width="8" height="3" fill="#d1d5db" stroke="#9ca3af" stroke-width="1"/><polygon points="12,22 20,22 16,29" fill="#fef3c7" stroke="#92400e" stroke-width="1"/><circle cx="16" cy="29" r="1.2" fill="#1f2937"/></g></svg>`,
    7, 25,
  ),

  erase: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect x="3" y="11" width="26" height="14" rx="2" fill="#fca5a5" stroke="#dc2626" stroke-width="1.5"/><rect x="3" y="11" width="11" height="14" rx="2" fill="#f87171" stroke="#dc2626" stroke-width="1"/><line x1="1" y1="27" x2="31" y2="27" stroke="#dc2626" stroke-width="2"/></svg>`,
    16, 22,
  ),

  select: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><polygon points="5,2 5,20 9,16 13,26 16,25 12,15 18,15" fill="white" stroke="#1f2937" stroke-width="1.2" stroke-linejoin="round"/><rect x="17" y="17" width="13" height="13" fill="none" stroke="#2563eb" stroke-width="1.5" stroke-dasharray="3,2"/></svg>`,
    5, 2,
  ),

  line: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><line x1="3" y1="29" x2="29" y2="3" stroke="#1f2937" stroke-width="2" stroke-linecap="round"/><circle cx="3" cy="29" r="3" fill="#10b981"/><circle cx="29" cy="3" r="2.5" fill="#374151"/></svg>`,
    3, 29,
  ),

  circle: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><circle cx="16" cy="16" r="13" fill="none" stroke="#374151" stroke-width="2"/><line x1="13" y1="16" x2="19" y2="16" stroke="#374151" stroke-width="2"/><line x1="16" y1="13" x2="16" y2="19" stroke="#374151" stroke-width="2"/></svg>`,
    16, 16,
  ),

  ellipse: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><ellipse cx="16" cy="16" rx="14" ry="9" fill="none" stroke="#374151" stroke-width="2"/><line x1="13" y1="16" x2="19" y2="16" stroke="#374151" stroke-width="2"/><line x1="16" y1="13" x2="16" y2="19" stroke="#374151" stroke-width="2"/></svg>`,
    16, 16,
  ),

  vline: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><line x1="16" y1="3" x2="16" y2="29" stroke="#374151" stroke-width="2"/><polygon points="12,8 16,1 20,8" fill="#374151"/><polygon points="12,24 16,31 20,24" fill="#374151"/><line x1="8" y1="16" x2="24" y2="16" stroke="#9ca3af" stroke-width="1" stroke-dasharray="3,2"/></svg>`,
    16, 16,
  ),

  vcircle: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><ellipse cx="16" cy="16" rx="7" ry="14" fill="none" stroke="#374151" stroke-width="2"/><line x1="4" y1="16" x2="28" y2="16" stroke="#9ca3af" stroke-width="1" stroke-dasharray="3,2"/><line x1="13" y1="16" x2="19" y2="16" stroke="#374151" stroke-width="2"/><line x1="16" y1="13" x2="16" y2="19" stroke="#374151" stroke-width="2"/></svg>`,
    16, 16,
  ),

  vellipse: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><ellipse cx="16" cy="16" rx="11" ry="14" fill="none" stroke="#374151" stroke-width="2"/><line x1="2" y1="16" x2="30" y2="16" stroke="#9ca3af" stroke-width="1" stroke-dasharray="3,2"/><line x1="13" y1="16" x2="19" y2="16" stroke="#374151" stroke-width="2"/><line x1="16" y1="13" x2="16" y2="19" stroke="#374151" stroke-width="2"/></svg>`,
    16, 16,
  ),

  wall: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect x="14" y="4" width="4" height="20" rx="1" fill="#c7d2fe" stroke="#4338ca" stroke-width="1.5"/><circle cx="16" cy="4" r="2.5" fill="#4338ca"/><circle cx="16" cy="28" r="3" fill="#10b981"/><line x1="5" y1="28" x2="27" y2="28" stroke="#4338ca" stroke-width="1.5" stroke-linecap="round"/></svg>`,
    16, 28,
  ),

  div: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect x="3" y="8" width="26" height="18" rx="2" fill="none" stroke="#374151" stroke-width="2"/><rect x="6" y="11" width="10" height="2.5" rx="1" fill="#374151"/><rect x="6" y="15.5" width="14" height="2.5" rx="1" fill="#374151"/><rect x="6" y="20" width="8" height="2.5" rx="1" fill="#374151"/><circle cx="26" cy="26" r="4" fill="#10b981"/><line x1="24" y1="26" x2="28" y2="26" stroke="white" stroke-width="1.5"/><line x1="26" y1="24" x2="26" y2="28" stroke="white" stroke-width="1.5"/></svg>`,
    3, 8,
  ),

  text: mkCur(
    `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"><rect x="5" y="5" width="22" height="3" rx="1" fill="#1f2937"/><rect x="14" y="5" width="4" height="18" rx="1" fill="#1f2937"/><line x1="10" y1="27" x2="22" y2="27" stroke="#10b981" stroke-width="2" stroke-linecap="round"/><circle cx="10" cy="27" r="2" fill="#10b981"/></svg>`,
    10, 27,
  ),
};

export const TIP_MAP: Record<Tool, string> = {
  block:    "Click top face → stack  |  Click bottom face → place below  |  Drag → orbit",
  pencil:   "Left-drag → draw  |  Right-drag → orbit  |  Scroll → zoom",
  erase:    "Click / drag → erase block or line  |  Right-click also erases",
  select:   "Click → select  |  Shift+Click → multi-select  |  Click empty → deselect",
  none:     "No tool — Drag → orbit  |  Scroll → zoom",
  line:     "1st click → start  |  2nd click → end  |  Esc → cancel",
  circle:   "1st click → center  |  2nd click → radius  |  Esc → cancel",
  ellipse:  "1st click → center  |  2nd click → corner  |  Esc → cancel",
  vline:    "Orbit to face wall → 1st click start  |  2nd click end  |  Esc → cancel",
  vcircle:  "Orbit to face wall → 1st click center  |  2nd click radius  |  Esc → cancel",
  vellipse: "Orbit to face wall → 1st click center  |  2nd click corner  |  Esc → cancel",
  wall:     "1st click → wall start  |  2nd click → wall end (uses Height)  |  Esc → cancel",
  div:      "1st click → center  |  2nd click → corner  |  type text  |  Esc → cancel",
  text:     "Click anywhere → type label → Enter to place  |  Esc → cancel",
};
