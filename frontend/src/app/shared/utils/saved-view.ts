const NAMESPACE = 'vs:view:';

export function loadSavedView<T>(key: string, fallback: T): T {
  try {
    const raw = sessionStorage.getItem(NAMESPACE + key);
    if (!raw) return fallback;
    return { ...fallback, ...(JSON.parse(raw) as T) };
  } catch {
    return fallback;
  }
}

export function persistSavedView(key: string, view: unknown): void {
  try {
    sessionStorage.setItem(NAMESPACE + key, JSON.stringify(view));
  } catch {
    /* sessionStorage may be unavailable; non-fatal */
  }
}

export function clearSavedView(key: string): void {
  try {
    sessionStorage.removeItem(NAMESPACE + key);
  } catch {
    /* non-fatal */
  }
}
