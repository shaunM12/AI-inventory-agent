import { EMPTY_SESSION_METRICS, STORAGE_KEYS } from "./constants";
import { aggregateSessionMetrics } from "./metrics";
import { getToolTaskSummary } from "./toolTaskStatus";
import type { ChatMessage, Conversation, TurnMetrics } from "./types";

function newId(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function normalizeToolMessage(message: ChatMessage): ChatMessage {
  if (message.role !== "tool" || !message.toolCall) {
    return message;
  }

  const raw = message.content.trim();
  if (!raw.startsWith("[") && !raw.startsWith("{")) {
    return message;
  }

  const { status, summary } = getToolTaskSummary(raw, message.toolCall);
  return {
    ...message,
    content: summary,
    taskStatus: status,
  };
}

function sanitizeMessages(messages: ChatMessage[]): ChatMessage[] {
  return messages
    .filter((message) => !(message.role === "agent" && message.toolCall))
    .map(normalizeToolMessage);
}

export function createConversation(title = "New chat"): Conversation {
  const now = new Date().toISOString();
  return {
    id: newId(),
    title,
    createdAt: now,
    updatedAt: now,
    messages: [],
    messageHistory: [],
    sessionMetrics: { ...EMPTY_SESSION_METRICS },
    turnMetrics: [],
  };
}

export function loadConversations(): Conversation[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.conversations);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as Conversation[];
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.map((conversation) => ({
      ...conversation,
      messages: sanitizeMessages(conversation.messages),
    }));
  } catch {
    return [];
  }
}

export function saveConversations(conversations: Conversation[]): void {
  localStorage.setItem(STORAGE_KEYS.conversations, JSON.stringify(conversations));
}

export function loadActiveConversationId(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(STORAGE_KEYS.activeId);
}

export function saveActiveConversationId(id: string): void {
  localStorage.setItem(STORAGE_KEYS.activeId, id);
}

export function upsertConversation(
  conversations: Conversation[],
  conversation: Conversation,
): Conversation[] {
  const index = conversations.findIndex((item) => item.id === conversation.id);
  if (index === -1) {
    return [conversation, ...conversations];
  }
  const next = [...conversations];
  next[index] = conversation;
  return next;
}

export function searchConversations(
  conversations: Conversation[],
  query: string,
): Conversation[] {
  const needle = query.trim().toLowerCase();
  if (!needle) {
    return conversations;
  }
  return conversations.filter((conversation) => {
    if (conversation.title.toLowerCase().includes(needle)) {
      return true;
    }
    return conversation.messages.some((message) =>
      message.content.toLowerCase().includes(needle),
    );
  });
}

export function clearConversationData(conversation: Conversation): Conversation {
  return {
    ...conversation,
    updatedAt: new Date().toISOString(),
    messages: [],
    messageHistory: [],
    sessionMetrics: { ...EMPTY_SESSION_METRICS },
    turnMetrics: [],
  };
}

export function buildTitleFromMessage(message: string): string {
  const trimmed = message.trim();
  if (!trimmed) {
    return "New chat";
  }
  return trimmed.length > 48 ? `${trimmed.slice(0, 48)}…` : trimmed;
}

export function eventsToMessages(
  events: Array<{
    actor: string;
    message: string;
    tool_call: string;
    timestamp: string;
  }>,
  showReply: boolean,
  reply: string,
): ChatMessage[] {
  const messages: ChatMessage[] = [];

  for (const event of events) {
    if (event.actor === "user") {
      messages.push({
        id: newId(),
        role: "user",
        content: event.message,
        timestamp: event.timestamp,
      });
      continue;
    }

    if (event.actor === "agent" && event.tool_call) {
      continue;
    }

    if (event.actor === "tool") {
      const { status, summary } = getToolTaskSummary(
        event.message,
        event.tool_call,
      );
      messages.push({
        id: newId(),
        role: "tool",
        content: summary,
        toolCall: event.tool_call,
        timestamp: event.timestamp,
        taskStatus: status,
      });
      continue;
    }

    if (event.actor === "agent" && !event.tool_call) {
      if (showReply || !reply) {
        messages.push({
          id: newId(),
          role: "agent",
          content: event.message,
          timestamp: event.timestamp,
        });
      }
    }
  }

  return messages;
}

export function appendTurnToConversation(
  conversation: Conversation,
  userMessage: string,
  response: {
    events: Array<{
      actor: string;
      message: string;
      tool_call: string;
      timestamp: string;
    }>;
    message_history: Record<string, unknown>[];
    metrics: TurnMetrics;
    show_reply: boolean;
    reply: string;
  },
): Conversation {
  const newMessages = eventsToMessages(
    response.events,
    response.show_reply,
    response.reply,
  );
  const turnMetrics = [...conversation.turnMetrics, response.metrics];

  return {
    ...conversation,
    title:
      conversation.messages.length === 0
        ? buildTitleFromMessage(userMessage)
        : conversation.title,
    updatedAt: new Date().toISOString(),
    messages: [...conversation.messages, ...newMessages],
    messageHistory: response.message_history,
    turnMetrics,
    sessionMetrics: aggregateSessionMetrics(turnMetrics),
  };
}
