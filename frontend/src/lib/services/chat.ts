import { api } from "@/lib/api"

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
  const resp = await api.get<CqrsSessionList>("/v1/chat/sessions")
  return resp.items
}

export async function getSessionMessages(
  sessionId: string,
  limit = 50,
  offset = 0,
): Promise<ChatMessage[]> {
  const resp = await api.get<CqrsMessageList>(
    `/v1/chat/sessions/${sessionId}/messages?limit=${limit}&offset=${offset}`,
  )
  return resp.items
}

export async function saveMessage(
  sessionId: string,
  role: "user" | "assistant",
  content: string,
  model?: string,
): Promise<{ id: string }> {
  return api.post<{ id: string }>("/v1/chat/messages", {
    session_id: sessionId,
    role,
    content,
    model: model ?? null,
  })
}
