import { clientFetch } from "@/lib/client-api"
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
  name: string
  sheet_w: number
  sheet_d: number
  grid_step: number
  elements: SheetElements
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

export interface PaginatedSheets {
  items: SheetListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// ── API calls ─────────────────────────────────────────────────────────────────

export async function apiCreateSheet(payload: {
  name: string
  sheet_w: number
  sheet_d: number
  grid_step: number
  elements: SheetElements
}): Promise<SheetData | null> {
  return clientFetch<SheetData>("/api/plot/sheets", { method: "POST", body: payload })
}

export async function apiGetSheet(id: string): Promise<SheetData | null> {
  return clientFetch<SheetData>(`/api/plot/sheets/${id}`)
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
): Promise<SheetData | null> {
  return clientFetch<SheetData>(`/api/plot/sheets/${id}`, { method: "PUT", body: payload })
}

export async function apiListSheets(): Promise<SheetListItem[]> {
  return (await clientFetch<SheetListItem[]>("/api/plot/sheets")) ?? []
}

export async function apiDeleteSheet(id: string): Promise<void> {
  await clientFetch(`/api/plot/sheets/${id}`, { method: "DELETE" })
}
