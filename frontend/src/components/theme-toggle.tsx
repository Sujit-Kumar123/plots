"use client"

import { Sun, Moon, Monitor, Palette } from "lucide-react"
import { useTheme, type ColorTheme, type Mode } from "@/components/theme-provider"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const MODES: { value: Mode; icon: React.ElementType; label: string }[] = [
  { value: "light",  icon: Sun,     label: "Light"  },
  { value: "system", icon: Monitor, label: "System" },
  { value: "dark",   icon: Moon,    label: "Dark"   },
]

const COLOR_THEMES: { value: ColorTheme; label: string; color: string }[] = [
  { value: "neutral", label: "Neutral", color: "oklch(0.556 0 0)"           },
  { value: "red",     label: "Red",     color: "oklch(0.577 0.245 27.325)"  },
  { value: "orange",  label: "Orange",  color: "oklch(0.638 0.205 43.769)"  },
  { value: "amber",   label: "Amber",   color: "oklch(0.666 0.179 58.318)"  },
  { value: "yellow",  label: "Yellow",  color: "oklch(0.681 0.162 75.834)"  },
  { value: "lime",    label: "Lime",    color: "oklch(0.648 0.200 131.684)" },
  { value: "green",   label: "Green",   color: "oklch(0.527 0.175 142.495)" },
  { value: "emerald", label: "Emerald", color: "oklch(0.596 0.145 163.225)" },
  { value: "teal",    label: "Teal",    color: "oklch(0.600 0.118 184.704)" },
  { value: "cyan",    label: "Cyan",    color: "oklch(0.609 0.126 221.723)" },
  { value: "sky",     label: "Sky",     color: "oklch(0.588 0.158 241.966)" },
  { value: "blue",    label: "Blue",    color: "oklch(0.546 0.245 262.881)" },
  { value: "indigo",  label: "Indigo",  color: "oklch(0.511 0.262 276.966)" },
  { value: "violet",  label: "Violet",  color: "oklch(0.541 0.281 293.009)" },
  { value: "purple",  label: "Purple",  color: "oklch(0.558 0.238 292.717)" },
  { value: "fuchsia", label: "Fuchsia", color: "oklch(0.591 0.293 322.896)" },
  { value: "pink",    label: "Pink",    color: "oklch(0.592 0.249 0.827)"   },
  { value: "rose",    label: "Rose",    color: "oklch(0.596 0.232 13.557)"  },
]

export function ThemeToggle() {
  const { colorTheme, mode, setColorTheme, setMode } = useTheme()

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" className="w-full justify-start gap-3">
          <Palette className="h-4 w-4 shrink-0" />
          <span>Appearance</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent side="right" align="end" className="w-64 p-3 space-y-3">
        {/* Mode selector */}
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-2">Mode</p>
          <div className="flex gap-1">
            {MODES.map(({ value, icon: Icon, label }) => (
              <Button
                key={value}
                variant={mode === value ? "secondary" : "ghost"}
                size="sm"
                className="flex-1 flex-col h-auto gap-1 py-2 px-1"
                onClick={() => setMode(value)}
              >
                <Icon className="h-4 w-4" />
                <span className="text-[10px]">{label}</span>
              </Button>
            ))}
          </div>
        </div>

        {/* Color palette — 3-column grid */}
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-2">Color</p>
          <div className="grid grid-cols-3 gap-1">
            {COLOR_THEMES.map(({ value, label, color }) => (
              <button
                key={value}
                onClick={() => setColorTheme(value)}
                title={label}
                className={cn(
                  "flex items-center gap-2 rounded-md px-2 py-1.5 text-xs transition-colors hover:bg-muted text-left",
                  colorTheme === value && "bg-muted font-semibold ring-1 ring-border"
                )}
              >
                <span
                  className="size-3.5 shrink-0 rounded-full ring-1 ring-black/10"
                  style={{ background: color }}
                />
                <span className="truncate">{label}</span>
              </button>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}
