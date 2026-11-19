# Open Notebook Bilingual (双语增强版)

> **基于 Open Notebook 开源框架理念深度打造，全链路支持中英双语，100% 对标 Google NotebookLM 最新最全能力集。**

---

## 🌟 项目亮点 (Highlights)

- 🔒 **数据自主与隐私主权 (100% Private & Self-Hosted)**：所有笔记、文档、向量与对话均存储在本地（SQLite），杜绝数据外泄与云端模型训练风险。
- 🌐 **全链路中英双语 (Full-Link Bilingual Support)**：UI 界面一键中英文切换、中英双语优化提示词、双语分词混合检索、中英文自然人声音频播客合成。
- 🎙️ **对标 Google NotebookLM 最新全能播客工坊 (Audio Overview Suite)**：
  - **4 种最新音频格式**：深度对谈 (Deep Dive)、极简速报 (The Brief)、专家评审 (The Critique)、正反辩论 (The Debate)。
  - **时长控制与自定义指令**：支持 Short (1-2分钟)、Medium (5-8分钟)、Long (15+分钟) 及自定义指导 Prompt。
  - **零成本高质量神经语音**：内置 Edge-TTS（支持微软普通话男声「云希」、女声「晓晓」以及英文「Guy」「Jenny」）。
- 🧠 **Studio 创意工坊与多模态成果 (8 大全能知识套件)**：
  1. **交互式思维导图 (Mind Map)**：SVG 动态层级图，支持平移、缩放、节点高亮与导出为 PNG。
  2. **执行简报 (Executive Briefing Doc)**：结构化决策提炼与战略建议。
  3. **深度学习指南 (Study Guide)**：核心术语解释、重点难点解析与考点提炼。
  4. **高频问答集 (FAQ Guide)**：梳理读者最关心的核心疑点及权威答复。
  5. **事件时间轴 (Timeline)**：提炼发展脉络与关键里程碑。
  6. **自测问答与测验 (Quiz & Knowledge Check)**：选择题与开放探讨题互动。
  7. **抽认卡 (Flashcards)**：3D 翻转卡片，支持主动回忆与背诵。
  8. **演示文稿大纲 & 直接下载 PPTX (Presentation Slides)**：不仅生成幻灯片结构，还可直接一键下载标准 `.pptx` 演示文稿！
- 🔍 **严格知识溯源与交互式引用 (Grounding & Exact Citations)**：
  - 回答中精准插入行内引用标号 `[1]`, `[2]`。
  - 鼠标悬停实时浮层预览引用的原文片段。
  - 点击引用自动拉起来源抽屉，平滑滚动至对应分块并高亮背景。
- 🔄 **知识双向闭环 (Bidirectional Knowledge Loop)**：
  - 对话回答、Studio 产物一键保存为独立笔记 (Notes)。
  - 任意笔记支持「一键转为知识来源 (Promote to Source)」，让提炼后的知识反哺知识库，实现滚雪球式研究。
- 🤖 **全模型生态兼容 (Multi-Model Support)**：
  - 原生覆盖：DeepSeek (V3 & R1)、Anthropic Claude、OpenAI (GPT-4o/o3)、Google Gemini、Kimi (Moonshot)、阿里通义千问、本地 Ollama 以及任何 OpenAI 兼容 API。

---

## 🆚 能力对标表 (Capability Parity Matrix)

| 核心能力维度 | Google NotebookLM | Open Notebook 原版 | **Open Notebook Bilingual (本项目)** |
|---|---|---|---|
| **数据隐私** | 闭源云端存储 | 开源自托管 (SurrealDB) | **开源自托管 (轻量 SQLite / 容器化)** |
| **模型支持** | 仅限 Google Gemini | 20+ 国际/本地模型 | **DeepSeek + Claude + OpenAI + Gemini + Kimi + 通义千问 + Ollama** |
| **中英双语体验** | 偏向英文，中文有翻译感 | 多语言 UI 但 Prompt 偏西化 | **全链路中英双语：UI + 提示词 + 双语分词检索 + 双语音色** |
| **播客模式 (Audio Overview)** | 深度对谈 / 极简速报 / 批判 / 辩论 | 多角色对谈 | **完整 4 种模式：Deep Dive, The Brief, The Critique, The Debate** |
| **播客语音合成 (TTS)** | 闭源 Google 独占音色 | 需额外配置商业 TTS | **内置免费 Edge-TTS (晓晓/云希/Jenny/Guy) + OpenAI TTS** |
| **交互式思维导图** | 基础树形展开 | 需外接插件 | **原生内置交互式 SVG 思维导图 + 平移缩放 + 一键导出 PNG** |
| **抽认卡 (Flashcards)** | 基础列表 | 无 | **内置 3D 翻转抽认卡交互组件** |
| **演示文稿导出** | 仅输出文字大纲 | 仅文字 | **直接生成并下载标准微软 `.pptx` 幻灯片文件** |
| **引用精准溯源** | 行内引用 + 点击跳转 | 来源引用 | **`[n]` 浮层预览 + 点击跳转定位分块 + 高亮显示** |
| **笔记反哺知识库** | 支持 Note to Source | 笔记功能 | **完整支持：保存回答/Studio为笔记 -> 笔记一键转为来源进入 RAG** |

---

## 🏗️ 目录架构 (Project Architecture)

