import { TOAST_TONE_STYLES } from "../../constants/ui";
import type { ToastItem } from "../../types/ui";
import { cn } from "../../utils/cn";

interface ToastViewportProps {
  onDismiss: (toastId: string) => void;
  toasts: ToastItem[];
}

export default function ToastViewport({
  onDismiss,
  toasts,
}: ToastViewportProps) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div
      aria-live="polite"
      className="fixed right-4 top-4 z-40 grid w-[min(24rem,calc(100vw-2rem))] gap-3"
    >
      {toasts.map((toast) => (
        <div
          className={cn(
            "flex items-start gap-4 rounded-2xl border p-4 shadow-floating backdrop-blur-xl",
            TOAST_TONE_STYLES[toast.tone],
          )}
          key={toast.id}
          role="status"
        >
          <div className="flex-1 space-y-1">
            <strong className="block text-sm font-semibold text-ink">
              {toast.title}
            </strong>
            <p className="m-0 text-sm leading-6 text-slate-600">{toast.message}</p>
          </div>

          <button
            aria-label="Dismiss notification"
            className="rounded-full p-1 text-lg leading-none text-slate-500 transition hover:bg-ink/5 hover:text-ink"
            onClick={() => onDismiss(toast.id)}
            type="button"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
