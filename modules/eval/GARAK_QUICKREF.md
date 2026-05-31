# Garak 快速參考卡

## 🎯 一分鐘快速啟動

### 方案 A：測試模式（不攻擊真實模型）
```bash
# 使用 dummy 模型生成惡意提示詞
python -m garak \
    --model_type test \
    --model_name dummy \
    --probes promptinject,dan \
    --report_prefix shield_garak_audit
```

### 方案 B：攻擊 NVIDIA NIM
```bash
export NVAPI_KEY="your_nvidia_api_key"
python -m garak \
    --model_type nim \
    --model_name meta/llama-3.1-70b-instruct \
    --probes promptinject \
    --report_prefix shield_garak_audit
```

### 方案 C：攻擊 Google Gemini
```bash
export GEMINI_API_KEY="your_gemini_api_key"
python -m garak \
    --model_type google \
    --model_name gemini-2.0-flash-exp \
    --probes promptinject,dan \
    --report_prefix shield_garak_audit
```

---

## 📦 Garak 探測器庫（Probes）

### 查看所有可用探測器
```bash
python -m garak --list_probes
```

### 常用探測器類別

| 探測器 | 說明 | 攻擊目標 | 推薦用途 |
|-------|------|---------|---------|
| `promptinject` | 提示詞注入 | 繞過系統提示詞 | 基礎安全測試 |
| `dan` | Do Anything Now | 越獄攻擊 | 護欄壓力測試 |
| `xss` | 跨站腳本注入 | 生成惡意網頁代碼 | Web 安全測試 |
| `malwaregen` | 惡意軟體生成 | 產生病毒/勒索軟體 | 濫用防護測試 |
| `encoding` | 編碼繞過 | Base64/Unicode 混淆 | 檢測器規避測試 |
| `sysprompt_extraction` | 系統提示詞洩漏 | 竊取系統配置 | 機密保護測試 |
| `leakreplay` | 資料洩漏 | 重放訓練資料 | 隱私保護測試 |
| `packagehallucination` | 幻覺套件 | 生成假的程式庫 | 供應鏈安全測試 |
| `snowball` | 滾雪球攻擊 | 多輪累積越獄 | 進階安全測試 |

### 組合多個探測器
```bash
# 同時使用三種攻擊手法
python -m garak \
    --model_type nim \
    --model_name meta/llama-3.1-70b-instruct \
    --probes promptinject,dan,sysprompt_extraction \
    --report_prefix shield_garak_audit
```

---

## 🔧 Garak 參數控制

### 速率限制（避免 API 封鎖）
```bash
# 每秒 0.1 個請求（即 10 秒 1 個）
python -m garak \
    --model_type nim \
    --model_name meta/llama-3.1-70b-instruct \
    --probes promptinject \
    --parallel 1 \
    --rate 0.1
```

### 限制測試數量
```bash
# 只執行 50 次攻擊測試
python -m garak \
    --model_type nim \
    --model_name meta/llama-3.1-70b-instruct \
    --probes dan \
    --generations 50
```

### 自訂輸出路徑
```bash
# 指定報告前綴（會自動加上時間戳）
python -m garak \
    --model_type test \
    --model_name dummy \
    --probes promptinject \
    --report_prefix my_custom_audit
```

---

## 📊 支援的模型類型

### 雲端 API
```bash
# NVIDIA NIM
--model_type nim --model_name meta/llama-3.1-70b-instruct

# OpenAI
--model_type openai --model_name gpt-4

# Google Gemini
--model_type google --model_name gemini-2.0-flash-exp

# Anthropic Claude
--model_type anthropic --model_name claude-3-opus-20240229

# Cohere
--model_type cohere --model_name command-r-plus
```

### 本地部署
```bash
# Ollama
--model_type ollama --model_name llama3:8b

# vLLM
--model_type vllm --model_name Qwen/Qwen2.5-72B-Instruct

# Hugging Face Transformers
--model_type huggingface --model_name meta-llama/Llama-3.1-8B-Instruct
```

### 測試模式
```bash
# Dummy 模型（不呼叫真實 API，只生成測資）
--model_type test --model_name dummy
```

---

## 🔍 查看 Garak 報告

### 報告位置
```
Linux/Mac: ~/.local/share/garak/garak_runs/
Windows:   ~/AppData/Local/garak/garak/garak_runs/
```

### 報告檔案格式
```
shield_garak_audit_YYYYMMDD_HHMMSS.report.jsonl  # 詳細日誌
shield_garak_audit_YYYYMMDD_HHMMSS.report.html   # 視覺化報告
```

