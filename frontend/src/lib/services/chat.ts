"use server"

import { cqrsFetch } from "@/lib/server-api"

export interface ChatMessage {
  id: string
  session_id: string
  role: "user" | "assistant" | "system"
  content: string
  model: string | null
  token_count: number | null
  created_at: string
}

export interface ChatSession {
  id: string
  title: string
  message_count: number
  last_message_preview: string | null
  updated_at: string
}

interface CqrsMessageList {
  total: number
  limit: number
  offset: number
  items: ChatMessage[]
}

interface CqrsSessionList {
  total: number
  limit: number
  offset: number
  items: ChatSession[]
}

export async function listChatSessions(): Promise<ChatSession[]> {
  const resp = await cqrsFetch<CqrsSessionList>("/api/v1/chat/sessions")
  return resp?.items ?? []
}

export async function getSessionMessages(
  sessionId: string,
  limit = 50,
  offset = 0,
): Promise<ChatMessage[]> {
  const resp = await cqrsFetch<CqrsMessageList>(
    `/api/v1/chat/sessions/${sessionId}/messages?limit=${limit}&offset=${offset}`,
  )
  return resp?.items ?? []
}

export async function saveMessage(
  sessionId: string,
  role: "user" | "assistant",
  content: string,
  model?: string,
): Promise<{ id: string }> {
  const result = await cqrsFetch<{ id: string }>("/api/v1/chat/messages", {
    method: "POST",
    body: {
      session_id: sessionId,
      role,
      content,
      model: model ?? null,
    },
  })
  if (!result) throw new Error("Failed to save message")
  return result
}
