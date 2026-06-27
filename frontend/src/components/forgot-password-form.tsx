"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import { forgotPassword } from "@/lib/services/client/auth"
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
import { Input } from "@/components/ui/input"
import { Spinner } from "@/components/ui/spinner"

export function ForgotPasswordForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [email, setEmail]     = useState("")
  const [sent, setSent]       = useState(false)
  const [error, setError]     = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.SyntheticEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      await forgotPassword(email)
      setSent(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  if (sent) {
    return (
      <div className={cn("flex flex-col gap-6", className)} {...props}>
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Check your email</CardTitle>
            <CardDescription>
              If <strong>{email}</strong> is registered, a reset link has been
              sent. Check your inbox and spam folder.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <FieldGroup>
              <Field>
                <FieldDescription className="text-center">
                  <a
                    href="/login"
                    className="text-primary underline-offset-4 hover:underline"
                  >
                    Back to login
                  </a>
                </FieldDescription>
              </Field>
            </FieldGroup>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-xl">Forgot your password?</CardTitle>
          <CardDescription>
            Enter your email and we&apos;ll send you a reset link.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="email">Email</FieldLabel>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                />
              </Field>

              {error && (
                <p className="text-sm text-destructive text-center">{error}</p>
              )}

              <Field>
                <Button type="submit" disabled={loading}>
                  {loading && <Spinner />}
                  {loading ? "Sending…" : "Send reset link"}
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
