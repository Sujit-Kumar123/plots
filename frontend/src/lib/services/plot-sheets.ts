"use server"

import { cqrsFetch } from "@/lib/server-api"
import type { BlockInfo, DivPanelInfo, FurnitureInfo, TextInfo, WallInfo } from "@/app/plot/_components/_types"

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

export type SerializedFurniturePlacement = FurnitureInfo

export interface SheetElements {
  blocks: SerializedBlock[]
  penLines: SerializedLine[]
  walls: SerializedWall[]
  divPanels: SerializedDivPanel[]
  textSprites: SerializedText[]
  furniturePlacements: SerializedFurniturePlacement[]
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

export interface PaginatedSheets {
  items: SheetListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface SheetCommandResult {
  id: string
  name?: string
  version: number
}

// ── Server actions ────────────────────────────────────────────────────────────

export async function apiCreateSheet(payload: {
  name: string
  sheet_w: number
  sheet_d: number
  grid_step: number
  elements: SheetElements
}): Promise<SheetCommandResult> {
  const result = await cqrsFetch<SheetCommandResult>("/api/v1/plots", {
    method: "POST",
    body: payload,
  })
  if (!result) throw new Error("Failed to create sheet")
  return result
}

export async function apiGetSheet(id: string): Promise<SheetData> {
  const result = await cqrsFetch<SheetData>(`/api/v1/plots/${id}`)
  if (!result) throw new Error(`Sheet ${id} not found`)
  return result
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
  const result = await cqrsFetch<SheetCommandResult>(`/api/v1/plots/${id}`, {
    method: "PUT",
    body: payload,
  })
  if (!result) throw new Error(`Failed to update sheet ${id}`)
  return result
}

export async function apiListSheets(): Promise<SheetListItem[]> {
  const resp = await cqrsFetch<{
    total: number
    limit: number
    offset: number
    items: SheetListItem[]
  }>("/api/v1/plots")
  return resp?.items ?? []
}

export async function apiDeleteSheet(id: string): Promise<void> {
  await cqrsFetch<void>(`/api/v1/plots/${id}`, { method: "DELETE" })
}
