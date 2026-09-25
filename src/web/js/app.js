/**
 * PPT-Gen Studio - Orquestrador Principal da Aplicação
 * Sincronização de Sessão, Renderização de Views, Ciclo de Vida e Bootstrap
 */

// ============================================================================
// 1. Sincronização com o Backend
// ============================================================================
async function fetchSession() {
  try {
    const res = await fetch(apiUrl('/api/session'));
    if (!res.ok) throw new Error('Falha ao obter sessão');
    const data = await res.json();
    if (dom.fileProtocolNotice) {
      dom.fileProtocolNotice.style.display = 'none';
    }
    updateSessionState(data);
  } catch (err) {
    if (window.location.protocol === 'file:' && !isNativeWebView() && dom.fileProtocolNotice) {
      dom.fileProtocolNotice.style.display = 'block';
    } else if (!isNativeWebView()) {
      showToast('Erro ao sincronizar com servidor: ' + err.message, 'error');
    }
  }
}

function updateSessionState(data) {
  state.items = data.items || [];
  state.sourceDescription = data.source_description || '';
  state.suggestedFilename = data.suggested_filename || 'Apresentacao.pptx';
  state.suggestedOutputDir = data.suggested_output_dir || '';

  renderViews();
}

// ============================================================================
// 2. Renderização de Interfaces (Upload vs Editor)
// ============================================================================
function renderViews() {
  const count = state.items.length;

  if (count === 0) {
    // Modo Inicial (Hero + Dropzone)
    if (dom.uploadView) dom.uploadView.style.display = 'flex';
    if (dom.editorView) dom.editorView.style.display = 'none';
    return;
  }

  // Modo Editor / Workspace de Slides
  if (dom.uploadView) dom.uploadView.style.display = 'none';
  if (dom.editorView) dom.editorView.style.display = 'block';

  if (dom.slideCountTag) {
    dom.slideCountTag.textContent = `${count} slide${count === 1 ? '' : 's'}`;
  }
  if (dom.sourceDescLabel) {
    dom.sourceDescLabel.textContent = state.sourceDescription;
    dom.sourceDescLabel.title = state.sourceDescription;
  }

  // Atualização dos campos de exportação (se ainda não alterados pelo usuário)
  if (dom.exportFilenameInput) {
    if (!dom.exportFilenameInput.value.trim() || dom.exportFilenameInput.dataset.autoFilled !== 'false') {
      dom.exportFilenameInput.value = state.suggestedFilename.replace(/\.pptx$/i, '');
      dom.exportFilenameInput.dataset.autoFilled = 'true';
    }
  }
  if (dom.exportFolderInput) {
    if (!dom.exportFolderInput.value.trim() || dom.exportFolderInput.dataset.autoFilled !== 'false') {
      dom.exportFolderInput.value = state.suggestedOutputDir;
      dom.exportFolderInput.title = state.suggestedOutputDir;
      dom.exportFolderInput.dataset.autoFilled = 'true';
    }
  }

  // Renderização da Grade de Cards dos Slides
  if (dom.slidesGrid) {
    dom.slidesGrid.innerHTML = '';
    state.items.forEach((item, index) => {
      const card = createSlideCard(item, index);
      dom.slidesGrid.appendChild(card);
    });
  }
}

// ============================================================================
// 3. Manipulação de Slides (Reordenar, Girar, Remover)
// ============================================================================
async function handleMoveCard(fromIndex, toIndex) {
  const newItems = [...state.items];
  const [moved] = newItems.splice(fromIndex, 1);
  newItems.splice(toIndex, 0, moved);

  // Atualização otimista imediata na UI
  state.items = newItems;
  renderViews();

  try {
    const ids = newItems.map((it) => it.id);
    const res = await fetch(apiUrl('/api/reorder'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_ids: ids }),
    });
    if (!res.ok) throw new Error('Falha ao salvar nova ordem');
  } catch (err) {
    showToast('Erro ao reordenar: ' + err.message, 'error');
    fetchSession();
  }
}

async function rotateItem(itemId) {
  try {
    const res = await fetch(apiUrl('/api/rotate'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId, direction: 'cw' }),
    });
    if (!res.ok) throw new Error('Falha ao girar imagem');
    const data = await res.json();
    updateSessionState(data);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function removeItem(itemId) {
  try {
    const res = await fetch(apiUrl('/api/remove'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_ids: [itemId] }),
    });
    if (!res.ok) throw new Error('Falha ao remover slide');
    const data = await res.json();
    updateSessionState(data);
    showToast('Slide removido', 'info');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ============================================================================
// 4. Alternância e Persistência do Tema (Claro / Escuro)
// ============================================================================
if (dom.themeToggleBtn) {
  dom.themeToggleBtn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const nextTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nextTheme);
    localStorage.setItem('ppt_gen_theme', nextTheme);
  });
}

// ============================================================================
// 5. Inicialização e Bootstrap
// ============================================================================
document.addEventListener('DOMContentLoaded', async () => {
  const savedTheme = localStorage.getItem('ppt_gen_theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);

  if (isNativeWebView() && !isPyWebView()) {
    await new Promise((resolve) => {
      const handler = () => {
        window.removeEventListener('pywebviewready', handler);
        resolve();
      };
      window.addEventListener('pywebviewready', handler);
      setTimeout(handler, 800);
    });
  }

  fetchSession();
});

window.addEventListener('pywebviewready', () => {
  if (dom.fileProtocolNotice) dom.fileProtocolNotice.style.display = 'none';
  fetchSession();
});
