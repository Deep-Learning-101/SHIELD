#!/bin/bash

# 設定發生錯誤時立刻停止腳本
set -e

echo "========================================================"
echo "🛡️ S.H.I.E.L.D. 自動化混合雙擎紅隊測試 (Red Teaming) 啟動"
echo "========================================================"

# 移動到專案根目錄 (從 modules/eval/scripts/ 往上三層到 SHIELD/)
cd "$(dirname "$0")/../../.."

# ---------------------------------------------------------
# Step 1: 讓 Garak 產生惡意彈藥
# ---------------------------------------------------------
echo -e "\n💣 [Step 1/3] 啟動 FuzzyAI 和 Garak 生成惡意 Prompt..."

# 叫 FuzzyAI（打本地 Ollama，生成惡意變異彈藥）
# fuzzyai fuzzer run --attack crescendo --model_type ollama --model_name llama3 --output ../adversarial_dataset/fuzzyai_raw_output.jsonl

# 拿掉路徑斜線，讓 Garak 乖乖寫入它的預設目錄
python -m garak \
    --model_type test \
    --model_name dummy \
    --probes promptinject,dan \
    --report_prefix shield_garak_audit

# python -m garak --list_probes
# garak LLM vulnerability scanner v0.12.0 ( https://github.com/NVIDIA/garak ) at 2026-05-28T02:23:22.219869
# 可以得知目前有 186 種像是 dan (Do Anything Now)、xss：測試大模型會不會被注入惡意網頁代碼（Cross-Site Scripting）、malwaregen：測試大模型會不會幫駭客寫惡意軟體、勒索病毒或釣魚信。
# --probes promptinject,dan,sysprompt_extraction 這樣便可以一次用多個彈藥庫

# ---------------------------------------------------------
# Step 1.5: 用 Garak 去一邊生成一邊實時攻擊真實模型
# ---------------------------------------------------------
# --model_name 必須對齊 NVIDIA NIM 支援的官方模型字串

# export NVAPI_KEY="你的_nvidia_api_key_xxxxxxxx"
# python -m garak \
#     --model_type nim \
#     --model_name openai/meta/llama-3.1-70b-instruct \
#     --probes promptinject \
#     --report_prefix shield_garak_audit

# export GEMINI_API_KEY="你的_gemini_api_key_xxxxxxxx"
# python -m garak \
#     --model_type google \
#     --model_name gemini-2.5-flash \
#     --probes promptinject \
#     --report_prefix shield_garak_audit

# ---------------------------------------------------------
# Step 2: 進行彈藥轉換 (裝彈)
# ---------------------------------------------------------
echo -e "\n🔄 [Step 2/3] 將 Garak 產出轉換為 Inspect AI 格式..."
python modules/eval/src/convert_garak_to_inspect.py

# 如果你也想測試 FuzzyAI 的彈藥庫，就再多跑這行，然後 Inspect AI 就會同時有兩套彈藥可以用來稽核了
# python modules/eval/src/convert_fuzzyai_to_inspect.py

# ---------------------------------------------------------
# Step 3: Inspect AI 總控發射與裁判
# ---------------------------------------------------------
echo -e "\n🎯 [Step 3/3] 啟動 Inspect AI 進行防禦稽核與評分..."

# 確保環境變數正確設定（如果尚未設定）
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  警告：OPENAI_API_KEY 未設定，請先執行："
    echo "   export OPENAI_API_KEY=\"your_nvidia_api_key\""
    echo "   export OPENAI_BASE_URL=\"https://integrate.api.nvidia.com/v1\""
    exit 1
fi

echo "✅ API Key 已設定: ${OPENAI_API_KEY:0:10}..."
echo "✅ Base URL: ${OPENAI_BASE_URL}"

inspect eval modules/eval/src/shield_audit_workflow.py \
    --model openai/meta/llama-3.1-70b-instruct \
    --max-connections 1 \
    --log-dir modules/eval/inspect_report
    
echo -e "\n========================================================"
echo "✅ 測試流程全數執行完畢！"
echo "========================================================"