### 快速查看結果
```bash
# 查看最新報告
ls -lt ~/.local/share/garak/garak_runs/ | head -5

# 統計攻擊成功率
grep '"passed": false' ~/.local/share/garak/garak_runs/shield_garak_audit*.jsonl | wc -l
```

---

## 🛡️ 整合至 SHIELD 工作流程

### 完整流程（現有）
```bash
# 1. 執行 Garak 生成惡意提示詞
python -m garak \
    --model_type test \
    --model_name dummy \
    --probes promptinject,dan \
    --report_prefix shield_garak_audit

# 2. 轉換為 Inspect AI 格式
python src/convert_garak_to_inspect.py

# 3. 執行 Inspect AI 審計
inspect eval src/shield_audit_workflow.py \
    --model openai/meta/llama-3.1-70b-instruct
```

### 使用整合腳本（推薦）
```bash
# 一鍵執行完整流程
bash scripts/run_audit.sh
```

---

## 💡 實戰範例

### 範例 1：快速安全檢查（5 分鐘）
```bash
python -m garak \
    --model_type test \
    --model_name dummy \
    --probes promptinject \
    --report_prefix quick_check
```

### 範例 2：標準紅隊測試（30 分鐘）
```bash
export NVAPI_KEY="your_key"
python -m garak \
    --model_type nim \
    --model_name meta/llama-3.1-70b-instruct \
    --probes promptinject,dan,encoding \
    --rate 0.5 \
    --report_prefix standard_redteam
```

### 範例 3：完整滲透測試（2 小時）
```bash
export NVAPI_KEY="your_key"
python -m garak \
    --model_type nim \
    --model_name meta/llama-3.1-70b-instruct \
    --probes promptinject,dan,xss,malwaregen,sysprompt_extraction,leakreplay \
    --rate 0.2 \
    --report_prefix full_pentest
```

### 範例 4：多模型對比測試
```bash
# 測試 Llama 3.1
export NVAPI_KEY="your_key"
python -m garak \
    --model_type nim \
    --model_name meta/llama-3.1-70b-instruct \
    --probes promptinject,dan \
    --report_prefix llama31_test

# 測試 Gemini
export GEMINI_API_KEY="your_key"
python -m garak \
    --model_type google \
    --model_name gemini-2.0-flash-exp \
    --probes promptinject,dan \
    --report_prefix gemini_test

# 對比報告
python scripts/compare_garak_reports.py llama31_test gemini_test
```

---

## 🔥 進階用法

### 自訂探測器配置
```bash
# 使用配置檔案
python -m garak --config my_custom_config.yaml
```

### 過濾特定探測器
```bash
# 只使用 HijackHateHumans 和 HijackKillHumans
python -m garak \
    --model_type test \
    --model_name dummy \
    --probes promptinject.HijackHateHumans,promptinject.HijackKillHumans
```

### 調整偵測器敏感度
```bash
# 設定更嚴格的檢測標準
python -m garak \
    --model_type nim \
    --model_name meta/llama-3.1-70b-instruct \
    --probes dan \
    --detector-threshold 0.3
```

---

## 🚨 故障排除

### 錯誤: `ModuleNotFoundError: No module named 'garak'`
```bash
pip install garak
```

### 錯誤: `API key not found`
```bash
# 檢查環境變數
echo $NVAPI_KEY
echo $GEMINI_API_KEY

# 重新設定
export NVAPI_KEY="your_key"
```

### 錯誤: `Rate limit exceeded`
```bash
# 降低請求頻率
python -m garak \
    --model_type nim \
    --model_name meta/llama-3.1-70b-instruct \
    --probes promptinject \
    --rate 0.1  # 10 秒一次
```

### 錯誤: 找不到報告檔案
```bash
# 檢查 Garak 預設目錄
ls -la ~/.local/share/garak/garak_runs/

# 使用絕對路徑指定報告位置
python -m garak \
    --model_type test \
    --model_name dummy \
    --probes promptinject \
    --report_dir /absolute/path/to/reports
```

---

## 📖 進階學習資源

- **官方文檔**: https://github.com/NVIDIA/garak
- **探測器清單**: https://garak.ai/probes
- **最佳實踐**: https://garak.ai/best-practices
- **NIST AI RMF 對應**: https://garak.ai/nist-mapping

---

## ⚠️ 安全與合規

### 使用限制
- ✅ 授權的紅隊演練
- ✅ 企業內部安全測試
- ✅ 學術研究與教學
- ❌ 未經授權攻擊第三方服務
- ❌ 生成或傳播惡意內容

### 資料保護
- 所有報告儲存於本地
- 不自動上傳至雲端
- 敏感資料需手動脫敏

---

**版本**: v1.0.0  
**更新**: 2026-05-31  
**Garak 版本**: v0.12.0+
