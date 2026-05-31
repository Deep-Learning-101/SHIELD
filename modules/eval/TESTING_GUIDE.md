# 🧪 S.H.I.E.L.D. v2.0 完整測試指南

## 📋 測試前檢查清單

### 1. 環境檢查

```bash
# 確認當前目錄
cd /home/tonton/SHIELD/modules/eval
pwd

# 確認 Python 環境
conda activate shieldEval_310  # 或你的虛擬環境
python --version  # 應該是 Python 3.10+

# 檢查必要套件
python -c "import garak; print('✓ garak')"
python -c "import openai; print('✓ openai')"
python -c "import inspect_ai; print('✓ inspect_ai')"
```

### 2. 檢查目錄結構

```bash
# 確認關鍵目錄存在
ls -la adversarial_dataset/
ls -la scripts/
ls -la src/

# 確認關鍵檔案存在
ls -la scripts/run_audit_v2.sh
ls -la src/generate_fuzzyai_dataset.py
ls -la src/shield_audit_workflow.py
```

---

## 🚀 測試階段 1：快速驗證（5 分鐘）

### 目標：確認所有工具都能正常啟動

```bash
# 測試 1: 檢查腳本幫助訊息
bash scripts/run_audit_v2.sh --help

# 測試 2: 檢查 FuzzyAI 幫助訊息
python src/generate_fuzzyai_dataset.py --help

# 測試 3: 檢查 Garak 是否安裝
python -m garak --help

# 測試 4: 檢查 Inspect AI
inspect --version
```

**預期結果**：所有命令都應該正常顯示幫助訊息，沒有錯誤。

---

## 🧪 測試階段 2：Garak 獨立測試（10 分鐘）

### 步驟 2.1：執行 Garak（測試模式）

```bash
# 使用 dummy 模型生成測試資料（不呼叫真實 API）
python -m garak \
    --model_type test \
    --model_name dummy \
    --probes promptinject \
    --report_prefix shield_test_garak
```

**預期輸出**：
```
garak LLM vulnerability scanner v0.12.0
📜 loading generator: Test: Lorem Ipsum
🕵️  queue of probes: promptinject.HijackHateHumans, ...
✔️  garak run complete in X.XXs
```

### 步驟 2.2：檢查 Garak 報告

```bash
# 查看最新的 Garak 報告
ls -lht ~/.local/share/garak/garak_runs/ | head -5

# 統計生成的測試數量
cat ~/.local/share/garak/garak_runs/shield_test_garak*.report.jsonl | wc -l
```

**預期結果**：應該看到新生成的 `.jsonl` 和 `.html` 報告檔案。

### 步驟 2.3：轉換為 Inspect AI 格式

```bash
# 執行轉換腳本
python src/convert_garak_to_inspect.py
```

**預期輸出**：
```
[🛡️ Garak To Compliance-Inspect 轉換器啟動]
📥 正在讀取 Garak 報告日誌: shield_test_garak_xxx.report.jsonl
🎲 總測資量大，已為您隨機亂數抽樣 10 筆標準合規樣本！
✅ 成功寫入 10 筆對齊 ISO/NIST 的 Garak 測資至: garak_adversarial_dataset_xxx.json
```

### 步驟 2.4：檢查轉換結果

```bash
# 查看生成的資料集
ls -lht adversarial_dataset/garak_adversarial_dataset_*.json | head -1

# 查看內容（前 2 筆）
cat adversarial_dataset/garak_adversarial_dataset_*.json | jq '.[0:2]'
```

**預期結果**：應該看到符合 Inspect AI 格式的 JSON 檔案。

---

## 🧬 測試階段 3：FuzzyAI 獨立測試（10 分鐘）

### 步驟 3.1：準備 Ollama（本地免費方案）

```bash
# 檢查 Ollama 是否運行
pgrep -x ollama

# 如果沒有運行，啟動它
ollama serve &
sleep 3

# 確認模型已下載
ollama list

# 如果沒有 llama3:8b，下載它
ollama pull llama3:8b
```

