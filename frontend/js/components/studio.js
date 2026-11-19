// Studio Component - Managing Google NotebookLM Parity Knowledge Artifacts & Podcast

class StudioManager {
  constructor(sourcesManager, notesManager) {
    this.sourcesManager = sourcesManager;
    this.notesManager = notesManager;
    this.container = document.getElementById('studio-content');
    this.activeNotebookId = null;
    this.artifacts = [];
    this.activeTool = null;
    this.mindmapViewer = null;

    this.setupUI();
  }

  setNotebook(notebookId) {
    this.activeNotebookId = notebookId;
    this.loadArtifacts();
  }

  setupUI() {
    this.renderToolSelector();
  }

  renderToolSelector() {
    const tools = [
      { id: 'podcast', icon: '🎙️', nameKey: 'tool_podcast', descKey: 'tool_podcast_desc', badge: 'Audio Overview' },
      { id: 'mindmap', icon: '🧠', nameKey: 'tool_mindmap', descKey: 'tool_mindmap_desc', badge: 'Interactive' },
      { id: 'briefing', icon: '📋', nameKey: 'tool_briefing', descKey: 'tool_briefing_desc', badge: 'Executive' },
      { id: 'study_guide', icon: '📖', nameKey: 'tool_study_guide', descKey: 'tool_study_guide_desc', badge: 'Learning' },
      { id: 'faq', icon: '❓', nameKey: 'tool_faq', descKey: 'tool_faq_desc', badge: 'Q&A' },
      { id: 'timeline', icon: '⏳', nameKey: 'tool_timeline', descKey: 'tool_timeline_desc', badge: 'History' },
      { id: 'quiz', icon: '🎯', nameKey: 'tool_quiz', descKey: 'tool_quiz_desc', badge: 'Testing' },
      { id: 'flashcards', icon: '🃏', nameKey: 'tool_flashcards', descKey: 'tool_flashcards_desc', badge: 'Active Recall' },
      { id: 'presentation', icon: '📊', nameKey: 'tool_presentation', descKey: 'tool_presentation_desc', badge: 'PPTX Export' }
    ];

    const selectorContainer = document.getElementById('studio-tools-grid');
    if (!selectorContainer) return;

    selectorContainer.innerHTML = tools.map(tInfo => `
      <div class="studio-card" data-tool="${tInfo.id}">
        <div class="studio-card-header">
          <span class="studio-card-icon">${tInfo.icon}</span>
          <span class="studio-badge">${tInfo.badge}</span>
        </div>
        <div class="studio-card-title">${t(tInfo.nameKey)}</div>
        <div class="studio-card-desc">${t(tInfo.descKey)}</div>
      </div>
    `).join('');

    selectorContainer.querySelectorAll('.studio-card').forEach(card => {
      card.addEventListener('click', () => {
        const tool = card.getAttribute('data-tool');
        this.openTool(tool);
      });
    });
  }

  async loadArtifacts() {
    if (!this.activeNotebookId) return;
    try {
      const data = await API.getStudioArtifacts(this.activeNotebookId);
      this.artifacts = data.artifacts || [];
      this.renderRecentArtifacts();
    } catch (e) {
      console.error('Failed to load artifacts', e);
    }
  }

  renderRecentArtifacts() {
    const listEl = document.getElementById('studio-artifacts-list');
    if (!listEl) return;
    if (this.artifacts.length === 0) {
      listEl.innerHTML = '<div class="empty-state-small">暂无已生成的工坊成果，请点击上方卡片创建。</div>';
      return;
    }

    listEl.innerHTML = this.artifacts.map(a => `
      <div class="artifact-item" data-id="${a.id}">
        <div class="artifact-info">
          <strong>${a.title}</strong>
          <span class="meta">${new Date(a.created_at).toLocaleString()}</span>
        </div>
        <div class="artifact-actions">
          <button class="btn btn-sm view-artifact-btn" data-id="${a.id}">查看 / View</button>
          <button class="btn-icon delete-artifact-btn" data-id="${a.id}">🗑️</button>
        </div>
      </div>
    `).join('');

    listEl.querySelectorAll('.view-artifact-btn').forEach(btn => {
      btn.onclick = () => {
        const id = btn.getAttribute('data-id');
        const art = this.artifacts.find(x => x.id === id);
        if (art) this.displayArtifactResult(art.artifact_type, art.content);
      };
    });

    listEl.querySelectorAll('.delete-artifact-btn').forEach(btn => {
      btn.onclick = async () => {
        const id = btn.getAttribute('data-id');
        await API.deleteStudioArtifact(id);
        this.loadArtifacts();
      };
    });
  }

