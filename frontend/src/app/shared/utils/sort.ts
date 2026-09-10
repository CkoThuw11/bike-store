export type SortDirection = 'asc' | 'desc' | null;

export interface SortState {
  key: string | null;
  direction: SortDirection;
}

export function cycleSort(current: SortState, key: string): SortState {
  if (current.key !== key) return { key, direction: 'asc' };
  if (current.direction === 'asc') return { key, direction: 'desc' };
  return { key: null, direction: null };
}

export function compareValues(a: unknown, b: unknown): number {
  if (a == null && b == null) return 0;
  if (a == null) return -1;
  if (b == null) return 1;
  if (typeof a === 'number' && typeof b === 'number') return a - b;
  return String(a).localeCompare(String(b), undefined, { numeric: true, sensitivity: 'base' });
}

export function sortRows<T>(rows: T[], state: SortState, getValue: (row: T, key: string) => unknown): T[] {
  if (!state.key || !state.direction) return rows;
  const sorted = [...rows].sort((a, b) =>
    compareValues(getValue(a, state.key!), getValue(b, state.key!))
  );
  return state.direction === 'desc' ? sorted.reverse() : sorted;
}