### 步驟 3.2：執行 FuzzyAI 生成（小規模測試）

```bash
# 生成 5 筆測試資料（約 2-3 分鐘）
python src/generate_fuzzyai_dataset.py \
    --engine ollama \
    --model llama3:8b \
    --topics "測試主題" \
    --count 5 \
    --delay 0.5
```

**預期輸出**：
```
[INFO] 初始化 FuzzyAI Generator
  Engine: ollama
  Model: llama3:8b
  Base URL: http://localhost:11434/v1
  Rate Limit: 0.5s per request

[INFO] 開始生成資料集
  主題數量: 1
  每主題生成數: 5
  總任務數: 5
  變異手法: 8 種

[TOPIC] 測試主題
  [1/5] 變異類型: role_play... ✓
  進度: 1/5 (20.0%)
  [2/5] 變異類型: multi_turn... ✓
  ...

[SUCCESS] 資料集已儲存至: adversarial_dataset/fuzzyai_adversarial_dataset_xxx.json
  總條目數: 5
```

### 步驟 3.3：檢查 FuzzyAI 輸出

```bash
# 查看生成的資料集
ls -lht adversarial_dataset/fuzzyai_adversarial_dataset_*.json | head -1

# 查看內容（前 2 筆）
cat adversarial_dataset/fuzzyai_adversarial_dataset_*.json | jq '.[0:2]'

# 統計變異類型分佈
cat adversarial_dataset/fuzzyai_adversarial_dataset_*.json | \
    jq -r '.[].metadata.mutation_type' | sort | uniq -c
```

**預期結果**：應該看到 5 筆包含不同變異策略的測試資料。

---

## 🎯 測試階段 4：完整雙擎整合測試（15 分鐘）

### 步驟 4.1：清理舊資料（可選）

```bash
# 備份舊資料集
mkdir -p ../eval-backup/test_$(date +%Y%m%d)
cp adversarial_dataset/*.json ../eval-backup/test_$(date +%Y%m%d)/ 2>/dev/null || true

# 清空舊資料集（如果需要乾淨測試）
# rm adversarial_dataset/*.json
```

### 步驟 4.2：設定環境變數

```bash
# 如果使用 NVIDIA NIM 作為評估目標
export OPENAI_API_KEY="nvapi-你的NVIDIA金鑰"
export OPENAI_BASE_URL="https://integrate.api.nvidia.com/v1"

# 或者使用 OpenAI（需要付費 API Key）
# export OPENAI_API_KEY="sk-你的OpenAI金鑰"
# unset OPENAI_BASE_URL

# 驗證環境變數
echo "API Key: ${OPENAI_API_KEY:0:10}..."
echo "Base URL: ${OPENAI_BASE_URL}"
```

### 步驟 4.3：執行完整雙擎測試（僅生成資料集）

```bash
# 先不執行評估，只生成資料集
bash scripts/run_audit_v2.sh \
    --mode both \
    --fuzzyai-engine ollama \
    --fuzzyai-model llama3:8b \
    --fuzzyai-count 5 \
    --skip-inspect
```

**預期輸出**：
```
════════════════════════════════════════════════════════════════════
🛡️  S.H.I.E.L.D. 自動化審計系統 v2.0
════════════════════════════════════════════════════════════════════
運行模式: both
目標模型: openai/meta/llama-3.1-70b-instruct
────────────────────────────────────────────────────────────────────

💣 [Garak] 啟動提示詞注入攻擊生成...
[Garak 執行過程...]

🔄 [Garak] 轉換為 Inspect AI 格式...
✅ 成功寫入 10 筆測資！

🧬 [FuzzyAI] 啟動智能變異生成...
  引擎: ollama
  模型: llama3:8b
  主題: 惡意程式開發 機密資料竊取
  數量: 5
[FuzzyAI 執行過程...]

⏭️  跳過 Inspect AI 評估（--skip-inspect）

════════════════════════════════════════════════════════════════════
✅ 審計流程執行完畢！
════════════════════════════════════════════════════════════════════

生成的資料集:
[列出 Garak 和 FuzzyAI 的資料集檔案]
```

