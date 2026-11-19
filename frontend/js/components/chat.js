// Chat Component with SSE Streaming, Interactive Citation Badges, and Save to Note

class ChatManager {
  constructor(sourcesManager, notesManager) {
    this.sourcesManager = sourcesManager;
    this.notesManager = notesManager;
    this.container = document.getElementById('chat-messages');
    this.input = document.getElementById('chat-input');
    this.sendBtn = document.getElementById('chat-send-btn');
    this.clearBtn = document.getElementById('chat-clear-btn');
    this.activeNotebookId = null;
    this.citationsRegistry = [];
    this.isStreaming = false;

    this.setupEvents();
  }

  setNotebook(notebookId) {
    this.activeNotebookId = notebookId;
    this.loadHistory();
  }

  setupEvents() {
    this.sendBtn.onclick = () => this.sendMessage();
    this.input.onkeydown = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    };
    this.clearBtn.onclick = async () => {
      if (confirm(t('chat_clear_confirm'))) {
        await API.clearChatHistory(this.activeNotebookId);
        this.container.innerHTML = '';
      }
    };
  }

  async loadHistory() {
    if (!this.activeNotebookId) return;
    this.container.innerHTML = '';
    const data = await API.getChatHistory(this.activeNotebookId);
    (data.messages || []).forEach(msg => {
      this.renderMessage(msg.role, msg.content, msg.citations || []);
    });
    this.scrollToBottom();
  }

  renderMessage(role, content, citations = []) {
    const msgEl = document.createElement('div');
    msgEl.className = `chat-message ${role}`;
    
    // Register citations for this message
    const citationsMap = {};
    citations.forEach(c => {
      citationsMap[c.citation_index] = c;
    });

    let formattedContent = content;
    if (role === 'assistant') {
      // Parse markdown if marked library is available
      if (window.marked) {
        formattedContent = window.marked.parse(content);
      }
      // Replace [1], [2] etc with interactive badges
      formattedContent = formattedContent.replace(/\[(\d+)\]/g, (match, p1) => {
        const citeInfo = citationsMap[p1];
        const title = citeInfo ? `${citeInfo.source_title}\n${citeInfo.snippet}` : `Citation ${p1}`;
        return `<span class="citation-badge" data-cite-index="${p1}" title="${title}">[${p1}]</span>`;
      });
    }

    msgEl.innerHTML = `
      <div class="message-role-tag">${role === 'user' ? '👤 提问 / Question' : '🤖 AI 助手 / NotebookLM'}</div>
      <div class="message-body">${formattedContent}</div>
      ${role === 'assistant' ? `
        <div class="message-actions">
          <button class="btn btn-sm save-note-action-btn" title="${t('save_to_note')}">💾 ${t('save_to_note')}</button>
        </div>
      ` : ''}
    `;

    // Wire citation badge clicks
    msgEl.querySelectorAll('.citation-badge').forEach(badge => {
      badge.addEventListener('click', () => {
        const idx = parseInt(badge.getAttribute('data-cite-index'));
        const cite = citationsMap[idx];
        if (cite && this.sourcesManager) {
          this.sourcesManager.openSourceDetail(cite.source_id, cite.chunk_index);
        }
      });
    });

    // Wire save to note
    const saveBtn = msgEl.querySelector('.save-note-action-btn');
    if (saveBtn) {
      saveBtn.onclick = async () => {
        const firstLine = content.split('\n')[0].replace(/[#*`]/g, '').trim().slice(0, 30) || 'Chat Insight';
        await API.createNote(this.activeNotebookId, firstLine, content);
        saveBtn.textContent = `✅ ${t('saved_success')}`;
        setTimeout(() => {
          saveBtn.textContent = `💾 ${t('save_to_note')}`;
        }, 2000);
        if (this.notesManager) {
          this.notesManager.loadNotes();
        }
      };
    }

    this.container.appendChild(msgEl);
    this.scrollToBottom();
    return msgEl;
  }

  async sendMessage() {
    if (this.isStreaming) return;
    const text = this.input.value.trim();
    if (!text) return;

    this.input.value = '';
    this.renderMessage('user', text);

    const sourceIds = this.sourcesManager.getSelectedIds();

    // Create assistant message placeholder
    const assistantMsgEl = document.createElement('div');
    assistantMsgEl.className = 'chat-message assistant streaming';
    assistantMsgEl.innerHTML = `
      <div class="message-role-tag">🤖 AI 助手 / NotebookLM</div>
      <div class="message-body"><span class="cursor-blink">▍</span></div>
    `;
    this.container.appendChild(assistantMsgEl);
    this.scrollToBottom();

    const bodyEl = assistantMsgEl.querySelector('.message-body');
    let fullText = '';
    let currentCitations = [];
    this.isStreaming = true;

    await API.streamChat(
      this.activeNotebookId,
      text,
      sourceIds,
      (citations) => {
        currentCitations = citations;
      },
      (token) => {
        fullText += token;
        let rendered = window.marked ? window.marked.parse(fullText) : fullText;
        // Turn [1], [2] into badges on the fly
        rendered = rendered.replace(/\[(\d+)\]/g, `<span class="citation-badge" data-cite-index="$1">[$1]</span>`);
        bodyEl.innerHTML = rendered + '<span class="cursor-blink">▍</span>';
        this.scrollToBottom();
      },
      () => {
        this.isStreaming = false;
        assistantMsgEl.classList.remove('streaming');
        // Replace with finalized message and citations wired
        assistantMsgEl.remove();
        this.renderMessage('assistant', fullText, currentCitations);
      },
      (err) => {
        this.isStreaming = false;
        bodyEl.innerHTML = `<span class="error-text">对话请求失败: ${err.message}</span>`;
      }
    );
  }

  scrollToBottom() {
    this.container.scrollTop = this.container.scrollHeight;
  }
}
