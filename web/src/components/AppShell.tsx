"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";

import { resetPanelLayout } from "@/components/layout/ResponsiveLayout";
import { StatusDot } from "@/components/ui/StatusDot";
import { checkApiHealth, fetchAgentConfig, sendChatMessage } from "@/lib/api";
import { createTurnMetrics } from "@/lib/metrics";
import {
  appendTurnToConversation,
  clearConversationData,
  createConversation,
  loadActiveConversationId,
  loadConversations,
  saveActiveConversationId,
  saveConversations,
  searchConversations,
  upsertConversation,
} from "@/lib/storage";
import type { AgentConfig, ChatMessage, Conversation } from "@/lib/types";

const ResponsiveLayout = dynamic(
  () =>
    import("@/components/layout/ResponsiveLayout").then(
      (mod) => mod.ResponsiveLayout,
    ),
  {
    ssr: false,
    loading: () => (
      <div className="flex min-h-0 flex-1 items-center justify-center text-sm text-[var(--text-muted)]">
        Loading layout…
      </div>
    ),
  },
);

function findConversation(
  conversations: Conversation[],
  id: string | null,
): Conversation | null {
  if (!id) {
    return null;
  }
  return conversations.find((conversation) => conversation.id === id) ?? null;
}

export function AppShell() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [config, setConfig] = useState<AgentConfig | null>(null);
  const [apiOnline, setApiOnline] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [inventoryRefreshToken, setInventoryRefreshToken] = useState(0);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const stored = loadConversations();
    const storedActiveId = loadActiveConversationId();

    if (stored.length === 0) {
      const starter = createConversation();
      setConversations([starter]);
      setActiveId(starter.id);
    } else {
      setConversations(stored);
      const validActive =
        storedActiveId && stored.some((item) => item.id === storedActiveId)
          ? storedActiveId
          : stored[0].id;
      setActiveId(validActive);
    }

    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    saveConversations(conversations);
    if (activeId) {
      saveActiveConversationId(activeId);
    }
  }, [conversations, activeId, hydrated]);

  useEffect(() => {
    void (async () => {
      const online = await checkApiHealth();
      setApiOnline(online);
      if (online) {
        try {
          const agentConfig = await fetchAgentConfig();
          setConfig(agentConfig);
        } catch {
          setConfig(null);
        }
      }
    })();
  }, []);

  const activeConversation = useMemo(
    () => findConversation(conversations, activeId),
    [conversations, activeId],
  );

  const filteredConversations = useMemo(
    () => searchConversations(conversations, searchQuery),
    [conversations, searchQuery],
  );

  const lastTurn =
    activeConversation?.turnMetrics[activeConversation.turnMetrics.length - 1] ??
    null;

  const handleNewChat = useCallback(() => {
    const conversation = createConversation();
    setConversations((current) => [conversation, ...current]);
    setActiveId(conversation.id);
    setChatError(null);
    setSearchQuery("");
  }, []);

  const handleSelectConversation = useCallback((id: string) => {
    setActiveId(id);
    setChatError(null);
  }, []);

  const handleClearConversation = useCallback(() => {
    if (!activeId) {
      return;
    }
    setConversations((current) =>
      current.map((conversation) =>
        conversation.id === activeId
          ? clearConversationData(conversation)
          : conversation,
      ),
    );
    setChatError(null);
  }, [activeId]);

  const handleSend = useCallback(
    async (message: string) => {
      if (!activeConversation) {
        return;
      }

      setChatLoading(true);
      setChatError(null);

      try {
        const response = await sendChatMessage({
          message,
          message_history:
            activeConversation.messageHistory.length > 0
              ? activeConversation.messageHistory
              : [],
        });

        setConfig(response.config);

        const turnMetrics = createTurnMetrics(
          response.metrics,
          crypto.randomUUID(),
          new Date().toISOString(),
        );

        const updated = appendTurnToConversation(activeConversation, message, {
          events: response.events,
          message_history: response.message_history,
          metrics: turnMetrics,
          show_reply: response.show_reply,
          reply: response.reply,
        });

        setConversations((current) => upsertConversation(current, updated));

        if (response.inventory_products?.length) {
          setInventoryRefreshToken((value) => value + 1);
        }
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Unknown chat error";
        setChatError(errorMessage);

        const errorChatMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: "error",
          content: errorMessage,
          timestamp: new Date().toISOString(),
        };

        setConversations((current) =>
          current.map((conversation) =>
            conversation.id === activeConversation.id
              ? {
                  ...conversation,
                  updatedAt: new Date().toISOString(),
                  messages: [...conversation.messages, errorChatMessage],
                }
              : conversation,
          ),
        );
      } finally {
        setChatLoading(false);
      }
    },
    [activeConversation],
  );

  if (!hydrated || !activeConversation) {
    return (
      <div className="flex h-[100dvh] items-center justify-center bg-[var(--bg-app)] text-sm text-[var(--text-muted)]">
        Loading workspace…
      </div>
    );
  }

  return (
    <div className="flex h-[100dvh] flex-col overflow-hidden bg-[var(--bg-app)] text-[var(--text-primary)]">
      <header className="flex shrink-0 items-center justify-between gap-2 border-b border-[var(--border)] px-3 py-2.5 sm:gap-4 sm:px-4">
        <div className="min-w-0">
          <h1 className="truncate text-sm font-semibold">inventory-agent</h1>
          <p className="hidden text-[11px] text-[var(--text-muted)] sm:block">
            Henderson & Las Vegas inventory
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap items-center justify-end gap-2 sm:gap-3">
          <StatusDot
            online={apiOnline}
            label={apiOnline ? "API online" : "API offline"}
          />
          <StatusDot
            online={Boolean(config?.llm_configured)}
            label={config?.llm_configured ? "LLM ready" : "LLM not configured"}
          />
          <button
            type="button"
            onClick={() => {
              resetPanelLayout();
              window.location.reload();
            }}
            className="hidden min-h-11 rounded-md border border-[var(--border)] px-2 py-1 text-[11px] text-[var(--text-muted)] hover:border-[var(--accent)] hover:text-[var(--text-primary)] sm:inline-block sm:min-h-0"
            title="Reset panel sizes"
          >
            Reset layout
          </button>
        </div>
      </header>

      <ResponsiveLayout
        config={config}
        refreshToken={inventoryRefreshToken}
        conversations={filteredConversations}
        activeId={activeId}
        activeConversation={activeConversation}
        searchQuery={searchQuery}
        chatLoading={chatLoading}
        chatError={chatError}
        lastTurn={lastTurn}
        apiOnline={apiOnline}
        onSearchChange={setSearchQuery}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onClearConversation={handleClearConversation}
        onSend={(message) => void handleSend(message)}
        onDismissError={() => setChatError(null)}
      />
    </div>
  );
}
