"use server"

import { cookies } from "next/headers"
import { serverFetch } from "@/lib/server-api"
import type { AuthUser } from "@/lib/types/auth"

const BACKEND = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000"
const IS_PROD = process.env.NODE_ENV === "production"

// Match auth-service auth_config.py defaults
const ACCESS_MAX_AGE  = 30 * 60            // 30 minutes
const REFRESH_MAX_AGE = 7 * 24 * 60 * 60  // 7 days

interface AuthTokens {
  access_token: string
  refresh_token: string
}

interface LoginRegisterData {
  user: AuthUser
  tokens: AuthTokens
}

async function _postPublic(path: string, body: unknown): Promise<{ success: boolean; data: unknown }> {
  const res = await fetch(`${BACKEND}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail ?? err?.message ?? `Request failed (${res.status})`)
  }
  return res.json()
}

async function _setAuthCookies(tokens: AuthTokens) {
  const cs = await cookies()
  cs.set("access_token", tokens.access_token, {
    httpOnly: true,
    path: "/",
    sameSite: "lax",
    secure: IS_PROD,
    maxAge: ACCESS_MAX_AGE,
  })
  cs.set("refresh_token", tokens.refresh_token, {
    httpOnly: true,
    path: "/",
    sameSite: "lax",
    secure: IS_PROD,
    maxAge: REFRESH_MAX_AGE,
  })
}

export async function loginAction(email: string, password: string): Promise<AuthUser> {
  const json = await _postPublic("/api/auth/login", { email, password })
  const { user, tokens } = json.data as LoginRegisterData
  await _setAuthCookies(tokens)
  return user
}

export async function registerAction(
  email: string,
  password: string,
  fname?: string,
  lname?: string,
): Promise<AuthUser> {
  const json = await _postPublic("/api/auth/register", { email, password, fname, lname })
  const { user, tokens } = json.data as LoginRegisterData
  await _setAuthCookies(tokens)
  return user
}

export async function logoutAction(): Promise<void> {
  try {
    await serverFetch<null>("/api/auth/logout", { method: "POST" })
  } catch {
    // Proceed with cleanup even if the backend call fails
  }
  const cs = await cookies()
  cs.delete("access_token")
  cs.delete("refresh_token")
}

export async function forgotPasswordAction(email: string): Promise<void> {
  await _postPublic("/api/auth/forgot-password", { email })
}

export async function resetPasswordAction(token: string, new_password: string): Promise<void> {
  await _postPublic("/api/auth/reset-password", { token, new_password })
}
