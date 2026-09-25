/**
 * PPT-Gen Studio - Configuração & Detecção de Ambiente
 * Interceptação transparente de requisições PyWebView e Utilitários Globais
 */

// 1. Detecção de Ambiente Nativo PyWebView (Zero-Port)
const isNativeWebView = () =>
  typeof window.pywebview !== 'undefined' ||
  Boolean(window.chrome?.webview) ||
  Boolean(window.__pywebview__);

const isPyWebView = () =>
  typeof window.pywebview !== 'undefined' && Boolean(window.pywebview.api);

// Intercepta transparentemente chamadas fetch quando executando no PyWebView nativo
const _originalFetch = window.fetch;
window.fetch = async function (resource, options = {}) {
  const url = typeof resource === 'string' ? resource : (resource && resource.url ? resource.url : '');
  const isApiCall = url.includes('/api/') || url.startsWith('/api/');

  if (isApiCall && isNativeWebView()) {
    // Se a ponte pywebview.api ainda está sendo inicializada
    if (!isPyWebView()) {
      await new Promise((resolve) => {
        if (isPyWebView()) return resolve();
        const handler = () => {
          window.removeEventListener('pywebviewready', handler);
          resolve();
        };
        window.addEventListener('pywebviewready', handler);
        setTimeout(handler, 1200);
      });
    }

    if (isPyWebView()) {
      const cleanPath = url.replace(/^https?:\/\/[^\/]+/, '');
      const method = (options.method || 'GET').toUpperCase();
      let body = options.body;
      if (typeof body === 'string') {
        try {
          body = JSON.parse(body);
        } catch (_) {}
      }
      try {
        const res = await window.pywebview.api.request(cleanPath, method, body);
        if (!res || !res.ok) {
          return {
            ok: false,
            status: res?.status || 500,
            json: async () => ({ detail: res?.error || 'Erro interno' }),
            text: async () => res?.error || 'Erro interno',
            headers: { get: () => 'application/json' },
          };
        }
        return {
          ok: true,
          status: res.status || 200,
          json: async () => res.data,
          text: async () => JSON.stringify(res.data),
          headers: { get: () => 'application/json' },
        };
      } catch (err) {
        console.error('[PyWebView IPC Request Error]', err);
        return {
          ok: false,
          status: 500,
          json: async () => ({ detail: err.message || 'Erro de comunicação interna' }),
          text: async () => err.message || 'Erro de comunicação interna',
          headers: { get: () => 'application/json' },
        };
      }
    }
  }

  return _originalFetch.apply(this, arguments);
};

// 2. Resolução de endpoint da API para chamadas IPC nativas
function apiUrl(endpoint) {
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://') || endpoint.startsWith('data:')) {
    return endpoint;
  }
  return endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
}

// 3. Formatação amigável de bytes
function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}
