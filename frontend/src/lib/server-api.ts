import { cookies, headers } from "next/headers"

const BACKEND = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000"
const CQRS_GATEWAY = process.env.CQRS_GATEWAY_URL ?? "http://api-gateway:8000"

interface ServerApiResponse<T> {
  success: boolean
  data: T | null
  message: string | null
  errors: unknown | null
}

interface FetchOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE"
  body?: unknown
  next?: { tags?: string[]; revalidate?: number | false }
}

// ── Server-side refresh mutex ─────────────────────────────────────────────────
// When concurrent server actions from the same user all receive a 401, only
// ONE /auth/refresh call is made. Others wait on the shared promise so the
// backend's refresh-token rotation only needs to happen once.
//
//   Access token expired
//         │
//         ▼
//   5 server actions get 401
//         │
//         ▼
//   Action #1: no lock for this refresh_token → starts refresh, sets lock
//   Actions #2-5: lock exists → await the same promise
//         │
//         ▼
//   Refresh succeeds → returns new access_token to all 5 callers
//         │
//         ▼
//   Each server action retries with the new token

const _refreshInFlight = new Map<string, Promise<string | null>>()

async function refreshServerToken(): Promise<string | null> {
  const cookieStore = await cookies()
  const refreshToken = cookieStore.get("refresh_token")?.value
  if (!refreshToken) return null

  // Reuse an in-flight refresh for the same refresh_token
  const existing = _refreshInFlight.get(refreshToken)
  if (existing) return existing

  const promise = (async (): Promise<string | null> => {
    try {
      const res = await fetch(`${BACKEND}/api/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
        cache: "no-store",
      })
      if (!res.ok) return null

      // Tokens are in the standard { success, data: { access_token, refresh_token } } envelope
      const body = await res.json().catch(() => null)
      const newAccess: string | undefined = body?.data?.access_token
      const newRefresh: string | undefined = body?.data?.refresh_token

      // Persist the rotated refresh_token immediately. The backend revokes the old
      // token on every rotation — if we don't update the cookie here, the next
      // refresh attempt uses the now-revoked token and the user gets logged out.
      if (newRefresh) {
        try {
          const cs = await cookies()
          cs.set("refresh_token", newRefresh, {
            httpOnly: true,
            path: "/",
            sameSite: "lax",
            secure: process.env.NODE_ENV === "production",
            maxAge: 7 * 24 * 60 * 60,
          })
        } catch {
          // cookies().set() unavailable outside server actions / route handlers
        }
      }

      if (newAccess) return newAccess

      // Fallback: parse from Set-Cookie header
      const setCookie = res.headers.get("set-cookie") ?? ""
      const match = setCookie.match(/(?:^|,\s*)access_token=([^;,\s]+)/)
      return match?.[1] ?? null
    } finally {
      _refreshInFlight.delete(refreshToken)
    }
  })()

  _refreshInFlight.set(refreshToken, promise)
  return promise
}

async function getAuthHeaders(overrideToken?: string): Promise<HeadersInit> {
  let token: string | undefined = overrideToken
  if (!token) {
    const cookieStore = await cookies()
    token = cookieStore.get("access_token")?.value
  }

  // Forward the real client IP so the backend rate-limiter buckets by user,
  // not by the Next.js server address.
  let clientIp: string | undefined
  try {
    const h = await headers()
    clientIp =
      h.get("x-real-ip") ??
      h.get("x-forwarded-for")?.split(",")[0]?.trim() ??
      undefined
  } catch {
    // headers() is unavailable outside a request context (e.g. build time)
  }

  return {
    "Content-Type": "application/json",
    ...(token ? { Cookie: `access_token=${token}` } : {}),
    ...(clientIp ? { "X-Real-IP": clientIp } : {}),
  }
}

async function persistNewToken(newToken: string) {
  try {
    const cs = await cookies()
    cs.set("access_token", newToken, {
      httpOnly: true,
      path: "/",
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      maxAge: 30 * 60,  // match JWT exp so the cookie expires with the token
    })
  } catch {
    // cookies().set() is only available inside server actions / route handlers
  }
}

// ── serverFetch ───────────────────────────────────────────────────────────────
// Calls the main backend (auth-service, profile-service, admin-service, etc.)
// Unwraps the standard { success, data, message, errors } envelope.

export async function serverFetch<T>(
  path: string,
  { method = "GET", body, next }: FetchOptions = {},
  _retryToken?: string,
): Promise<T | null> {
  const res = await fetch(`${BACKEND}${path}`, {
    method,
    headers: await getAuthHeaders(_retryToken),
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    ...(next ? { next } : { cache: "no-store" }),
  })

  // Auto-refresh on 401, retry once with the new token
  if (res.status === 401 && _retryToken === undefined) {
    const newToken = await refreshServerToken()
    if (newToken) {
      await persistNewToken(newToken)
      return serverFetch(path, { method, body, next }, newToken)
    }
    throw new Error("Session expired. Please log in again.")
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail ?? err?.message ?? `Request failed (${res.status})`)
  }

  const json: ServerApiResponse<T> = await res.json()
  return json.data ?? null
}

// ── cqrsFetch ─────────────────────────────────────────────────────────────────
// Calls the CQRS api-gateway directly. Returns raw JSON (no envelope wrapper).

export async function cqrsFetch<T>(
  path: string,
  { method = "GET", body, next }: FetchOptions = {},
  _retryToken?: string,
): Promise<T | null> {
  const res = await fetch(`${CQRS_GATEWAY}${path}`, {
    method,
    headers: await getAuthHeaders(_retryToken),
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    ...(next ? { next } : { cache: "no-store" }),
  })

  if (res.status === 204) return null

  // Auto-refresh on 401, retry once with the new token
  if (res.status === 401 && _retryToken === undefined) {
    const newToken = await refreshServerToken()
    if (newToken) {
      await persistNewToken(newToken)
      return cqrsFetch(path, { method, body, next }, newToken)
    }
    throw new Error("Session expired. Please log in again.")
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail ?? err?.message ?? `Request failed (${res.status})`)
  }

  return res.json() as Promise<T>
}
