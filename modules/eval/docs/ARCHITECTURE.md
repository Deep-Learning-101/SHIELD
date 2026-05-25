# S.H.I.E.L.D. 專案結構說明

## 📁 目錄架構

```
SHIELD-Eval/
├── config/
│   └── audit_config.yaml          # 統一配置檔案（核心配置中樞）
│
├── src/
│   └── shield_audit_workflow.py   # Inspect AI 工作流程編排器（主程式）
│
├── scripts/
│   └── setup_ubuntu_env.sh        # Ubuntu 環境自動化部署腳本
│
├── requirements-audit.txt         # Python 依賴套件清單
├── .gitignore                     # Git 忽略規則（機密保護）
├── README.md                      # 專案說明文件（繁體中文）
└── LICENSE                        # MIT 開源授權協議
```

## 📄 核心檔案說明

### 1. `config/audit_config.yaml` (111 行)
**功能**: 配置驅動的核心配置檔案

**關鍵區塊**:
- `audit_target`: 審計目標端點與身份驗證
- `data_refinery`: 合成資料生成控制
- `weapons_loadout`: 攻擊端武器選擇（GenAI + CV/Audio）
- `evaluation_judges`: 裁判端評估器選擇

**特色**:
- 支援環境變數替換（例如 `${SHIELD_TARGET_API_KEY}`）
- 階層式結構，清晰分離關注點
- 詳細註釋，每個參數都有說明

### 2. `src/shield_audit_workflow.py` (445 行)
**功能**: 混合雙擎審計工作流程編排器

**核心函數**:
- `load_audit_config()`: YAML 配置載入器
- `build_genai_attack_solvers()`: GenAI 文字攻擊 Solver 建構器
- `build_cv_audio_attack_solvers()`: CV/Audio 對抗攻擊 Solver 建構器
- `build_genai_evaluation_scorers()`: GenAI 文字評估 Scorer 建構器
- `build_cv_audio_evaluation_scorers()`: CV/Audio 可解釋性 Scorer 建構器
- `@task shield_hybrid_audit()`: Inspect AI 主任務定義

**設計模式**:
- Actor-Judge 三角架構
- 配置驅動的動態組裝
- 包含詳細的 TODO 註釋，標示整合點

**執行方式**:
```bash
# 生產模式（使用 Inspect AI）
inspect eval src/shield_audit_workflow.py

# 測試模式（驗證建構器邏輯）
python src/shield_audit_workflow.py
```

### 3. `scripts/setup_ubuntu_env.sh` (133 行)
**功能**: Ubuntu Server 環境自動化部署腳本

**執行步驟**:
1. 更新 APT 套件庫索引
2. 安裝 Python 3.10 與 build-essential
3. 建立虛擬環境 `shield-audit-env`
4. 安裝 `requirements-audit.txt` 所有依賴

**特色**:
- 彩色日誌輸出（INFO/SUCCESS/WARNING/ERROR）
- 冪等性設計（重複執行不會出錯）
- 詳細的部署後指引

### 4. `requirements-audit.txt` (48 行)
**功能**: Python 依賴套件清單

**套件分類**:
- 核心排程器: `inspect-ai`
- 攻擊端（GenAI）: `garak`
- 攻擊端（CV/Audio）: `adversarial-robustness-toolbox`, `foolbox`
- 裁判端（GenAI）: `trulens-eval`, `giskard`
- 裁判端（CV/Audio）: `shap`, `captum`
- 基礎設施: `pyyaml`, `python-dotenv`

### 5. `.gitignore` (177 行)
**功能**: Git 版本控制忽略規則

**關鍵保護**:
- 審計敏感資料: `audit_results/`, `*.log`, `*.eval`
- AI 模型權重: `*.safetensors`, `*.bin`, `*.pt`, `models/`
- 機敏配置: `*.key`, `*.pem`, `.env`
- 雲端憑證: AWS/GCP/Azure 憑證檔案

### 6. `README.md` (374 行)
**功能**: 專業級專案說明文件（繁體中文）

**包含內容**:
- 專案願景與混合雙擎架構介紹
- Actor-Judge 三角架構圖解
- 兵器譜分類（攻擊端 vs 裁判端）
- 完整的安裝與部署教學
- 配置說明與使用範例
- 安全性與合規指南
- 貢獻指南與參考文獻

---

## 🚀 快速啟動流程

```bash
# 1. 執行自動化部署
./scripts/setup_ubuntu_env.sh

# 2. 啟用虛擬環境
source shield-audit-env/bin/activate

# 3. 設定環境變數（如需）
export SHIELD_TARGET_API_KEY="your_api_key"

# 4. 測試建構器
python src/shield_audit_workflow.py

# 5. 執行審計
inspect eval src/shield_audit_workflow.py
```

---

## 📊 程式碼統計

| 檔案 | 行數 | 說明 |
|------|------|------|
| `requirements-audit.txt` | 48 | Python 依賴套件 |
| `config/audit_config.yaml` | 111 | 配置檔案 |
| `src/shield_audit_workflow.py` | 445 | 主程式（核心邏輯） |
| `scripts/setup_ubuntu_env.sh` | 133 | 部署腳本 |
| `README.md` | 374 | 專案文件 |
| `.gitignore` | 177 | 忽略規則 |
| **總計** | **1288** | **6 個核心檔案** |

---

## 🎯 下一步開發優先級

### 第一階段：武器整合（攻擊端）
- [ ] 整合 Garak 提示注入探測器
- [ ] 實作 IBM ART 對抗樣本生成 Solver
- [ ] 實作 Foolbox 黑盒攻擊 Solver

### 第二階段：裁判整合（評估端）
- [ ] 整合 Giskard 毒性與偏見檢測 Scorer
- [ ] 實作 SHAP 可解釋性 Scorer
- [ ] 實作 Captum 歸因分析 Scorer

### 第三階段：資料精煉廠
- [ ] 實作 Gemma-4-31B-CRACK 合成資料生成器
- [ ] 支援多語言對抗樣本生成（繁體中文、英文、日文）

### 第四階段：目標端整合
- [ ] 整合 NVIDIA NeMo Guardrails
- [ ] 支援 Nemotron-Safety-Guard 評估

### 第五階段：報告系統
- [ ] 實作 HTML 報告生成器
- [ ] 實作 JSON 摘要輸出器
- [ ] 實作 SHAP/Captum 視覺化儀表板

---

## 📧 專案作者

- **作者**: TonTon H.-D. Huang Ph.D.
- **Email**: TonTon@TWMAN.ORG
- **網站**: https://TWMAN.ORG

---

**建構日期**: 2026-05-24  
**專案作者**: TonTon H.-D. Huang Ph.D.  
**授權**: MIT License
