import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ToastService } from './toast.service';

@Component({
  selector: 'app-toast-region',
  standalone: true,
  templateUrl: './toast-region.component.html',
  styleUrl: './toast-region.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToastRegionComponent {
  private readonly svc = inject(ToastService);
  readonly toasts = this.svc.toasts;

  dismiss(id: number): void {
    this.svc.dismiss(id);
  }

  invokeAction(id: number): void {
    const t = this.toasts().find((x) => x.id === id);
    if (t?.action) {
      t.action.handler();
      this.dismiss(id);
    }
  }
}
