# 🛡️ SHIELD Core Module

**核心防禦系統模組** - Sovereign Heuristic Intelligence & Enterprise Logic Defense

**[TonTon H.-D. Huang Ph.D.](https://TWMAN.ORG)**


---

## 📋 模組說明

Core 模組是 SHIELD 的核心引擎，包含主權 AI 防禦系統的所有核心功能。

## 📁 檔案結構

```
core/
├── app.py              # 主應用程式 (Streamlit UI)
├── llm.py              # LLM 核心功能與推理引擎
├── llm_utils.py        # LLM 工具函數
├── search.py           # 企業知識搜尋引擎
├── scrape.py           # 網頁爬蟲與資料擷取
├── health.py           # 系統健康檢查
├── init_ontology.py    # 防禦知識本體初始化
├── config.py           # 配置文件
├── requirements.txt    # Python 依賴套件
└── pageindex/          # 頁面索引子模組
    ├── __init__.py
    ├── page_index.py
    ├── page_index_md.py
    ├── batch_preprocess.py
    ├── client.py
    ├── retrieve.py
    ├── utils.py
    └── config.yaml
```

## 🚀 快速開始

### 安裝依賴

```bash
cd core
pip install -r requirements.txt
```

### 環境變數設定

需要設置以下環境變數：

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
```

### 啟動應用

```bash
streamlit run app.py
```
或者是想要指定特定的 PORT (EX: 8000) 的話就是這樣
```bash
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```

應用程式將在 `http://localhost:8501` 或者  `http://localhost:8000` 啟動。

## 🧩 核心功能模組

### 1. **app.py** - 主應用程式
- Streamlit 前端界面
- 整合所有子系統
- 提供互動式操作介面

### 2. **llm.py / llm_utils.py** - LLM 引擎
- 大語言模型整合
- Prompt 工程與優化
- 多模型支援（Gemini, Claude 等）

### 3. **search.py** - 企業知識搜尋
- 語義搜尋引擎
- 文檔檢索與排序
- 跨文件查詢

### 4. **init_ontology.py** - 知識本體
- 企業資產本體建置
- 合規矩陣關聯
- 防禦知識圖譜

### 5. **pageindex/** - 頁面索引系統
- PDF 文檔結構化
- 大綱樹狀索引
- 圖表資產提取

### 6. **health.py** - 健康檢查
- 系統狀態監控
- 服務可用性檢測

### 7. **scrape.py** - 資料擷取
- 網頁爬蟲
- 內容清洗與解析

## 🔗 資源引用

Core 模組採用 Monorepo 架構，會引用上層 `shared/` 目錄中的資源：

- **資料庫與數據**: `../shared/data/`
- **圖片與媒體**: `../shared/assets/`

## 📝 配置說明

主要配置項在 `config.py` 中，包括：

- API 密鑰管理
- 模型參數設定
- 系統行為配置

## 🧪 測試

獨立測試知識本體建置：

```bash
python init_ontology.py
```

## 📦 依賴套件

主要依賴（詳見 `requirements.txt`）：

- `streamlit` - Web UI 框架
- `google-genai` - Gemini API
- `networkx` - 圖論與知識圖譜
- `pandas` - 資料處理
- `pyvis` - 網絡可視化
- `PyMuPDF` (fitz) - PDF 處理

## 🔧 開發注意事項

1. **路徑引用**: 所有 `data/` 和 `assets/` 的引用已更新為相對於 Monorepo 根目錄
2. **模組導入**: 內部模組使用相對導入（如 `from config import ...`）
3. **獨立運行**: 可獨立測試各模組功能