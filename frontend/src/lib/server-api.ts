import { cookies, headers } from "next/headers"

const BACKEND = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000"

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

async function getAuthHeaders(): Promise<HeadersInit> {
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value

  // Forward the browser's real IP so the backend rate-limiter buckets by
  // actual user, not by the Next.js server address (127.0.0.1).
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

export async function serverFetch<T>(
  path: string,
  { method = "GET", body, next }: FetchOptions = {},
): Promise<T | null> {
  const res = await fetch(`${BACKEND}${path}`, {
    method,
    headers: await getAuthHeaders(),
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    // When `next` is provided (e.g. tags), let Next.js manage caching;
    // otherwise disable caching so mutations are always fresh.
    ...(next ? { next } : { cache: "no-store" }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail ?? err?.message ?? `Request failed (${res.status})`)
  }

  const json: ServerApiResponse<T> = await res.json()
  return json.data ?? null
}
