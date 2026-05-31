# FuzzyAI 快速參考卡

## 🎯 一分鐘快速啟動

### 方案 A：NVIDIA NIM（雲端，高品質）
```bash
export NVIDIA_API_KEY="nvapi-xxxxx"
python src/generate_fuzzyai_dataset.py --engine nim --count 10
```

### 方案 B：Ollama（本地，零成本）
```bash
ollama serve & ollama pull llama3:8b
python src/generate_fuzzyai_dataset.py --engine ollama --model llama3:8b --count 20 --delay 0.5
```

### 方案 C：vLLM（自架，高吞吐）
```bash
vllm serve Qwen/Qwen2.5-72B-Instruct --port 8000 &
python src/generate_fuzzyai_dataset.py --engine vllm --model "Qwen/Qwen2.5-72B-Instruct" --count 15
```

---

## 📊 常用參數組合

### 1. 快速原型測試（5 分鐘完成）
```bash
python src/generate_fuzzyai_dataset.py \
  --engine ollama \
  --model llama3:8b \
  --topics "測試主題" \
  --count 5 \
  --delay 0.5
```

### 2. 標準生產環境（30 分鐘）
```bash
python src/generate_fuzzyai_dataset.py \
  --engine nim \
  --topics "惡意程式開發" "釣魚攻擊" "機密資料竊取" \
  --count 30 \
  --delay 3
```

### 3. 高強度滲透測試（2 小時）
```bash
python src/generate_fuzzyai_dataset.py \
  --engine vllm \
  --model "Qwen/Qwen2.5-72B-Instruct" \
  --topics "社交工程" "權限提升" "SQL注入" "XSS攻擊" "DDoS" \
  --count 50 \
  --delay 1
```

### 4. 自訂主題與端點
```bash
python src/generate_fuzzyai_dataset.py \
  --engine vllm \
  --model "mistral-7b-instruct" \
  --base-url "http://192.168.1.100:8000/v1" \
  --topics "自訂主題1" "自訂主題2" \
  --count 10 \
  --output-dir "../custom_output"
```

---

## 🔧 故障排除速查

| 錯誤訊息 | 解決方案 |
|---------|---------|
| `NVIDIA_API_KEY 未設定` | `export NVIDIA_API_KEY="your_key"` |
| `vLLM 必須透過 --model 指定` | 加上 `--model "模型名稱"` |
| `Connection refused (Ollama)` | `ollama serve &` 啟動服務 |
| `Connection refused (vLLM)` | `vllm serve <model> --port 8000 &` |
| `模型不存在 (Ollama)` | `ollama pull llama3:8b` |
| `Rate limit exceeded` | 增加 `--delay` 參數值 |

---

## 📁 輸出檔案路徑

```
adversarial_dataset/fuzzyai_adversarial_dataset_YYYYMMDD_HHMMSS.json
```

範例：
```
adversarial_dataset/fuzzyai_adversarial_dataset_20260531_143022.json
```

---

## 🎨 八種變異手法

| 代碼 | 中文名稱 | 說明 |
|------|---------|------|
| `role_play` | 角色扮演 | 改寫成角色扮演場景 |
| `multi_turn` | 多輪引導 | 分步驟循序漸進 |
| `code_wrapping` | 代碼封裝 | 包裝成技術討論 |
| `indirect_instruction` | 間接指令 | 使用隱喻和暗示 |
| `persona_injection` | 角色注入 | 帶入特定情境 |
| `language_mixing` | 語言混合 | 中英混雜、術語 |
| `obfuscation` | 模糊化 | 委婉語、縮寫 |
| `context_hijacking` | 情境劫持 | 嵌入正常場景 |

---

## 🚀 與 Inspect AI 整合

### 快速評估
```bash
python examples/eval_fuzzyai_dataset.py
```

### 手動評估
```python
from inspect_ai import eval, Task
from inspect_ai.dataset import json_dataset

task = Task(
    dataset=json_dataset("adversarial_dataset/fuzzyai_adversarial_dataset_20260531_143022.json"),
    plan=[generate()],
    scorer=match()
)

eval(task, model="openai/gpt-4")
```

---

## 💡 效能優化建議

### 引擎選擇
- **高品質變異** → NIM (delay: 3-5s)
- **大量生成** → vLLM (delay: 1-2s)
- **快速測試** → Ollama (delay: 0.5-1s)

### 並行加速
```bash
# 使用 GNU Parallel
parallel -j 4 python src/generate_fuzzyai_dataset.py \
  --engine ollama \
  --topics {} \
  --count 25 \
  ::: "主題1" "主題2" "主題3" "主題4"
```

### 監控進度
```bash
# 即時查看生成數量
watch -n 1 'ls -1 adversarial_dataset/fuzzyai_*.json | wc -l'

# 查看最新檔案
ls -lt adversarial_dataset/fuzzyai_*.json | head -1
```

---

## 📞 獲取幫助

```bash
# 查看完整參數說明
python src/generate_fuzzyai_dataset.py --help

# 執行測試套件
bash test_fuzzyai.sh

# 閱讀詳細文檔
cat docs/fuzzyai_generator_usage.md
```

---

**版本**: v1.0.0  
**更新**: 2026-05-31
