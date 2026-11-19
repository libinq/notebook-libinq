// API Client for Open Notebook Bilingual

const API = {
  // Notebooks
  async getNotebooks() {
    const res = await fetch('/api/notebooks');
    return res.json();
  },
  async createNotebook(title, description = '') {
    const res = await fetch('/api/notebooks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description })
    });
    return res.json();
  },
  async deleteNotebook(id) {
    const res = await fetch(`/api/notebooks/${id}`, { method: 'DELETE' });
    return res.json();
  },

  // Sources
  async getSources(notebookId) {
    const res = await fetch(`/api/sources?notebook_id=${notebookId}`);
    return res.json();
  },
  async getSourceDetail(sourceId) {
    const res = await fetch(`/api/sources/${sourceId}`);
    return res.json();
  },
  async uploadFile(notebookId, file) {
    const formData = new FormData();
    formData.append('notebook_id', notebookId);
    formData.append('file', file);
    const res = await fetch('/api/sources/upload', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },
  async addUrl(notebookId, url) {
    const res = await fetch('/api/sources/url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notebook_id: notebookId, url })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to add URL');
    }
    return res.json();
  },
  async addText(notebookId, title, content) {
    const res = await fetch('/api/sources/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notebook_id: notebookId, title, content })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to add text');
    }
    return res.json();
  },
  async deleteSource(sourceId) {
    const res = await fetch(`/api/sources/${sourceId}`, { method: 'DELETE' });
    return res.json();
  },

  // Chat
  async getChatHistory(notebookId) {
    const res = await fetch(`/api/chat/history?notebook_id=${notebookId}`);
    return res.json();
  },
  async clearChatHistory(notebookId) {
    const res = await fetch(`/api/chat/history?notebook_id=${notebookId}`, { method: 'DELETE' });
    return res.json();
  },
  async streamChat(notebookId, message, sourceIds, onCitation, onToken, onDone, onError) {
    try {
      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notebook_id: notebookId, message, source_ids: sourceIds })
      });

      if (!res.ok) {
        throw new Error(`Chat error (${res.status})`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data:')) continue;
          const dataStr = line.slice(5).trim();
          if (dataStr === '[DONE]') {
            onDone();
            return;
          }
          try {
            const parsed = JSON.parse(dataStr);
            if (parsed.type === 'citations') {
              onCitation(parsed.citations);
            } else if (parsed.type === 'token') {
              onToken(parsed.token);
            }
          } catch (e) {
            console.error('SSE JSON parse error', e);
          }
        }
      }
      onDone();
    } catch (err) {
      onError(err);
    }
  },

  // Podcasts
  async getPodcasts(notebookId) {
    const res = await fetch(`/api/podcast?notebook_id=${notebookId}`);
    return res.json();
  },
  async generatePodcast(notebookId, formatType, language, durationMode, guidance, sourceIds) {
    const res = await fetch('/api/podcast/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        notebook_id: notebookId,
        format_type: formatType,
        language: language,
        duration_mode: durationMode,
        guidance: guidance,
        source_ids: sourceIds
      })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Podcast generation failed');
    }
    return res.json();
  },
  async deletePodcast(id) {
    const res = await fetch(`/api/podcast/${id}`, { method: 'DELETE' });
    return res.json();
  },

  // Studio
  async getStudioArtifacts(notebookId) {
    const res = await fetch(`/api/studio?notebook_id=${notebookId}`);
    return res.json();
  },
  async generateStudioArtifact(notebookId, artifactType, language, sourceIds) {
    const res = await fetch('/api/studio/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        notebook_id: notebookId,
        artifact_type: artifactType,
        language: language,
        source_ids: sourceIds
      })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Studio generation failed');
    }
    return res.json();
  },
  async deleteStudioArtifact(id) {
    const res = await fetch(`/api/studio/${id}`, { method: 'DELETE' });
    return res.json();
  },

  // Notes
  async getNotes(notebookId) {
    const res = await fetch(`/api/notes?notebook_id=${notebookId}`);
    return res.json();
  },
  async createNote(notebookId, title, content) {
    const res = await fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notebook_id: notebookId, title, content })
    });
    return res.json();
  },
  async updateNote(id, title, content) {
    const res = await fetch(`/api/notes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content })
    });
    return res.json();
  },
  async deleteNote(id) {
    const res = await fetch(`/api/notes/${id}`, { method: 'DELETE' });
    return res.json();
  },
  async promoteNote(id) {
    const res = await fetch(`/api/notes/${id}/promote`, { method: 'POST' });
    return res.json();
  },

  // Settings
  async getSettings() {
    const res = await fetch('/api/settings');
    return res.json();
  },
  async saveSettings(provider, apiKey, baseUrl, model) {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider,
        api_key: apiKey,
        base_url: baseUrl,
        model
      })
    });
    return res.json();
  },
  async testConnection(provider, apiKey, baseUrl, model) {
    const res = await fetch('/api/settings/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider,
        api_key: apiKey,
        base_url: baseUrl,
        model
      })
    });
    return res.json();
  }
};
