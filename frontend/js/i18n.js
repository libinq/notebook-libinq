// Bilingual Dictionary for Chinese (Simplified) and English

const translations = {
  "zh": {
    // App header
    "app_title": "Open Notebook",
    "app_badge": "双语增强版 · 对标 NotebookLM",
    "switch_lang": "English",
    "theme_light": "浅色",
    "theme_dark": "深色",
    "settings_btn": "模型设置",
    
    // Notebooks
    "notebook_selector": "选择笔记本",
    "new_notebook": "新建笔记本",
    "notebook_name_prompt": "请输入笔记本名称：",
    "delete_notebook_confirm": "确定删除此笔记本及其所有来源与笔记吗？",
    
    // Left column: Sources
    "sources_title": "来源资料",
    "add_source": "添加来源",
    "source_types": "支持 PDF, Word, PPT, Excel, 网页链接, YouTube",
    "select_all": "全选",
    "unselect_all": "取消全选",
    "upload_file": "上传本地文件",
    "add_web_url": "添加网页链接",
    "add_youtube": "添加 YouTube 视频",
    "paste_text": "粘贴文本",
    "source_empty": "尚未添加任何资料，请点击上方按钮添加。",
    "view_source": "查看原文与分块",
    "delete_source_confirm": "确定删除该来源吗？",
    
    // Middle column: Chat
    "chat_title": "来源对话与引用溯源",
    "chat_placeholder": "基于所选来源向 AI 提问...（支持中英文）",
    "chat_clear": "清空对话",
    "chat_clear_confirm": "确定清空当前对话记录吗？",
    "send_btn": "发送",
    "sources_selected_hint": "已勾选 {count} 个来源参与回答",
    "thinking_hint": "AI 正在分析资料并组织回答...",
    "citation_tooltip": "点击跳转到原文分块高亮：",
    "save_to_note": "保存为笔记",
    "saved_success": "已保存到笔记库！",
    
    // Right column: Studio & Notes
    "studio_tab": "Studio 创意工坊",
    "notes_tab": "知识笔记",
    "studio_desc": "将多模态资料一键转化为高价值知识成果",
    
    // Studio Tools
    "tool_mindmap": "交互式思维导图",
    "tool_mindmap_desc": "可视化展示知识脉络与层级结构",
    "tool_podcast": "AI 音频对谈 / 播客",
    "tool_podcast_desc": "双人对谈、速报、评审批判与辩论",
    "tool_briefing": "执行简报",
    "tool_briefing_desc": "结构化高层总结与战略建议",
    "tool_study_guide": "深度学习指南",
    "tool_study_guide_desc": "核心术语、定义与考点解析",
    "tool_faq": "常见问题解答 (FAQ)",
    "tool_faq_desc": "梳理最核心的问答集",
    "tool_timeline": "事件时间线",
    "tool_timeline_desc": "脉络梳理与关键里程碑",
    "tool_quiz": "互动测验与考核",
    "tool_quiz_desc": "选择题与开放式思考题自测",
    "tool_flashcards": "抽认卡 (Flashcards)",
    "tool_flashcards_desc": "双面卡片翻转辅助主动回忆",
    "tool_presentation": "幻灯片大纲 & PPTX",
    "tool_presentation_desc": "演示文稿大纲并导出 .pptx 文件",
    
    // Podcast Controls
    "podcast_format": "播客模式：",
    "format_deep_dive": "深度对谈 (Deep Dive - 双人启发式)",
    "format_brief": "极简速报 (The Brief - 单人精练)",
    "format_critique": "专家评审 (The Critique - 挑剔检视)",
    "format_debate": "正反辩论 (The Debate - 观点交锋)",
    "podcast_duration": "预计时长：",
    "duration_short": "简短 (1-2 分钟)",
    "duration_medium": "标准 (5-8 分钟)",
    "duration_long": "深度 (15+ 分钟)",
    "podcast_guidance": "引导提示词 (选填)：",
    "podcast_guidance_ph": "例如：着重探讨技术挑战和商业落地，语气幽默风趣...",
    "generate_podcast_btn": "生成音频播客",
    "generating_podcast": "正在创作播客脚本并合成双语音频，请稍候...",
    "download_audio": "下载音频 (.mp3)",
    "download_pptx": "下载演示文稿 (.pptx)",
    
    // Notes
    "new_note": "新建笔记",
    "note_title_ph": "笔记标题",
    "note_content_ph": "输入笔记内容...",
    "save_note_btn": "保存修改",
    "promote_note": "转为知识来源 (RAG 回流)",
    "promoted_badge": "已作为来源",
    "notes_empty": "暂无笔记，点击上方新建或在对话中「保存为笔记」",
    
    // Settings Modal
    "settings_title": "大模型与 API 配置",
    "provider_label": "选择 AI 服务商：",
    "api_key_label": "API Key：",
    "base_url_label": "接口地址 (Base URL)：",
    "model_label": "模型 ID (Model Name)：",
    "test_btn": "测试连接",
    "save_settings_btn": "保存并启用",
    "saved_ok": "配置已保存并生效！"
  },
  
  "en": {
    // App header
    "app_title": "Open Notebook",
    "app_badge": "Bilingual Pro · NotebookLM Parity",
    "switch_lang": "中文",
    "theme_light": "Light",
    "theme_dark": "Dark",
    "settings_btn": "Model Settings",
    
    // Notebooks
    "notebook_selector": "Select Notebook",
    "new_notebook": "New Notebook",
    "notebook_name_prompt": "Enter notebook name:",
    "delete_notebook_confirm": "Delete this notebook and all its sources?",
    
    // Left column: Sources
    "sources_title": "Sources",
    "add_source": "Add Source",
    "source_types": "Supports PDF, Word, PPT, Excel, Web URLs, YouTube",
    "select_all": "Select All",
    "unselect_all": "Unselect All",
    "upload_file": "Upload Local File",
    "add_web_url": "Add Web URL",
    "add_youtube": "Add YouTube Video",
    "paste_text": "Paste Text",
    "source_empty": "No sources added yet. Click above to add.",
    "view_source": "View Source & Chunks",
    "delete_source_confirm": "Delete this source?",
    
    // Middle column: Chat
    "chat_title": "Chat & Inline Grounding",
    "chat_placeholder": "Ask anything about selected sources...",
    "chat_clear": "Clear History",
    "chat_clear_confirm": "Clear current chat history?",
    "send_btn": "Send",
    "sources_selected_hint": "{count} sources selected for answer",
    "thinking_hint": "Analyzing sources and synthesizing response...",
    "citation_tooltip": "Click to highlight source chunk:",
    "save_to_note": "Save as Note",
    "saved_success": "Saved to notes!",
    
    // Right column: Studio & Notes
    "studio_tab": "Studio",
    "notes_tab": "Notes",
    "studio_desc": "Transform multi-modal sources into rich knowledge artifacts",
    
    // Studio Tools
    "tool_mindmap": "Interactive Mind Map",
    "tool_mindmap_desc": "Visualize concept hierarchy and relationships",
    "tool_podcast": "AI Audio Overview / Podcast",
    "tool_podcast_desc": "Deep Dive, Brief, Critique, and Debate",
    "tool_briefing": "Executive Briefing Doc",
    "tool_briefing_desc": "High-level strategic summary and findings",
    "tool_study_guide": "Study Guide",
    "tool_study_guide_desc": "Key concepts, glossary, and review points",
    "tool_faq": "FAQ Guide",
    "tool_faq_desc": "Frequently asked questions with answers",
    "tool_timeline": "Timeline",
    "tool_timeline_desc": "Chronological progression & milestones",
    "tool_quiz": "Quiz & Knowledge Check",
    "tool_quiz_desc": "Multiple choice & discussion questions",
    "tool_flashcards": "Flashcards",
    "tool_flashcards_desc": "Flippable cards for active recall testing",
    "tool_presentation": "Presentation Deck & PPTX",
    "tool_presentation_desc": "Slide outlines with direct .pptx download",
    
    // Podcast Controls
    "podcast_format": "Podcast Format:",
    "format_deep_dive": "Deep Dive (Conversational exploration)",
    "format_brief": "The Brief (Rapid 1-2 min executive summary)",
    "format_critique": "The Critique (Constructive skepticism)",
    "format_debate": "The Debate (Opposing perspectives)",
    "podcast_duration": "Length:",
    "duration_short": "Short (1-2 min)",
    "duration_medium": "Standard (5-8 min)",
    "duration_long": "Deep (15+ min)",
    "podcast_guidance": "Guidance Prompt (Optional):",
    "podcast_guidance_ph": "e.g. Focus on technical challenges, maintain a lively tone...",
    "generate_podcast_btn": "Generate Audio Podcast",
    "generating_podcast": "Generating script and synthesizing neural audio...",
    "download_audio": "Download Audio (.mp3)",
    "download_pptx": "Download Presentation (.pptx)",
    
    // Notes
    "new_note": "New Note",
    "note_title_ph": "Note Title",
    "note_content_ph": "Type your note here...",
    "save_note_btn": "Save Note",
    "promote_note": "Promote to Source (RAG Loop)",
    "promoted_badge": "Active Source",
    "notes_empty": "No notes yet. Create one or save from chat answers.",
    
    // Settings Modal
    "settings_title": "Model & API Configuration",
    "provider_label": "AI Provider:",
    "api_key_label": "API Key:",
    "base_url_label": "Base URL:",
    "model_label": "Model Name:",
    "test_btn": "Test Connection",
    "save_settings_btn": "Save & Apply",
    "saved_ok": "Configuration saved successfully!"
  }
};

let currentLang = localStorage.getItem("open_notebook_lang") || "zh";

function t(key, params = {}) {
  const dict = translations[currentLang] || translations["zh"];
  let str = dict[key] || translations["en"][key] || key;
  for (const [k, v] of Object.entries(params)) {
    str = str.replace(`{${k}}`, v);
  }
  return str;
}

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("open_notebook_lang", lang);
  updateDOMTranslations();
}

function toggleLanguage() {
  setLanguage(currentLang === "zh" ? "en" : "zh");
}

function updateDOMTranslations() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    el.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-ph]").forEach(el => {
    const key = el.getAttribute("data-i18n-ph");
    el.setAttribute("placeholder", t(key));
  });
  document.querySelectorAll("[data-i18n-title]").forEach(el => {
    const key = el.getAttribute("data-i18n-title");
    el.setAttribute("title", t(key));
  });
  
  const switchBtn = document.getElementById("lang-switch-btn");
  if (switchBtn) {
    switchBtn.textContent = currentLang === "zh" ? "English" : "中文";
  }
}
