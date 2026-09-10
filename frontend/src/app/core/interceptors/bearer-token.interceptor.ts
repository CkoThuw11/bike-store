// ============================================================
// FILE: src/app/core/interceptors/bearer-token.interceptor.ts
// ============================================================
import {
  HttpInterceptorFn,
  HttpRequest,
  HttpHandlerFn,
  HttpErrorResponse,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../auth/auth.service';

const PUBLIC_PATHS = ['/auth/login', '/auth/register'];

function isPublicPath(url: string): boolean {
  return PUBLIC_PATHS.some((p) => url.includes(p));
}

function withBearer(req: HttpRequest<unknown>, token: string): HttpRequest<unknown> {
  return req.clone({
    setHeaders: { Authorization: `Bearer ${token}` },
  });
}

export const bearerTokenInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
) => {
  const auth = inject(AuthService);

  // Skip public auth endpoints
  if (isPublicPath(req.url)) {
    return next(req);
  }

  const token = auth.accessToken();
  const outgoing = token ? withBearer(req, token) : req;

  return next(outgoing).pipe(
    catchError((err) => {
      if (err instanceof HttpErrorResponse && err.status === 401 && token) {
        return auth.refresh().pipe(
          switchMap((res) => {
            const retried = withBearer(req, res.token_pair.access_token);
            return next(retried);
          }),
          catchError((refreshErr) => throwError(() => refreshErr))
        );
      }
      if (err instanceof HttpErrorResponse && err.status === 403 && token) {
        auth.forceForbiddenLogout();
      }
      return throwError(() => err);
    })
  );
};