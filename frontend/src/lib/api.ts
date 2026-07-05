// Relative '/api' works in Docker (Nginx proxies it) and in local dev
// (Next.js rewrites proxy it to the backend). Override with
// NEXT_PUBLIC_API_URL only when you need an explicit absolute URL.
const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? '/api').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// ── Refresh token mutex ───────────────────────────────────────────────────────
// When the access token expires, multiple concurrent requests each receive a
// 401. The first one triggers a SINGLE /auth/refresh call. The rest join a
// wait-queue and retry automatically once the new token is set by the backend.
//
//   Access token expired
//         │
//         ▼
//   5 requests get 401
//         │
//         ▼
//   Only Request #1 calls /refresh (isRefreshing = false → set to true)
//   Requests #2-5 push a callback to pendingRequests and await it
//         │
//         ▼
//   Refresh succeeds → drainQueue(null) resolves all 4 pending callbacks
//         │
//         ▼
//   All 5 requests retry with the new token (cookie set by backend)

let isRefreshing = false
let pendingRequests: Array<(error?: unknown) => void> = []

function drainQueue(error?: unknown) {
  pendingRequests.forEach(cb => cb(error))
  pendingRequests = []
}

async function refreshAccessToken(): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) throw new ApiError('Session expired. Please log in again.', 401)
}

async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  _isRetry = false,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...init.headers,
    },
  })

  // ── 401: refresh once, then retry ────────────────────────────────────────
  if (res.status === 401 && !_isRetry) {
    if (isRefreshing) {
      // Refresh already in flight — queue this request and wait
      await new Promise<void>((resolve, reject) => {
        pendingRequests.push((error?: unknown) => (error ? reject(error) : resolve()))
      })
      return apiFetch(path, init, true)
    }

    isRefreshing = true
    try {
      await refreshAccessToken()
      drainQueue()                          // refresh succeeded → unblock waiters
      return apiFetch(path, init, true)     // retry this request
    } catch (err) {
      drainQueue(err)                       // refresh failed → reject all waiters
      if (typeof window !== 'undefined') window.location.replace('/login')
      throw err
    } finally {
      isRefreshing = false
    }
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(
      body?.detail ?? body?.message ?? `Request failed (${res.status})`,
      res.status,
    )
  }

  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const api = {
  get<T>(path: string) {
    return apiFetch<T>(path)
  },
  post<T>(path: string, body?: unknown) {
    return apiFetch<T>(path, {
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  },
  patch<T>(path: string, body?: unknown) {
    return apiFetch<T>(path, {
      method: 'PATCH',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  },
  put<T>(path: string, body?: unknown) {
    return apiFetch<T>(path, {
      method: 'PUT',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  },
  delete<T>(path: string) {
    return apiFetch<T>(path, { method: 'DELETE' })
  },
}
