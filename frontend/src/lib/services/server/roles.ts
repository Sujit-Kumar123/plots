"use server"

import { revalidatePath, revalidateTag } from "next/cache"
import { serverFetch } from "@/lib/server-api"
import type { ApiRole } from "@/lib/types/roles"

const ROLES_PATH = "/dashboard/users/roles"

export async function fetchRoles(): Promise<ApiRole[]> {
  const data = await serverFetch<ApiRole[]>("/api/auth/roles", { next: { tags: ["roles"] } })
  return data ?? []
}

export async function getRoleDetail(roleId: string): Promise<ApiRole | null> {
  return serverFetch<ApiRole>(`/api/auth/roles/${roleId}`)
}

export async function createRole(body: {
  name: string
  short_name: string
  description?: string
}): Promise<{ error?: string }> {
  try {
    await serverFetch<ApiRole>("/api/auth/roles", { method: "POST", body })
    revalidateTag("roles", "default")
    revalidatePath(ROLES_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to create role." }
  }
}

export async function updateRole(
  roleId: string,
  body: { name?: string; short_name?: string; description?: string },
): Promise<{ error?: string }> {
  try {
    await serverFetch<ApiRole>(`/api/auth/roles/${roleId}`, { method: "PATCH", body })
    revalidateTag("roles", "default")
    revalidatePath(ROLES_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to update role." }
  }
}

export async function deleteRole(roleId: string): Promise<{ error?: string }> {
  try {
    await serverFetch<null>(`/api/auth/roles/${roleId}`, { method: "DELETE" })
    revalidateTag("roles", "default")
    revalidatePath(ROLES_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to delete role." }
  }
}

export async function assignRole(roleId: string, userId: string): Promise<{ error?: string }> {
  try {
    await serverFetch<null>(`/api/auth/roles/${roleId}/assign/${userId}`, { method: "POST" })
    revalidateTag("roles", "default")
    revalidatePath(ROLES_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to assign role." }
  }
}

export async function unassignRole(userId: string): Promise<{ error?: string }> {
  try {
    await serverFetch<null>(`/api/auth/roles/unassign/${userId}`, { method: "DELETE" })
    revalidateTag("roles", "default")
    revalidatePath(ROLES_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to unassign role." }
  }
}
