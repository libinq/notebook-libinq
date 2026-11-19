// Notes Component - Managing Insights & RAG Loopback

class NotesManager {
  constructor(sourcesManager) {
    this.sourcesManager = sourcesManager;
    this.container = document.getElementById('notes-list');
    this.activeNotebookId = null;
    this.notes = [];
    this.activeNote = null;

    this.setupUI();
  }

  setNotebook(notebookId) {
    this.activeNotebookId = notebookId;
    this.loadNotes();
  }

  setupUI() {
    const newBtn = document.getElementById('new-note-btn');
    if (newBtn) {
      newBtn.onclick = () => this.openNoteEditor();
    }
  }

  async loadNotes() {
    if (!this.activeNotebookId) return;
    try {
      const data = await API.getNotes(this.activeNotebookId);
      this.notes = data.notes || [];
      this.render();
    } catch (e) {
      console.error('Failed to load notes', e);
    }
  }

  render() {
    if (this.notes.length === 0) {
      this.container.innerHTML = `
        <div class="empty-state-small">
          <p data-i18n="notes_empty">${t('notes_empty')}</p>
        </div>
      `;
      return;
    }

    this.container.innerHTML = this.notes.map(n => `
      <div class="note-card ${n.is_source ? 'is-promoted' : ''}" data-id="${n.id}">
        <div class="note-header">
          <div class="note-title">💡 ${n.title}</div>
          ${n.is_source ? `<span class="badge badge-success">${t('promoted_badge')}</span>` : ''}
        </div>
        <div class="note-snippet">${n.content.slice(0, 120)}...</div>
        <div class="note-footer">
          <span class="note-date">${new Date(n.updated_at).toLocaleDateString()}</span>
          <div class="note-actions">
            ${!n.is_source ? `
              <button class="btn btn-xs btn-outline promote-note-btn" data-id="${n.id}" title="${t('promote_note')}">🔄 ${t('promote_note')}</button>
            ` : ''}
            <button class="btn btn-xs edit-note-btn" data-id="${n.id}">✏️</button>
            <button class="btn btn-xs delete-note-btn" data-id="${n.id}">🗑️</button>
          </div>
        </div>
      </div>
    `).join('');

    this.container.querySelectorAll('.edit-note-btn').forEach(btn => {
      btn.onclick = () => {
        const id = btn.getAttribute('data-id');
        const note = this.notes.find(x => x.id === id);
        if (note) this.openNoteEditor(note);
      };
    });

    this.container.querySelectorAll('.delete-note-btn').forEach(btn => {
      btn.onclick = async () => {
        const id = btn.getAttribute('data-id');
        if (confirm('确定删除该笔记？')) {
          await API.deleteNote(id);
          this.loadNotes();
        }
      };
    });

    this.container.querySelectorAll('.promote-note-btn').forEach(btn => {
      btn.onclick = async () => {
        const id = btn.getAttribute('data-id');
        btn.textContent = '正在转为来源...';
        await API.promoteNote(id);
        await this.loadNotes();
        if (this.sourcesManager) {
          await this.sourcesManager.loadSources();
        }
      };
    });
  }

  openNoteEditor(note = null) {
    this.activeNote = note;
    const modal = document.getElementById('note-modal');
    modal.style.display = 'flex';
    
    const titleInput = document.getElementById('note-title-input');
    const contentInput = document.getElementById('note-content-input');
    
    titleInput.value = note ? note.title : '';
    contentInput.value = note ? note.content : '';

    const saveBtn = document.getElementById('save-note-btn');
    saveBtn.onclick = async () => {
      const title = titleInput.value.trim() || 'Untitled Note';
      const content = contentInput.value.trim();
      if (!content) return;

      if (this.activeNote) {
        await API.updateNote(this.activeNote.id, title, content);
      } else {
        await API.createNote(this.activeNotebookId, title, content);
      }
      modal.style.display = 'none';
      this.loadNotes();
    };

    const cancelBtn = document.getElementById('cancel-note-btn');
    cancelBtn.onclick = () => {
      modal.style.display = 'none';
    };
  }
}
