const API = (process.env.NEXT_PUBLIC_API_URL ?? "/api").replace(/\/$/, "")

interface ApiResponse<T> {
  success: boolean
  data: T | null
  message: string | null
  errors: unknown | null
}

export async function clientFetch<T>(
  path: string,
  options: { method?: string; body?: unknown } = {},
): Promise<T | null> {
  const res = await fetch(`${API}${path}`, {
    method: options.method ?? "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...(options.body !== undefined ? { body: JSON.stringify(options.body) } : {}),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail ?? err?.message ?? `Request failed (${res.status})`)
  }

  const json: ApiResponse<T> = await res.json()
  return json.data ?? null
}
