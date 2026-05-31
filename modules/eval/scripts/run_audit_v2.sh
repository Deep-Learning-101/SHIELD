#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════
# S.H.I.E.L.D. 統一審計入口 - 升級版 v2.0
# 支援多模式運行：Garak / FuzzyAI / 雙擎 / 自訂資料集
# ═══════════════════════════════════════════════════════════════════════

set -e

# ───────────────────────────────────────────────────────────────────────
# 顏色輸出
# ───────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ───────────────────────────────────────────────────────────────────────
# 預設參數
# ───────────────────────────────────────────────────────────────────────
MODE="both"  # garak | fuzzyai | both | custom
GARAK_COUNT=10
GARAK_PROBES="promptinject,dan"
FUZZYAI_ENGINE="ollama"
FUZZYAI_MODEL="llama3:8b"
FUZZYAI_COUNT=10
FUZZYAI_TOPICS=("惡意程式開發" "機密資料竊取")
FUZZYAI_DELAY=0.5
CUSTOM_DATASET=""
TARGET_MODEL="openai/meta/llama-3.1-70b-instruct"
MAX_CONNECTIONS=1

# ───────────────────────────────────────────────────────────────────────
# 幫助訊息
# ───────────────────────────────────────────────────────────────────────
show_help() {
    cat << EOF
═══════════════════════════════════════════════════════════════════════
🛡️  S.H.I.E.L.D. 統一審計入口 v2.0
═══════════════════════════════════════════════════════════════════════

用法: $0 [選項]

運行模式:
  --mode MODE           運行模式 (garak|fuzzyai|both|custom) [預設: both]
    garak              僅執行 Garak 紅隊測試
    fuzzyai            僅執行 FuzzyAI 變異生成
    both               執行 Garak + FuzzyAI 雙擎模式
    custom             使用自訂資料集

FuzzyAI 參數:
  --fuzzyai-engine ENGINE    引擎類型 (nim|vllm|ollama) [預設: ollama]
  --fuzzyai-model MODEL      模型名稱 [預設: llama3:8b]
  --fuzzyai-count NUM        每主題生成數 [預設: 10]
  --fuzzyai-topics "T1 T2"   攻擊主題（空格分隔）[預設: "惡意程式開發 機密資料竊取"]
  --fuzzyai-delay SEC        API 呼叫延遲 [預設: 0.5]

Garak 參數:
  --garak-count NUM          從 Garak 結果中抽樣的測資數量 [預設: 10]
  --garak-probes PROBES      探測器清單（逗號分隔）[預設: promptinject,dan]

自訂資料集:
  --dataset PATH             自訂資料集路徑（使用 custom 模式時必填）

Inspect AI 參數:
  --model MODEL              目標模型 [預設: openai/meta/llama-3.1-70b-instruct]
  --max-connections NUM      最大並發數 [預設: 1]

其他:
  --skip-inspect             跳過 Inspect AI 評估（僅生成資料集）
  -h, --help                 顯示此幫助訊息

範例:
  # 完整雙擎模式（推薦）
  $0 --mode both --fuzzyai-count 20

  # 僅 Garak
  $0 --mode garak

  # 僅 FuzzyAI（使用 NVIDIA NIM）
  export NVIDIA_API_KEY="your_key"
  $0 --mode fuzzyai --fuzzyai-engine nim --fuzzyai-count 30

  # 使用自訂資料集
  $0 --mode custom --dataset ../custom_datasets/my_data.json

═══════════════════════════════════════════════════════════════════════
EOF
}

# ───────────────────────────────────────────────────────────────────────
# 參數解析
# ───────────────────────────────────────────────────────────────────────
SKIP_INSPECT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --garak-count)
            GARAK_COUNT="$2"
            shift 2
            ;;
        --garak-probes)
            GARAK_PROBES="$2"
            shift 2
            ;;
        --fuzzyai-engine)
            FUZZYAI_ENGINE="$2"
            shift 2
            ;;
        --fuzzyai-model)
            FUZZYAI_MODEL="$2"
            shift 2
            ;;
        --fuzzyai-count)
            FUZZYAI_COUNT="$2"
            shift 2
            ;;
        --fuzzyai-topics)
            IFS=' ' read -r -a FUZZYAI_TOPICS <<< "$2"
            shift 2
            ;;
        --fuzzyai-delay)
            FUZZYAI_DELAY="$2"
            shift 2
            ;;
        --dataset)
            CUSTOM_DATASET="$2"
            shift 2
            ;;
        --model)
            TARGET_MODEL="$2"
            shift 2
            ;;
        --max-connections)
            MAX_CONNECTIONS="$2"
            shift 2
            ;;
        --skip-inspect)
            SKIP_INSPECT=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}錯誤: 未知參數 $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# ───────────────────────────────────────────────────────────────────────
# 前置檢查
# ───────────────────────────────────────────────────────────────────────
if [ "$MODE" = "custom" ] && [ -z "$CUSTOM_DATASET" ]; then
    echo -e "${RED}錯誤: custom 模式必須指定 --dataset 參數${NC}"
    exit 1
fi

# 移動到專案根目錄
cd "$(dirname "$0")/../../.."

echo "════════════════════════════════════════════════════════════════════"
echo -e "${GREEN}🛡️  S.H.I.E.L.D. 自動化審計系統 v2.0${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}運行模式:${NC} $MODE"
echo -e "${BLUE}目標模型:${NC} $TARGET_MODEL"
echo "────────────────────────────────────────────────────────────────────"

