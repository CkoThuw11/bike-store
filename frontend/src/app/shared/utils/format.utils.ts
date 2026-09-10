// ============================================================
// FILE: src/app/shared/utils/format.utils.ts
// ============================================================

/**
 * Normalize price/discount from backend — may arrive as string or number.
 */
export function parseDecimal(value: string | number | null | undefined): number {
  if (value === null || value === undefined) return 0;
  return parseFloat(String(value));
}

/**
 * Format a price value as USD currency string.
 */
export function formatPrice(value: string | number | null | undefined): string {
  const num = parseDecimal(value);
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(num);
}

/**
 * Format an ISO datetime string to a readable local date.
 */
export function formatDate(value: string | null | undefined): string {
  if (!value) return '—';
  const d = new Date(value);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format an ISO datetime string to readable local date + time.
 */
export function formatDateTime(value: string | null | undefined): string {
  if (!value) return '—';
  const d = new Date(value);
  if (isNaN(d.getTime())) return '—';
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Get initials from a full name string (up to 2 characters).
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0].toUpperCase())
    .join('');
}

/**
 * Return a time-of-day greeting string.
 */
export function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}