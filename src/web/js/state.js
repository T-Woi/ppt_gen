/**
 * PPT-Gen Studio - Estado Global e Mapeamento do DOM
 */

// Estado da Aplicação
const state = {
  items: [],
  sourceDescription: '',
  suggestedFilename: '',
  suggestedOutputDir: '',
  aspectRatio: '16:9',
  fitMode: 'fit',
  bgColor: '#FFFFFF',
  pdfDpi: 200,
  draggedCardIndex: null,
  activePreviewIndex: null,
};

// Mapeamento Centralizado de Elementos do DOM
const dom = {
  // Views Principais
  uploadView: document.getElementById('uploadView'),
  editorView: document.getElementById('editorView'),

  // Header & Status
  btnLogoHome: document.getElementById('btnLogoHome'),
  themeToggleBtn: document.getElementById('themeToggleBtn'),
  btnShortcutsHelp: document.getElementById('btnShortcutsHelp'),
  fileProtocolNotice: document.getElementById('fileProtocolNotice'),

  // Tela Inicial / Upload
  dropArea: document.getElementById('dropArea'),
  btnPickFolder: document.getElementById('btnPickFolder'),
  btnPickPdf: document.getElementById('btnPickPdf'),
  btnPickImages: document.getElementById('btnPickImages'),

  // Toolbar do Editor
  slideCountTag: document.getElementById('slideCountTag'),
  sourceDescLabel: document.getElementById('sourceDescLabel'),
  slidesGrid: document.getElementById('slidesGrid'),
  btnAddMoreToggle: document.getElementById('btnAddMoreToggle'),
  addMoreMenu: document.getElementById('addMoreMenu'),
  btnAddFolder: document.getElementById('btnAddFolder'),
  btnAddPdf: document.getElementById('btnAddPdf'),
  btnAddImages: document.getElementById('btnAddImages'),
  btnNaturalSort: document.getElementById('btnNaturalSort'),
  btnReverseOrder: document.getElementById('btnReverseOrder'),
  btnClearAll: document.getElementById('btnClearAll'),

  // Sidebar de Configurações
  aspectSegmented: document.getElementById('aspectSegmented'),
  fitSegmented: document.getElementById('fitSegmented'),
  colorButtons: document.querySelectorAll('.color-swatch-btn'),
  exportFilenameInput: document.getElementById('exportFilenameInput'),
  exportFolderInput: document.getElementById('exportFolderInput'),
  btnBrowseDest: document.getElementById('btnBrowseDest'),
  btnExportPptx: document.getElementById('btnExportPptx'),
  exportSpinner: document.getElementById('exportSpinner'),
  exportBtnContent: document.getElementById('exportBtnContent'),

  // Modal de Preview / Lightbox
  previewModal: document.getElementById('previewModal'),
  modalImage: document.getElementById('modalImage'),
  modalSlideTitle: document.getElementById('modalSlideTitle'),
  modalSlideMeta: document.getElementById('modalSlideMeta'),
  modalCounter: document.getElementById('modalCounter'),
  btnCloseModal: document.getElementById('btnCloseModal'),
  btnPrevSlide: document.getElementById('btnPrevSlide'),
  btnNextSlide: document.getElementById('btnNextSlide'),
  btnModalRotate: document.getElementById('btnModalRotate'),

  // Modal de Sucesso
  successModal: document.getElementById('successModal'),
  successFileName: document.getElementById('successFileName'),
  successFilePath: document.getElementById('successFilePath'),
  successSlideCount: document.getElementById('successSlideCount'),
  successFileSize: document.getElementById('successFileSize'),
  btnOpenPresentation: document.getElementById('btnOpenPresentation'),
  btnOpenFolder: document.getElementById('btnOpenFolder'),
  btnResetToHome: document.getElementById('btnResetToHome'),

  // Modal de Atalhos
  shortcutsModal: document.getElementById('shortcutsModal'),
  btnCloseShortcutsModal: document.getElementById('btnCloseShortcutsModal'),

  // Modal de Carregamento (Loading)
  loadingModal: document.getElementById('loadingModal'),
  loadingTitle: document.getElementById('loadingTitle'),
  loadingMessage: document.getElementById('loadingMessage'),

  // Modal de Alertas e Confirmações
  appAlertModal: document.getElementById('appAlertModal'),
  alertModalTitle: document.getElementById('alertModalTitle'),
  alertModalMessage: document.getElementById('alertModalMessage'),
  alertModalIcon: document.getElementById('alertModalIcon'),
  alertBtnCancel: document.getElementById('alertBtnCancel'),
  alertBtnOk: document.getElementById('alertBtnOk'),

  // Fallbacks de Arquivo no Navegador
  browserFileInput: document.getElementById('browserFileInput'),

  // Container de Toasts
  toastContainer: document.getElementById('toastContainer'),
};

// Variáveis de Controle de Arquivos Exportados (Escopo Global Seguro)
let lastGeneratedFilePath = null;
let lastGeneratedFolderPath = null;
