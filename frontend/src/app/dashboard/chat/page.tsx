"use client";

import {
  Conversation,
  ConversationContent,
  ConversationDownload,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import {
  Message,
  MessageAction,
  MessageActions,
  MessageContent,
  MessageResponse,
  MessageToolbar,
} from "@/components/ai-elements/message";
import {
  PromptInput,
  PromptInputActionAddAttachments,
  PromptInputActionAddScreenshot,
  PromptInputActionMenu,
  PromptInputActionMenuContent,
  PromptInputActionMenuTrigger,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputTools,
} from "@/components/ai-elements/prompt-input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DefaultChatTransport, isTextUIPart } from "ai";
import { useChat } from "@ai-sdk/react";
import {
  AlertCircle,
  BotMessageSquare,
  Code2,
  CopyIcon,
  FileText,
  HelpCircle,
  RefreshCwIcon,
  Sparkles,
  Zap,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

const transport = new DefaultChatTransport({ api: "/api/chat" });

const SUGGESTED_PROMPTS = [
  { icon: HelpCircle, label: "What can you do?",      prompt: "help" },
  { icon: Code2,      label: "Show a code example",   prompt: "Show me a TypeScript code example" },
  { icon: FileText,   label: "Explain this interface", prompt: "What features does this chat interface have?" },
  { icon: Zap,        label: "Getting started",        prompt: "How do I connect a real AI model to this chat?" },
];

const FEATURE_BADGES = [
  "Streaming responses",
  "Markdown rendering",
  "File attachments",
  "Screenshot capture",
  "Copy & regenerate",
  "Export as Markdown",
];

// Animates text in word-by-word like a stream
function useStreamingText(text: string | null, delayMs = 35) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (!text) {
      setDisplayed("");
      setDone(false);
      return;
    }
    setDisplayed("");
    setDone(false);
    const words = text.match(/\S+\s*/g) ?? [text];
    let i = 0;
    const id = setInterval(() => {
      if (i >= words.length) {
        clearInterval(id);
        setDone(true);
        return;
      }
      setDisplayed((prev) => prev + words[i]);
      i++;
    }, delayMs);
    return () => clearInterval(id);
  }, [text, delayMs]);

  return { displayed, done };
}