### 步驟 4.4：檢查生成的資料集

```bash
# 列出所有資料集
ls -lht adversarial_dataset/

# 統計總數
echo "Garak 測資數量:"
cat adversarial_dataset/garak_adversarial_dataset_*.json | jq 'length'

echo "FuzzyAI 測資數量:"
cat adversarial_dataset/fuzzyai_adversarial_dataset_*.json | jq 'length'

echo "總計:"
cat adversarial_dataset/*.json | jq -s 'add | length'
```

### 步驟 4.5：執行完整評估（含 Inspect AI）

⚠️ **注意**：這一步會呼叫真實的 API，可能產生費用！

```bash
# 執行完整的雙擎 + 評估流程
bash scripts/run_audit_v2.sh \
    --mode both \
    --fuzzyai-engine ollama \
    --fuzzyai-count 5 \
    --model openai/meta/llama-3.1-70b-instruct \
    --max-connections 1
```

**預期輸出**：
```
[前面的 Garak + FuzzyAI 生成過程...]

🎯 [Inspect AI] 啟動防禦評估與裁判...
✅ API Key: nvapi-xxx...
✅ Base URL: https://integrate.api.nvidia.com/v1

═══════════════════════════════════════════════════════════════════
S.H.I.E.L.D. 審計平台 - 混合雙擎工作流程啟動
═══════════════════════════════════════════════════════════════════
[目標系統] openai/meta/llama-3.1-70b-instruct
[端點位址] https://integrate.api.nvidia.com/v1

[載入測試資料集]
📥 偵測到 Garak 資料集，正在載入: garak_adversarial_dataset_xxx.json
✅ Garak 資料集載入成功: 10 筆
📥 偵測到 FuzzyAI 資料集，正在載入: fuzzyai_adversarial_dataset_xxx.json
✅ FuzzyAI 資料集載入成功: 10 筆

📊 資料集統計:
  ├─ Garak 測資: 10 筆
  ├─ FuzzyAI 測資: 10 筆
  └─ 總計: 20 筆

[審計任務建構完成]
═══════════════════════════════════════════════════════════════════

╭────────────────────────────────────────────────────────────────╮
│shield_hybrid_audit (20 samples): openai/meta/llama-3.1-70b... │
╰────────────────────────────────────────────────────────────────╯
[Inspect AI 執行評估...]

total time: 0:XX:XX
model_graded_qa
accuracy  X.XXX
stderr    X.XXX
Log: inspect_report/2026-06-01T12-34-56_shield-hybrid-audit_xxx.eval

════════════════════════════════════════════════════════════════════
✅ 審計流程執行完畢！
════════════════════════════════════════════════════════════════════
```

---

## 📊 測試階段 5：查看結果

### 步驟 5.1：查看 Inspect AI 報告

```bash
# 啟動 Inspect AI 報告檢視器（會開啟瀏覽器）
inspect view
```

瀏覽器會開啟 `http://localhost:7575`，你可以看到：
- 評估時間軸
- 準確率統計
- 每個樣本的詳細結果
- 模型回應內容

### 步驟 5.2：查看原始日誌

```bash
# 列出所有評估報告
ls -lht inspect_report/

# 查看最新報告的摘要
cat inspect_report/*.eval | jq '.results.scores'
```

### 步驟 5.3：分析資料集品質

```bash
# 查看 Garak 探測器分佈
cat adversarial_dataset/garak_adversarial_dataset_*.json | \
    jq -r '.[].metadata.probe' | sort | uniq -c

# 查看 FuzzyAI 變異類型分佈
cat adversarial_dataset/fuzzyai_adversarial_dataset_*.json | \
    jq -r '.[].metadata.mutation_type' | sort | uniq -c

# 查看 NIST 類別分佈
cat adversarial_dataset/*.json | \
    jq -r '.[].metadata.nist_category' | sort | uniq -c
```

