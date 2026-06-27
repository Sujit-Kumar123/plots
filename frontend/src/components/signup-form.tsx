"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/context/auth-context"
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
  FieldSeparator,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { PasswordInput } from "@/components/ui/password-input"
import { Spinner } from "@/components/ui/spinner"

const GOOGLE_ENABLED = process.env.NEXT_PUBLIC_AUTH_GOOGLE_ENABLED === "true"
const AZURE_ENABLED  = process.env.NEXT_PUBLIC_AUTH_AZURE_ENABLED  === "true"

export function SignupForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const { register } = useAuth()
  const [fname, setFname]           = useState("")
  const [lname, setLname]           = useState("")
  const [email, setEmail]           = useState("")
  const [password, setPassword]     = useState("")
  const [confirm, setConfirm]       = useState("")
  const [error, setError]           = useState("")
  const [loading, setLoading]       = useState(false)

  async function handleSubmit(e: React.SyntheticEvent) {
    e.preventDefault()
    if (password !== confirm) {
      setError("Passwords do not match")
      return
    }
    setError("")
    setLoading(true)
    try {
      await register(email, password, fname || undefined, lname || undefined)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-xl">Create an account</CardTitle>
          <CardDescription>
            {GOOGLE_ENABLED || AZURE_ENABLED
              ? "Sign up with your account or credentials"
              : "Sign up with your email and password"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <FieldGroup>
              {(GOOGLE_ENABLED || AZURE_ENABLED) && (
                <>
                  <Field>
                    {GOOGLE_ENABLED && (
                      <Button
                        variant="outline"
                        type="button"
                        onClick={() => { window.location.href = "/api/auth/google" }}
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                          <path d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z" fill="currentColor" />
                        </svg>
                        Sign up with Google
                      </Button>
                    )}
                    {AZURE_ENABLED && (
                      <Button
                        variant="outline"
                        type="button"
                        onClick={() => { window.location.href = "/api/auth/azure" }}
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                          <path d="M11.4 24H0l8.4-14.5L3.9 2.3 11.4 24zm1.1-24l8.4 14.5L3.9 24H24L12.5 0z" fill="currentColor" />
                        </svg>
                        Sign up with Azure AD
                      </Button>
                    )}
                  </Field>
                  <FieldSeparator className="*:data-[slot=field-separator-content]:bg-card">
                    Or continue with
                  </FieldSeparator>
                </>
              )}

              <div className="grid grid-cols-2 gap-4">
                <Field>
                  <FieldLabel htmlFor="fname">First name</FieldLabel>
                  <Input
                    id="fname"
                    placeholder="John"
                    value={fname}
                    onChange={(e) => setFname(e.target.value)}
                    disabled={loading}
                  />
                </Field>
                <Field>
                  <FieldLabel htmlFor="lname">Last name</FieldLabel>
                  <Input
                    id="lname"
                    placeholder="Doe"
                    value={lname}
                    onChange={(e) => setLname(e.target.value)}
                    disabled={loading}
                  />
                </Field>
              </div>

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

              <Field>
                <FieldLabel htmlFor="password">Password</FieldLabel>
                <PasswordInput
                  id="password"
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
                <Button type="submit" disabled={loading}>
                  {loading && <Spinner />}
                  {loading ? "Creating account…" : "Create account"}
                </Button>
                <FieldDescription className="text-center">
                  Already have an account?{" "}
                  <a href="/login">Login</a>
                </FieldDescription>
              </Field>
            </FieldGroup>
          </form>
        </CardContent>
      </Card>
      <FieldDescription className="px-6 text-center">
        By clicking continue, you agree to our <a href="#">Terms of Service</a>{" "}
        and <a href="#">Privacy Policy</a>.
      </FieldDescription>
    </div>
  )
}
