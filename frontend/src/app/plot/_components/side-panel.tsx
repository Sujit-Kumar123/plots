"use client";

import React from "react";
import type { Tool } from "./_types";
import { SheetSwitcher } from "./sheet-switcher";

type BtnProps = React.ButtonHTMLAttributes<HTMLButtonElement> & { active?: boolean };
const Btn = ({ active, className = "", ...props }: BtnProps) => (
  <button
    {...props}
    className={[
      "w-full px-3 py-2 text-xs text-left rounded-md border-2 cursor-pointer transition-colors",
      active
        ? "bg-primary text-primary-foreground border-primary"
        : "bg-secondary text-secondary-foreground border-border hover:bg-accent hover:text-accent-foreground",
      className,
    ].join(" ")}
  />
);

interface SidePanelProps {
  curTool: Tool;
  curColor: string;
  curH: number;
  curW: number;
  curD: number;
  selCount: number;
  rotLocked: boolean;
  canUndo: boolean;
  canRedo: boolean;
  sheetW: number;
  sheetD: number;
  showSheetCfg: boolean;
  doTool: (t: Tool) => void;
  doColor: (c: string) => void;
  doHeight: (h: number) => void;
  doWidth: (w: number) => void;
  doDepth: (d: number) => void;
  doUndo: () => void;
  doRedo: () => void;
  doFill: () => void;
  doClear: () => void;
  doToggleRotation: () => void;
  doPrint: () => void;
  onToggleSheetCfg: () => void;
  viewMode: "2d" | "3d";
  doViewMode: (mode: "2d" | "3d") => void;
  sheetId: string | null;
  sheetName: string;
  isSaving: boolean;
  doSave: () => void;
  doSetSheetName: (name: string) => void;
  gridStep: number;
  doGridStep: (dir: 1 | -1) => void;
  curBorderW: number;
  curBorderR: number;
  doBorderW: (v: number) => void;
  doBorderR: (v: number) => void;
}

