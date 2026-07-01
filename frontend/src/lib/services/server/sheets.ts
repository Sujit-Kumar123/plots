"use server"

import { revalidatePath } from "next/cache"
import { cqrsFetch } from "@/lib/server-api"
import type { PaginatedSheets, SheetListItem } from "@/lib/services/plot-sheets"

const SHEETS_PATH = "/dashboard/sheets"

export interface FetchSheetsParams {
  page?: number
  page_size?: number
  search?: string
}

interface CqrsPlotList {
  total: number
  limit: number
  offset: number
  items: SheetListItem[]
}

const EMPTY: PaginatedSheets = { items: [], total: 0, page: 1, page_size: 12, total_pages: 0 }

export async function fetchSheets(params: FetchSheetsParams = {}): Promise<PaginatedSheets> {
  const { page = 1, page_size = 12, search } = params
  const limit = page_size
  const offset = (page - 1) * page_size
  const qs = new URLSearchParams({ limit: String(limit), offset: String(offset) })
  if (search) qs.set("q", search)

  try {
    const path = search ? `/api/v1/plots/search?${qs}` : `/api/v1/plots?${qs}`
    const resp = await cqrsFetch<CqrsPlotList>(path)
    if (!resp) return EMPTY
    return {
      items: resp.items,
      total: resp.total,
      page,
      page_size: resp.limit,
      total_pages: resp.total > 0 ? Math.ceil(resp.total / resp.limit) : 0,
    }
  } catch {
    return EMPTY
  }
}

export async function deleteSheetAction(id: string): Promise<{ error?: string }> {
  try {
    await cqrsFetch(`/api/v1/plots/${id}`, { method: "DELETE" })
    revalidatePath(SHEETS_PATH)
    return {}
  } catch (err) {
    return { error: err instanceof Error ? err.message : "Failed to delete sheet." }
  }
}