  openTool(toolId) {
    this.activeTool = toolId;
    const modal = document.getElementById('studio-modal');
    modal.style.display = 'flex';
    
    const titleEl = document.getElementById('studio-modal-title');
    const bodyEl = document.getElementById('studio-modal-body');

    if (toolId === 'podcast') {
      titleEl.textContent = '🎙️ AI 音频对谈 / Podcast Studio (对标 NotebookLM)';
      bodyEl.innerHTML = `
        <div class="podcast-config-form">
          <div class="form-group">
            <label><strong>${t('podcast_format')}</strong></label>
            <select id="p-format" class="form-control">
              <option value="deep_dive">${t('format_deep_dive')}</option>
              <option value="brief">${t('format_brief')}</option>
              <option value="critique">${t('format_critique')}</option>
              <option value="debate">${t('format_debate')}</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group half">
              <label><strong>语种 / Language:</strong></label>
              <select id="p-lang" class="form-control">
                <option value="zh">🇨🇳 中文普通话 (晓晓 & 云希 自然音色)</option>
                <option value="en">🇺🇸 English (Jenny & Guy Neural)</option>
              </select>
            </div>
            <div class="form-group half">
              <label><strong>${t('podcast_duration')}</strong></label>
              <select id="p-duration" class="form-control">
                <option value="short">${t('duration_short')}</option>
                <option value="medium" selected>${t('duration_medium')}</option>
                <option value="long">${t('duration_long')}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label><strong>${t('podcast_guidance')}</strong></label>
            <input type="text" id="p-guidance" class="form-control" placeholder="${t('podcast_guidance_ph')}">
          </div>
          <button id="p-generate-btn" class="btn btn-primary btn-block">🚀 ${t('generate_podcast_btn')}</button>
          <div id="p-result-area" style="margin-top:20px;"></div>
        </div>
      `;

      bodyEl.querySelector('#p-generate-btn').onclick = () => this.generatePodcastAction();
    } else {
      titleEl.textContent = `工坊生成 / Studio: ${toolId.toUpperCase()}`;
      bodyEl.innerHTML = `
        <div class="studio-generate-prompt">
          <p>基于当前勾选的来源资料，系统将使用大模型提炼并生成 <strong>${toolId}</strong>。</p>
          <div class="form-group">
            <label>生成语种 / Language:</label>
            <select id="artifact-lang" class="form-control">
              <option value="zh">中文 (简体)</option>
              <option value="en">English</option>
            </select>
          </div>
          <button id="generate-artifact-btn" class="btn btn-primary">⚡ 开始生成 / Generate Now</button>
          <div id="artifact-result-area" style="margin-top:20px;"></div>
        </div>
      `;

      bodyEl.querySelector('#generate-artifact-btn').onclick = () => this.generateArtifactAction(toolId);
    }
  }

  async generatePodcastAction() {
    const formatType = document.getElementById('p-format').value;
    const language = document.getElementById('p-lang').value;
    const durationMode = document.getElementById('p-duration').value;
    const guidance = document.getElementById('p-guidance').value;
    const resArea = document.getElementById('p-result-area');

    resArea.innerHTML = `
      <div class="loading-state">
        <div class="spinner"></div>
        <p>${t('generating_podcast')}</p>
      </div>
    `;

    try {
      const sourceIds = this.sourcesManager.getSelectedIds();
      const result = await API.generatePodcast(
        this.activeNotebookId,
        formatType,
        language,
        durationMode,
        guidance,
        sourceIds
      );
      this.displayPodcastResult(result, resArea);
    } catch (e) {
      resArea.innerHTML = `<div class="error-state">播客生成失败: ${e.message}</div>`;
    }
  }

