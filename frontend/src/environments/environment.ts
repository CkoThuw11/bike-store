export const environment = {
  production: false,
  // Empty string keeps requests relative (same-origin), so they flow through
  // the Angular dev-server proxy (proxy.conf.json) and avoid CORS entirely.
  // Use the absolute backend URL only if you want to bypass the proxy.
  apiUrl: ''
};
