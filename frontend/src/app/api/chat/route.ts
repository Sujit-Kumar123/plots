import {
  createUIMessageStream,
  createUIMessageStreamResponse,
  isTextUIPart,
  UIMessage,
} from "ai";

export const maxDuration = 30;

const DEMO_RESPONSES: Record<string, string> = {
  default: `I'm a **demo AI assistant** running entirely in your browser — no API key required.

Here's what this chat interface supports:

- **Streaming responses** — text arrives token by token, just like a real model
- **Markdown rendering** — *italic*, **bold**, \`inline code\`, and fenced code blocks
- **File attachments** — attach images or files via the **+** button
- **Screenshot capture** — grab your screen directly from the toolbar
- **Copy & regenerate** — action buttons on every assistant message
- **Conversation download** — export the full chat as Markdown
- **Sticky scroll** — the view follows new messages automatically

To connect a real LLM, add \`OPENAI_API_KEY\` to your \`.env\` and swap in the OpenAI route.`,

  hello: `Hello! I'm your **demo AI assistant**.\n\nI'm here to showcase the chat UI. Ask me anything and I'll return a nicely formatted demo response.`,

  help: `Here are a few things you can try:\n\n1. Type a message and press **Enter** to send\n2. Use **Shift+Enter** for a new line\n3. Click **+** to attach a file or capture a screenshot\n4. Hover an assistant message to see **copy** and **regenerate** buttons\n5. Click the **download** icon (top-right) to export the conversation as Markdown`,

  code: `Here's a quick TypeScript example using \`@ai-sdk/react\`:\n\n\`\`\`typescript\nimport { useChat } from "@ai-sdk/react";\nimport { DefaultChatTransport } from "ai";\n\nconst transport = new DefaultChatTransport({ api: "/api/chat" });\n\nexport default function Chat() {\n  const { messages, sendMessage, status } = useChat({ transport });\n\n  return (\n    <div>\n      {messages.map(m => (\n        <p key={m.id}>\n          <b>{m.role}:</b>{" "}\n          {m.parts.filter(p => p.type === "text").map(p => p.text).join("")}\n        </p>\n      ))}\n      <button\n        onClick={() => sendMessage({ text: "Hello!" })}\n        disabled={status !== "idle"}\n      >\n        Send\n      </button>\n    </div>\n  );\n}\n\`\`\``,
};

function pickResponse(messages: UIMessage[]): string {
  const last = messages.at(-1);
  if (!last) return DEMO_RESPONSES.default;
  const text = last.parts
    .filter(isTextUIPart)
    .map((p) => p.text)
    .join("")
    .toLowerCase();
  if (/\b(hi|hello|hey)\b/.test(text)) return DEMO_RESPONSES.hello;
  if (/\b(help|what can|how to)\b/.test(text)) return DEMO_RESPONSES.help;
  if (/\b(code|example|typescript|javascript|snippet)\b/.test(text))
    return DEMO_RESPONSES.code;
  return DEMO_RESPONSES.default;
}

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();
  const fullText = pickResponse(messages);
  // Split on whitespace boundaries so spaces are preserved between words
  const chunks = fullText.match(/\S+\s*/g) ?? [fullText];

  const stream = createUIMessageStream({
    execute: async ({ writer }) => {
      writer.write({ type: "start-step" });
      writer.write({ type: "text-start", id: "t0" });
      for (const chunk of chunks) {
        writer.write({ type: "text-delta", id: "t0", delta: chunk });
        await new Promise((r) => setTimeout(r, 30));
      }
      writer.write({ type: "text-end", id: "t0" });
    },
    onError: (error) =>
      error instanceof Error ? error.message : "An unexpected error occurred.",
  });

  return createUIMessageStreamResponse({ stream });
}