export function SidePanel({
  curTool, curColor, curH, curW, curD, selCount, rotLocked, canUndo, canRedo,
  sheetW, sheetD, showSheetCfg, viewMode, gridStep, curBorderW, curBorderR,
  sheetId, sheetName, isSaving,
  doTool, doColor, doHeight, doWidth, doDepth, doUndo, doRedo, doFill, doClear,
  doToggleRotation, doPrint, onToggleSheetCfg, doViewMode, doGridStep, doBorderW, doBorderR,
  doSave, doSetSheetName,
}: SidePanelProps) {
  return (
    <div className="absolute top-3 left-3 z-10 bg-card rounded-xl shadow-lg p-3.5 w-48 flex flex-col gap-2 overflow-y-auto max-h-[calc(100vh-24px)] border border-border">
      <h3 className="text-xs font-semibold text-card-foreground">🏗️ 3D Plot</h3>

      <SheetSwitcher currentSheetId={sheetId} />

      {/* Sheet name + save */}
      <div className="flex flex-col gap-1 border-b border-border pb-2">
        <input
          value={sheetName}
          onChange={(e) => doSetSheetName(e.target.value)}
          placeholder="Sheet name…"
          className="w-full px-2 py-1 text-xs bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
        />
        <button
          onClick={doSave}
          disabled={isSaving}
          className="w-full py-1.5 text-xs rounded-md border-2 bg-primary/10 text-primary border-primary/30 hover:bg-primary/20 cursor-pointer transition-colors disabled:opacity-50"
        >
          {isSaving ? "Saving…" : sheetId ? "💾 Save" : "💾 Save Sheet"}
        </button>
      </div>

      {/* 2D / 3D view toggle */}
      <div className="flex gap-1.5">
        <button
          onClick={() => doViewMode("3d")}
          className={[
            "flex-1 py-1.5 text-xs rounded-md border-2 cursor-pointer transition-colors font-semibold",
            viewMode === "3d"
              ? "bg-primary text-primary-foreground border-primary"
              : "bg-secondary text-secondary-foreground border-border hover:bg-accent hover:text-accent-foreground",
          ].join(" ")}
        >
          3D
        </button>
        <button
          onClick={() => doViewMode("2d")}
          className={[
            "flex-1 py-1.5 text-xs rounded-md border-2 cursor-pointer transition-colors font-semibold",
            viewMode === "2d"
              ? "bg-primary text-primary-foreground border-primary"
              : "bg-secondary text-secondary-foreground border-border hover:bg-accent hover:text-accent-foreground",
          ].join(" ")}
        >
          2D
        </button>
      </div>

      <Btn active={curTool === "block"}  onClick={() => doTool("block")}>🧱 Place Block</Btn>
      <Btn active={curTool === "pencil"} onClick={() => doTool("pencil")}>✏️ Draw Line</Btn>
      <Btn active={curTool === "erase"}  onClick={() => doTool("erase")}>🗑 Erase</Btn>
      <Btn active={curTool === "select"} onClick={() => doTool("select")}>↗ Select</Btn>
      <Btn active={curTool === "none"}   onClick={() => doTool("none")}>✋ Deselect All</Btn>

      <Btn active={curTool === "wall"} onClick={() => doTool("wall")}>🧱 Wall</Btn>
      <Btn active={curTool === "div"}  onClick={() => doTool("div")}>📋 Div Panel</Btn>

      {curTool === "div" && (
        <div className="flex flex-col gap-1.5 bg-muted/50 border border-border rounded-md p-2">
          <div className="flex flex-col gap-1">
            <span className="text-[11px] text-muted-foreground">Border Width: <b>{curBorderW}</b></span>
            <input
              type="range" min={1} max={20} value={curBorderW}
              onChange={(e) => doBorderW(+e.target.value)}
              className="w-full cursor-pointer accent-primary"
            />
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-[11px] text-muted-foreground">Border Radius: <b>{curBorderR}%</b></span>
            <input
              type="range" min={0} max={50} value={curBorderR}
              onChange={(e) => doBorderR(+e.target.value)}
              className="w-full cursor-pointer accent-primary"
            />
          </div>
        </div>
      )}

      <Btn active={curTool === "text"} onClick={() => doTool("text")}>🔤 Text Label</Btn>

      <div className="border-t border-border text-[10px] text-muted-foreground text-center pt-1">── SHAPES ──</div>

      <Btn active={curTool === "line"}     onClick={() => doTool("line")}>📏 H. Line</Btn>
      <Btn active={curTool === "circle"}   onClick={() => doTool("circle")}>⭕ H. Circle</Btn>
      <Btn active={curTool === "ellipse"}  onClick={() => doTool("ellipse")}>🔵 H. Ellipse</Btn>
      <Btn active={curTool === "vline"}    onClick={() => doTool("vline")}>↕ V. Line</Btn>
      <Btn active={curTool === "vcircle"}  onClick={() => doTool("vcircle")}>⭕ V. Circle</Btn>
      <Btn active={curTool === "vellipse"} onClick={() => doTool("vellipse")}>🔵 V. Ellipse</Btn>

      {/* Color */}
      <div className="flex flex-col gap-1">
        <span className="text-[11px] text-muted-foreground">Color</span>
        <input
          type="color" value={curColor}
          onChange={(e) => doColor(e.target.value)}
          className="w-full h-8 rounded border border-border cursor-pointer bg-background"
        />
      </div>

      {/* Fill selected */}
      <button
        onClick={doFill}
        className="w-full py-1.5 text-xs rounded-md border-2 bg-primary/10 text-primary border-primary/30 hover:bg-primary/20 cursor-pointer transition-colors"
      >
        🎨 Fill Selected ({selCount})
      </button>

      <div className="border-t border-border text-[10px] text-muted-foreground text-center pt-1">── BLOCK SIZE ──</div>

      {/* Height / Width / Depth */}
      <div className="flex flex-col gap-1">
        <span className="text-[11px] text-muted-foreground">Height: <b>{curH}</b></span>
        <input
          type="range" min={1} max={8} value={curH}
          onChange={(e) => doHeight(+e.target.value)}
          className="w-full cursor-pointer accent-primary"
        />
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-[11px] text-muted-foreground">Width: <b>{curW}</b></span>
        <input
          type="range" min={1} max={8} value={curW}
          onChange={(e) => doWidth(+e.target.value)}
          className="w-full cursor-pointer accent-primary"
        />
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-[11px] text-muted-foreground">Depth: <b>{curD}</b></span>
        <input
          type="range" min={1} max={8} value={curD}
          onChange={(e) => doDepth(+e.target.value)}
          className="w-full cursor-pointer accent-primary"
        />
      </div>

      <div className="border-t border-border text-[10px] text-muted-foreground text-center pt-1">── GRID ──</div>

      {/* Grid step */}
      <div className="flex items-center justify-between gap-1">
        <span className="text-[11px] text-muted-foreground">Grid: <b>{gridStep}</b> unit</span>
        <div className="flex gap-1">
          <button
            onClick={() => doGridStep(-1)}
            className="w-6 h-6 text-xs rounded border border-border bg-secondary text-secondary-foreground hover:bg-accent cursor-pointer"
          >−</button>
          <button
            onClick={() => doGridStep(1)}
            className="w-6 h-6 text-xs rounded border border-border bg-secondary text-secondary-foreground hover:bg-accent cursor-pointer"
          >+</button>
        </div>
      </div>

      <div className="border-t border-border text-[10px] text-muted-foreground text-center pt-1">── SHEET ──</div>

      {/* Sheet size button */}
      <button
        onClick={onToggleSheetCfg}
        className={[
          "w-full py-1.5 text-xs rounded-md border-2 cursor-pointer transition-colors",
          showSheetCfg
            ? "bg-primary text-primary-foreground border-primary"
            : "bg-secondary text-secondary-foreground border-border hover:bg-accent hover:text-accent-foreground",
        ].join(" ")}
      >
        📐 Sheet Size
      </button>

      {/* Current size badge */}
      <div className="flex items-center justify-center gap-1.5 bg-muted border border-border rounded-md py-1.5">
        <span className="text-[10px] text-muted-foreground">W</span>
        <span className="text-xs font-bold text-primary">{sheetW}</span>
        <span className="text-[10px] text-muted-foreground">×</span>
        <span className="text-[10px] text-muted-foreground">D</span>
        <span className="text-xs font-bold text-primary">{sheetD}</span>
        <span className="text-[10px] text-muted-foreground">units</span>
      </div>

      {/* Rotation toggle */}
      <button
        onClick={doToggleRotation}
        className={[
          "w-full py-1.5 text-xs rounded-md border-2 font-semibold cursor-pointer transition-colors",
          rotLocked
            ? "bg-destructive/10 text-destructive border-destructive/30 hover:bg-destructive/20"
            : "bg-primary/10 text-primary border-primary/30 hover:bg-primary/20",
        ].join(" ")}
      >
        {rotLocked ? "🔒 Rotation OFF" : "🔓 Rotation ON"}
      </button>

      {/* Undo / Redo */}
      <div className="flex gap-1.5">
        <button
          onClick={doUndo} disabled={!canUndo}
          className="flex-1 py-1.5 text-xs rounded-md border-2 border-border bg-secondary text-secondary-foreground cursor-pointer disabled:opacity-40 hover:enabled:bg-accent hover:enabled:text-accent-foreground"
        >
          ◀ Back
        </button>
        <button
          onClick={doRedo} disabled={!canRedo}
          className="flex-1 py-1.5 text-xs rounded-md border-2 border-border bg-secondary text-secondary-foreground cursor-pointer disabled:opacity-40 hover:enabled:bg-accent hover:enabled:text-accent-foreground"
        >
          Fwd ▶
        </button>
      </div>

      {/* Clear */}
      <button
        onClick={doClear}
        className="w-full py-1.5 text-xs rounded-md border-2 bg-destructive/10 text-destructive border-destructive/30 hover:bg-destructive/20 cursor-pointer transition-colors"
      >
        🗑️ Clear All
      </button>

      {/* Print */}
      <button
        onClick={doPrint}
        className="w-full py-1.5 text-xs rounded-md border-2 bg-primary/10 text-primary border-primary/30 hover:bg-primary/20 cursor-pointer transition-colors"
      >
        🖨️ Print to Console
      </button>
    </div>
  );
}