export default function ChatPage() {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { messages, sendMessage, status, stop, regenerate, error, clearError } =
    useChat({ transport });

  // Build a friendly, markdown-formatted error string for streaming
  const errorText = error
    ? `> ⚠️ **Something went wrong**\n>\n> ${error.message || "An unexpected error occurred. Please try again."}`
    : null;

  const { displayed: streamedError, done: errorDone } = useStreamingText(errorText);

  const getMessageText = (message: (typeof messages)[0]) =>
    message.parts.filter(isTextUIPart).map((p) => p.text).join("");

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).then(() => toast.success("Copied to clipboard"));
  };

  const isEmpty = messages.length === 0 && !error;

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="relative flex flex-1 flex-col overflow-hidden">
        <Conversation className="flex-1">
          <ConversationContent>
            {isEmpty ? (
              /* ── Demo landing ── */
              <div className="flex flex-col items-center justify-center gap-8 py-12 px-4 text-center max-w-2xl mx-auto w-full">
                <div className="flex flex-col items-center gap-4">
                  <div className="flex size-16 items-center justify-center rounded-2xl bg-primary/10 text-primary ring-1 ring-primary/20">
                    <BotMessageSquare className="size-8" />
                  </div>
                  <div className="space-y-2">
                    <h2 className="text-2xl font-semibold tracking-tight">AI Assistant</h2>
                    <p className="text-muted-foreground text-sm leading-relaxed max-w-md">
                      A fully-featured chat interface built with{" "}
                      <span className="font-medium text-foreground">ai-elements</span> and the{" "}
                      <span className="font-medium text-foreground">Vercel AI SDK</span>.
                      Streaming, markdown, attachments — all included.
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap justify-center gap-2">
                  {FEATURE_BADGES.map((f) => (
                    <Badge key={f} variant="secondary" className="text-xs font-normal">
                      <Sparkles className="mr-1 size-3 text-primary" />
                      {f}
                    </Badge>
                  ))}
                </div>

                <div className="grid grid-cols-2 gap-2 w-full max-w-lg">
                  {SUGGESTED_PROMPTS.map(({ icon: Icon, label, prompt }) => (
                    <Button
                      key={label}
                      variant="outline"
                      className="h-auto flex-col gap-1.5 py-3 px-4 text-left items-start"
                      onClick={() => sendMessage({ text: prompt })}
                      disabled={status !== "ready"}
                    >
                      <Icon className="size-4 text-muted-foreground" />
                      <span className="text-xs font-medium leading-tight">{label}</span>
                    </Button>
                  ))}
                </div>

                <p className="text-xs text-muted-foreground">
                  Click a prompt above or type your own message below
                </p>
              </div>
            ) : (
              <>
                {/* ── Normal messages ── */}
                {messages.map((message) => (
                  <Message key={message.id} from={message.role}>
                    <MessageContent>
                      <MessageResponse
                        isAnimating={status === "streaming" && message === messages.at(-1)}
                      >
                        {getMessageText(message)}
                      </MessageResponse>
                    </MessageContent>
                    {message.role === "assistant" && (
                      <MessageToolbar>
                        <MessageActions>
                          <MessageAction
                            tooltip="Copy"
                            onClick={() => handleCopy(getMessageText(message))}
                          >
                            <CopyIcon className="size-3.5" />
                          </MessageAction>
                          <MessageAction tooltip="Regenerate" onClick={() => regenerate()}>
                            <RefreshCwIcon className="size-3.5" />
                          </MessageAction>
                        </MessageActions>
                      </MessageToolbar>
                    )}
                  </Message>
                ))}

                {/* ── Streaming error message ── */}
                {error && (
                  <Message from="assistant">
                    <MessageContent className="border border-destructive/30 bg-destructive/5 text-destructive dark:text-red-400">
                      <div className="flex items-start gap-2">
                        <AlertCircle className="mt-0.5 size-4 shrink-0 text-destructive dark:text-red-400" />
                        <MessageResponse isAnimating={!errorDone}>
                          {streamedError}
                        </MessageResponse>
                      </div>
                    </MessageContent>
                    {errorDone && (
                      <MessageToolbar>
                        <MessageActions>
                          <MessageAction
                            tooltip="Retry"
                            onClick={() => { clearError(); regenerate(); }}
                          >
                            <RefreshCwIcon className="size-3.5" />
                          </MessageAction>
                        </MessageActions>
                      </MessageToolbar>
                    )}
                  </Message>
                )}
              </>
            )}
          </ConversationContent>

          <ConversationScrollButton />

          {messages.length > 0 && (
            <ConversationDownload messages={messages} filename="chat-conversation.md" />
          )}
        </Conversation>
      </div>

      {/* Input area */}
      <div className="border-t bg-background p-4">
        <PromptInput
          onSubmit={({ text }) => {
            if (!text.trim()) return;
            if (error) clearError();
            sendMessage({ text });
          }}
          className="max-w-2xl mx-auto"
        >
          <PromptInputTextarea
            ref={textareaRef}
            placeholder="Ask anything… (Enter to send, Shift+Enter for new line)"
          />
          <PromptInputFooter>
            <PromptInputTools>
              <PromptInputActionMenu>
                <PromptInputActionMenuTrigger tooltip="Attach files or screenshot" />
                <PromptInputActionMenuContent>
                  <PromptInputActionAddAttachments />
                  <PromptInputActionAddScreenshot />
                </PromptInputActionMenuContent>
              </PromptInputActionMenu>
            </PromptInputTools>
            <PromptInputSubmit status={status} onStop={stop} />
          </PromptInputFooter>
        </PromptInput>
        <p className="mt-2 text-center text-xs text-muted-foreground">
          Demo mode — no API key required. Responses are simulated.
        </p>
      </div>
    </div>
  );
}
