"use client";

import { useState, useEffect, useRef } from "react";

interface TextInputOverlayProps {
  pos: { x: number; y: number };
  color: string;
  onCommit: (text: string) => void;
  onCancel: () => void;
}

export function TextInputOverlay({ pos, color, onCommit, onCancel }: TextInputOverlayProps) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const commit = () => value.trim() ? onCommit(value.trim()) : onCancel();

  return (
    <div
      className="absolute z-50 flex items-center gap-1.5 bg-card border border-border rounded-xl shadow-2xl p-2"
      style={{ left: pos.x, top: pos.y, transform: "translate(-50%, calc(-100% - 10px))" }}
    >
      {/* color swatch */}
      <span
        className="w-3 h-3 rounded-full flex-shrink-0 ring-1 ring-border"
        style={{ background: color }}
      />
      <input
        ref={inputRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter")  { e.preventDefault(); commit(); }
          if (e.key === "Escape") { e.preventDefault(); onCancel(); }
        }}
        placeholder="Type label…"
        className="w-36 px-2 py-1 text-xs bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
      />
      <button
        onClick={commit}
        className="px-2 py-1 text-xs rounded-md bg-primary text-primary-foreground hover:bg-primary/90 cursor-pointer"
      >
        ✓
      </button>
      <button
        onClick={onCancel}
        className="px-2 py-1 text-xs rounded-md bg-secondary text-secondary-foreground hover:bg-accent cursor-pointer"
      >
        ✕
      </button>
      {/* pointer arrow */}
      <div
        className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0"
        style={{
          borderLeft: "6px solid transparent",
          borderRight: "6px solid transparent",
          borderTop: "6px solid hsl(var(--border))",
        }}
      />
    </div>
  );
}
