import type { ChatMessage } from "@/lib/types";

interface ChatMessageItemProps {
  message: ChatMessage;
}

function roleStyles(role: ChatMessage["role"]) {
  switch (role) {
    case "user":
      return "border-[var(--user)]/25 bg-[var(--user)]/8";
    case "agent":
      return "border-[var(--agent)]/25 bg-[var(--agent)]/8";
    case "tool":
      return "border-[var(--tool)]/25 bg-[var(--tool)]/8";
    case "error":
      return "border-[var(--danger)]/35 bg-[var(--danger)]/10";
    default:
      return "border-[var(--border)] bg-[var(--bg-elevated)]";
  }
}

function roleLabel(role: ChatMessage["role"]) {
  switch (role) {
    case "user":
      return "You";
    case "agent":
      return "inventory-agent";
    case "tool":
      return "Action";
    case "error":
      return "Error";
    default:
      return role;
  }
}

function TaskStatusBadge({ status }: { status: "completed" | "failed" }) {
  const completed = status === "completed";
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide ${
        completed
          ? "bg-[var(--success)]/15 text-[var(--success)]"
          : "bg-[var(--danger)]/15 text-[var(--danger)]"
      }`}
    >
      {completed ? "Completed" : "Failed"}
    </span>
  );
}

export function ChatMessageItem({ message }: ChatMessageItemProps) {
  return (
    <article
      className={`rounded-lg border px-4 py-3 ${roleStyles(message.role)} ${
        message.role === "user" ? "ml-8" : message.role === "agent" ? "mr-4" : ""
      }`}
    >
      <header className="mb-2 flex items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-[var(--text-primary)]">
            {roleLabel(message.role)}
          </span>
          {message.toolCall && message.role === "tool" ? (
            <span className="rounded-full bg-[var(--bg-app)] px-2 py-0.5 text-[10px] text-[var(--tool)]">
              {message.toolCall.replace(/_/g, " ")}
            </span>
          ) : null}
          {message.role === "tool" && message.taskStatus ? (
            <TaskStatusBadge status={message.taskStatus} />
          ) : null}
        </div>
        <time className="shrink-0 text-[10px] text-[var(--text-muted)]">
          {new Date(message.timestamp).toLocaleTimeString()}
        </time>
      </header>

      <p className="whitespace-pre-wrap text-sm leading-relaxed text-[var(--text-primary)]">
        {message.content}
      </p>
    </article>
  );
}
