"use server"

import { revalidatePath } from "next/cache"
import { serverFetch } from "@/lib/server-api"
import type { PaginatedSheets } from "@/lib/services/plot-sheets"

const SHEETS_PATH = "/dashboard/sheets"

export interface FetchSheetsParams {
  page?: number
  page_size?: number
  search?: string
}

const EMPTY: PaginatedSheets = { items: [], total: 0, page: 1, page_size: 12, total_pages: 0 }

export async function fetchSheets(params: FetchSheetsParams = {}): Promise<PaginatedSheets> {
  const { page = 1, page_size = 12, search } = params
  const qs = new URLSearchParams({ page: String(page), page_size: String(page_size) })
  if (search) qs.set("search", search)
  try {
    return (await serverFetch<PaginatedSheets>(`/api/plot/sheets?${qs}`)) ?? EMPTY
  } catch {
    return EMPTY
  }
}

export async function deleteSheetAction(id: string): Promise<{ error?: string }> {
  try {
    await serverFetch(`/api/plot/sheets/${id}`, { method: "DELETE" })
    revalidatePath(SHEETS_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to delete sheet." }
  }
}
