// Relative '/api' works in Docker (Nginx proxies it) and in local dev
// (Next.js rewrites proxy it to the backend).  Override with
// NEXT_PUBLIC_API_URL only when you need an explicit absolute URL.
const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? '/api').replace(/\/$/, '')

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...init.headers,
    },
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const message =
      body?.detail ?? body?.message ?? `Request failed (${res.status})`
    throw new ApiError(message, res.status)
  }

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
