# S.H.I.E.L.D. 審計架構分析與整合建議

## 📊 現況分析

### 目前的三個工具流程

```
┌─────────────────────────────────────────────────────────────────┐
│ 工具 A: Garak (現有流程)                                         │
├─────────────────────────────────────────────────────────────────┤
│ 1. garak 生成對抗樣本 → ~/.local/share/garak/garak_runs/       │
│ 2. convert_garak_to_inspect.py → adversarial_dataset/*.json    │
│ 3. inspect eval shield_audit_workflow.py                        │
│                                                                  │
│ 控制方式: scripts/run_audit.sh (已整合)                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 工具 B: FuzzyAI (新建工具)                                       │
├─────────────────────────────────────────────────────────────────┤
│ 1. generate_fuzzyai_dataset.py → adversarial_dataset/*.json    │
│ 2. inspect eval examples/eval_fuzzyai_dataset.py                │
│                                                                  │
│ 控制方式: 獨立執行 (未整合)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 工具 C: shield_audit_workflow.py (整合中樞)                     │
├─────────────────────────────────────────────────────────────────┤
│ - 從 adversarial_dataset/ 自動載入最新的 Garak 資料集          │
│ - 動態組裝攻擊端 Solver                                          │
│ - 動態組裝裁判端 Scorer                                          │
│ - 執行完整審計流程                                               │
│                                                                  │
│ 問題: 尚未支援 FuzzyAI 資料集載入                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 整合建議方案

### 方案 A：輕量整合（推薦⭐⭐⭐⭐⭐）

**理念**: 保持工具獨立性，透過統一入口協調

#### 優點
✅ **職責清晰**: 每個工具專注自己的任務
✅ **易於維護**: 各工具可獨立開發與測試
✅ **彈性高**: 可以單獨使用任一工具或組合使用
✅ **擴展性強**: 未來新增其他生成器（如 AdversarialNLP）只需加入 run_audit.sh

#### 架構設計

```bash
# scripts/run_audit.sh 升級版
┌─────────────────────────────────────────────────────────────────┐
│ 統一入口: run_audit.sh --mode [garak|fuzzyai|both|custom]      │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─ [模式 1] --mode garak
         │   └─ 執行現有 Garak 流程
         │
         ├─ [模式 2] --mode fuzzyai
         │   ├─ 1. generate_fuzzyai_dataset.py
         │   └─ 2. inspect eval shield_audit_workflow.py
         │
         ├─ [模式 3] --mode both (預設)
         │   ├─ 1. garak 生成
         │   ├─ 2. convert_garak_to_inspect.py
         │   ├─ 3. generate_fuzzyai_dataset.py
         │   └─ 4. inspect eval shield_audit_workflow.py (載入兩個資料集)
         │
         └─ [模式 4] --mode custom
             └─ 透過 --dataset 參數指定自訂資料集路徑
```

#### shield_audit_workflow.py 升級重點

```python
# 在 Step 4 資料集載入段落加入 FuzzyAI 支援

dataset = []

# 1. 載入 Garak 資料集 (現有邏輯)
if weapons.get('enable_garak_injection', False):
    garak_files = glob.glob(str(dataset_dir / "garak_adversarial_dataset_*.json"))
    # ... 載入邏輯

# 2. 載入 FuzzyAI 資料集 (新增)
if weapons.get('enable_fuzzyai', False):
    fuzzyai_files = glob.glob(str(dataset_dir / "fuzzyai_adversarial_dataset_*.json"))
    if fuzzyai_files:
        latest_fuzzyai = max(fuzzyai_files, key=os.path.getctime)
        # ... 載入邏輯
        print(f"📥 偵測到 FuzzyAI 資料集，正在載入: {Path(latest_fuzzyai).name}")

# 3. 合併資料集
print(f"✅ 總共載入 {len(dataset)} 筆測資 (Garak: {garak_count}, FuzzyAI: {fuzzyai_count})")
```

#### config/audit_config.yaml 升級

```yaml
weapons_loadout:
  genai_text:
    enable_garak_injection: true
    enable_fuzzyai: true  # 新增開關
    fuzzyai_config:  # 新增配置區塊
      engine: "ollama"
      model: "llama3:8b"
      topics:
        - "惡意程式開發"
        - "機密資料竊取"
        - "釣魚攻擊"
      count_per_topic: 10
      delay: 0.5
```

---

### 方案 B：深度整合（不推薦❌）

**理念**: 將 FuzzyAI 完全嵌入 shield_audit_workflow.py

#### 缺點
❌ **耦合過緊**: FuzzyAI 變成 workflow 的一部分
❌ **難以測試**: 無法單獨測試 FuzzyAI 生成邏輯
❌ **降低彈性**: 無法在其他專案中重用 FuzzyAI
❌ **增加複雜度**: workflow 腳本變得臃腫

#### 為什麼不推薦？

```python
# 這樣做會讓 shield_audit_workflow.py 變成巨石腳本
@task
def shield_hybrid_audit():
    # 1. 初始化 Garak
    # 2. 執行 Garak
    # 3. 轉換 Garak 結果
    # 4. 初始化 FuzzyAI (新增)
    # 5. 執行 FuzzyAI (新增)
    # 6. 轉換 FuzzyAI 結果 (新增)
    # 7. 合併資料集
    # 8. 執行評估
    # ... 500+ 行代碼
