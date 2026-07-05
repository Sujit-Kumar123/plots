"use server"

import { serverFetch } from "@/lib/server-api"
import type { AuthUser } from "@/lib/types/auth"

export async function updateProfile(data: {
  fname?: string
  lname?: string
  phone?: string
}): Promise<AuthUser> {
  const result = await serverFetch<AuthUser>("/api/profile/me", {
    method: "PATCH",
    body: data,
  })
  if (!result) throw new Error("Profile update failed")
  return result
}

export async function changePasswordAction(
  current_password: string,
  new_password: string,
): Promise<void> {
  await serverFetch<null>("/api/auth/change-password", {
    method: "POST",
    body: { current_password, new_password },
  })
}

export async function getMeAction(): Promise<AuthUser | null> {
  try {
    return await serverFetch<AuthUser>("/api/profile/me")
  } catch {
    return null
  }
}
