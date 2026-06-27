"use client"

import { useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import { resetPassword as authResetPassword } from "@/lib/services/client/auth"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { PasswordInput } from "@/components/ui/password-input"
import { Spinner } from "@/components/ui/spinner"

export function ResetPasswordForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const searchParams        = useSearchParams()
  const router              = useRouter()
  const token               = searchParams.get("token") ?? ""

  const [password, setPassword]   = useState("")
  const [confirm, setConfirm]     = useState("")
  const [error, setError]         = useState("")
  const [loading, setLoading]     = useState(false)
  const [success, setSuccess]     = useState(false)

  async function handleSubmit(e: React.SyntheticEvent) {
    e.preventDefault()
    if (password !== confirm) {
      setError("Passwords do not match")
      return
    }
    if (!token) {
      setError("Reset token is missing. Use the link from your email.")
      return
    }
    setError("")
    setLoading(true)
    try {
      await authResetPassword(token, password)
      setSuccess(true)
      setTimeout(() => router.push("/login"), 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed")
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className={cn("flex flex-col gap-6", className)} {...props}>
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Password reset</CardTitle>
            <CardDescription>
              Your password has been updated. Redirecting to login…
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-xl">Reset your password</CardTitle>
          <CardDescription>Enter a new password for your account.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="password">New password</FieldLabel>
                <PasswordInput
                  id="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                />
              </Field>

              <Field>
                <FieldLabel htmlFor="confirm-password">Confirm password</FieldLabel>
                <PasswordInput
                  id="confirm-password"
                  placeholder="••••••••"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  required
                  disabled={loading}
                />
              </Field>

              {error && (
                <p className="text-sm text-destructive text-center">{error}</p>
              )}

              <Field>
                <Button type="submit" disabled={loading || !token}>
                  {loading && <Spinner />}
                  {loading ? "Resetting…" : "Reset password"}
                </Button>
                <FieldDescription className="text-center">
                  Remember your password?{" "}
                  <a
                    href="/login"
                    className="text-primary underline-offset-4 hover:underline"
                  >
                    Back to login
                  </a>
                </FieldDescription>
              </Field>
            </FieldGroup>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