```

---

## ✅ 最終建議：方案 A（輕量整合）

### 實施步驟

#### 階段 1：升級 shield_audit_workflow.py（15 分鐘）
- [x] 在資料集載入段落加入 FuzzyAI 支援
- [x] 自動偵測並載入 `fuzzyai_adversarial_dataset_*.json`
- [x] 統計並顯示 Garak/FuzzyAI 各自的測資數量

#### 階段 2：升級 run_audit.sh（20 分鐘）
- [x] 加入 `--mode` 參數（garak/fuzzyai/both/custom）
- [x] 加入 FuzzyAI 相關參數傳遞（--fuzzyai-engine, --fuzzyai-count 等）
- [x] 加入 `--dataset` 參數支援自訂資料集

#### 階段 3：升級 audit_config.yaml（5 分鐘）
- [x] 加入 `enable_fuzzyai` 開關
- [x] 加入 `fuzzyai_config` 配置區塊

#### 階段 4：建立文檔（10 分鐘）
- [x] GARAK_QUICKREF.md（Garak 快速參考）
- [x] 更新 README.md（加入整合說明）
- [x] 更新 FUZZYAI_QUICKREF.md（加入整合範例）

---

## 📋 整合後的使用範例

### 範例 1：只用 Garak
```bash
bash scripts/run_audit.sh --mode garak
```

### 範例 2：只用 FuzzyAI
```bash
bash scripts/run_audit.sh --mode fuzzyai \
  --fuzzyai-engine ollama \
  --fuzzyai-count 20 \
  --fuzzyai-topics "惡意程式" "釣魚攻擊"
```

### 範例 3：Garak + FuzzyAI 雙擎模式（推薦）
```bash
bash scripts/run_audit.sh --mode both \
  --fuzzyai-engine nim \
  --fuzzyai-count 30
```

### 範例 4：使用自訂資料集
```bash
bash scripts/run_audit.sh --mode custom \
  --dataset ../custom_datasets/my_adversarial_data.json
```

---

## 🎨 視覺化架構圖

```
┌───────────────────────────────────────────────────────────────────┐
│                    scripts/run_audit.sh                           │
│                   (統一入口 + 參數路由)                            │
└───────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
        ┌───────▼────────┐            ┌────────▼─────────┐
        │  Garak 生成器  │            │ FuzzyAI 生成器   │
        │  (promptinject │            │ (8種變異策略)    │
        │   dan, sysprompt)           │  NIM/vLLM/Ollama │
        └───────┬────────┘            └────────┬─────────┘
                │                               │
                │ convert_garak_to_inspect.py   │
                │                               │
                ▼                               ▼
    garak_adversarial_dataset_    fuzzyai_adversarial_dataset_
         YYYYMMDD_HHMMSS.json         YYYYMMDD_HHMMSS.json
                │                               │
                └───────────────┬───────────────┘
                                │
                    ┌───────────▼───────────┐
                    │ shield_audit_workflow │
                    │    (Inspect AI)       │
                    │                       │
                    │ ├─ 自動偵測資料集     │
                    │ ├─ 組裝 Solver       │
                    │ ├─ 組裝 Scorer       │
                    │ └─ 執行審計          │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │   inspect_report/     │
                    │   (審計報告輸出)      │
                    └───────────────────────┘
```

---

## 🔑 關鍵設計原則

1. **鬆耦合**: 生成器與評估器分離
2. **高內聚**: 每個工具專注自己的功能
3. **可測試性**: 所有工具可獨立測試
4. **可擴展性**: 易於新增其他生成器
5. **使用者友善**: 統一入口，簡單參數

---

## 📊 對比總結

| 特性 | 方案 A (輕量整合) | 方案 B (深度整合) |
|------|------------------|------------------|
| 工具獨立性 | ✅ 高 | ❌ 低 |
| 維護成本 | ✅ 低 | ❌ 高 |
| 彈性 | ✅ 高 | ❌ 低 |
| 擴展性 | ✅ 易 | ❌ 難 |
| 測試難度 | ✅ 低 | ❌ 高 |
| 學習曲線 | ✅ 平緩 | ❌ 陡峭 |
| 推薦指數 | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## 結論

**推薦採用方案 A（輕量整合）**，原因：
1. 符合 Unix 哲學：做好一件事
2. 易於維護與擴展
3. 保持工具的可重用性
4. 降低系統複雜度
5. 更好的錯誤隔離

下一步：是否要我開始實施方案 A？
