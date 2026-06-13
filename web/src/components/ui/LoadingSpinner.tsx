interface LoadingSpinnerProps {
  label?: string;
}

export function LoadingSpinner({ label = "Loading…" }: LoadingSpinnerProps) {
  return (
    <div className="flex items-center gap-2 text-sm text-[var(--text-muted)]">
      <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--accent)]" />
      <span>{label}</span>
    </div>
  );
}
