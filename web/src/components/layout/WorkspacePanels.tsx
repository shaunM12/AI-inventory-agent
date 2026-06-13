"use client";

import { useState } from "react";

import { ActiveChat } from "@/components/chat/ActiveChat";
import { ConversationHistory } from "@/components/chat/ConversationHistory";
import { MetricsSidebar } from "@/components/metrics/MetricsSidebar";
import type { AgentConfig, Conversation, TurnMetrics } from "@/lib/types";

type WorkspaceTab = "chat" | "history" | "metrics";

const TABS: Array<{ id: WorkspaceTab; label: string }> = [
  { id: "chat", label: "Chat" },
  { id: "history", label: "History" },
  { id: "metrics", label: "Metrics" },
];

export interface WorkspacePanelProps {
  config: AgentConfig | null;
  conversations: Conversation[];
  activeId: string | null;
  activeConversation: Conversation;
  searchQuery: string;
  chatLoading: boolean;
  chatError: string | null;
  lastTurn: TurnMetrics | null;
  apiOnline: boolean;
  onSearchChange: (value: string) => void;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onClearConversation: () => void;
  onSend: (message: string) => void;
  onDismissError: () => void;
}

export function MobileWorkspaceTabs(props: WorkspacePanelProps) {
  const [tab, setTab] = useState<WorkspaceTab>("chat");

  return (
    <div className="flex h-full min-h-0 flex-col">
      <nav
        className="flex shrink-0 gap-1 border-b border-[var(--border)] px-2 py-2"
        aria-label="Workspace sections"
      >
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setTab(item.id)}
            className={`min-h-11 flex-1 rounded-md px-3 py-2 text-xs font-medium transition sm:text-sm ${
              tab === item.id
                ? "bg-[var(--accent)]/15 text-[var(--accent)] ring-1 ring-[var(--accent)]/30"
                : "text-[var(--text-muted)] hover:bg-[var(--bg-elevated)]"
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>
      <div className="min-h-0 flex-1 overflow-hidden px-1.5 py-1.5 sm:px-2 sm:py-2">
        {tab === "chat" ? (
          <ActiveChat
            conversation={props.activeConversation}
            loading={props.chatLoading}
            error={props.chatError}
            onSend={props.onSend}
            onDismissError={props.onDismissError}
          />
        ) : null}
        {tab === "history" ? (
          <ConversationHistory
            conversations={props.conversations}
            activeId={props.activeId}
            searchQuery={props.searchQuery}
            onSearchChange={props.onSearchChange}
            onSelect={props.onSelectConversation}
            onNewChat={props.onNewChat}
            onClear={props.onClearConversation}
          />
        ) : null}
        {tab === "metrics" ? (
          <MetricsSidebar
            config={props.config}
            conversation={props.activeConversation}
            apiOnline={props.apiOnline}
            lastTurn={props.lastTurn}
          />
        ) : null}
      </div>
    </div>
  );
}