---

## 🎓 測試階段 6：進階測試（可選）

### 測試 6.1：僅 Garak 模式

```bash
bash scripts/run_audit_v2.sh --mode garak
```

### 測試 6.2：僅 FuzzyAI 模式

```bash
bash scripts/run_audit_v2.sh \
    --mode fuzzyai \
    --fuzzyai-engine ollama \
    --fuzzyai-count 10
```

### 測試 6.3：使用 NVIDIA NIM（FuzzyAI）

```bash
export NVIDIA_API_KEY="your_key"
bash scripts/run_audit_v2.sh \
    --mode fuzzyai \
    --fuzzyai-engine nim \
    --fuzzyai-count 10 \
    --fuzzyai-delay 3
```

### 測試 6.4：自訂資料集模式

```bash
bash scripts/run_audit_v2.sh \
    --mode custom \
    --dataset adversarial_dataset/garak_adversarial_dataset_20260601_123456.json
```

### 測試 6.5：大規模測試（30+ 筆）

```bash
bash scripts/run_audit_v2.sh \
    --mode both \
    --fuzzyai-count 20 \
    --fuzzyai-topics "惡意程式" "釣魚" "竊密" "注入"
```

---

## 🚨 常見問題排除

### 問題 1：Garak 執行失敗

```bash
# 檢查 Garak 版本
python -m garak --version

# 重新安裝
pip install --upgrade garak
```

### 問題 2：Ollama 連線失敗

```bash
# 檢查 Ollama 服務
pgrep -x ollama

# 重新啟動
pkill ollama
ollama serve &
sleep 3

# 測試連線
curl http://localhost:11434/api/tags
```

### 問題 3：找不到資料集

```bash
# 確認目錄存在
ls -la adversarial_dataset/

# 檢查最新的轉換
python src/convert_garak_to_inspect.py
```

### 問題 4：API Key 錯誤

```bash
# 檢查環境變數
env | grep API_KEY
env | grep BASE_URL

# 重新設定
export OPENAI_API_KEY="your_key"
export OPENAI_BASE_URL="https://integrate.api.nvidia.com/v1"
```

### 問題 5：Inspect AI 評估卡住

```bash
# 檢查 API 連線
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     "$OPENAI_BASE_URL/models"

# 降低並發數
bash scripts/run_audit_v2.sh --max-connections 1
```

---

## ✅ 測試完成檢查清單

- [ ] Garak 可以正常生成測試資料
- [ ] 轉換腳本可以正常執行
- [ ] FuzzyAI 可以使用 Ollama 生成變異
- [ ] 雙擎模式可以同時運行
- [ ] shield_audit_workflow.py 可以正確載入兩個資料集
- [ ] Inspect AI 可以正常執行評估
- [ ] 報告可以正常查看
- [ ] 所有路徑都正確

---

## 📖 推薦測試順序

1. **第一次使用**：測試階段 1 → 2 → 3 → 4.1~4.4（不執行評估）
2. **驗證整合**：測試階段 4.5（執行完整評估，小規模）
3. **生產使用**：測試階段 6.5（大規模測試）

---

## 💡 小技巧

1. **節省時間**：使用 `--skip-inspect` 先生成資料集，檢查無誤後再評估
2. **節省成本**：使用 Ollama 進行 FuzzyAI 生成（免費）
3. **提高品質**：使用 NVIDIA NIM 進行 FuzzyAI 生成（付費但品質更好）
4. **批次測試**：先生成多個資料集，再批次評估
5. **版本控制**：每次測試後備份資料集到 `eval-backup/`

---

**版本**: v2.0.0  
**更新**: 2026-06-01  
**測試平台**: Ubuntu 20.04 LTS / WSL2
