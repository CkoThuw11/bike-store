import { Injectable, signal } from '@angular/core';

export type ToastKind = 'success' | 'error' | 'info' | 'warning';

export interface ToastAction {
  label: string;
  handler: () => void;
}

export interface Toast {
  id: number;
  kind: ToastKind;
  message: string;
  action?: ToastAction;
  timeoutId?: ReturnType<typeof setTimeout>;
}

const DEFAULT_DURATION = 4000;

@Injectable({ providedIn: 'root' })
export class ToastService {
  private nextId = 1;
  readonly toasts = signal<Toast[]>([]);

  show(kind: ToastKind, message: string, action?: ToastAction, duration = DEFAULT_DURATION): number {
    const id = this.nextId++;
    const toast: Toast = { id, kind, message, action };
    if (duration > 0) {
      toast.timeoutId = setTimeout(() => this.dismiss(id), duration);
    }
    this.toasts.update((list) => [...list, toast]);
    return id;
  }

  success(message: string, action?: ToastAction): number {
    return this.show('success', message, action);
  }
  error(message: string, action?: ToastAction): number {
    return this.show('error', message, action, 6000);
  }
  info(message: string, action?: ToastAction): number {
    return this.show('info', message, action);
  }
  warning(message: string, action?: ToastAction): number {
    return this.show('warning', message, action);
  }

  dismiss(id: number): void {
    this.toasts.update((list) => {
      const found = list.find((t) => t.id === id);
      if (found?.timeoutId) clearTimeout(found.timeoutId);
      return list.filter((t) => t.id !== id);
    });
  }
}
