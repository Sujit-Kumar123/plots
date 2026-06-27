"use client"

import * as React from "react"

export type ColorTheme =
  | "neutral"
  | "red"    | "orange" | "amber"   | "yellow"
  | "lime"   | "green"  | "emerald" | "teal"
  | "cyan"   | "sky"    | "blue"    | "indigo"
  | "violet" | "purple" | "fuchsia" | "pink"
  | "rose"
export type Mode = "light" | "dark" | "system"

interface ThemeContextValue {
  colorTheme: ColorTheme
  mode: Mode
  setColorTheme: (theme: ColorTheme) => void
  setMode: (mode: Mode) => void
}

const ThemeContext = React.createContext<ThemeContextValue | null>(null)

function applyTheme(colorTheme: ColorTheme, mode: Mode) {
  const root = document.documentElement
  root.setAttribute("data-theme", colorTheme)
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
  const isDark = mode === "dark" || (mode === "system" && prefersDark)
  root.classList.toggle("dark", isDark)
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [colorTheme, setColorThemeState] = React.useState<ColorTheme>("neutral")
  const [mode, setModeState] = React.useState<Mode>("system")

  // On mount: read persisted values and apply
  React.useEffect(() => {
    const savedColor = (localStorage.getItem("color-theme") as ColorTheme) ?? "neutral"
    const savedMode = (localStorage.getItem("theme-mode") as Mode) ?? "system"
    setColorThemeState(savedColor)
    setModeState(savedMode)
    applyTheme(savedColor, savedMode)
  }, [])

  // Re-apply whenever color or mode changes
  React.useEffect(() => {
    applyTheme(colorTheme, mode)
    localStorage.setItem("color-theme", colorTheme)
    localStorage.setItem("theme-mode", mode)
  }, [colorTheme, mode])

  // Keep in sync when system preference changes
  React.useEffect(() => {
    if (mode !== "system") return
    const mq = window.matchMedia("(prefers-color-scheme: dark)")
    const handler = () => applyTheme(colorTheme, "system")
    mq.addEventListener("change", handler)
    return () => mq.removeEventListener("change", handler)
  }, [mode, colorTheme])

  return (
    <ThemeContext.Provider
      value={{
        colorTheme,
        mode,
        setColorTheme: setColorThemeState,
        setMode: setModeState,
      }}
    >
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const ctx = React.useContext(ThemeContext)
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider")
  return ctx
}
