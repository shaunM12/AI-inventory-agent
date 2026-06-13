import type { AgentConfig, Conversation, TurnMetrics } from "@/lib/types";

interface MetricsSidebarProps {
  config: AgentConfig | null;
  conversation: Conversation | null;
  apiOnline: boolean;
  lastTurn: TurnMetrics | null;
}

function MetricRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between gap-2 py-1.5 text-[11px]">
      <span className="text-[var(--text-muted)]">{label}</span>
      <span className="font-mono tabular-nums text-[var(--text-primary)]">{value}</span>
    </div>
  );
}

export function MetricsSidebar({
  config,
  conversation,
  apiOnline,
  lastTurn,
}: MetricsSidebarProps) {
  const session = conversation?.sessionMetrics;

  return (
    <section className="flex h-full min-h-0 w-full flex-col overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--bg-panel)]">
      <header className="shrink-0 border-b border-[var(--border)] px-3 py-2.5">
        <h2 className="text-sm font-semibold text-[var(--text-primary)]">Metrics</h2>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        <div className="mb-3 rounded-md bg-[var(--bg-elevated)]/60 p-2.5">
          <p className="mb-1 text-[10px] uppercase tracking-wide text-[var(--text-muted)]">
            Model
          </p>
          <MetricRow label="Status" value={apiOnline ? "online" : "offline"} />
          <MetricRow label="Name" value={config?.model ?? "—"} />
          <MetricRow
            label="LLM"
            value={config?.llm_configured ? "ready" : "missing key"}
          />
        </div>

        {lastTurn ? (
          <div className="mb-3 rounded-md bg-[var(--bg-elevated)]/60 p-2.5">
            <p className="mb-1 text-[10px] uppercase tracking-wide text-[var(--text-muted)]">
              Last turn
            </p>
            <MetricRow label="Tokens" value={lastTurn.totalTokens} />
            <MetricRow label="Latency" value={`${lastTurn.latencyMs} ms`} />
            <MetricRow label="Tools" value={lastTurn.toolCalls} />
          </div>
        ) : null}

        {session && session.turnCount > 0 ? (
          <div className="rounded-md bg-[var(--bg-elevated)]/60 p-2.5">
            <p className="mb-1 text-[10px] uppercase tracking-wide text-[var(--text-muted)]">
              Session
            </p>
            <MetricRow label="Turns" value={session.turnCount} />
            <MetricRow label="Total tokens" value={session.totalTokens} />
            <MetricRow label="Avg latency" value={`${session.avgLatencyMs} ms`} />
          </div>
        ) : null}
      </div>
    </section>
  );
}
