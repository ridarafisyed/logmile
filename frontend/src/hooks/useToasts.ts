import { useEffect, useRef, useState } from "react";

import type { ToastItem, ToastTone } from "../types/ui";

const TOAST_DURATION_MS = 6000;

interface ToastInput {
  title: string;
  message: string;
  tone?: ToastTone;
}

export function useToasts() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const timeoutIdsRef = useRef<Map<string, number>>(new Map());

  useEffect(() => {
    return () => {
      timeoutIdsRef.current.forEach((timeoutId) => {
        window.clearTimeout(timeoutId);
      });
      timeoutIdsRef.current.clear();
    };
  }, []);

  function dismissToast(toastId: string) {
    const timeoutId = timeoutIdsRef.current.get(toastId);
    if (timeoutId !== undefined) {
      window.clearTimeout(timeoutId);
      timeoutIdsRef.current.delete(toastId);
    }

    setToasts((previousToasts) =>
      previousToasts.filter((toast) => toast.id !== toastId),
    );
  }

  function pushToast({ title, message, tone = "info" }: ToastInput) {
    const toastId = crypto.randomUUID();
    setToasts((previousToasts) => [
      ...previousToasts,
      { id: toastId, title, message, tone },
    ]);

    const timeoutId = window.setTimeout(() => {
      dismissToast(toastId);
    }, TOAST_DURATION_MS);
    timeoutIdsRef.current.set(toastId, timeoutId);
  }

  return {
    toasts,
    pushToast,
    dismissToast,
  };
}
