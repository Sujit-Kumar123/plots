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

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const { login } = useAuth()
  const [email, setEmail]       = useState("")
  const [password, setPassword] = useState("")
  const [error, setError]       = useState("")
  const [loading, setLoading]   = useState(false)

  async function handleSubmit(e: React.SyntheticEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      await login(email, password)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader className="text-center">
          <CardTitle className="text-xl">Welcome back</CardTitle>
          <CardDescription>
            {GOOGLE_ENABLED || AZURE_ENABLED
              ? "Login with your account or credentials"
              : "Login with your email and password"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <FieldGroup>
              {/* SSO buttons */}
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
                        Login with Google
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
                        Login with Azure AD
                      </Button>
                    )}
                  </Field>
                  <FieldSeparator className="*:data-[slot=field-separator-content]:bg-card">
                    Or continue with
                  </FieldSeparator>
                </>
              )}

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
                <div className="flex items-center">
                  <FieldLabel htmlFor="password">Password</FieldLabel>
                  <a
                    href="/forgot-password"
                    className="ml-auto text-sm text-primary underline-offset-4 hover:underline"
                  >
                    Forgot your password?
                  </a>
                </div>
                <PasswordInput
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
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
                  {loading ? "Signing in…" : "Login"}
                </Button>
                <FieldDescription className="text-center">
                  Don&apos;t have an account? <a href="/signup">Sign up</a>
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
