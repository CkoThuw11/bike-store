// ============================================================
// FILE: src/app/app.config.ts  (REPLACE existing file)
// ============================================================
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { routes } from './app.routes';
import { bearerTokenInterceptor } from './core/interceptors/bearer-token.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([bearerTokenInterceptor])),
  ],
};