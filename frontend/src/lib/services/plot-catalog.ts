"use server"

import { cqrsFetch } from "@/lib/server-api"

export interface CatalogItem {
  id: string
  name: string
  category: string
  width: number
  height: number
  depth: number
  default_color: string
  price: number | null
  description: string | null
  created_at: string
  updated_at: string
}

export interface CatalogListResponse {
  total: number
  limit: number
  offset: number
  items: CatalogItem[]
}

export async function apiListCatalogItems(params?: {
  category?: string
  q?: string
}): Promise<CatalogItem[]> {
  const search = new URLSearchParams()
  if (params?.category) search.set("category", params.category)
  if (params?.q) search.set("q", params.q)
  const qs = search.toString()
  const resp = await cqrsFetch<CatalogListResponse>(`/api/v1/catalog${qs ? `?${qs}` : ""}`)
  return resp?.items ?? []
}
