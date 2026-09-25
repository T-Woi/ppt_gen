/**
 * PPT-Gen Studio - Master Script Loader (Compatibilidade Retroativa)
 * Carrega em ordem síncrona a arquitetura modular segmentada se invocado diretamente
 */
(function () {
  if (window._pptGenLoaded) return;

  const scriptFiles = [
    'js/config.js',
    'js/state.js',
    'js/components/modals.js',
    'js/components/slide-card.js',
    'js/components/lightbox.js',
    'js/pages/upload.js',
    'js/pages/editor.js',
    'js/app.js',
  ];

  // Se os scripts modulares já estão presentes no DOM, não faz carregamento redundante
  const existingScripts = Array.from(document.querySelectorAll('script')).map((s) => s.getAttribute('src') || '');
  if (existingScripts.some((src) => src.includes('js/app.js') || src.includes('js/config.js'))) {
    window._pptGenLoaded = true;
    return;
  }

  window._pptGenLoaded = true;

  function loadNext(index) {
    if (index >= scriptFiles.length) return;
    const s = document.createElement('script');
    s.src = scriptFiles[index];
    s.onload = () => loadNext(index + 1);
    s.onerror = (e) => console.error(`Falha ao carregar script modular: ${scriptFiles[index]}`, e);
    document.head.appendChild(s);
  }

  loadNext(0);
})();