```
open-notebook-bilingual/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI 核心入口、CORS、静态资源挂载
│   │   ├── config.py                   # 路径与系统环境变量配置
│   │   ├── db.py                       # SQLite 持久化数据库初始化与操作封装
│   │   ├── ingestion/
│   │   │   ├── parser.py               # 多模态解析器 (PDF, DOCX, PPTX, XLSX, TXT, MD) + 智能分块
│   │   │   ├── web_reader.py           # 网页链接抓取 + 正文提取 Markdown
│   │   │   └── youtube.py              # YouTube 视频字幕抓取
│   │   ├── retrieval/
│   │   │   ├── tokenizer.py            # 中英文双语分词器 (零第三方 C 库依赖)
│   │   │   └── bm25.py                 # BM25Okapi 混合排重与精确引用映射
│   │   ├── llm/
│   │   │   ├── provider.py             # 统一多大模型客户端适配器 (支持流式 SSE)
│   │   │   └── prompts.py              # 精心调优的中英双语系统提示词库
│   │   ├── podcast/
│   │   │   ├── generator.py            # 4 大播客剧本生成引擎
│   │   │   └── tts.py                  # 双语 Edge-TTS 音色合成与多音轨合并
│   │   ├── studio/
│   │   │   ├── artifacts.py            # 8 大创意工坊产物生成器
│   │   │   └── pptx_exporter.py        # 真实 .pptx 演示文稿生成与导出
│   │   └── api/
│   │       ├── routes_notebooks.py     # 笔记本 CRUD
│   │       ├── routes_sources.py       # 来源上传、抓取、分块详情
│   │       ├── routes_chat.py          # SSE 流式对话与行内引用绑定
│   │       ├── routes_podcast.py       # 播客生成、音频流服务
│   │       ├── routes_studio.py        # Studio 成果生成与 PPTX 下载
│   │       ├── routes_notes.py         # 笔记管理与反哺来源
│   │       └── routes_settings.py      # 模型设置、连接测试
│   └── requirements.txt                # Python 依赖包清单
├── frontend/
│   ├── index.html                      # 现代化三栏响应式 HTML5 页面
│   ├── css/
│   │   └── style.css                   # 现代化设计系统 (支持亮暗主题、抽认卡翻转、引用高亮)
│   └── js/
│       ├── i18n.js                     # 完整中英双语国际化字典与切换引擎
│       ├── api.js                      # 前后端通信客户端 (REST + SSE 流式)
│       ├── app.js                      # 页面主控制器与事件编排
│       ├── components/
│       │   ├── sources.js              # 来源勾选、详情查看、分块定位高亮
│       │   ├── chat.js                 # 流式对话、[n] 引用气泡交互、保存笔记
│       │   ├── studio.js               # 创意工坊控制器、音频播放器、剧本同步
│       │   ├── mindmap.js              # 交互式思维导图 SVG 引擎 (缩放/拖拽/PNG导出)
│       │   ├── notes.js                # 笔记编辑与反哺知识库
│       │   └── settings.js             # 模型设置可视化配置弹窗
│       └── lib/
│           └── marked.min.js           # 本地独立 Markdown 解析器
├── data/                               # 本地持久化数据目录 (SQLite + 上传文件 + 合成音频)
├── docker-compose.yml                  # 生产级 Docker 编排配置
├── Dockerfile                          # 多阶段构建 Dockerfile
├── start.py                            # Python 一键启动运行器 (自动检测安装依赖)
├── start.bat                           # Windows 一键启动脚本
├── .env.example                        # 环境变量模板
└── README.md                           # 中英双语项目手册
```

---

## 🚀 快速启动指南 (Quick Start)

### 方式一：本地极速运行 (Local Run - 推荐)

#### 前置要求
- Python 3.10+
- （可选）FFmpeg（用于音频拼接，若未安装会自动回退为无损流式合并）

#### 启动步骤
1. **进入项目目录**：
   ```bash
   cd open-notebook-bilingual
   ```
2. **安装依赖**：
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **启动服务**：
   - Windows 用户直接双击 `start.bat` 或运行：
     ```bash
     python start.py
     ```
4. **打开浏览器**：
   访问 `http://localhost:8502` 即可开始使用！

---

### 方式二：Docker 容器化部署 (Docker Deployment)

对于希望在服务器或私有云中长期稳定运行的用户：

```bash
cd open-notebook-bilingual
docker compose up -d
```
服务将在 `http://<服务器IP>:8502` 自动就绪，容器内置了完整 Python 运行环境与 FFmpeg 音频工具。

---

## ⚙️ 模型配置与离线演示模式 (Model Configuration)

1. **零门槛离线体验**：
   - 即使尚未填写 API Key，系统内置了**离线演示模式**，您可以完整体验添加文档、分块浏览、思维导图可视化等所有 UI 交互。
2. **可视化配置大模型**：
   - 点击右上角「**⚙️ 模型设置 / Model Settings**」：
   - **服务商选择**：可直接在下拉菜单中选择 **DeepSeek**、**OpenAI**、**Claude**、**Google Gemini**、**Kimi**、**通义千问** 或 **本地 Ollama**。
   - 输入对应 API Key 后，点击「**测试连接**」，绿灯确认后点击「**保存并启用**」，即可立即生效！配置保存在本地数据库中，重启不丢失。

---

## 🎧 音频播客使用小贴士 (Podcast Guide)

1. 在左侧勾选您想要参与播客讨论的来源（如论文、技术文档、项目方案）。
2. 在右侧切换到「**Studio 创意工坊**」，点击第一张卡片「**AI 音频对谈 / Podcast**」。
3. 选择您喜欢的播客形式：
   - **Deep Dive**：两位主持人以启发、互动的形式全面拆解。
   - **The Brief**：1 位主播快速凝练最核心要点。
   - **The Critique**：挑剔、批判视角审视材料潜在漏洞。
   - **The Debate**：正反方观点辩论。
4. 语言可选择「中文」或「English」，系统将自动调度对应的高清神经发音人进行音频合成，并提供逐字稿与 MP3 下载！

---

## 📄 授权协议 (License)

本项目基于宽松的 MIT License 开源，欢迎自由二次开发与商业化落地。
