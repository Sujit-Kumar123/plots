import { api } from "@/lib/api"
import type { ApiResponse, AuthUser } from "@/lib/types/auth"

export interface LoginResult {
  user: AuthUser
}

export interface RegisterResult {
  user: AuthUser
}

export async function login(email: string, password: string): Promise<LoginResult> {
  const res = await api.post<ApiResponse<LoginResult>>("/auth/login", { email, password })
  if (!res.data) throw new Error("Login failed")
  return res.data
}

export async function register(
  email: string,
  password: string,
  fname?: string,
  lname?: string,
): Promise<RegisterResult> {
  const res = await api.post<ApiResponse<RegisterResult>>("/auth/register", {
    email,
    password,
    fname,
    lname,
  })
  if (!res.data) throw new Error("Registration failed")
  return res.data
}

export async function logout(): Promise<void> {
  await api.post("/auth/logout")
}

export async function forgotPassword(email: string): Promise<void> {
  await api.post("/auth/forgot-password", { email })
}

export async function resetPassword(token: string, new_password: string): Promise<void> {
  await api.post("/auth/reset-password", { token, new_password })
}

export async function changePassword(
  current_password: string,
  new_password: string,
): Promise<void> {
  await api.post("/auth/change-password", { current_password, new_password })
}

export async function getMe(): Promise<AuthUser | null> {
  try {
    const res = await api.get<ApiResponse<AuthUser>>("/profile/me")
    return res.data ?? null
  } catch {
    return null
  }
}
