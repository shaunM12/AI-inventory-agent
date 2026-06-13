interface StatusDotProps {
  online: boolean;
  label: string;
}

export function StatusDot({ online, label }: StatusDotProps) {
  return (
    <span className="inline-flex items-center gap-2 text-xs text-[var(--text-muted)]">
      <span
        className={`h-2 w-2 rounded-full ${online ? "bg-[var(--success)]" : "bg-[var(--danger)]"}`}
        aria-hidden
      />
      {label}
    </span>
  );
}