# ───────────────────────────────────────────────────────────────────────
# 執行 Garak
# ───────────────────────────────────────────────────────────────────────
if [ "$MODE" = "garak" ] || [ "$MODE" = "both" ]; then
    echo -e "\n${YELLOW}💣 [Garak] 啟動提示詞注入攻擊生成...${NC}"
    echo -e "${BLUE}  探測器:${NC} $GARAK_PROBES"
    echo -e "${BLUE}  抽樣數量:${NC} $GARAK_COUNT"
    python -m garak \
        --model_type test \
        --model_name dummy \
        --probes "$GARAK_PROBES" \
        --report_prefix shield_garak_audit

    echo -e "\n${YELLOW}🔄 [Garak] 轉換為 Inspect AI 格式（抽樣 $GARAK_COUNT 筆）...${NC}"
    python modules/eval/src/convert_garak_to_inspect.py --sample-size $GARAK_COUNT
fi

# ───────────────────────────────────────────────────────────────────────
# 執行 FuzzyAI
# ───────────────────────────────────────────────────────────────────────
if [ "$MODE" = "fuzzyai" ] || [ "$MODE" = "both" ]; then
    echo -e "\n${YELLOW}🧬 [FuzzyAI] 啟動智能變異生成...${NC}"
    echo -e "${BLUE}  引擎:${NC} $FUZZYAI_ENGINE"
    echo -e "${BLUE}  模型:${NC} $FUZZYAI_MODEL"
    echo -e "${BLUE}  主題:${NC} ${FUZZYAI_TOPICS[@]}"
    echo -e "${BLUE}  數量:${NC} $FUZZYAI_COUNT"

    # 檢查引擎依賴
    case $FUZZYAI_ENGINE in
        nim)
            if [ -z "$NVIDIA_API_KEY" ]; then
                echo -e "${RED}錯誤: NVIDIA_API_KEY 環境變數未設定${NC}"
                echo "請執行: export NVIDIA_API_KEY=\"your_key\""
                exit 1
            fi
            ;;
        ollama)
            if ! pgrep -x "ollama" > /dev/null; then
                echo -e "${YELLOW}警告: Ollama 服務未運行，嘗試啟動...${NC}"
                ollama serve > /dev/null 2>&1 &
                sleep 3
            fi
            ;;
        vllm)
            if [ -z "$FUZZYAI_MODEL" ]; then
                echo -e "${RED}錯誤: vLLM 引擎必須指定 --fuzzyai-model${NC}"
                exit 1
            fi
            ;;
    esac

    # 執行 FuzzyAI（直接傳遞陣列，不使用 eval）
    python modules/eval/src/generate_fuzzyai_dataset.py \
        --engine "$FUZZYAI_ENGINE" \
        --model "$FUZZYAI_MODEL" \
        --count "$FUZZYAI_COUNT" \
        --delay "$FUZZYAI_DELAY" \
        --topics "${FUZZYAI_TOPICS[@]}"
fi

# ───────────────────────────────────────────────────────────────────────
# 執行 Inspect AI 評估
# ───────────────────────────────────────────────────────────────────────
if [ "$SKIP_INSPECT" = false ]; then
    echo -e "\n${YELLOW}🎯 [Inspect AI] 啟動防禦評估與裁判...${NC}"

    # 環境變數檢查
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}警告: OPENAI_API_KEY 未設定${NC}"
        echo "請執行: export OPENAI_API_KEY=\"your_api_key\""
        echo "        export OPENAI_BASE_URL=\"https://integrate.api.nvidia.com/v1\""
    fi

    echo -e "${GREEN}✅ API Key:${NC} ${OPENAI_API_KEY:0:10}..."
    echo -e "${GREEN}✅ Base URL:${NC} ${OPENAI_BASE_URL}"

    # 根據模式選擇資料集參數
    INSPECT_ARGS=""
    if [ "$MODE" = "custom" ]; then
        echo -e "${BLUE}使用自訂資料集:${NC} $CUSTOM_DATASET"
        INSPECT_ARGS="--dataset $CUSTOM_DATASET"
    fi

    inspect eval modules/eval/src/shield_audit_workflow.py \
        --model "$TARGET_MODEL" \
        --max-connections "$MAX_CONNECTIONS" \
        --log-dir modules/eval/inspect_report \
        $INSPECT_ARGS
else
    echo -e "\n${YELLOW}⏭️  跳過 Inspect AI 評估（--skip-inspect）${NC}"
fi

# ───────────────────────────────────────────────────────────────────────
# 完成訊息
# ───────────────────────────────────────────────────────────────────────
echo -e "\n════════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ 審計流程執行完畢！${NC}"
echo "════════════════════════════════════════════════════════════════════"

# 顯示生成的資料集
echo -e "\n${BLUE}生成的資料集:${NC}"
if [ "$MODE" = "garak" ] || [ "$MODE" = "both" ]; then
    ls -lht modules/eval/adversarial_dataset/garak_adversarial_dataset_*.json 2>/dev/null | head -1 || echo "  無 Garak 資料集"
fi
if [ "$MODE" = "fuzzyai" ] || [ "$MODE" = "both" ]; then
    ls -lht modules/eval/adversarial_dataset/fuzzyai_adversarial_dataset_*.json 2>/dev/null | head -1 || echo "  無 FuzzyAI 資料集"
fi

# 顯示報告位置
if [ "$SKIP_INSPECT" = false ]; then
    echo -e "\n${BLUE}審計報告:${NC}"
    echo "  modules/eval/inspect_report/"
    echo -e "\n${BLUE}查看報告:${NC}"
    echo "  inspect view"
fi

echo ""
