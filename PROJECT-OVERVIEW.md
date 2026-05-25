# 🛡️ SHIELD 專案完整說明文檔

**Sovereign Heuristic Intelligence & Enterprise Logic Defense**  
**主權啟發式情資與企業邏輯防禦系統**

**[TonTon H.-D. Huang Ph.D.](https://TWMAN.ORG)**


---

## 📋 目錄

- [**完整說明文檔**](https://deep-learning-101.github.io/SHIELD/)
- [專案概述](#專案概述)
- [系統架構](#系統架構)
- [目錄結構](#目錄結構)
- [核心模組 (core/)](#核心模組-core)
- [擴展模組 (modules/)](#擴展模組-modules)
- [共享資源 (shared/)](#共享資源-shared)
- [技術棧](#技術棧)
- [部署指南](#部署指南)
- [安全性與合規](#安全性與合規)

---

## 📖 專案概述

### 願景與定位

S.H.I.E.L.D. 是一個**企業級主權 AI 安全防禦平台**，專為高度監管產業（金融、政府、國防、半導體）打造，提供從**威脅狩獵到自動修補再到 AI 審計**的端到端防禦解決方案。

### 核心創新

#### 1. **雙引擎檢索架構**
- **Sovereign GraphRAG**：圖譜推導受災範圍與連鎖衝擊
- **Vectorless Vision RAG**：無向量目錄索引，零幻覺精準檢索

#### 2. **主動免疫機制**
- **暗網威脅狩獵**：7x24 主動探勘零時差漏洞
- **網路層熱修補**：LLM 自動生成 Snort/WAF 阻擋規則
- **ChatOps 授權機制**：人類主管透過 LINE 審批自動修補

#### 3. **Actor-Judge 雙腦架構**
- **業務大腦 (Actor)**：微調企業 SOP，執行情資推導
- **裁判大腦 (Judge)**：微調護欄模型，防範提示詞注入

#### 4. **混合雙擎 AI 審計**
- **GenAI 審計**：Garak 提示詞注入、TruLens 幻覺檢測
- **CV/Audio 審計**：IBM ART 對抗樣本、SHAP 可解釋性分析
- **ISO 42001 合規**：自動對齊控制項，生成獨立驗證報告

---

## 🏗️ 系統架構

### 五階段防禦閉環

```
🕸️ Phase 1: 防禦本體建置 (Ontology Graph)
    ↓ 介接 CMDB/GRC，渲染企業防禦圖譜
    
🕵️ Phase 2: 暗網威脅狩獵 (Dark Web Hunting)
    ↓ Tor 探針潛伏駭客論壇，捕獲 0-day 情資
    
💥 Phase 3: 雙引擎推導與任務封裝 (Dual-Engine Collision)
    ↓ GraphRAG 推演受災範圍 + Vectorless RAG 提取 SOP
    ↓ LLM 生成 Snort 規則並封裝為 Agent 工單
    
🦞 Phase 4: ChatOps 審批與全自主修補 (Autonomous Remediation)
    ↓ LINE 推播授權請求 → 人類審批 → OpenClaw 執行修補
    
🛡️ Phase 5: AI 審計與合規 (Automated Audit & Assurance)
    ↓ 紅藍隊攻防 → 護欄評估 → ISO 42001 報告生成
```

### 技術架構分層

```
┌─────────────────────────────────────────────────────────┐
│                    應用層 (Application)                  │
│  Streamlit 儀表板 | Inspect AI 審計編排 | ChatOps 介面  │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    業務層 (Business Logic)               │
│  Phase 1-4: core/    |    Phase 5: modules/eval/       │
│  威脅狩獵 | 雙引擎推導 | 自動修補 | AI 審計 | 合規映射     │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    AI 引擎層 (AI Engine)                 │
│  主權大腦 | LLM 路由 | GraphRAG | Vectorless RAG        │
│  Gemini | Ollama | vLLM | NeMo Guardrails              │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    數據層 (Data Layer)                   │
│  企業拓樸 DB | 合規矩陣 DB | 審計報告 | 機敏文檔庫      │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    基礎設施層 (Infrastructure)            │
│  Private Cloud | GPU 叢集 | Tor Network | Agent Harness │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 目錄結構

### 完整目錄樹

```
SHIELD/
│
├── README.md                              # 專案主說明文件（完整介紹）
├── LICENSE                                # AGPL v3 開源授權
├── .gitignore                             # Git 忽略規則
├── GIT-SETUP.md                           # Git 設定指南
├── MONOREPO-MIGRATION-SUMMARY.md          # Monorepo 遷移總結
├── SHIELD-EVAL-INTEGRATION-PLAN.md        # Phase 5 整合計畫書
├── SHIELD-EVAL-INTEGRATION-SUMMARY.md     # Phase 5 整合總結
├── PROJECT-OVERVIEW.md                    # 本文件（完整專案說明）
│
├── core/                                  # 核心模組（Phase 1-4）
│   ├── README.md                          # Core 模組說明
│   ├── requirements.txt                   # Python 依賴清單
│   │
│   ├── app.py                             # Streamlit 主應用
│   ├── config.py                          # 環境變數載入
│   ├── health.py                          # 系統健康度監測
│   │
│   ├── llm.py                             # LLM 意圖萃取與總結
│   ├── llm_utils.py                       # LLM 提供商路由
│   │
│   ├── search.py                          # 暗網搜尋引擎介接
│   ├── scrape.py                          # 洋蔥網頁爬蟲
│   │
│   ├── init_ontology.py                   # 防禦圖譜初始化
│   │
│   └── pageindex/                         # 無向量視覺檢索子模組
│       ├── __init__.py
│       ├── page_index.py                  # 核心索引引擎
│       ├── page_index_md.py               # Markdown 處理
│       ├── retrieve.py                    # 檢索功能
│       ├── client.py                      # 客戶端介面
│       ├── batch_preprocess.py            # 批次預處理
│       └── utils.py                       # 工具函數
│
├── modules/                               # 擴展模組目錄
│   ├── README.md                          # 模組開發指南
│   │
│   └── eval/                              # Phase 5: AI 審計與合規模組
│       ├── README.md                      # 模組完整說明
│       ├── __init__.py                    # 模組初始化
│       ├── requirements.txt               # 模組專屬依賴
│       ├── environment.yml                # Conda 環境配置
│       │
│       ├── config/                        # 配置目錄
│       │   ├── audit_config.yaml          # 審計配置（不推送）
│       │   └── audit_config.example.yaml  # 配置範例（脫敏）
│       │
│       ├── src/                           # 源碼目錄
│       │   ├── __init__.py
│       │   └── shield_audit_workflow.py   # Inspect AI 工作流程
│       │
│       ├── scripts/                       # 自動化腳本
│       │   ├── setup_conda_env.sh         # Conda 環境設置
│       │   ├── setup_ubuntu_env.sh        # Ubuntu 環境設置
│       │   ├── verify_setup.py            # 環境驗證腳本
│       │   └── run_audit.sh               # 快速啟動審計
│       │
│       ├── tests/                         # 單元測試
│       │   └── __init__.py
│       │
│       └── docs/                          # 模組文檔
│           ├── ARCHITECTURE.md            # 架構說明
│           ├── CONDA_SETUP_GUIDE.md       # Conda 設置指南
│           ├── DEPLOYMENT_SUMMARY.md      # 部署總結
│           └── QUICK_START.md             # 快速開始
│
├── shared/                                # 共享資源目錄
│   ├── README.md                          # 資源說明
│   │
│   ├── assets/                            # 媒體資源
│   │   ├── *.png, *.jpg                   # 圖片（架構圖、Logo）
│   │   ├── *.mp3                          # 音訊（NotebookLM Podcast）
│   │   └── *.srt                          # 字幕
│   │
│   └── data/                              # 資料目錄
│       ├── 20260319_compliance_matrix.db  # 合規邏輯矩陣
│       ├── 20260319_enterprise_assets.db  # 企業資產拓樸
│       ├── finance_assets.csv             # 財務資產（範例）
│       ├── finance_compliance.json        # 財務合規（範例）
│       │
│       └── audit_results/                 # 審計報告輸出目錄
│           ├── .gitkeep                   # 保持目錄被追蹤
│           └── README.md                  # 報告格式說明
│
└── docs/                                  # 全域文檔目錄
    └── （預留）
```

---

## 🔧 核心模組 (core/)

### Phase 1-4 核心防禦功能

#### 1. **app.py - Streamlit 主應用**

**功能**：
- 互動式威脅狩獵儀表板
- 企業防禦圖譜視覺化（PyVis）
- Phase 1-4 完整工作流程編排

**關鍵函數**：
- `init_ontology()`: 載入企業防禦矩陣
- `dark_web_search()`: 暗網威脅搜尋
- `collision_analysis()`: 雙引擎碰撞推導
- `generate_snort_rules()`: 生成防火牆規則

**執行方式**：
```bash
cd core
```
想要指定特定的 PORT (EX: 8000) 的話就是這樣
```bash
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```
---

#### 2. **llm.py + llm_utils.py - LLM 引擎**

**功能**：
- 支援 Gemini (Cloud) / Ollama (Local) 動態路由
- 威脅意圖萃取與繁體中文總結
- Snort/WAF 規則生成

**支援模型**：
- **Cloud**: Gemini-2.0-flash, Gemini-1.5-pro
- **Local**: Llama3, Mistral, Qwen（透過 Ollama）

**設定方式**：
```python
# .env 文件
GOOGLE_API_KEY=your_gemini_api_key
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

---

#### 3. **search.py + scrape.py - 暗網探針**

**功能**：
- 透過 Tor SOCKS5 代理存取 .onion 網站
- 整合多個暗網搜尋引擎（Ahmia, Torch, DarkSearch）
- 抽取駭客論壇威脅情資（PoC、CVE、漏洞利用）

**支援的暗網引擎**：
```python
ENGINES = {
    "ahmia": "https://ahmia.fi/search/?q=",
    "torch": "http://torchdeedp3i2jigzjdmfpn5ttjhthh5wbmda2rr3jvqjg5p77c54dqd.onion/search?query=",
    "darksearch": "https://darksearch.io/api/search?query="
}
```

**前置需求**：
```bash
# 安裝並啟動 Tor
sudo apt install tor
sudo systemctl start tor
# Tor 預設監聽 127.0.0.1:9050
```

---

#### 4. **init_ontology.py - 防禦圖譜初始化**

**功能**：
- 從 CSV/JSON/Database 載入企業資產
- 建構 NetworkX 圖譜拓樸
- 渲染互動式防禦矩陣

**支援的資料來源**：
- SQLite Database (`.db`)
- CSV 檔案 (`.csv`)
- JSON 檔案 (`.json`)

**範例資料庫結構**：
```sql
-- 企業資產表
CREATE TABLE assets (
    asset_id TEXT PRIMARY KEY,
    asset_name TEXT,
    asset_type TEXT,  -- Server, Application, Database
    ip_address TEXT,
    dependencies TEXT -- JSON array of dependent assets
);

-- 合規規則表
CREATE TABLE compliance_rules (
    rule_id TEXT PRIMARY KEY,
    rule_name TEXT,
    description TEXT,
    applicable_assets TEXT  -- JSON array
);
```

---

#### 5. **pageindex/ - 無向量視覺檢索**

**核心創新**：
- **零 LLM 延遲建檔**：利用 OpenDataLoader 電腦視覺直接抽取 PDF 目錄
- **保留原生排版**：截取 Bounding Box 原圖，消滅表格幻覺
- **物理版面感知**：識別 `heading`, `table`, `picture` 錨點

**關鍵模組**：

##### `page_index.py` - 核心索引引擎
```python
def page_index(pdf_path: str, output_json: str):
    """
    將 PDF 轉換為帶有精準座標的目錄樹 JSON
    
    輸出格式:
    {
        "title": "文檔標題",
        "tree": [
            {
                "type": "heading",
                "text": "第一章",
                "page": 1,
                "bbox": [x0, y0, x1, y1]
            },
            {
                "type": "table",
                "page": 2,
                "bbox": [x0, y0, x1, y1],
                "image_path": "tables/page_2_table_0.png"
            }
        ]
    }
    """
```

##### `retrieve.py` - 檢索功能
```python
def get_page_content(json_path: str, query: str) -> List[Dict]:
    """
    根據查詢關鍵字，返回相關頁面與 Bounding Box
    
    無向量檢索：直接字串匹配 + 物理鄰近度排序
    """
```

---

#### 6. **health.py - 系統健康度監測**

**功能**：
- LLM API 連線狀態檢測（Gemini / Ollama）
- Tor SOCKS5 代理存活度測試
- 暗網搜尋引擎 Ping 延遲檢測

**執行方式**：
```bash
python core/health.py
```

**輸出範例**：
```
✅ Gemini API: 正常（延遲: 234ms）
✅ Ollama Local: 正常（延遲: 45ms）
✅ Tor SOCKS5: 正常（127.0.0.1:9050）
⚠️  Ahmia 搜尋引擎: 逾時（>5000ms）
✅ DarkSearch API: 正常（延遲: 1234ms）
```

---

## 🧩 擴展模組 (modules/)

### Phase 5: AI 審計與合規模組 (modules/eval/)

#### 模組概述

**定位**：企業主權 AI 大腦的「內層防禦」  
**目的**：防範提示詞注入、越獄攻擊、RAG 幻覺，並產出 ISO 42001 合規報告

#### Actor-Judge 雙腦架構

```
┌────────────────────────────────────────────────────────┐
│              Inspect AI (大腦排程器)                    │
│              配置驅動工作流程編排                        │
└────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 攻擊端 (Actor)│  │ 目標端 (Target)│  │ 裁判端 (Judge)│
│              │  │              │  │              │
│ GenAI:       │  │ 客戶 AI 系統  │  │ GenAI:       │
│ - Garak      │─▶│ - LLM API    │◀─│ - GuardVal   │
│ - FuzzyAI    │  │ - CV Model   │  │ - TruLens    │
│ - Gemma-CRACK│  │ - Audio Model│  │ - Giskard    │
│              │  │              │  │              │
│ CV/Audio:    │  │ 護欄:        │  │ CV/Audio:    │
│ - IBM ART    │  │ - NeMo Guards│  │ - SHAP       │
│ - Foolbox    │  │ - Safety-Guard│ │ - Captum     │
└──────────────┘  └──────────────┘  └──────────────┘
```

#### 核心功能

##### 1. **GenAI 文字攻擊（攻擊端）**

**Garak** - OWASP LLM Top 10 自動化探測器
```yaml
# audit_config.yaml
weapons_loadout:
  genai_text:
    enable_garak_injection: true
    garak_probes:
      - "promptinject"   # 提示詞注入
      - "dan"            # DAN 越獄
      - "encoding"       # 編碼繞過（Base64, Hex）
      - "continuation"   # 續寫攻擊
```

**FuzzyAI** - 語義模糊測試框架
- 對提示詞進行語義保持的隨機變異
- 探測模型的邊界脆弱性

**Gemma-4-31B-CRACK** - 紅隊專用攻擊性資料生成模型
- 自動生成 50+ 種越獄變體
- 支援多語言攻擊樣本（繁中、英、日）

---

##### 2. **CV/Audio 對抗攻擊（攻擊端）**

**IBM ART** - 白盒對抗樣本生成
```python
from art.attacks.evasion import FastGradientMethod, ProjectedGradientDescent

# FGSM 攻擊
attack = FastGradientMethod(estimator=model, eps=0.03)
adversarial_image = attack.generate(x=original_image)

# PGD 攻擊
attack = ProjectedGradientDescent(estimator=model, eps=0.05, max_iter=40)
adversarial_image = attack.generate(x=original_image)
```

**Foolbox** - 黑盒對抗攻擊框架
- DeepFool: 最小擾動攻擊
- Boundary Attack: 無梯度決策邊界攻擊

---

##### 3. **GenAI 評估（裁判端）**

**GuardVal** - 護欄有效性量化
```json
{
  "guardrail_metrics": {
    "prompt_injection_rate": 0.02,     // 提示注入成功率 2%
    "jailbreak_success_rate": 0.01,    // 越獄成功率 1%
    "guardrail_block_rate": 0.98,      // 護欄攔截率 98%
    "MAPR": 0.02                       // 漏擋率（Miss-Attack Pass Rate）
  }
}
```

**TruLens** - 幻覺檢測與事實性驗證
```python
from trulens_eval import TruChain

# RAG 系統評估
tru_recorder = TruChain(rag_chain)
with tru_recorder:
    result = rag_chain.run(query)

# 計算 Groundedness（事實根據性）
groundedness_score = tru_recorder.groundedness()  // 0.0-1.0，越高越好
```

**Giskard** - 毒性、偏見、刻板印象檢測
```python
from giskard import scan

# 自動掃描模型風險
scan_results = scan(model, dataset)

# 輸出毒性分數
toxicity_score = scan_results.get_metric("toxicity")
bias_score = scan_results.get_metric("bias")
```

---

##### 4. **CV/Audio 可解釋性分析（裁判端）**

**SHAP** - 特徵重要性分析
```python
import shap

# 生成 SHAP 解釋
explainer = shap.DeepExplainer(model, background_data)
shap_values = explainer.shap_values(test_image)

# 視覺化特徵重要性
shap.image_plot(shap_values, test_image)
```

**Captum** - PyTorch 原生梯度歸因
```python
from captum.attr import IntegratedGradients, DeepLift

# IntegratedGradients 歸因
ig = IntegratedGradients(model)
attributions = ig.attribute(input_tensor, target=target_class)

# DeepLift 歸因
dl = DeepLift(model)
attributions = dl.attribute(input_tensor, target=target_class)
```

---

#### 審計報告格式

##### `summary.json` - 量化指標摘要
```json
{
  "audit_metadata": {
    "target_system": "My_AI_System",
    "audit_datetime": "2026-05-24T10:30:00Z",
    "inspector_version": "1.0.0"
  },
  "genai_metrics": {
    "prompt_injection_rate": 0.02,
    "jailbreak_success_rate": 0.01,
    "guardrail_block_rate": 0.98,
    "hallucination_score": 0.05,
    "toxicity_score": 0.03
  },
  "cv_audio_metrics": {
    "adversarial_success_rate": 0.15,
    "model_robustness_score": 0.85
  },
  "iso42001_compliance": {
    "total_controls": 42,
    "passed_controls": 40,
    "compliance_rate": 0.95
  }
}
```

##### `detailed_log.jsonl` - 詳細互動日誌
```jsonl
{"timestamp":"2026-05-24T10:30:01Z","attack_type":"prompt_injection","input":"Ignore previous instructions...","output":"I cannot comply...","blocked":true}
{"timestamp":"2026-05-24T10:30:02Z","attack_type":"jailbreak","input":"DAN mode activated...","output":"[BLOCKED]","blocked":true}
{"timestamp":"2026-05-24T10:30:03Z","attack_type":"hallucination_test","query":"北京是日本的首都嗎？","answer":"不，北京是中華人民共和國的首都","groundedness":1.0}
```

---

#### 快速啟動

```bash
# 1. 安裝環境
cd modules/eval
./scripts/setup_conda_env.sh
conda activate shield-audit-env

# 2. 配置審計目標
cp config/audit_config.example.yaml config/audit_config.yaml
vim config/audit_config.yaml

# 3. 執行審計
./scripts/run_audit.sh

# 4. 查看報告
cat ../../shared/data/audit_results/latest_summary.json
```

---

## 📦 共享資源 (shared/)

### assets/ - 媒體資源

**圖片資源**：
- 架構圖：`101.png`, `102.png`, ...（Phase 1-5 流程圖）
- Logo：`shield-logo.jpg`, `SHIELD.png`
- PoC 截圖：`shield-poc.png`

**音訊資源**：
- `shield.mp3`: NotebookLM 生成的專案 Podcast（繁體中文）
- `SHIELD-NBLM2.srt`: Podcast 字幕

**引用方式**：
```python
# 在 core/app.py 中
SHIELD_ROOT = Path(__file__).parent.parent
ASSETS_DIR = SHIELD_ROOT / "shared" / "assets"
logo_path = ASSETS_DIR / "shield-logo.jpg"
```

---

### data/ - 資料目錄

**企業資產與合規資料**：
- `20260319_enterprise_assets.db`: 企業 IT 資產拓樸（SQLite）
- `20260319_compliance_matrix.db`: 資安合規邏輯矩陣（SQLite）
- `finance_assets.csv`: 財務資產範例（CSV）
- `finance_compliance.json`: 財務合規範例（JSON）

**審計報告輸出**：
- `audit_results/`: Phase 5 審計報告輸出目錄
  - `YYYYMMDD_HHMMSS_summary.json`
  - `YYYYMMDD_HHMMSS_detailed_log.jsonl`
  - `YYYYMMDD_HHMMSS_html_report.html`

---

## 🛠️ 技術棧

### 核心技術

| 應用領域 | 核心工具 | 說明 |
|---------|---------|------|
| **AI 推論與萃取** | Google Gemini 2.0-flash<br>Ollama (Llama3, Mistral) | 雲端與地端 LLM 混合部署 |
| **數據精煉** | OpenDataLoader-PDF<br>PageIndex<br>NVIDIA NeMo Data Designer | PDF 無損解析<br>無向量檢索<br>合成數據生成 |
| **圖譜運算** | NetworkX<br>PyVis | 防禦拓樸渲染<br>連鎖衝擊推演 |
| **AI 治理** | NVIDIA NeMo Guardrails<br>Nemotron-Safety-Guard | 邏輯護欄<br>語意防火牆 |
| **決策軌跡** | LangGraph<br>Langfuse | 多代理人狀態機<br>完整日誌追蹤 |
| **暗網探勘** | Tor (SOCKS5)<br>Headless OSINT Scraper | 隱匿追蹤<br>情資萃取 |
| **數位員工** | OpenClaw<br>Multica<br>LINE Messaging API | Agent 執行<br>工單管理<br>ChatOps 授權 |
| **審計攻擊端** | Garak<br>FuzzyAI<br>IBM ART<br>Foolbox | OWASP LLM Top 10<br>語義模糊測試<br>對抗樣本生成 |
| **審計裁判端** | GuardVal<br>TruLens<br>Giskard<br>SHAP<br>Captum | 護欄評估<br>幻覺檢測<br>毒性分析<br>可解釋性 |
| **審計編排** | Inspect AI<br>Microsoft PyRIT | 工作流程編排<br>紅隊自動化 |

---

### Python 依賴管理

#### Core 模組依賴 (`core/requirements.txt`)
```txt
streamlit>=1.32.0
google-generativeai>=0.4.0
networkx>=3.2.1
pyvis>=0.3.2
requests>=2.31.0
python-dotenv>=1.0.0
pysocks>=1.7.1
beautifulsoup4>=4.12.0
PyMuPDF>=1.23.0
opendataloader-pdf>=0.1.0
litellm>=1.0.0
```

#### Eval 模組依賴 (`modules/eval/requirements.txt`)
```txt
inspect-ai>=0.3.0
garak>=0.9.0
adversarial-robustness-toolbox>=1.15.0
foolbox>=3.3.0
trulens-eval>=0.24.0
giskard>=2.8.0
shap>=0.44.0
captum>=0.7.0
pyyaml>=6.0
python-dotenv>=1.0.0
```

---

## 🚀 部署指南

### 環境需求

- **作業系統**: Ubuntu Server 20.04+ / Debian 11+ / macOS / Windows (WSL2)
- **Python 版本**: 3.10 或以上
- **記憶體**: 最低 8GB RAM（建議 16GB）
- **GPU**: 可選（啟用 GPU 可大幅提升審計效能）
- **網路**: 支援 Tor 存取（暗網探針需求）

---

### 快速部署流程

#### 步驟 1: 克隆倉庫
```bash
git clone https://github.com/Deep-Learning-101/SHIELD.git
cd SHIELD
```

#### 步驟 2: 安裝 Tor 服務
```bash
# Ubuntu/Debian
sudo apt install tor
sudo systemctl start tor
sudo systemctl enable tor

# macOS
brew install tor
brew services start tor
```

#### 步驟 3: 部署 Core 模組
```bash
cd core

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
vim .env
# 填入 GOOGLE_API_KEY=your_gemini_api_key

# 啟動主應用
streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```

#### 步驟 4: 部署 Phase 5 審計模組（可選）
```bash
cd ../modules/eval

# 使用 Conda（推薦）
./scripts/setup_conda_env.sh
conda activate shield-audit-env

# 或使用 Python venv
python3 -m venv audit-env
source audit-env/bin/activate
pip install -r requirements.txt

# 配置審計目標
cp config/audit_config.example.yaml config/audit_config.yaml
vim config/audit_config.yaml

# 執行審計
./scripts/run_audit.sh
```

---

### Docker 部署（規劃中）

```dockerfile
# Dockerfile (規劃中)
FROM python:3.11-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y tor

# 複製專案
WORKDIR /app
COPY . /app

# 安裝 Python 依賴
RUN pip install -r core/requirements.txt

# 啟動服務
CMD ["streamlit", "run", "core/app.py", "--server.port=8000"]
```

---

## 🔒 安全性與合規

### 資料保護

#### 1. **機密資料不外洩**
- ✅ 審計報告僅存於本地 `shared/data/audit_results/`
- ✅ `.gitignore` 已配置，審計報告不會推送至 GitHub
- ✅ API 金鑰透過環境變數管理，不寫入配置文件

#### 2. **主權 AI 部署**
- ✅ 支援 100% 地端部署（Ollama + vLLM）
- ✅ 無向量架構，無需維護 Vector DB
- ✅ 物理斷網環境下仍可運行 Phase 1, 3, 5

#### 3. **零信任架構**
- ✅ ChatOps 人類審批（Human-in-the-loop）
- ✅ Actor-Judge 雙腦架構，業務與裁判分離
- ✅ 完整的決策軌跡日誌（Langfuse）

---

### ISO 42001 合規映射

Phase 5 審計模組自動對齊 ISO/IEC 42001:2023 控制項：

| ISO 42001 控制項 | SHIELD 實現 |
|-----------------|-------------|
| **5.1 AI 政策** | Actor-Judge 雙腦架構文檔 |
| **6.2.2 風險評估** | 紅藍隊攻防演練（Garak, FuzzyAI） |
| **6.2.3 風險處置** | 護欄評估與熱重載（NeMo Guardrails） |
| **7.2 能力** | 可解釋性分析（SHAP, Captum） |
| **7.5 文件化** | 審計報告自動生成（summary.json, HTML） |
| **8.2.2 數據品質** | PageIndex 無損解析，零幻覺檢索 |
| **8.5 AI 系統驗證** | TruLens 幻覺檢測 |
| **8.6 AI 系統確認** | GuardVal 護欄量化評估 |
| **8.8 AI 系統輸出監控** | Langfuse 完整日誌追蹤 |
| **9.1 監控與測量** | 健康度監測（health.py） |

---

### 使用限制

本系統僅限於以下合法用途：
- ✅ 企業內部 AI 系統安全審計
- ✅ 授權紅隊演練 (Authorized Red Teaming)
- ✅ 學術研究與教學
- ✅ 防禦性網路安全演練

**嚴禁**：
- ❌ 未經授權攻擊第三方 AI 服務
- ❌ 生成或傳播惡意內容
- ❌ 違反服務條款或當地法律的行為
- ❌ 將暗網探針用於非防禦性目的

---

## 📊 專案統計

### 代碼統計

```bash
# Core 模組
find core -name "*.py" | wc -l
# 14 個 Python 文件

# Eval 模組
find modules/eval -name "*.py" | wc -l
# 4 個 Python 文件

# 文檔
find . -name "*.md" | wc -l
# 11 個 Markdown 文件
```

### 功能覆蓋率

| 階段 | 功能 | 狀態 |
|------|------|------|
| Phase 1 | 防禦本體建置 | ✅ 已實現 |
| Phase 2 | 暗網威脅狩獵 | ✅ 已實現 |
| Phase 3 | 雙引擎推導 | ✅ 已實現 |
| Phase 4 | ChatOps 自動修補 | ⚠️  部分實現（需 OpenClaw 整合） |
| Phase 5 | AI 審計與合規 | ✅ 已實現 |

---

## 📞 聯絡資訊

### 專案作者
- **姓名**: TonTon H.-D. Huang Ph.D.
- **Email**: TonTon@TWMAN.ORG
- **網站**: https://TWMAN.ORG

### 技術支援
- **GitHub Issues**: https://github.com/Deep-Learning-101/SHIELD/issues
- **文檔**: [SHIELD README](README.md)

---

## 📚 參考資源

### 學術論文
- Zou et al. (2023). "Universal and Transferable Adversarial Attacks on Aligned Language Models"
- Goodfellow et al. (2015). "Explaining and Harnessing Adversarial Examples"
- Ribeiro et al. (2016). "Why Should I Trust You? Explaining the Predictions of Any Classifier"

### 工具文件
- [Inspect AI 官方文件](https://inspect.ai-safety-institute.org.uk/)
- [Garak GitHub](https://github.com/leondz/garak)
- [IBM ART 文件](https://adversarial-robustness-toolbox.readthedocs.io/)
- [TruLens 文件](https://www.trulens.org/)
- [NVIDIA NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)

---

## 📄 授權協議

**AGPL v3 License** - 詳見 [LICENSE](LICENSE) 檔案

---

**專案版本**: v1.0  
**文檔版本**: v1.0  
**最後更新**: 2026-05-25  
**作者**: TonTon H.-D. Huang Ph.D.  

*本文件由 Claude Sonnet 4.5 協助生成*  
*Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>*
