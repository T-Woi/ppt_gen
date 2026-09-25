/**
 * PPT-Gen Studio - Lógica da Página do Editor / Workspace
 * Gerenciamento de toolbar, configurações de slide, ordenação e exportação PPTX
 */

// ============================================================================
// 1. Menu "+ Adicionar Mais" e Ações da Barra de Ferramentas
// ============================================================================
if (dom.btnAddMoreToggle && dom.addMoreMenu) {
  dom.btnAddMoreToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = dom.addMoreMenu.classList.toggle('show');
    dom.btnAddMoreToggle.setAttribute('aria-expanded', String(isOpen));
  });

  document.addEventListener('click', () => {
    dom.addMoreMenu.classList.remove('show');
    dom.btnAddMoreToggle.setAttribute('aria-expanded', 'false');
  });
}

if (dom.btnAddFolder) {
  dom.btnAddFolder.addEventListener('click', () => triggerSelectFolder(true));
}

if (dom.btnAddPdf) {
  dom.btnAddPdf.addEventListener('click', () => triggerSelectPdf(true));
}

if (dom.btnAddImages) {
  dom.btnAddImages.addEventListener('click', () => triggerSelectImages(true));
}

// Ordenação Natural (1, 2, ..., 10)
if (dom.btnNaturalSort) {
  dom.btnNaturalSort.addEventListener('click', async () => {
    try {
      const res = await fetch(apiUrl('/api/sort-natural'), { method: 'POST' });
      const data = await res.json();
      updateSessionState(data);
      showToast('Reordenado por ordem natural (1, 2, ..., 10)', 'success');
    } catch (err) {
      await showAlertModal('Erro ao ordenar: ' + err.message, 'Erro de Ordenação', 'error');
    }
  });
}

// Inverter Ordem dos Slides
if (dom.btnReverseOrder) {
  dom.btnReverseOrder.addEventListener('click', async () => {
    try {
      const res = await fetch(apiUrl('/api/reverse'), { method: 'POST' });
      const data = await res.json();
      updateSessionState(data);
      showToast('Sequência dos slides invertida', 'info');
    } catch (err) {
      await showAlertModal('Erro ao inverter: ' + err.message, 'Erro de Inversão', 'error');
    }
  });
}

// Limpar Toda a Sessão
if (dom.btnClearAll) {
  dom.btnClearAll.addEventListener('click', async () => {
    const confirmed = await showConfirmModal(
      'Deseja realmente limpar todos os slides carregados na sessão atual?',
      'Limpar Sessão',
      'Limpar Tudo',
      true
    );
    if (!confirmed) return;
    try {
      showLoading('Limpando Sessão...', 'Removendo todos os slides e redefinindo o espaço de trabalho...');
      await fetch(apiUrl('/api/clear'), { method: 'POST' });
      await fetchSession();
      showToast('Sessão reiniciada', 'info');
    } catch (err) {
      await showAlertModal(err.message, 'Erro ao Limpar', 'error');
    } finally {
      hideLoading();
    }
  });
}

// Retorno à Tela Inicial pelo Logo
if (dom.btnLogoHome) {
  dom.btnLogoHome.addEventListener('click', async () => {
    if (state.items.length > 0) {
      const confirmed = await showConfirmModal(
        'Deseja voltar para a tela inicial? (Os slides atuais continuarão na sessão até serem limpos)',
        'Voltar ao Início',
        'Voltar'
      );
      if (confirmed) {
        dom.uploadView.style.display = 'flex';
        dom.editorView.style.display = 'none';
      }
    }
  });
}

// ============================================================================
// 2. Configurações da Barra Lateral (Aspect Ratio, Fit, Cores de Fundo)
// ============================================================================
// Proporção (16:9 vs 4:3)
if (dom.aspectSegmented) {
  dom.aspectSegmented.querySelectorAll('.segment-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      dom.aspectSegmented.querySelectorAll('.segment-btn').forEach((b) => {
        b.classList.remove('active');
        b.setAttribute('aria-checked', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-checked', 'true');
      state.aspectRatio = btn.dataset.val;
    });
  });
}

// Modo de Enquadramento (fit vs fill vs stretch)
if (dom.fitSegmented) {
  dom.fitSegmented.querySelectorAll('.segment-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      dom.fitSegmented.querySelectorAll('.segment-btn').forEach((b) => {
        b.classList.remove('active');
        b.setAttribute('aria-checked', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-checked', 'true');
      state.fitMode = btn.dataset.val;
    });
  });
}

// Cor de Fundo dos Slides
if (dom.colorButtons) {
  dom.colorButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      dom.colorButtons.forEach((b) => {
        b.classList.remove('active');
        b.setAttribute('aria-checked', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-checked', 'true');
      state.bgColor = btn.dataset.color;
    });
  });
}

// Diálogo de Seleção de Pasta de Destino
if (dom.btnBrowseDest) {
  dom.btnBrowseDest.addEventListener('click', async () => {
    try {
      const res = await fetch(apiUrl('/api/select/destination'), { method: 'POST' });
      const data = await res.json();
      if (data.output_dir && dom.exportFolderInput) {
        dom.exportFolderInput.value = data.output_dir;
        dom.exportFolderInput.title = data.output_dir;
        dom.exportFolderInput.dataset.autoFilled = 'false';
      }
      if (data.filename && dom.exportFilenameInput) {
        dom.exportFilenameInput.value = data.filename.replace(/\.pptx$/i, '');
        dom.exportFilenameInput.dataset.autoFilled = 'false';
      }
    } catch (err) {
      await showAlertModal(err.message, 'Erro ao Selecionar Destino', 'error');
    }
  });
}

