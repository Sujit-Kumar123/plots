"use client";

import type { Tool } from "./_types";
import { TIP_MAP } from "./_constants";

interface TipBarProps {
  curTool: Tool;
}

export function TipBar({ curTool }: TipBarProps) {
  return (
    <div className="absolute bottom-3 left-1/2 -translate-x-1/2 bg-foreground/65 text-background text-xs px-4 py-1.5 rounded-full pointer-events-none whitespace-nowrap">
      {TIP_MAP[curTool]}
    </div>
  );
}
