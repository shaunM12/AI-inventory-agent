interface ErrorBannerProps {
  title?: string;
  message: string;
  onDismiss?: () => void;
}

export function ErrorBanner({
  title = "Something went wrong",
  message,
  onDismiss,
}: ErrorBannerProps) {
  return (
    <div className="rounded-md border border-[var(--danger)]/40 bg-[var(--danger)]/10 px-3 py-2 text-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-medium text-[var(--danger)]">{title}</p>
          <p className="mt-1 whitespace-pre-wrap text-[var(--text-primary)]">{message}</p>
        </div>
        {onDismiss ? (
          <button
            type="button"
            onClick={onDismiss}
            className="shrink-0 text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)]"
          >
            Dismiss
          </button>
        ) : null}
      </div>
    </div>
  );
}
