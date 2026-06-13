interface ChatComposerProps {
  disabled: boolean;
  onSend: (message: string) => void;
}

export function ChatComposer({ disabled, onSend }: ChatComposerProps) {
  return (
    <form
      className="border-t border-[var(--border)] p-3"
      onSubmit={(event) => {
        event.preventDefault();
        const form = event.currentTarget;
        const input = form.elements.namedItem("message") as HTMLTextAreaElement;
        const value = input.value.trim();
        if (!value || disabled) {
          return;
        }
        onSend(value);
        input.value = "";
      }}
    >
      <div className="flex flex-col gap-2 sm:flex-row">
        <textarea
          name="message"
          rows={2}
          disabled={disabled}
          placeholder={
            disabled
              ? "Waiting for inventory-agent…"
              : "Ask about inventory…"
          }
          className="min-h-[52px] flex-1 resize-none rounded-md border border-[var(--border)] bg-[var(--bg-app)] px-3 py-2.5 text-base text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--accent)] disabled:opacity-60 sm:text-sm"
        />
        <button
          type="submit"
          disabled={disabled}
          className="min-h-11 shrink-0 rounded-md border border-[var(--accent)] bg-[var(--accent)]/15 px-4 py-2.5 text-sm font-medium text-[var(--accent)] hover:bg-[var(--accent)]/25 disabled:cursor-not-allowed disabled:opacity-50 sm:self-end"
        >
          Send
        </button>
      </div>
    </form>
  );
}
