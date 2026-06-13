import type { Conversation } from "@/lib/types";

import { ChatComposer } from "./ChatComposer";
import { ChatMessageItem } from "./ChatMessageItem";
import { ErrorBanner } from "../ui/ErrorBanner";
import { LoadingSpinner } from "../ui/LoadingSpinner";

interface ActiveChatProps {
  conversation: Conversation | null;
  loading: boolean;
  error: string | null;
  onSend: (message: string) => void;
  onDismissError: () => void;
}

export function ActiveChat({
  conversation,
  loading,
  error,
  onSend,
  onDismissError,
}: ActiveChatProps) {
  return (
    <section className="flex h-full min-h-0 w-full flex-col overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--bg-panel)]">
      <header className="shrink-0 border-b border-[var(--border)] px-4 py-2.5">
        <h2 className="text-sm font-semibold text-[var(--text-primary)]">Chat</h2>
        <p className="truncate text-xs text-[var(--text-muted)]">
          {conversation?.title ?? "No conversation selected"}
        </p>
      </header>

      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-3">
        {!conversation ? (
          <p className="text-sm text-[var(--text-muted)]">
            Create or select a conversation to begin.
          </p>
        ) : conversation.messages.length === 0 ? (
          <p className="text-sm text-[var(--text-muted)]">
            Ask about inventory, stock updates, transfers, or low-stock alerts.
          </p>
        ) : (
          conversation.messages.map((message) => (
            <ChatMessageItem key={message.id} message={message} />
          ))
        )}

        {loading ? (
          <LoadingSpinner label="inventory-agent is thinking…" />
        ) : null}

        {error ? (
          <ErrorBanner
            title="Chat request failed"
            message={error}
            onDismiss={onDismissError}
          />
        ) : null}
      </div>

      <ChatComposer disabled={loading || !conversation} onSend={onSend} />
    </section>
  );
}
