/**
 * PPT-Gen Studio - Componente Slide Card & Drag and Drop
 */

function createSlideCard(item, index) {
  const card = document.createElement('div');
  card.className = 'slide-card';
  card.dataset.id = item.id;
  card.dataset.index = index;
  card.draggable = true;

  const isPdf = item.source_type === 'pdf_page';
  const tag = isPdf ? `Pág. ${item.page_index + 1}` : (item.title.split('.').pop() || 'IMG').toUpperCase();
  const thumbUrl = item.thumbnail_url && item.thumbnail_url.startsWith('data:')
    ? item.thumbnail_url
    : apiUrl(`${item.thumbnail_url}?r=${item.rotation}`);

  const dimText = (item.original_width && item.original_height)
    ? `${item.original_width}×${item.original_height}`
    : 'Auto';

  const formattedNum = String(index + 1).padStart(2, '0');

  card.innerHTML = `
    <div class="card-preview-wrap">
      <span class="card-index-badge">#${formattedNum}</span>
      <span class="card-format-badge">${tag}</span>
      <div class="card-hover-actions">
        <button class="card-action-btn btn-rotate" type="button" title="Girar 90° no sentido horário">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21.5 2v6h-6"></path>
            <path d="M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path>
          </svg>
        </button>
        <button class="card-action-btn btn-zoom" type="button" title="Visualizar slide ampliado">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="11" y1="8" x2="11" y2="14"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
        </button>
        <button class="card-action-btn btn-trash" type="button" title="Remover slide">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      </div>
      <img src="${thumbUrl}" alt="${item.title}" loading="lazy">
    </div>
    <div class="card-caption">
      <span class="card-title-text" title="${item.title}">${item.title}</span>
      <span class="card-dimensions-tag">${dimText}</span>
    </div>
  `;

  // Drag & Drop para Reordenação
  card.addEventListener('dragstart', (e) => {
    state.draggedCardIndex = index;
    card.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', item.id);
  });

  card.addEventListener('dragend', () => {
    card.classList.remove('dragging');
    document.querySelectorAll('.slide-card').forEach(c => c.classList.remove('drag-over'));
  });

  card.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    card.classList.add('drag-over');
  });

  card.addEventListener('dragleave', () => {
    card.classList.remove('drag-over');
  });

  card.addEventListener('drop', (e) => {
    e.preventDefault();
    card.classList.remove('drag-over');
    const fromIdx = state.draggedCardIndex;
    const toIdx = index;
    if (fromIdx !== null && fromIdx !== toIdx) {
      handleMoveCard(fromIdx, toIdx);
    }
  });

  // Ações nos Botões do Card
  card.querySelector('.btn-rotate').addEventListener('click', (e) => {
    e.stopPropagation();
    rotateItem(item.id);
  });

  card.querySelector('.btn-zoom').addEventListener('click', (e) => {
    e.stopPropagation();
    openPreview(index);
  });

  card.querySelector('.card-preview-wrap').addEventListener('click', () => {
    openPreview(index);
  });

  card.querySelector('.btn-trash').addEventListener('click', (e) => {
    e.stopPropagation();
    removeItem(item.id);
  });

  return card;
}
