// ============================================================
// FILE: src/app/core/api/api-error.ts
// ============================================================
import { HttpErrorResponse } from '@angular/common/http';
import { AppError } from '../../shared/types';

export function normalizeError(err: unknown): AppError {
  if (err instanceof HttpErrorResponse) {
    const body = err.error;

    // Backend domain error shape: { status, error, message, meta? }
    if (body && typeof body === 'object' && 'error' in body) {
      return {
        status: body['status'] ?? err.status,
        code: body['error'] ?? 'UNKNOWN_ERROR',
        message: body['message'] ?? 'An unexpected error occurred.',
        fieldErrors: {},
        raw: body,
      };
    }

    // FastAPI validation error shape: { detail: [...] }
    if (body && typeof body === 'object' && 'detail' in body) {
      const fieldErrors: Record<string, string> = {};
      if (Array.isArray(body['detail'])) {
        for (const item of body['detail']) {
          const field = item?.loc?.slice(-1)[0] ?? 'field';
          fieldErrors[field] = item?.msg ?? 'Invalid value';
        }
      }
      return {
        status: err.status,
        code: 'REQUEST_VALIDATION_ERROR',
        message: 'Please check the fields below.',
        fieldErrors,
        raw: body,
      };
    }

    return {
      status: err.status,
      code: 'HTTP_ERROR',
      message: err.message || 'Network error.',
      fieldErrors: {},
      raw: err,
    };
  }

  return {
    status: 0,
    code: 'UNKNOWN_ERROR',
    message: 'An unexpected error occurred.',
    fieldErrors: {},
    raw: err,
  };
}

/**
 * Map backend error codes to friendly UI messages.
 */
export function friendlyMessage(code: string, fallback: string): string {
  const map: Record<string, string> = {
    INVALID_CREDENTIALS: 'Incorrect email or password.',
    ACCOUNT_INACTIVE: 'This account has been deactivated.',
    EMAIL_ALREADY_EXISTS: 'An account with this email already exists.',
    ENTITY_ALREADY_EXISTS: 'This record already exists.',
    ENTITY_NOT_FOUND: 'The requested record was not found.',
    FORBIDDEN: 'You do not have permission to perform this action.',
    ADMIN_ONLY: 'Only admin accounts can access this dashboard.',
    TOKEN_EXPIRED: 'Your session has expired. Please log in again.',
    TOKEN_INVALID: 'Invalid session. Please log in again.',
    SECURITY_BREACH: 'Security issue detected. Please log in again.',
  };
  return map[code] ?? fallback;
}
