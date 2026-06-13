import type { Conversation } from "@/lib/types";

interface ConversationHistoryProps {
  conversations: Conversation[];
  activeId: string | null;
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onClear: () => void;
}

export function ConversationHistory({
  conversations,
  activeId,
  searchQuery,
  onSearchChange,
  onSelect,
  onNewChat,
  onClear,
}: ConversationHistoryProps) {
  return (
    <section className="flex h-full min-h-0 w-full flex-col overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--bg-panel)]">
      <header className="shrink-0 border-b border-[var(--border)] p-3">
        <div className="mb-2 flex items-center justify-between gap-2">
          <h2 className="text-sm font-semibold text-[var(--text-primary)]">History</h2>
          <button
            type="button"
            onClick={onNewChat}
            className="rounded-md border border-[var(--border)] px-2 py-1 text-[11px] text-[var(--accent)] hover:border-[var(--accent)]"
          >
            New
          </button>
        </div>
        <input
          type="search"
          value={searchQuery}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search…"
          className="w-full rounded-md border border-[var(--border)] bg-[var(--bg-app)] px-2 py-1.5 text-xs text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--accent)]"
        />
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto p-2">
        {conversations.length === 0 ? (
          <p className="px-2 py-3 text-xs text-[var(--text-muted)]">No conversations yet.</p>
        ) : (
          <ul className="space-y-1">
            {conversations.map((conversation) => {
              const active = conversation.id === activeId;
              const preview =
                conversation.messages.find((message) => message.role === "user")
                  ?.content ?? "Empty conversation";
              return (
                <li key={conversation.id}>
                  <button
                    type="button"
                    onClick={() => onSelect(conversation.id)}
                    className={`w-full rounded-md px-2 py-2 text-left transition ${
                      active
                        ? "bg-[var(--accent)]/10 ring-1 ring-[var(--accent)]/40"
                        : "hover:bg-[var(--bg-elevated)]"
                    }`}
                  >
                    <p className="truncate text-xs font-medium text-[var(--text-primary)]">
                      {conversation.title}
                    </p>
                    <p className="mt-0.5 truncate text-[10px] text-[var(--text-muted)]">
                      {preview}
                    </p>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <footer className="shrink-0 border-t border-[var(--border)] p-2">
        <button
          type="button"
          onClick={onClear}
          disabled={!activeId}
          className="w-full rounded-md px-2 py-1.5 text-[11px] text-[var(--danger)] hover:bg-[var(--danger)]/10 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Clear conversation
        </button>
      </footer>
    </section>
  );
}
