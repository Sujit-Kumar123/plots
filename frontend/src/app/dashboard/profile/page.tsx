"use client"

import { useState } from "react"
import {
  Camera,
  CheckCircle2,
  KeyRound,
  Mail,
  Phone,
  Settings,
  Shield,
  User,
  XCircle,
} from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { PasswordInput } from "@/components/ui/password-input"
import { Separator } from "@/components/ui/separator"
import { Spinner } from "@/components/ui/spinner"
import { useAuth } from "@/context/auth-context"
import { api } from "@/lib/api"
import { changePassword } from "@/lib/services/client/auth"
import type { ApiResponse, AuthUser } from "@/lib/types/auth"

const roleVariant: Record<string, "default" | "secondary" | "outline"> = {
  superadmin: "default",
  admin: "secondary",
  member: "outline",
}

function StatusMessage({ success, error }: { success: string; error: string }) {
  if (error)
    return (
      <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
        <XCircle className="size-4 shrink-0" />
        {error}
      </div>
    )
  if (success)
    return (
      <div className="flex items-center gap-2 rounded-lg border border-green-500/30 bg-green-500/5 px-3 py-2 text-sm text-green-700 dark:text-green-400">
        <CheckCircle2 className="size-4 shrink-0" />
        {success}
      </div>
    )
  return null
}

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()

  const [fname, setFname] = useState(user?.profile?.fname ?? "")
  const [lname, setLname] = useState(user?.profile?.lname ?? "")
  const [phone, setPhone] = useState(user?.profile?.phone ?? "")

  const [profileMsg, setProfileMsg] = useState("")
  const [profileErr, setProfileErr] = useState("")
  const [profileSaving, setProfileSaving] = useState(false)

  const [curPwd, setCurPwd] = useState("")
  const [newPwd, setNewPwd] = useState("")
  const [conPwd, setConPwd] = useState("")
  const [pwdMsg, setPwdMsg] = useState("")
  const [pwdErr, setPwdErr] = useState("")
  const [pwdSaving, setPwdSaving] = useState(false)

  const roleName =
    user?.role?.short_name ?? "member"
  const initials =
    `${(fname || user?.profile?.fname || "")[0] ?? ""}${(lname || user?.profile?.lname || "")[0] ?? ""}`.toUpperCase() || "?"
  const fullName =
    [fname, lname].filter(Boolean).join(" ") ||
    user?.email?.split("@")[0] ||
    "User"

  async function handleProfileSave(e: React.SyntheticEvent) {
    e.preventDefault()
    setProfileMsg("")
    setProfileErr("")
    setProfileSaving(true)
    try {
      await api.patch<ApiResponse<AuthUser>>("/profile/me", { fname, lname, phone })
      await refreshUser()
      setProfileMsg("Profile updated successfully")
    } catch (err) {
      setProfileErr(err instanceof Error ? err.message : "Update failed")
    } finally {
      setProfileSaving(false)
    }
  }

  async function handlePasswordChange(e: React.SyntheticEvent) {
    e.preventDefault()
    setPwdMsg("")
    setPwdErr("")
    if (newPwd !== conPwd) {
      setPwdErr("New passwords do not match")
      return
    }
    setPwdSaving(true)
    try {
      await changePassword(curPwd, newPwd)
      setPwdMsg("Password changed successfully")
      setCurPwd("")
      setNewPwd("")
      setConPwd("")
    } catch (err) {
      setPwdErr(err instanceof Error ? err.message : "Password change failed")
    } finally {
      setPwdSaving(false)
    }
  }

  return (
    <div className="flex flex-col gap-6 p-6 w-full">

      {/* Page heading */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Profile</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Manage your personal information and account settings.
        </p>
      </div>

      {/* Row 1: Identity (narrow) + Personal Information (wide) */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-[2fr_3fr] md:items-stretch">

      {/* Card 1 — Identity */}
      <Card className="flex flex-col">
        <CardContent className="flex flex-1 flex-col items-center justify-center gap-4 py-10 px-6 text-center">
          <div className="relative">
            <Avatar className="size-28">
              <AvatarImage src={user?.profile?.photo ?? ""} />
              <AvatarFallback className="bg-primary/10 text-primary text-3xl font-semibold">
                {initials}
              </AvatarFallback>
            </Avatar>
            <button
              type="button"
              aria-label="Change photo"
              className="absolute bottom-1 right-1 flex size-7 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-md hover:bg-primary/90 transition-colors"
            >
              <Camera className="size-3.5" />
            </button>
          </div>

          <div className="flex flex-col items-center gap-1.5">
            <p className="text-xl font-semibold">{fullName}</p>
            <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <Mail className="size-3.5 shrink-0" />
              <span className="break-all">{user?.email}</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-2">
            <Badge variant={roleVariant[roleName] ?? "outline"}>
              <Shield className="size-3" />
              {roleName}
            </Badge>
            {user?.is_verified && (
              <Badge
                variant="outline"
                className="border-green-500/30 text-green-700 bg-green-500/5 dark:text-green-400"
              >
                <CheckCircle2 className="size-3" />
                Verified
              </Badge>
            )}
            {!user?.is_active && (
              <Badge variant="outline" className="border-destructive/30 text-destructive">
                Inactive
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Card 2 — Personal Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <User className="size-4 text-primary" />
            Personal Information
          </CardTitle>
          <CardDescription>Update your name and contact details.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleProfileSave} className="flex flex-col gap-5">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="first-name">First name</Label>
                <Input
                  id="first-name"
                  value={fname}
                  onChange={(e) => setFname(e.target.value)}
                  placeholder="John"
                  disabled={profileSaving}
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="last-name">Last name</Label>
                <Input
                  id="last-name"
                  value={lname}
                  onChange={(e) => setLname(e.target.value)}
                  placeholder="Doe"
                  disabled={profileSaving}
                />
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="phone" className="flex items-center gap-1.5">
                <Phone className="size-3.5 text-muted-foreground" />
                Phone number
              </Label>
              <Input
                id="phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 (555) 000-0000"
                disabled={profileSaving}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email-display" className="flex items-center gap-1.5">
                <Mail className="size-3.5 text-muted-foreground" />
                Email
              </Label>
              <Input
                id="email-display"
                type="email"
                value={user?.email ?? ""}
                disabled
                className="opacity-60 cursor-not-allowed"
              />
              <p className="text-xs text-muted-foreground">Email cannot be changed here.</p>
            </div>

            <StatusMessage success={profileMsg} error={profileErr} />

            <div className="flex justify-end">
              <Button type="submit" disabled={profileSaving} className="w-fit">
                {profileSaving && <Spinner />}
                {profileSaving ? "Saving…" : "Save changes"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      </div>{/* end row 1 */}

      {/* Row 2: Change Password (wide) + Account Details (narrow) */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-[3fr_2fr] md:items-stretch">

      {/* Card 3 — Change Password */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <KeyRound className="size-4 text-primary" />
            Change Password
          </CardTitle>
          <CardDescription>
            Choose a strong password you don&apos;t use elsewhere.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePasswordChange} className="flex flex-col gap-5">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="current-password">Current password</Label>
              <PasswordInput
                id="current-password"
                placeholder="••••••••"
                value={curPwd}
                onChange={(e) => setCurPwd(e.target.value)}
                required
                disabled={pwdSaving}
              />
            </div>

            <Separator />

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="new-password">New password</Label>
              <PasswordInput
                id="new-password"
                placeholder="••••••••"
                value={newPwd}
                onChange={(e) => setNewPwd(e.target.value)}
                required
                disabled={pwdSaving}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="confirm-new-password">Confirm new password</Label>
              <PasswordInput
                id="confirm-new-password"
                placeholder="••••••••"
                value={conPwd}
                onChange={(e) => setConPwd(e.target.value)}
                required
                disabled={pwdSaving}
              />
            </div>

            <StatusMessage success={pwdMsg} error={pwdErr} />

            <div className="flex justify-end">
              <Button type="submit" disabled={pwdSaving} className="w-fit">
                {pwdSaving && <Spinner />}
                {pwdSaving ? "Updating…" : "Update password"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Card 4 — Account Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Settings className="size-4 text-primary" />
            Account Details
          </CardTitle>
          <CardDescription>Read-only information about your account.</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {[
            { label: "Email",    value: user?.email ?? "—",               icon: <Mail className="size-4 text-muted-foreground" /> },
            { label: "Role",     value: roleName,                         icon: <Shield className="size-4 text-muted-foreground" /> },
            { label: "Auth",     value: user?.auth_source ?? "email",     icon: <KeyRound className="size-4 text-muted-foreground" /> },
            { label: "Status",   value: user?.is_active ? "Active" : "Inactive", icon: <CheckCircle2 className="size-4 text-muted-foreground" /> },
            { label: "Verified", value: user?.is_verified ? "Yes" : "No", icon: <Settings className="size-4 text-muted-foreground" /> },
          ].map(({ label, value, icon }, i, arr) => (
            <div key={label}>
              <div className="flex items-center justify-between px-6 py-3.5">
                <div className="flex items-center gap-2.5 text-sm text-muted-foreground">
                  {icon}
                  {label}
                </div>
                <span className="text-sm font-medium">{value}</span>
              </div>
              {i < arr.length - 1 && <Separator />}
            </div>
          ))}
        </CardContent>
      </Card>

      </div>{/* end row 2 */}

    </div>
  )
}