  displayPodcastResult(podcast, container) {
    container.innerHTML = `
      <div class="podcast-result-card">
        <h3>🎉 ${podcast.title}</h3>
        ${podcast.audio_url ? `
          <div class="audio-player-wrapper">
            <audio controls src="${podcast.audio_url}" style="width: 100%; margin: 15px 0;"></audio>
            <div>
              <a href="${podcast.audio_url}" download="podcast.mp3" class="btn btn-sm btn-outline">⬇️ ${t('download_audio')}</a>
            </div>
          </div>
        ` : '<div class="alert alert-warning">音频正在生成中或已完成文字剧本</div>'}
        <div class="podcast-transcript-header">
          <strong>对话逐字稿 / Dialogue Transcript:</strong>
        </div>
        <div class="podcast-script-turns">
          ${(podcast.script || []).map((t, i) => `
            <div class="script-turn ${i % 2 === 0 ? 'speaker-a' : 'speaker-b'}">
              <div class="speaker-name">🎙️ ${t.speaker}</div>
              <div class="speaker-text">${t.text}</div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  async generateArtifactAction(toolId) {
    const lang = document.getElementById('artifact-lang').value;
    const resArea = document.getElementById('artifact-result-area');
    resArea.innerHTML = `
      <div class="loading-state">
        <div class="spinner"></div>
        <p>AI 正在深度研读资料并生成中，请稍候...</p>
      </div>
    `;

    try {
      const sourceIds = this.sourcesManager.getSelectedIds();
      const res = await API.generateStudioArtifact(this.activeNotebookId, toolId, lang, sourceIds);
      this.displayArtifactResult(toolId, res.content, resArea);
      this.loadArtifacts();
    } catch (e) {
      resArea.innerHTML = `<div class="error-state">生成失败: ${e.message}</div>`;
    }
  }

  displayArtifactResult(toolId, content, targetContainer = null) {
    const container = targetContainer || document.getElementById('studio-modal-body');
    const modal = document.getElementById('studio-modal');
    modal.style.display = 'flex';

    if (toolId === 'mindmap' && content.data) {
      container.innerHTML = `<div id="mindmap-canvas" style="width: 100%; height: 500px; background: #fafafa; border: 1px solid #e2e8f0; border-radius: 8px;"></div>`;
      this.mindmapViewer = new MindMapViewer('mindmap-canvas');
      this.mindmapViewer.render(content.data);
    } else if (toolId === 'flashcards' && content.data) {
      const cards = content.data.flashcards || [];
      container.innerHTML = `
        <div class="flashcards-grid">
          ${cards.map((c, i) => `
            <div class="flashcard-card" onclick="this.classList.toggle('flipped')">
              <div class="flashcard-inner">
                <div class="flashcard-front">
                  <span class="card-num">#${i + 1} ${c.category || 'Concept'}</span>
                  <div class="card-q">${c.question}</div>
                  <span class="card-hint">点击翻转查看解析 👆</span>
                </div>
                <div class="flashcard-back">
                  <span class="card-num">#${i + 1} 答案解析</span>
                  <div class="card-a">${c.answer}</div>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    } else if (toolId === 'presentation') {
      const pptData = content.data || {};
      container.innerHTML = `
        <div class="presentation-result">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <h3>📊 ${pptData.title || '演示文稿'}</h3>
            ${content.pptx_url ? `
              <a href="${content.pptx_url}" class="btn btn-primary" download>⬇️ ${t('download_pptx')}</a>
            ` : ''}
          </div>
          <div class="slides-preview-list">
            ${(pptData.slides || []).map(s => `
              <div class="slide-card">
                <div class="slide-header">Slide ${s.slide_number}: ${s.title}</div>
                <ul class="slide-bullets">
                  ${(s.bullets || []).map(b => `<li>${b}</li>`).join('')}
                </ul>
                ${s.speaker_notes ? `<div class="slide-notes"><strong>演讲者备注:</strong> ${s.speaker_notes}</div>` : ''}
              </div>
            `).join('')}
          </div>
        </div>
      `;
    } else {
      // Markdown render
      const md = content.markdown || content.raw || '';
      const html = window.marked ? window.marked.parse(md) : md;
      container.innerHTML = `
        <div class="markdown-artifact-view">
          ${html}
        </div>
      `;
    }
  }
}
