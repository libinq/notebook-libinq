// Sources Component - Managing Multi-modal Ingestion & Citation Highlighting

class SourcesManager {
  constructor() {
    this.container = document.getElementById('sources-list');
    this.counterEl = document.getElementById('sources-selected-count');
    this.sources = [];
    this.selectedIds = new Set();
    this.activeNotebookId = null;
    this.modalEl = document.getElementById('source-detail-modal');
    this.setupModal();
  }

  setNotebook(notebookId) {
    this.activeNotebookId = notebookId;
    this.loadSources();
  }

  async loadSources() {
    if (!this.activeNotebookId) return;
    this.container.innerHTML = '<div class="loading-state">加载来源中...</div>';
    try {
      const data = await API.getSources(this.activeNotebookId);
      this.sources = data.sources || [];
      // Select all sources by default
      this.selectedIds = new Set(this.sources.map(s => s.id));
      this.render();
      this.updateCount();
    } catch (e) {
      this.container.innerHTML = `<div class="error-state">加载失败: ${e.message}</div>`;
    }
  }

  getSelectedIds() {
    return Array.from(this.selectedIds);
  }

  updateCount() {
    if (this.counterEl) {
      this.counterEl.textContent = t('sources_selected_hint', { count: this.selectedIds.size });
    }
  }

  render() {
    if (this.sources.length === 0) {
      this.container.innerHTML = `
        <div class="empty-state">
          <p data-i18n="source_empty">${t('source_empty')}</p>
        </div>
      `;
      return;
    }

    const typeIcons = {
      file: '📄',
      url: '🌐',
      youtube: '▶️',
      text: '📝',
      note: '💡'
    };

    this.container.innerHTML = this.sources.map(s => `
      <div class="source-item ${this.selectedIds.has(s.id) ? 'selected' : ''}" data-id="${s.id}">
        <input type="checkbox" class="source-checkbox" data-id="${s.id}" ${this.selectedIds.has(s.id) ? 'checked' : ''}>
        <div class="source-content" data-id="${s.id}">
          <div class="source-title">
            <span class="source-icon">${typeIcons[s.source_type] || '📄'}</span>
            <span class="title-text" title="${s.title}">${s.title}</span>
          </div>
          <div class="source-meta">
            <span>${s.char_count} 字符</span>
            <span>·</span>
            <span>${s.chunk_count || 0} 个分块</span>
          </div>
        </div>
        <div class="source-actions">
          <button class="btn-icon view-source-btn" data-id="${s.id}" title="查看原文与分块">👁️</button>
          <button class="btn-icon delete-source-btn" data-id="${s.id}" title="删除来源">🗑️</button>
        </div>
      </div>
    `).join('');

    // Wire events
    this.container.querySelectorAll('.source-checkbox').forEach(cb => {
      cb.addEventListener('change', (e) => {
        const id = e.target.getAttribute('data-id');
        if (e.target.checked) {
          this.selectedIds.add(id);
        } else {
          this.selectedIds.delete(id);
        }
        this.updateItemSelectionState();
        this.updateCount();
      });
    });

    this.container.querySelectorAll('.view-source-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.openSourceDetail(btn.getAttribute('data-id'));
      });
    });

    this.container.querySelectorAll('.delete-source-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        if (confirm(t('delete_source_confirm'))) {
          await API.deleteSource(btn.getAttribute('data-id'));
          this.loadSources();
        }
      });
    });
  }

  updateItemSelectionState() {
    this.container.querySelectorAll('.source-item').forEach(item => {
      const id = item.getAttribute('data-id');
      if (this.selectedIds.has(id)) {
        item.classList.add('selected');
      } else {
        item.classList.remove('selected');
      }
    });
  }

  selectAll() {
    this.selectedIds = new Set(this.sources.map(s => s.id));
    this.container.querySelectorAll('.source-checkbox').forEach(cb => cb.checked = true);
    this.updateItemSelectionState();
    this.updateCount();
  }

  unselectAll() {
    this.selectedIds.clear();
    this.container.querySelectorAll('.source-checkbox').forEach(cb => cb.checked = false);
    this.updateItemSelectionState();
    this.updateCount();
  }

  setupModal() {
    const closeBtn = document.getElementById('close-source-modal');
    if (closeBtn) {
      closeBtn.onclick = () => {
        this.modalEl.style.display = 'none';
      };
    }
  }

  async openSourceDetail(sourceId, targetChunkIndex = null) {
    this.modalEl.style.display = 'flex';
    const bodyEl = document.getElementById('source-modal-body');
    const titleEl = document.getElementById('source-modal-title');
    titleEl.textContent = '加载来源中...';
    bodyEl.innerHTML = '<div class="loading-state">正在提取分块与文本...</div>';

    try {
      const source = await API.getSourceDetail(sourceId);
      titleEl.textContent = source.title;

      bodyEl.innerHTML = `
        <div class="source-chunks-header">
          <strong>文档分块列表 (共 ${source.chunks.length} 个分块，点击可高亮引用)</strong>
        </div>
        <div class="chunks-list">
          ${source.chunks.map(c => `
            <div class="chunk-card ${targetChunkIndex !== null && c.chunk_index === targetChunkIndex ? 'highlighted-chunk' : ''}" id="chunk-${sourceId}-${c.chunk_index}">
              <div class="chunk-badge">分块 #${c.chunk_index + 1} (偏移量: ${c.char_offset})</div>
              <div class="chunk-text">${c.content}</div>
            </div>
          `).join('')}
        </div>
      `;

      // If target chunk specified, scroll to it
      if (targetChunkIndex !== null) {
        setTimeout(() => {
          const targetEl = document.getElementById(`chunk-${sourceId}-${targetChunkIndex}`);
          if (targetEl) {
            targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, 100);
      }
    } catch (e) {
      bodyEl.innerHTML = `<div class="error-state">获取详情失败: ${e.message}</div>`;
    }
  }
}
