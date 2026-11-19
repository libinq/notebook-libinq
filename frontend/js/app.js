// Main Application Controller

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize i18n
  updateDOMTranslations();

  // Language switch
  const langBtn = document.getElementById('lang-switch-btn');
  if (langBtn) {
    langBtn.onclick = () => {
      toggleLanguage();
    };
  }

  // Dark/Light Theme toggle
  const themeBtn = document.getElementById('theme-toggle-btn');
  let isDark = localStorage.getItem('theme') === 'dark';
  const applyTheme = () => {
    document.body.classList.toggle('dark-mode', isDark);
    themeBtn.textContent = isDark ? '☀️ ' + t('theme_light') : '🌙 ' + t('theme_dark');
  };
  applyTheme();
  themeBtn.onclick = () => {
    isDark = !isDark;
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    applyTheme();
  };

  // Instantiate Sub-Managers
  const sourcesManager = new SourcesManager();
  const notesManager = new NotesManager(sourcesManager);
  const chatManager = new ChatManager(sourcesManager, notesManager);
  const studioManager = new StudioManager(sourcesManager, notesManager);
  const settingsManager = new SettingsManager();

  // Right sidebar tab switching (Studio vs Notes)
  const tabStudioBtn = document.getElementById('tab-studio-btn');
  const tabNotesBtn = document.getElementById('tab-notes-btn');
  const panelStudio = document.getElementById('panel-studio');
  const panelNotes = document.getElementById('panel-notes');

  tabStudioBtn.onclick = () => {
    tabStudioBtn.classList.add('active');
    tabNotesBtn.classList.remove('active');
    panelStudio.style.display = 'block';
    panelNotes.style.display = 'none';
  };

  tabNotesBtn.onclick = () => {
    tabNotesBtn.classList.add('active');
    tabStudioBtn.classList.remove('active');
    panelNotes.style.display = 'block';
    panelStudio.style.display = 'none';
  };

  // Notebooks setup
  const notebookSelect = document.getElementById('notebook-select');
  const newNotebookBtn = document.getElementById('new-notebook-btn');
  const deleteNotebookBtn = document.getElementById('delete-notebook-btn');

  let currentNotebookId = null;

  async function loadNotebooks() {
    const data = await API.getNotebooks();
    const notebooks = data.notebooks || [];
    notebookSelect.innerHTML = notebooks.map(n => `
      <option value="${n.id}">${n.title}</option>
    `).join('');

    if (notebooks.length > 0) {
      currentNotebookId = notebooks[0].id;
      notebookSelect.value = currentNotebookId;
      switchNotebook(currentNotebookId);
    }
  }

  function switchNotebook(id) {
    currentNotebookId = id;
    sourcesManager.setNotebook(id);
    chatManager.setNotebook(id);
    studioManager.setNotebook(id);
    notesManager.setNotebook(id);
  }

  notebookSelect.onchange = (e) => {
    switchNotebook(e.target.value);
  };

  newNotebookBtn.onclick = async () => {
    const title = prompt(t('notebook_name_prompt'));
    if (title && title.trim()) {
      const nb = await API.createNotebook(title.trim());
      await loadNotebooks();
      notebookSelect.value = nb.id;
      switchNotebook(nb.id);
    }
  };

  deleteNotebookBtn.onclick = async () => {
    if (confirm(t('delete_notebook_confirm'))) {
      await API.deleteNotebook(currentNotebookId);
      await loadNotebooks();
    }
  };

  // Select all / unselect all sources
  document.getElementById('select-all-sources-btn').onclick = () => sourcesManager.selectAll();
  document.getElementById('unselect-all-sources-btn').onclick = () => sourcesManager.unselectAll();

  // Add Source Modal
  const addSourceModal = document.getElementById('add-source-modal');
  const openAddSourceBtn = document.getElementById('add-source-btn');
  const closeAddSourceBtn = document.getElementById('close-add-source-modal');

  openAddSourceBtn.onclick = () => addSourceModal.style.display = 'flex';
  closeAddSourceBtn.onclick = () => addSourceModal.style.display = 'none';

  // Add Source Tab controls
  const srcTabFile = document.getElementById('src-tab-file');
  const srcTabUrl = document.getElementById('src-tab-url');
  const srcTabText = document.getElementById('src-tab-text');
  const srcBodyFile = document.getElementById('src-body-file');
  const srcBodyUrl = document.getElementById('src-body-url');
  const srcBodyText = document.getElementById('src-body-text');

  function selectSourceTypeTab(type) {
    [srcTabFile, srcTabUrl, srcTabText].forEach(t => t.classList.remove('active'));
    [srcBodyFile, srcBodyUrl, srcBodyText].forEach(b => b.style.display = 'none');
    if (type === 'file') {
      srcTabFile.classList.add('active');
      srcBodyFile.style.display = 'block';
    } else if (type === 'url') {
      srcTabUrl.classList.add('active');
      srcBodyUrl.style.display = 'block';
    } else {
      srcTabText.classList.add('active');
      srcBodyText.style.display = 'block';
    }
  }

  srcTabFile.onclick = () => selectSourceTypeTab('file');
  srcTabUrl.onclick = () => selectSourceTypeTab('url');
  srcTabText.onclick = () => selectSourceTypeTab('text');

  // File Upload
  const fileInput = document.getElementById('source-file-input');
  const fileSubmitBtn = document.getElementById('submit-file-btn');
  fileSubmitBtn.onclick = async () => {
    if (!fileInput.files || fileInput.files.length === 0) return alert('请先选择文件');
    const file = fileInput.files[0];
    fileSubmitBtn.textContent = '正在解析中...';
    try {
      await API.uploadFile(currentNotebookId, file);
      fileSubmitBtn.textContent = '上传完成';
      setTimeout(() => {
        addSourceModal.style.display = 'none';
        fileSubmitBtn.textContent = '开始上传与解析';
        fileInput.value = '';
        sourcesManager.loadSources();
      }, 800);
    } catch (e) {
      alert('上传解析失败: ' + e.message);
      fileSubmitBtn.textContent = '开始上传与解析';
    }
  };

  // URL / YouTube Submit
  const urlInput = document.getElementById('source-url-input');
  const urlSubmitBtn = document.getElementById('submit-url-btn');
  urlSubmitBtn.onclick = async () => {
    const url = urlInput.value.trim();
    if (!url) return alert('请输入网址');
    urlSubmitBtn.textContent = '正在抓取正文...';
    try {
      await API.addUrl(currentNotebookId, url);
      addSourceModal.style.display = 'none';
      urlInput.value = '';
      urlSubmitBtn.textContent = '抓取并添加到来源';
      sourcesManager.loadSources();
    } catch (e) {
      alert('抓取失败: ' + e.message);
      urlSubmitBtn.textContent = '抓取并添加到来源';
    }
  };

  // Text Submit
  const textTitleInput = document.getElementById('source-text-title');
  const textContentInput = document.getElementById('source-text-content');
  const textSubmitBtn = document.getElementById('submit-text-btn');
  textSubmitBtn.onclick = async () => {
    const title = textTitleInput.value.trim();
    const content = textContentInput.value.trim();
    if (!content) return alert('请输入文本内容');
    textSubmitBtn.textContent = '正在保存...';
    try {
      await API.addText(currentNotebookId, title, content);
      addSourceModal.style.display = 'none';
      textTitleInput.value = '';
      textContentInput.value = '';
      textSubmitBtn.textContent = '保存为新来源';
      sourcesManager.loadSources();
    } catch (e) {
      alert('保存失败: ' + e.message);
      textSubmitBtn.textContent = '保存为新来源';
    }
  };

  // Close modals on overlay click
  window.onclick = (e) => {
    if (e.target.classList.contains('modal-overlay')) {
      e.target.style.display = 'none';
    }
  };

  // Studio modal close
  document.getElementById('close-studio-modal').onclick = () => {
    document.getElementById('studio-modal').style.display = 'none';
  };

  // Initial load
  await loadNotebooks();
});
