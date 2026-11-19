// Settings Modal Component - Multi-Model Provider Configuration

class SettingsManager {
  constructor() {
    this.modal = document.getElementById('settings-modal');
    this.providerSelect = document.getElementById('setting-provider');
    this.apiKeyInput = document.getElementById('setting-api-key');
    this.baseUrlInput = document.getElementById('setting-base-url');
    this.modelInput = document.getElementById('setting-model');
    this.testBtn = document.getElementById('test-conn-btn');
    this.saveBtn = document.getElementById('save-settings-btn');
    this.statusAlert = document.getElementById('settings-status-alert');
    this.providersData = {};

    this.setupEvents();
  }

  setupEvents() {
    const openBtn = document.getElementById('open-settings-btn');
    if (openBtn) {
      openBtn.onclick = () => this.open();
    }

    const closeBtn = document.getElementById('close-settings-modal');
    if (closeBtn) {
      closeBtn.onclick = () => this.close();
    }

    this.providerSelect.onchange = () => this.onProviderChange();
    this.testBtn.onclick = () => this.testConnection();
    this.saveBtn.onclick = () => this.save();
  }

  async open() {
    this.modal.style.display = 'flex';
    this.statusAlert.style.display = 'none';
    try {
      const data = await API.getSettings();
      this.providersData = data.providers || {};
      this.providerSelect.value = data.active_provider || 'deepseek';
      this.onProviderChange();
    } catch (e) {
      console.error('Failed to load settings', e);
    }
  }

  close() {
    this.modal.style.display = 'none';
  }

  onProviderChange() {
    const prov = this.providerSelect.value;
    const pData = this.providersData[prov] || {};

    this.baseUrlInput.value = pData.base_url || '';
    this.modelInput.value = pData.model || '';
    this.apiKeyInput.value = '';
    this.apiKeyInput.placeholder = pData.has_key ? `已配置 (${pData.masked_key})，留空保持不变` : '请输入 API Key';
  }

  async testConnection() {
    const prov = this.providerSelect.value;
    const apiKey = this.apiKeyInput.value.trim();
    const baseUrl = this.baseUrlInput.value.trim();
    const model = this.modelInput.value.trim();

    this.statusAlert.style.display = 'block';
    this.statusAlert.className = 'alert alert-info';
    this.statusAlert.textContent = '正在测试连接中... / Testing connection...';

    try {
      const res = await API.testConnection(prov, apiKey, baseUrl, model);
      if (res.status === 'success') {
        this.statusAlert.className = 'alert alert-success';
        this.statusAlert.textContent = '✅ ' + res.message;
      } else {
        this.statusAlert.className = 'alert alert-danger';
        this.statusAlert.textContent = '❌ ' + res.message;
      }
    } catch (e) {
      this.statusAlert.className = 'alert alert-danger';
      this.statusAlert.textContent = '❌ 连接失败: ' + e.message;
    }
  }

  async save() {
    const prov = this.providerSelect.value;
    const apiKey = this.apiKeyInput.value.trim();
    const baseUrl = this.baseUrlInput.value.trim();
    const model = this.modelInput.value.trim();

    try {
      await API.saveSettings(prov, apiKey, baseUrl, model);
      this.statusAlert.style.display = 'block';
      this.statusAlert.className = 'alert alert-success';
      this.statusAlert.textContent = `✅ ${t('saved_ok')}`;
      setTimeout(() => {
        this.close();
      }, 1200);
    } catch (e) {
      this.statusAlert.style.display = 'block';
      this.statusAlert.className = 'alert alert-danger';
      this.statusAlert.textContent = '保存失败: ' + e.message;
    }
  }
}
