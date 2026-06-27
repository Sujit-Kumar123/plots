"use client"

import { useState } from "react"
import {
  Bell,
  Globe,
  Lock,
  Monitor,
  Moon,
  Palette,
  Shield,
  Sun,
  Trash2,
} from "lucide-react"
import { useTheme, type ColorTheme, type Mode } from "@/components/theme-provider"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"

/* ── Types ─────────────────────────────────────────────────────────────────── */

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

/* ── Toggle pill ────────────────────────────────────────────────────────────── */

function Toggle({
  checked,
  onChange,
}: {
  checked: boolean
  onChange: (v: boolean) => void
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={cn(
        "relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        checked ? "bg-primary" : "bg-input"
      )}
    >
      <span
        className={cn(
          "pointer-events-none block size-4 rounded-full bg-background shadow-sm ring-0 transition-transform",
          checked ? "translate-x-4" : "translate-x-0"
        )}
      />
    </button>
  )
}

/* ── Setting row ────────────────────────────────────────────────────────────── */

function SettingRow({
  label,
  description,
  checked,
  onChange,
}: {
  label: string
  description: string
  checked: boolean
  onChange: (v: boolean) => void
}) {
  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <div className="flex flex-col gap-0.5">
        <span className="text-sm font-medium">{label}</span>
        <span className="text-xs text-muted-foreground">{description}</span>
      </div>
      <Toggle checked={checked} onChange={onChange} />
    </div>
  )
}

/* ── Page ──────────────────────────────────────────────────────────────────── */

export default function SettingsPage() {
  const { colorTheme, mode, setColorTheme, setMode } = useTheme()

  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    marketing: false,
    security: true,
  })

  const [privacy, setPrivacy] = useState({
    publicProfile: false,
    activityStatus: true,
    twoFactor: false,
  })

  return (
    <div className="flex flex-col gap-6 p-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Manage your workspace preferences and account options.
        </p>
      </div>

      {/* ── Appearance ─────────────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Palette className="size-4 text-primary" />
            Appearance
          </CardTitle>
          <CardDescription>Choose your interface theme and accent color.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-5">
          {/* Mode */}
          <div className="flex flex-col gap-2">
            <p className="text-sm font-medium">Mode</p>
            <div className="flex gap-2">
              {MODES.map(({ value, icon: Icon, label }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setMode(value)}
                  className={cn(
                    "flex flex-1 flex-col items-center gap-1.5 rounded-lg border px-3 py-3 text-xs transition-colors",
                    mode === value
                      ? "border-primary bg-primary/5 text-primary font-semibold"
                      : "border-border text-muted-foreground hover:bg-muted"
                  )}
                >
                  <Icon className="size-4" />
                  {label}
                </button>
              ))}
            </div>
          </div>

          <Separator />

          {/* Color theme */}
          <div className="flex flex-col gap-2">
            <p className="text-sm font-medium">Accent color</p>
            <div className="grid grid-cols-6 gap-1.5 sm:grid-cols-9">
              {COLOR_THEMES.map(({ value, label, color }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setColorTheme(value)}
                  title={label}
                  className={cn(
                    "group flex flex-col items-center gap-1 rounded-md p-1.5 text-[10px] text-muted-foreground transition-colors hover:bg-muted",
                    colorTheme === value && "bg-muted font-semibold text-foreground ring-1 ring-border"
                  )}
                >
                  <span
                    className="size-5 rounded-full ring-1 ring-black/10 dark:ring-white/10"
                    style={{ background: color }}
                  />
                  <span className="truncate w-full text-center">{label}</span>
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ── Notifications ──────────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Bell className="size-4 text-primary" />
            Notifications
          </CardTitle>
          <CardDescription>Control how and when you receive notifications.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col divide-y divide-border">
          <SettingRow
            label="Email notifications"
            description="Receive updates and alerts via email."
            checked={notifications.email}
            onChange={(v) => setNotifications((p) => ({ ...p, email: v }))}
          />
          <SettingRow
            label="Push notifications"
            description="Get real-time alerts in your browser."
            checked={notifications.push}
            onChange={(v) => setNotifications((p) => ({ ...p, push: v }))}
          />
          <SettingRow
            label="Marketing emails"
            description="News, product updates, and promotions."
            checked={notifications.marketing}
            onChange={(v) => setNotifications((p) => ({ ...p, marketing: v }))}
          />
          <SettingRow
            label="Security alerts"
            description="Notifications about your account security."
            checked={notifications.security}
            onChange={(v) => setNotifications((p) => ({ ...p, security: v }))}
          />
        </CardContent>
      </Card>

      {/* ── Privacy & Security ─────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Shield className="size-4 text-primary" />
            Privacy &amp; Security
          </CardTitle>
          <CardDescription>Manage your visibility and account security settings.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col divide-y divide-border">
          <SettingRow
            label="Public profile"
            description="Allow others to view your profile page."
            checked={privacy.publicProfile}
            onChange={(v) => setPrivacy((p) => ({ ...p, publicProfile: v }))}
          />
          <SettingRow
            label="Show activity status"
            description="Let others see when you were last active."
            checked={privacy.activityStatus}
            onChange={(v) => setPrivacy((p) => ({ ...p, activityStatus: v }))}
          />
          <SettingRow
            label="Two-factor authentication"
            description="Add an extra layer of security to your account."
            checked={privacy.twoFactor}
            onChange={(v) => setPrivacy((p) => ({ ...p, twoFactor: v }))}
          />
        </CardContent>
      </Card>

      {/* ── Language & Region ──────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Globe className="size-4 text-primary" />
            Language &amp; Region
          </CardTitle>
          <CardDescription>Set your preferred language and timezone.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-0 divide-y divide-border">
          {[
            { label: "Language", value: "English (US)" },
            { label: "Timezone", value: "UTC+00:00" },
            { label: "Date format", value: "MM/DD/YYYY" },
          ].map(({ label, value }) => (
            <div key={label} className="flex items-center justify-between py-3 text-sm">
              <span className="text-muted-foreground">{label}</span>
              <span className="font-medium">{value}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* ── Sessions ───────────────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Lock className="size-4 text-primary" />
            Active Sessions
          </CardTitle>
          <CardDescription>Devices currently signed in to your account.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-0 divide-y divide-border">
          {[
            { device: "Chrome on Windows", location: "Mumbai, IN", current: true },
            { device: "Safari on iPhone", location: "Mumbai, IN", current: false },
          ].map(({ device, location, current }) => (
            <div key={device} className="flex items-center justify-between py-3">
              <div className="flex flex-col gap-0.5">
                <span className="text-sm font-medium flex items-center gap-2">
                  {device}
                  {current && (
                    <span className="text-[10px] font-semibold text-primary bg-primary/10 px-1.5 py-0.5 rounded-full">
                      Current
                    </span>
                  )}
                </span>
                <span className="text-xs text-muted-foreground">{location}</span>
              </div>
              {!current && (
                <Button variant="outline" size="sm" className="text-destructive hover:text-destructive">
                  Revoke
                </Button>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* ── Danger Zone ────────────────────────────────────────────────────── */}
      <Card className="border-destructive/40">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-destructive">
            <Trash2 className="size-4" />
            Danger Zone
          </CardTitle>
          <CardDescription>
            Permanent actions that cannot be undone.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium">Delete account</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                Permanently delete your account and all associated data.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="shrink-0 border-destructive/40 text-destructive hover:bg-destructive hover:text-destructive-foreground"
            >
              Delete account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
