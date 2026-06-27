"use server"

import { revalidatePath, revalidateTag } from "next/cache"
import { serverFetch } from "@/lib/server-api"
import type { ApiPermission, ApiRole, ListPermissionsParams, PaginatedPermissions } from "@/lib/types/roles"

const ROLES_PATH = "/dashboard/users/roles"

export async function fetchMissingPermissionCodes(): Promise<string[]> {
  try {
    const data = await serverFetch<string[]>("/api/auth/permissions/missing")
    return data ?? []
  } catch {
    return []
  }
}

export async function fetchPermissions(params: ListPermissionsParams = {}): Promise<PaginatedPermissions & { fetchError?: string }> {
  const { page = 1, page_size = 10 } = params
  const qs = new URLSearchParams({ page: String(page), page_size: String(page_size) })
  try {
    const data = await serverFetch<PaginatedPermissions>(`/api/auth/permissions?${qs}`, {
      next: { tags: ["permissions"] },
    })
    return data ?? { items: [], total: 0, page, page_size, total_pages: 0 }
  } catch (err) {
    return {
      items: [],
      total: 0,
      page,
      page_size,
      total_pages: 0,
      fetchError: err instanceof Error ? err.message : "Failed to load permissions.",
    }
  }
}

export async function createPermission(body: {
  name: string
  code: string
  description?: string
}): Promise<{ error?: string }> {
  try {
    await serverFetch<ApiPermission>("/api/auth/permissions", { method: "POST", body })
    revalidateTag("permissions", "default")
    revalidatePath(ROLES_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to create permission." }
  }
}

export async function updatePermission(
  permissionId: string,
  body: { name?: string; code?: string; description?: string },
): Promise<{ error?: string }> {
  try {
    await serverFetch<ApiPermission>(`/api/auth/permissions/${permissionId}`, { method: "PATCH", body })
    revalidateTag("permissions", "default")
    revalidatePath(ROLES_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to update permission." }
  }
}

export async function deletePermission(permissionId: string): Promise<{ error?: string }> {
  try {
    await serverFetch<null>(`/api/auth/permissions/${permissionId}`, { method: "DELETE" })
    revalidateTag("permissions", "default")
    revalidatePath(ROLES_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to delete permission." }
  }
}

export async function assignPermissionToRole(
  permissionId: string,
  roleId: string,
): Promise<{ error?: string }> {
  try {
    await serverFetch<ApiRole>(`/api/auth/permissions/${permissionId}/assign/${roleId}`, { method: "POST" })
    revalidateTag("roles", "default")
    revalidatePath(ROLES_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to assign permission." }
  }
}

export async function unassignPermissionFromRole(
  permissionId: string,
  roleId: string,
): Promise<{ error?: string }> {
  try {
    await serverFetch<ApiRole>(`/api/auth/permissions/${permissionId}/unassign/${roleId}`, { method: "DELETE" })
    revalidateTag("roles", "default")
    revalidatePath(ROLES_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to unassign permission." }
  }
}
