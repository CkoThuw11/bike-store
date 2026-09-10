// src/app/features/auth/login/login.component.ts
import { Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';

interface ReasonNotice {
  kind: 'info' | 'warning' | 'danger';
  text: string;
}

const REASON_NOTICES: Record<string, ReasonNotice> = {
  'admin-only': {
    kind: 'warning',
    text: 'This console is restricted to administrators. Please sign in with an admin account.',
  },
  expired: {
    kind: 'info',
    text: 'Your session has expired. Please sign in again.',
  },
  forbidden: {
    kind: 'danger',
    text: 'Your access was revoked. If this is unexpected, contact your administrator.',
  },
};

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  readonly loading = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly showPassword = signal(false);

  private readonly queryParams = toSignal(this.route.queryParamMap, {
    initialValue: this.route.snapshot.queryParamMap,
  });

  readonly reasonNotice = computed<ReasonNotice | null>(() => {
    const reason = this.queryParams().get('reason');
    return reason ? REASON_NOTICES[reason] ?? null : null;
  });

  readonly form = new FormGroup({
    email: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.email],
    }),
    password: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.minLength(6)],
    }),
  });

  togglePassword(): void {
    this.showPassword.update((v) => !v);
  }

  submit(): void {
    if (this.form.invalid || this.loading()) return;
    this.errorMessage.set(null);
    this.loading.set(true);

    const { email, password } = this.form.getRawValue();
    this.auth.login({ email, password }).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: (err) => {
        this.errorMessage.set(err?.message ?? 'Login failed. Please try again.');
        this.loading.set(false);
      },
    });
  }
}
