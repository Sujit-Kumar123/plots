"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { apiListSheets, type SheetListItem } from "@/lib/services/plot-sheets"

interface Props {
  currentSheetId: string | null
}

export function SheetSwitcher({ currentSheetId }: Props) {
  const router = useRouter()
  const [sheets, setSheets] = useState<SheetListItem[]>([])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (open && sheets.length === 0) {
      apiListSheets().then(setSheets).catch(() => {})
    }
  }, [open, sheets.length])

  return (
    <div className="flex flex-col gap-1 border-b border-border pb-2">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center justify-between w-full text-[11px] text-muted-foreground hover:text-foreground transition-colors"
      >
        <span className="font-semibold uppercase tracking-wide">My Sheets</span>
        <span>{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="flex flex-col gap-0.5 mt-1 max-h-40 overflow-y-auto">
          <button
            onClick={() => router.push("/plot")}
            className="w-full text-left px-2 py-1.5 text-xs rounded-md bg-primary/10 text-primary hover:bg-primary/20 cursor-pointer transition-colors"
          >
            + New Sheet
          </button>
          {sheets.length === 0 && (
            <p className="text-[10px] text-muted-foreground px-2 py-1">No saved sheets.</p>
          )}
          {sheets.map((s) => (
            <button
              key={s.id}
              onClick={() => router.push(`/plot?sheet=${s.id}`)}
              className={[
                "w-full text-left px-2 py-1.5 text-xs rounded-md cursor-pointer transition-colors truncate",
                s.id === currentSheetId
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground hover:bg-accent hover:text-accent-foreground",
              ].join(" ")}
            >
              {s.name || "Untitled Sheet"}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
