"use client";

import { useEffect, useRef, useState } from "react";

interface DivEditOverlayProps {
  rect: { x: number; y: number; w: number; h: number };
  color: string;
  onCommit: (text: string) => void;
  onCancel: () => void;
}

export function DivEditOverlay({ rect, color, onCommit, onCancel }: DivEditOverlayProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const cancelledRef = useRef(false);

  useEffect(() => { textareaRef.current?.focus(); }, []);

  const commit = () => {
    if (cancelledRef.current) return;
    onCommit(value.trim());
  };

  const cancel = () => {
    cancelledRef.current = true;
    onCancel();
  };

  return (
    <div
      className="absolute z-50"
      style={{ left: rect.x, top: rect.y, width: rect.w, height: rect.h }}
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); commit(); }
          if (e.key === "Escape") { e.preventDefault(); cancel(); }
        }}
        onBlur={commit}
        placeholder="Type here… (Enter to confirm, Esc to cancel)"
        className="w-full h-full resize-none text-sm p-2 focus:outline-none rounded"
        style={{
          color,
          border: `2px solid ${color}`,
          backgroundColor: `${color}22`,
          caretColor: color,
        }}
      />
    </div>
  );
}
