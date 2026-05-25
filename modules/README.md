# 🧩 SHIELD Modules

**擴展模組目錄** - 未來功能模組的家

**[TonTon H.-D. Huang Ph.D.](https://TWMAN.ORG)**

---

## 📋 目錄說明

這個目錄用於放置 SHIELD 的擴展功能模組。每個模組都是一個獨立的功能單元，可以單獨開發、測試和部署。

---

## ✅ 已實現的模組

### 1. **eval** - AI 審計與合規模組 🛡️
- **功能**: Phase 5 自動化審計與零信任 AI 治理
- **技術棧**: Inspect AI, PyRIT, Garak, TruLens, GuardVal, SHAP, Captum
- **狀態**: ✅ 已整合
- **文檔**: [eval/README.md](eval/README.md)

#### 核心功能
- 紅藍隊自主對抗（Garak 提示詞注入、越獄攻擊）
- 護欄評估（NeMo Guardrails 有效性量化）
- 幻覺檢測（RAG 系統事實性驗證）
- ISO 42001 合規映射與報告生成
- CV/Audio 對抗攻擊與可解釋性分析

#### Actor-Judge 雙腦架構
```
攻擊端 (Actor)          目標端 (Target)        裁判端 (Judge)
├─ Garak              ├─ 客戶 AI 系統       ├─ GuardVal
├─ FuzzyAI            ├─ NeMo Guards        ├─ TruLens
├─ Gemma-CRACK        └─ Vectorless RAG     ├─ Giskard
├─ IBM ART                                  ├─ SHAP
└─ Foolbox                                  └─ Captum
```

#### 快速啟動
```bash
cd modules/eval
./scripts/setup_conda_env.sh
conda activate shield-audit-env
./scripts/run_audit.sh
```

---

## 🏗️ 規劃中的模組

### 1. **module-auth** - 認證與授權模組
- 企業級身份認證
- 角色權限管理
- SSO 整合
- API 密鑰管理

### 2. **module-monitor** - 監控與告警模組
- 實時系統監控
- 異常行為檢測
- 告警通知系統
- 日誌分析

### 3. **module-audit** - 審計與合規模組
- 操作審計追蹤
- 合規報告生成
- 風險評估
- 政策檢查

### 4. **module-api** - API Gateway 模組
- RESTful API 接口
- GraphQL 支援
- API 限流與熔斷
- 請求驗證

### 5. **module-data-connector** - 資料連接器模組
- 多資料源整合
- ETL 流程管理
- 資料同步
- 格式轉換

---

## 📝 新增模組指南

### 模組結構模板

每個新模組應遵循以下目錄結構：

```
modules/
└── module-example/
    ├── README.md           # 模組說明文件
    ├── __init__.py         # Python 套件初始化
    ├── requirements.txt    # 模組專屬依賴
    ├── config.py           # 模組配置
    ├── main.py             # 主要邏輯
    ├── utils.py            # 工具函數
    ├── tests/              # 單元測試
    │   ├── __init__.py
    │   └── test_main.py
    └── docs/               # 模組文檔
        └── API.md
```

### 模組 README 模板

新增模組時，請複製以下模板到你的模組目錄：

```markdown
# 🎯 Module Name

**簡短描述** - 一句話說明模組功能

---

## 📋 功能說明

- 功能 1
- 功能 2
- 功能 3

## 🚀 快速開始

### 安裝依賴

\`\`\`bash
cd modules/module-name
pip install -r requirements.txt
\`\`\`

### 使用範例

\`\`\`python
from modules.module_name import MainClass

# 使用範例
instance = MainClass()
result = instance.do_something()
\`\`\`

## 🔧 配置說明

配置項說明...

## 🧪 測試

\`\`\`bash
pytest tests/
\`\`\`

## 📚 API 文檔

詳見 [docs/API.md](docs/API.md)
```

---

## 🔗 與 Core 模組的整合

### 引用共享資源

模組可以引用 `shared/` 目錄中的資源：

```python
import os

# 取得 SHIELD 根目錄
SHIELD_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 引用共享資源
ASSETS_DIR = os.path.join(SHIELD_ROOT, "shared", "assets")
DATA_DIR = os.path.join(SHIELD_ROOT, "shared", "data")
```

### 引用 Core 模組功能

```python
import sys
import os

# 將 core 加入 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

# 引用 core 功能
from llm import get_llm
from search import get_search_results
```

---

## 🎨 開發最佳實踐

### 1. **獨立性原則**
- 每個模組應該能夠獨立運行和測試
- 最小化對其他模組的依賴
- 清楚定義模組邊界

### 2. **配置管理**
- 使用環境變數管理敏感資訊
- 提供預設配置值
- 支援配置文件覆蓋

### 3. **錯誤處理**
- 完善的異常處理機制
- 有意義的錯誤訊息
- 日誌記錄關鍵操作

### 4. **文檔完整**
- README 說明模組用途
- API 文檔詳細完整
- 代碼註解清晰

### 5. **測試覆蓋**
- 單元測試覆蓋核心功能
- 整合測試驗證模組協作
- 提供測試數據和 mock

### 6. **版本管理**
- 遵循語義化版本規範
- CHANGELOG 記錄變更
- 向後兼容性考量

---

## 📦 依賴管理

### 模組依賴隔離

每個模組維護自己的 `requirements.txt`：

```txt
# module-example/requirements.txt
requests>=2.31.0
pydantic>=2.0.0
# 只列出此模組特有的依賴
```

### 共享依賴

Core 模組的依賴在 `core/requirements.txt` 中定義，所有模組都可以使用。

---

## 🚢 部署考量

### Docker 支援

每個模組可以提供自己的 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 複製模組代碼
COPY modules/module-example /app/module-example

# 安裝依賴
RUN pip install -r module-example/requirements.txt

CMD ["python", "-m", "module-example.main"]
```

### 環境變數

模組應該通過環境變數配置：

```bash
# .env.example
MODULE_EXAMPLE_API_KEY=your_api_key
MODULE_EXAMPLE_DEBUG=false
MODULE_EXAMPLE_PORT=8080
```