// ============================================================================
// 3. Exportação para Apresentação PowerPoint (PPTX)
// ============================================================================
if (dom.btnExportPptx) {
  dom.btnExportPptx.addEventListener('click', executeExport);
}

async function executeExport() {
  if (state.items.length === 0) {
    await showAlertModal('Adicione pelo menos um slide antes de converter para PowerPoint.', 'Atenção', 'warning');
    return;
  }

  const outDir = dom.exportFolderInput ? dom.exportFolderInput.value.trim() : '';
  const filename = dom.exportFilenameInput ? dom.exportFilenameInput.value.trim() : '';

  if (!outDir) {
    await showAlertModal('Informe a pasta onde deseja salvar a apresentação.', 'Pasta Obrigatória', 'warning');
    if (dom.exportFolderInput) dom.exportFolderInput.focus();
    return;
  }

  if (!filename) {
    await showAlertModal('Informe o nome da apresentação.', 'Nome Obrigatório', 'warning');
    if (dom.exportFilenameInput) dom.exportFilenameInput.focus();
    return;
  }

  const payload = {
    output_dir: outDir,
    filename: filename,
    aspect_ratio: state.aspectRatio,
    fit_mode: state.fitMode,
    bg_color: state.bgColor,
    pdf_dpi: state.pdfDpi,
  };

  // Ativa Estado de Carregamento
  if (dom.btnExportPptx) dom.btnExportPptx.disabled = true;
  if (dom.exportSpinner) dom.exportSpinner.style.display = 'inline-block';
  if (dom.exportBtnContent) dom.exportBtnContent.style.display = 'none';
  showLoading('Gerando Apresentação...', 'Construindo o arquivo PowerPoint e dimensionando os slides. Aguarde um instante...');

  try {
    const res = await fetch(apiUrl('/api/export'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Falha ao gerar apresentação.');
    }

    const data = await res.json();
    lastGeneratedFilePath = data.output_path;
    lastGeneratedFolderPath = data.output_dir || outDir;
    if (!lastGeneratedFolderPath && lastGeneratedFilePath) {
      lastGeneratedFolderPath = lastGeneratedFilePath.replace(/[/\\][^/\\]+$/, '');
    }

    // Preenche e Abre Modal de Sucesso
    if (dom.successFileName) dom.successFileName.textContent = data.filename;
    if (dom.successFilePath) {
      dom.successFilePath.textContent = data.output_path;
      dom.successFilePath.title = data.output_path;
    }
    if (dom.successSlideCount) dom.successSlideCount.textContent = data.total_slides;
    if (dom.successFileSize) dom.successFileSize.textContent = formatBytes(data.file_size_bytes);
    if (dom.successModal) dom.successModal.showModal();
  } catch (err) {
    await showAlertModal(err.message, 'Erro ao Gerar Apresentação', 'error');
  } finally {
    hideLoading();
    if (dom.btnExportPptx) dom.btnExportPptx.disabled = false;
    if (dom.exportSpinner) dom.exportSpinner.style.display = 'none';
    if (dom.exportBtnContent) dom.exportBtnContent.style.display = 'flex';
  }
}

// Ações no Modal de Sucesso
if (dom.btnOpenPresentation) {
  dom.btnOpenPresentation.addEventListener('click', async () => {
    if (!lastGeneratedFilePath) {
      await showAlertModal('Caminho da apresentação não disponível.', 'Aviso', 'warning');
      return;
    }
    try {
      const res = await fetch(apiUrl(`/api/open-file?path=${encodeURIComponent(lastGeneratedFilePath)}`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: lastGeneratedFilePath }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Não foi possível abrir o arquivo da apresentação.');
      }
    } catch (err) {
      console.error('[OpenPresentation Error]', err);
      await showAlertModal(err.message || 'Falha ao abrir a apresentação no PowerPoint.', 'Erro ao Abrir Apresentação', 'error');
    }
  });
}

if (dom.btnOpenFolder) {
  dom.btnOpenFolder.addEventListener('click', async () => {
    let targetFolder = lastGeneratedFolderPath;
    if (!targetFolder && lastGeneratedFilePath) {
      targetFolder = lastGeneratedFilePath.replace(/[/\\][^/\\]+$/, '');
    }
    if (!targetFolder) {
      await showAlertModal('Pasta de destino não identificada.', 'Aviso', 'warning');
      return;
    }
    try {
      const res = await fetch(apiUrl(`/api/open-file?path=${encodeURIComponent(targetFolder)}`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: targetFolder }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Não foi possível abrir a pasta de destino.');
      }
    } catch (err) {
      console.error('[OpenFolder Error]', err);
      await showAlertModal(err.message || 'Falha ao abrir a pasta no Windows Explorer.', 'Erro ao Abrir Pasta', 'error');
    }
  });
}

if (dom.btnResetToHome) {
  dom.btnResetToHome.addEventListener('click', async () => {
    if (dom.successModal) dom.successModal.close();
    await fetch(apiUrl('/api/clear'), { method: 'POST' });
    fetchSession();
  });
}
