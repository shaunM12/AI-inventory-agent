interface ResizeHandleProps {
  direction: "horizontal" | "vertical";
  label: string;
}

export function ResizeHandle({ direction, label }: ResizeHandleProps) {
  return (
    <div
      className={`group flex touch-none items-center justify-center bg-[var(--bg-app)] transition-colors hover:bg-[var(--accent)]/10 active:bg-[var(--accent)]/20 ${
        direction === "horizontal"
          ? "h-3 w-full cursor-row-resize sm:h-2.5"
          : "h-full w-3 cursor-col-resize sm:w-2.5"
      }`}
      aria-label={label}
      title={label}
    >
      <span
        data-resize-handle-indicator
        className={`rounded-full bg-[var(--border)] transition-colors group-hover:bg-[var(--accent)] group-active:bg-[var(--accent)] ${
          direction === "horizontal" ? "h-1 w-12" : "h-12 w-1"
        }`}
      />
    </div>
  );
}
