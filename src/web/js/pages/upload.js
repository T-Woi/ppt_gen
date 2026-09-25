/**
 * PPT-Gen Studio - Lógica da Página de Upload / Tela Inicial
 * Gerenciamento de seleção de pastas, PDFs, imagens e drag & drop
 */

// ============================================================================
// 1. Gatilhos de Seleção Nativa (Windows IPC / Servidor Local)
// ============================================================================
async function triggerSelectFolder(append = false) {
  try {
    showLoading('Aguardando Seleção...', 'Selecione a pasta no Windows para iniciar a leitura...');
    const res = await fetch(apiUrl(`/api/select/folder?append=${append}`), { method: 'POST' });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Nenhuma pasta selecionada');
    }
    const data = await res.json();
    updateSessionState(data);
    if (data.items && data.items.length > 0) {
      showToast(`${data.items.length} imagens carregadas com sucesso!`, 'success');
    }
  } catch (err) {
    await showAlertModal(err.message, 'Erro ao Carregar Pasta', 'error');
  } finally {
    hideLoading();
  }
}

async function triggerSelectPdf(append = false) {
  try {
    showLoading('Aguardando Seleção...', 'Selecione o arquivo PDF para iniciar a extração...');
    const res = await fetch(apiUrl(`/api/select/pdf?append=${append}`), { method: 'POST' });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Nenhum PDF selecionado');
    }
    const data = await res.json();
    updateSessionState(data);
    if (data.items && data.items.length > 0) {
      showToast(`${data.items.length} páginas do PDF extraídas!`, 'success');
    }
  } catch (err) {
    await showAlertModal(err.message, 'Erro ao Processar PDF', 'error');
  } finally {
    hideLoading();
  }
}

async function triggerSelectImages(append = false) {
  try {
    showLoading('Aguardando Seleção...', 'Selecione as imagens no Windows para adicionar aos slides...');
    const res = await fetch(apiUrl(`/api/select/images?append=${append}`), { method: 'POST' });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Nenhuma imagem selecionada');
    }
    const data = await res.json();
    updateSessionState(data);
    if (data.items && data.items.length > 0) {
      showToast(`${data.items.length} imagens adicionadas!`, 'success');
    }
  } catch (err) {
    await showAlertModal(err.message, 'Erro ao Carregar Imagens', 'error');
  } finally {
    hideLoading();
  }
}

// ============================================================================
// 2. Listeners de Ações na Página de Upload
// ============================================================================
if (dom.btnPickFolder) {
  dom.btnPickFolder.addEventListener('click', () => triggerSelectFolder(false));
}

if (dom.btnPickPdf) {
  dom.btnPickPdf.addEventListener('click', () => triggerSelectPdf(false));
}

if (dom.btnPickImages) {
  dom.btnPickImages.addEventListener('click', () => triggerSelectImages(false));
}

// Acessibilidade via teclado nos cartões de fonte
[dom.btnPickFolder, dom.btnPickPdf, dom.btnPickImages].forEach((card) => {
  if (!card) return;
  card.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      card.click();
    }
  });
});


// Drag & Drop Global / Na Dropzone
['dragenter', 'dragover'].forEach((eventName) => {
  window.addEventListener(eventName, (e) => {
    e.preventDefault();
    if (dom.dropArea) dom.dropArea.classList.add('drag-active');
  });
});

['dragleave', 'drop'].forEach((eventName) => {
  window.addEventListener(eventName, (e) => {
    e.preventDefault();
    if (dom.dropArea) dom.dropArea.classList.remove('drag-active');
  });
});

window.addEventListener('drop', async (e) => {
  const files = e.dataTransfer ? e.dataTransfer.files : null;
  if (!files || files.length === 0) return;

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }

  try {
    showLoading('Processando Arquivos...', `Importando ${files.length} arquivo(s) enviados...`);
    const res = await fetch(apiUrl(`/api/upload?append=${state.items.length > 0}`), {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Erro ao processar arquivos');
    }
    const data = await res.json();
    updateSessionState(data);
    showToast(`${data.items.length} slides prontos para organizar!`, 'success');
  } catch (err) {
    await showAlertModal(err.message, 'Erro ao Importar Arquivos', 'error');
  } finally {
    hideLoading();
  }
});

// Fallback de Seleção via Navegador Tradicional
if (dom.browserFileInput) {
  dom.browserFileInput.addEventListener('change', async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    try {
      showLoading('Carregando Arquivos...', `Processando ${files.length} arquivo(s)...`);
      const res = await fetch(apiUrl(`/api/upload?append=${state.items.length > 0}`), {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Erro ao carregar arquivos');
      }
      const data = await res.json();
      updateSessionState(data);
    } catch (err) {
      await showAlertModal(err.message, 'Erro de Upload', 'error');
    } finally {
      hideLoading();
    }
  });
}
