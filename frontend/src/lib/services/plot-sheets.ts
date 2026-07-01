import { api } from "@/lib/api"
import type { BlockInfo, DivPanelInfo, TextInfo, WallInfo } from "@/app/plot/_components/_types"

// ── Serialised element types ──────────────────────────────────────────────────

export interface SerializedBlock extends BlockInfo {
  color: string
}

export interface SerializedLine {
  color: string
  points: { x: number; y: number; z: number }[]
}

export interface SerializedWall extends WallInfo {
  color: string
}

export type SerializedDivPanel = DivPanelInfo

export type SerializedText = TextInfo

export interface SheetElements {
  blocks: SerializedBlock[]
  penLines: SerializedLine[]
  walls: SerializedWall[]
  divPanels: SerializedDivPanel[]
  textSprites: SerializedText[]
}

// ── API response types ────────────────────────────────────────────────────────

export interface SheetData {
  id: string
  user_id: string
  session_id: string | null
  name: string
  sheet_w: number
  sheet_d: number
  grid_step: number
  elements: SheetElements
  version: number
  element_count: number
  created_at: string
  updated_at: string
}

export interface SheetListItem {
  id: string
  name: string
  sheet_w: number
  sheet_d: number
  updated_at: string
}

// Paginated list shape — compatible with existing sheets grid UI
export interface PaginatedSheets {
  items: SheetListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// Minimal response from CQRS command services (write side)
export interface SheetCommandResult {
  id: string
  name?: string
  version: number
}

// ── API calls ─────────────────────────────────────────────────────────────────

export async function apiCreateSheet(payload: {
  name: string
  sheet_w: number
  sheet_d: number
  grid_step: number
  elements: SheetElements
}): Promise<SheetCommandResult> {
  return api.post<SheetCommandResult>("/v1/plots", payload)
}

export async function apiGetSheet(id: string): Promise<SheetData> {
  return api.get<SheetData>(`/v1/plots/${id}`)
}

export async function apiUpdateSheet(
  id: string,
  payload: {
    name?: string
    sheet_w?: number
    sheet_d?: number
    grid_step?: number
    elements?: SheetElements
  },
): Promise<SheetCommandResult> {
  return api.put<SheetCommandResult>(`/v1/plots/${id}`, payload)
}

export async function apiListSheets(): Promise<SheetListItem[]> {
  const resp = await api.get<{ total: number; limit: number; offset: number; items: SheetListItem[] }>("/v1/plots")
  return resp.items
}

export async function apiDeleteSheet(id: string): Promise<void> {
  await api.delete<void>(`/v1/plots/${id}`)
}
