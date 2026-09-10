// ============================================================
// FILE: src/app/core/auth/auth.service.ts
// ============================================================
import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, throwError, switchMap } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  UserDto,
  LoginCommand,
  RegisterCommand,
  LoginResponse,
  RegisterResponse,
  RefreshResponse,
  AppError,
} from '../../shared/types';
import { normalizeError, friendlyMessage } from '../api/api-error';

const SESSION_USER_KEY = 'vs_user';
const SESSION_TOKEN_KEY = 'vs_token';
const ADMIN_ONLY_ERROR: AppError = {
  status: 403,
  code: 'ADMIN_ONLY',
  message: 'Only admin accounts can access this dashboard.',
  fieldErrors: {},
  raw: null,
};

function isAppError(err: unknown): err is AppError {
  return !!err && typeof err === 'object' && 'code' in err && 'fieldErrors' in err;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly base = environment.apiUrl;

  // ── Signals ──────────────────────────────────────────────
  readonly user = signal<UserDto | null>(this.loadUser());
  readonly accessToken = signal<string | null>(this.loadToken());

  readonly isAuthenticated = computed(() => !!this.accessToken());
  readonly isAdmin = computed(() => this.user()?.role === 'ADMIN');

  // ── Persistence helpers ───────────────────────────────────
  private loadUser(): UserDto | null {
    try {
      const raw = sessionStorage.getItem(SESSION_USER_KEY);
      return raw ? (JSON.parse(raw) as UserDto) : null;
    } catch {
      return null;
    }
  }

  private loadToken(): string | null {
    return sessionStorage.getItem(SESSION_TOKEN_KEY);
  }

  private persist(user: UserDto, token: string): void {
    sessionStorage.setItem(SESSION_USER_KEY, JSON.stringify(user));
    sessionStorage.setItem(SESSION_TOKEN_KEY, token);
    this.user.set(user);
    this.accessToken.set(token);
  }

  clearSession(): void {
    sessionStorage.removeItem(SESSION_USER_KEY);
    sessionStorage.removeItem(SESSION_TOKEN_KEY);
    this.user.set(null);
    this.accessToken.set(null);
  }

  // ── Auth operations ───────────────────────────────────────
  login(command: LoginCommand): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.base}/auth/login`, command)
      .pipe(
        tap((res) => {
          if (res.user.role !== 'ADMIN') {
            this.clearSession();
            throw ADMIN_ONLY_ERROR;
          }
          this.persist(res.user, res.token_pair.access_token);
        }),
        catchError((err) => {
          const appErr = isAppError(err) ? err : normalizeError(err);
          return throwError(() => ({
            ...appErr,
            message: friendlyMessage(appErr.code, appErr.message),
          }));
        })
      );
  }

  register(command: RegisterCommand): Observable<LoginResponse> {
    return this.http
      .post<RegisterResponse>(`${this.base}/auth/register`, command)
      .pipe(
        switchMap(() => this.login({ email: command.email, password: command.password })),
        catchError((err) => {
          const appErr = normalizeError(err);
          return throwError(() => ({
            ...appErr,
            message: friendlyMessage(appErr.code, appErr.message),
          }));
        })
      );
  }

  refresh(): Observable<RefreshResponse> {
    return this.http
      .post<RefreshResponse>(`${this.base}/auth/refresh`, {}, { withCredentials: true })
      .pipe(
        tap((res) => {
          this.accessToken.set(res.token_pair.access_token);
          sessionStorage.setItem(SESSION_TOKEN_KEY, res.token_pair.access_token);
        }),
        catchError((err) => {
          this.clearSession();
          this.router.navigate(['/login'], { queryParams: { reason: 'expired' } });
          return throwError(() => normalizeError(err));
        })
      );
  }

  forceForbiddenLogout(): void {
    this.clearSession();
    this.router.navigate(['/login'], { queryParams: { reason: 'forbidden' } });
  }

  logout(): void {
    this.http
      .post(`${this.base}/auth/logout`, {}, { withCredentials: true })
      .subscribe({
        complete: () => {
          this.clearSession();
          this.router.navigate(['/login']);
        },
        error: () => {
          this.clearSession();
          this.router.navigate(['/login']);
        },
      });
  }
}
