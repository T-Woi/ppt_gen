/**
 * PPT-Gen Studio - Módulo de Modais, Alertas e Notificações
 */

let alertResolvePromise = null;

// Modal de Carregamento / Spinner
function showLoading(title = 'Carregando Arquivos...', message = 'Lendo e processando dados em alta performance. Aguarde um instante.') {
  if (dom.loadingTitle) dom.loadingTitle.textContent = title;
  if (dom.loadingMessage) dom.loadingMessage.textContent = message;
  if (dom.loadingModal && !dom.loadingModal.open) {
    dom.loadingModal.showModal();
  }
}

function hideLoading() {
  if (dom.loadingModal && dom.loadingModal.open) {
    dom.loadingModal.close();
  }
}

// Modal Centralizado de Alerta (Aviso / Erro / Sucesso)
function showAlertModal(message, title = 'Aviso', type = 'info') {
  return new Promise((resolve) => {
    alertResolvePromise = resolve;
    if (dom.alertModalTitle) dom.alertModalTitle.textContent = title;
    if (dom.alertModalMessage) dom.alertModalMessage.textContent = message;

    if (dom.alertModalIcon) {
      dom.alertModalIcon.className = `alert-icon-box ${type}`;
      if (type === 'error') {
        dom.alertModalIcon.innerHTML = `<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
      } else if (type === 'warning') {
        dom.alertModalIcon.innerHTML = `<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
      } else if (type === 'success') {
        dom.alertModalIcon.innerHTML = `<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="9 12 12 15 17 10"></polyline></svg>`;
      } else {
        dom.alertModalIcon.innerHTML = `<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
      }
    }

    if (dom.alertBtnCancel) dom.alertBtnCancel.style.display = 'none';
    if (dom.alertBtnOk) {
      dom.alertBtnOk.textContent = 'Entendido';
      dom.alertBtnOk.className = 'btn btn-brand btn-sm';
    }

    if (dom.appAlertModal && !dom.appAlertModal.open) {
      dom.appAlertModal.showModal();
    }
    if (dom.alertBtnOk) dom.alertBtnOk.focus();
  });
}

// Modal Centralizado de Confirmação (Sim / Não)
function showConfirmModal(message, title = 'Confirmação', confirmText = 'Confirmar', isDanger = false) {
  return new Promise((resolve) => {
    alertResolvePromise = resolve;
    if (dom.alertModalTitle) dom.alertModalTitle.textContent = title;
    if (dom.alertModalMessage) dom.alertModalMessage.textContent = message;

    if (dom.alertModalIcon) {
      dom.alertModalIcon.className = `alert-icon-box ${isDanger ? 'warning' : 'info'}`;
      dom.alertModalIcon.innerHTML = isDanger
        ? `<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`
        : `<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
    }

    if (dom.alertBtnCancel) {
      dom.alertBtnCancel.style.display = 'inline-flex';
      dom.alertBtnCancel.textContent = 'Cancelar';
    }
    if (dom.alertBtnOk) {
      dom.alertBtnOk.textContent = confirmText;
      dom.alertBtnOk.className = isDanger ? 'btn btn-danger btn-sm' : 'btn btn-brand btn-sm';
    }

    if (dom.appAlertModal && !dom.appAlertModal.open) {
      dom.appAlertModal.showModal();
    }
    if (dom.alertBtnOk) dom.alertBtnOk.focus();
  });
}

// Configura Listeners de Botões do Modal de Alertas
if (dom.alertBtnOk) {
  dom.alertBtnOk.addEventListener('click', () => {
    if (dom.appAlertModal) dom.appAlertModal.close();
    if (alertResolvePromise) {
      alertResolvePromise(true);
      alertResolvePromise = null;
    }
  });
}

if (dom.alertBtnCancel) {
  dom.alertBtnCancel.addEventListener('click', () => {
    if (dom.appAlertModal) dom.appAlertModal.close();
    if (alertResolvePromise) {
      alertResolvePromise(false);
      alertResolvePromise = null;
    }
  });
}

if (dom.appAlertModal) {
  dom.appAlertModal.addEventListener('cancel', () => {
    if (alertResolvePromise) {
      alertResolvePromise(false);
      alertResolvePromise = null;
    }
  });

  dom.appAlertModal.addEventListener('click', (e) => {
    if (e.target === dom.appAlertModal) {
      dom.appAlertModal.close();
      if (alertResolvePromise) {
        alertResolvePromise(false);
        alertResolvePromise = null;
      }
    }
  });
}

// Intercepta alerts padrão do navegador com o modal estilizado
window.alert = (msg) => showAlertModal(String(msg), 'Alerta', 'info');

// Notificações Toast Leves
function showToast(message, type = 'info', duration = 3500) {
  if (!dom.toastContainer) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const iconSvg = type === 'success'
    ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`
    : type === 'error'
    ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`
    : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;

  toast.innerHTML = `${iconSvg}<span>${message}</span>`;
  dom.toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(24px) scale(0.96)';
    setTimeout(() => toast.remove(), 250);
  }, duration);
}
