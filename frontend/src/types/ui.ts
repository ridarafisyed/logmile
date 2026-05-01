export type ToastTone = "error" | "info" | "success";

export interface ToastItem {
  id: string;
  title: string;
  message: string;
  tone: ToastTone;
}
