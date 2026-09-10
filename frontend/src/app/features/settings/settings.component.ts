import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { AuthService } from '../../core/auth/auth.service';
import { getInitials } from '../../shared/utils/format.utils';

@Component({
  selector: 'app-settings',
  standalone: true,
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettingsComponent {
  private readonly auth = inject(AuthService);

  readonly user = this.auth.user;
  readonly confirming = signal(false);

  readonly initials = computed(() => {
    const u = this.user();
    return u ? getInitials(u.fullname) : '?';
  });

  startLogout(): void {
    this.confirming.set(true);
  }

  cancelLogout(): void {
    this.confirming.set(false);
  }

  confirmLogout(): void {
    this.auth.logout();
  }
}
