export type Tool =
  | "block" | "pencil" | "erase" | "select" | "none"
  | "line" | "circle" | "ellipse"
  | "vline" | "vcircle" | "vellipse"
  | "wall" | "div" | "text";

export interface BlockInfo {
  gx: number; gz: number;
  bottomY: number; height: number; topY: number;
  width: number; depth: number;
}

export interface UndoCmd { undo: () => void; redo: () => void; }

export interface ShapeAnchor { wx: number; wy: number; wz: number; gx: number; gz: number; }

export interface WallInfo {
  x1: number; z1: number;
  x2: number; z2: number;
  bottomY: number; height: number;
}

export interface DivPanelInfo {
  cx: number; cz: number;
  rx: number; rz: number;
  text: string; color: string;
  borderWidth: number;
  borderRadius: number;
}

export interface TextInfo {
  wx: number; wy: number; wz: number;
  text: string;
  color: string;
}
