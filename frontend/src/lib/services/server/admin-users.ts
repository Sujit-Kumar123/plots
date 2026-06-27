"use server"

import { revalidatePath } from "next/cache"
import { serverFetch } from "@/lib/server-api"
import type { AdminUser, PaginatedUsers, ListUsersParams } from "@/lib/types/admin-users"

const USERS_PATH = "/dashboard/users"

export async function fetchUsers(params: ListUsersParams = {}): Promise<PaginatedUsers> {
  const { page = 1, page_size = 10, role, is_active } = params
  const qs = new URLSearchParams({ page: String(page), page_size: String(page_size) })
  if (role !== undefined) qs.set("role", role)
  if (is_active !== undefined) qs.set("is_active", String(is_active))
  const data = await serverFetch<PaginatedUsers>(`/api/admin/users?${qs}`)
  return data ?? { items: [], total: 0, page, page_size, total_pages: 0 }
}

export async function getUserDetail(userId: string): Promise<AdminUser | null> {
  return serverFetch<AdminUser>(`/api/admin/users/${userId}`)
}

export async function updateUser(
  userId: string,
  params: { role_id?: string; is_active?: boolean },
): Promise<{ error?: string }> {
  try {
    const qs = new URLSearchParams()
    if (params.role_id !== undefined) qs.set("role_id", params.role_id)
    if (params.is_active !== undefined) qs.set("is_active", String(params.is_active))
    await serverFetch<AdminUser>(`/api/admin/users/${userId}?${qs}`, { method: "PUT" })
    revalidatePath(USERS_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to update user." }
  }
}

export async function deleteUser(userId: string): Promise<{ error?: string }> {
  try {
    await serverFetch<null>(`/api/admin/users/${userId}`, { method: "DELETE" })
    revalidatePath(USERS_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to delete user." }
  }
}

export async function deactivateUser(userId: string): Promise<{ error?: string }> {
  try {
    await serverFetch<AdminUser>(`/api/admin/users/${userId}/deactivate`, { method: "POST" })
    revalidatePath(USERS_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to deactivate user." }
  }
}

export async function activateUser(userId: string): Promise<{ error?: string }> {
  try {
    await serverFetch<AdminUser>(`/api/admin/users/${userId}/activate`, { method: "POST" })
    revalidatePath(USERS_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to activate user." }
  }
}
