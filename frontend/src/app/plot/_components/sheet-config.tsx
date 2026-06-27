"use client";

import { SHEET_PRESETS } from "./_constants";

interface SheetConfigProps {
  sheetW: number;
  sheetD: number;
  draftW: string;
  draftD: string;
  setDraftW: (v: string) => void;
  setDraftD: (v: string) => void;
  onClose: () => void;
  buildGrid: (w: number, d: number) => void;
  doApplySheet: () => void;
}

export function SheetConfig({
  sheetW, sheetD, draftW, draftD,
  setDraftW, setDraftD,
  onClose, buildGrid, doApplySheet,
}: SheetConfigProps) {
  return (
    <>
      {/* backdrop */}
      <div
        className="absolute inset-0 z-20"
        onClick={onClose}
      />
      {/* dialog */}
      <div className="absolute top-3 left-52 z-30 bg-card rounded-xl shadow-xl p-4 w-56 flex flex-col gap-3 border border-border">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-card-foreground">📐 Sheet Size</span>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground text-sm leading-none cursor-pointer"
          >✕</button>
        </div>

        {/* Presets */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Presets</span>
          <div className="grid grid-cols-3 gap-1">
            {SHEET_PRESETS.map((p) => (
              <button
                key={p.label}
                onClick={() => { buildGrid(p.w, p.d); onClose(); }}
                className={[
                  "py-1.5 text-[11px] rounded border-2 cursor-pointer transition-colors",
                  sheetW === p.w && sheetD === p.d
                    ? "bg-primary text-primary-foreground border-primary"
                    : "bg-secondary text-secondary-foreground border-border hover:bg-accent hover:text-accent-foreground",
                ].join(" ")}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Custom inputs */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] text-muted-foreground uppercase tracking-wide">Custom</span>
          <div className="flex gap-2 items-center">
            <div className="flex flex-col gap-0.5 flex-1">
              <label className="text-[10px] text-muted-foreground">Width (W)</label>
              <input
                type="number" min={2} max={200} value={draftW}
                onChange={(e) => setDraftW(e.target.value)}
                className="w-full border border-border rounded px-2 py-1 text-xs text-foreground bg-background focus:outline-none focus:ring-1 focus:ring-ring"
              />
            </div>
            <span className="text-muted-foreground text-xs mt-4">×</span>
            <div className="flex flex-col gap-0.5 flex-1">
              <label className="text-[10px] text-muted-foreground">Depth (D)</label>
              <input
                type="number" min={2} max={200} value={draftD}
                onChange={(e) => setDraftD(e.target.value)}
                className="w-full border border-border rounded px-2 py-1 text-xs text-foreground bg-background focus:outline-none focus:ring-1 focus:ring-ring"
              />
            </div>
          </div>
          <button
            onClick={doApplySheet}
            className="w-full py-1.5 text-xs rounded-md bg-primary text-primary-foreground hover:bg-primary/90 cursor-pointer transition-colors"
          >
            Apply
          </button>
        </div>

        <p className="text-[10px] text-muted-foreground leading-relaxed">
          Blue border = sheet boundary.<br />
          Range: 2–200 units per side.
        </p>
      </div>
    </>
  );
}
