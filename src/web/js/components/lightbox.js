/**
 * PPT-Gen Studio - Lightbox Preview & Atalhos de Teclado
 */

async function openPreview(index) {
  if (index < 0 || index >= state.items.length) return;
  state.activePreviewIndex = index;
  const item = state.items[index];

  if (isPyWebView() && window.pywebview.api && window.pywebview.api.get_preview) {
    try {
      const dataUrl = await window.pywebview.api.get_preview(item.id);
      dom.modalImage.src = dataUrl;
    } catch (_) {
      dom.modalImage.src = apiUrl(`${item.preview_url}?r=${item.rotation}`);
    }
  } else {
    dom.modalImage.src = apiUrl(`${item.preview_url}?r=${item.rotation}`);
  }

  dom.modalSlideTitle.textContent = item.title;
  dom.modalSlideMeta.textContent = `${item.original_width || 'Auto'} × ${item.original_height || 'Auto'} • ${formatBytes(item.file_size_bytes)}`;
  dom.modalCounter.textContent = `Slide ${index + 1} de ${state.items.length}`;

  dom.previewModal.showModal();
}

// Listeners do Lightbox
if (dom.btnCloseModal) {
  dom.btnCloseModal.addEventListener('click', () => dom.previewModal.close());
}

if (dom.previewModal) {
  dom.previewModal.addEventListener('click', (e) => {
    if (e.target === dom.previewModal) dom.previewModal.close();
  });
}

if (dom.btnPrevSlide) {
  dom.btnPrevSlide.addEventListener('click', () => {
    if (state.activePreviewIndex !== null && state.activePreviewIndex > 0) {
      openPreview(state.activePreviewIndex - 1);
    }
  });
}

if (dom.btnNextSlide) {
  dom.btnNextSlide.addEventListener('click', () => {
    if (state.activePreviewIndex !== null && state.activePreviewIndex < state.items.length - 1) {
      openPreview(state.activePreviewIndex + 1);
    }
  });
}

if (dom.btnModalRotate) {
  dom.btnModalRotate.addEventListener('click', async () => {
    if (state.activePreviewIndex !== null) {
      const item = state.items[state.activePreviewIndex];
      await rotateItem(item.id);
      openPreview(state.activePreviewIndex);
    }
  });
}

// Modal de Atalhos
if (dom.btnShortcutsHelp) {
  dom.btnShortcutsHelp.addEventListener('click', () => dom.shortcutsModal.showModal());
}

if (dom.btnCloseShortcutsModal) {
  dom.btnCloseShortcutsModal.addEventListener('click', () => dom.shortcutsModal.close());
}

if (dom.shortcutsModal) {
  dom.shortcutsModal.addEventListener('click', (e) => {
    if (e.target === dom.shortcutsModal) dom.shortcutsModal.close();
  });
}

// Atalhos Globais de Teclado
window.addEventListener('keydown', (e) => {
  // Ctrl + Enter para converter
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    if (!dom.previewModal.open && !dom.successModal.open && !dom.shortcutsModal.open && !dom.appAlertModal.open) {
      executeExport();
    }
    return;
  }

  // Ctrl + T para alternar tema
  if ((e.ctrlKey || e.metaKey) && (e.key === 't' || e.key === 'T')) {
    e.preventDefault();
    dom.themeToggleBtn.click();
    return;
  }

  // F1 ou '?' para ajuda
  if (e.key === 'F1' || (e.key === '?' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName))) {
    e.preventDefault();
    dom.shortcutsModal.showModal();
    return;
  }

  // Teclas no modal de preview
  if (dom.previewModal.open) {
    if (e.key === 'ArrowLeft') {
      dom.btnPrevSlide.click();
    } else if (e.key === 'ArrowRight') {
      dom.btnNextSlide.click();
    } else if (e.key === 'r' || e.key === 'R') {
      dom.btnModalRotate.click();
    } else if (e.key === 'Escape') {
      dom.previewModal.close();
    }
  } else if (dom.successModal.open && e.key === 'Escape') {
    dom.successModal.close();
  } else if (dom.shortcutsModal.open && e.key === 'Escape') {
    dom.shortcutsModal.close();
  }
});
