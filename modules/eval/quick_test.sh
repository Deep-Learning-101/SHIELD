#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════
# S.H.I.E.L.D. 快速測試腳本
# 互動式引導測試流程
# ═══════════════════════════════════════════════════════════════════════

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     ███████╗██╗  ██╗██╗███████╗██╗     ██████╗                      ║
║     ██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗                     ║
║     ███████╗███████║██║█████╗  ██║     ██║  ██║                     ║
║     ╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║                     ║
║     ███████║██║  ██║██║███████╗███████╗██████╔╝                     ║
║     ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝                      ║
║                                                                      ║
║              🛡️  快速測試腳本 v2.0 🛡️                               ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# ───────────────────────────────────────────────────────────────────────
# 函數定義
# ───────────────────────────────────────────────────────────────────────

print_step() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 已安裝"
        return 0
    else
        print_error "$1 未安裝"
        return 1
    fi
}

press_enter() {
    echo -e "\n${YELLOW}按 Enter 繼續...${NC}"
    read
}

# ───────────────────────────────────────────────────────────────────────
# 測試階段 1: 環境檢查
# ───────────────────────────────────────────────────────────────────────

print_step "階段 1: 環境檢查"

echo "檢查 Python 環境..."
python --version
print_success "Python 版本正確"

echo -e "\n檢查必要套件..."
python -c "import garak" 2>/dev/null && print_success "garak 已安裝" || print_error "garak 未安裝 (執行: pip install garak)"
python -c "import openai" 2>/dev/null && print_success "openai 已安裝" || print_error "openai 未安裝 (執行: pip install openai)"
python -c "import inspect_ai" 2>/dev/null && print_success "inspect_ai 已安裝" || print_error "inspect_ai 未安裝 (執行: pip install inspect-ai)"

echo -e "\n檢查關鍵檔案..."
[ -f "scripts/run_audit_v2.sh" ] && print_success "run_audit_v2.sh 存在" || print_error "run_audit_v2.sh 不存在"
[ -f "src/generate_fuzzyai_dataset.py" ] && print_success "generate_fuzzyai_dataset.py 存在" || print_error "generate_fuzzyai_dataset.py 不存在"
[ -f "src/shield_audit_workflow.py" ] && print_success "shield_audit_workflow.py 存在" || print_error "shield_audit_workflow.py 不存在"

echo -e "\n檢查目錄..."
[ -d "adversarial_dataset" ] && print_success "adversarial_dataset/ 存在" || (mkdir -p adversarial_dataset && print_info "已創建 adversarial_dataset/")
[ -d "inspect_report" ] || mkdir -p inspect_report

press_enter

# ───────────────────────────────────────────────────────────────────────
# 測試階段 2: 主選單迴圈
# ───────────────────────────────────────────────────────────────────────

while true; do
    print_step "主選單"

    echo "請選擇要執行的測試："
    echo "  1) 快速測試 - Garak 獨立測試（5 分鐘，免費）"
    echo "  2) 快速測試 - FuzzyAI 獨立測試（5 分鐘）"
    echo "  3) 完整測試 - 雙擎生成（不評估）（10 分鐘，免費）"
    echo "  4) 完整測試 - 雙擎 + Inspect AI 評估（15 分鐘，需要 API Key）"
    echo "  5) 查看現有報告"
    echo "  6) 清理測試資料"
    echo "  0) 退出"
    echo ""
    read -p "請輸入選項 [0-6]: " choice

    case $choice in
    1)
        # ───────────────────────────────────────────────────────────────
        # 測試 1: Garak 獨立測試
        # ───────────────────────────────────────────────────────────────
        print_step "執行測試 1: Garak 獨立測試"

        echo -e "${BLUE}步驟 1/2: 選擇探測器${NC}"
        echo ""
        echo "請選擇 Garak 探測器（可多選）："
        echo "  1) promptinject (提示詞注入)"
        echo "  2) dan (Do Anything Now 越獄)"
        echo "  3) encoding (編碼繞過)"
        echo "  4) malwaregen (惡意軟體生成)"
        echo "  5) 全部 (1-4)"
        echo ""
        read -p "請輸入選項（可用空格分隔多個，例如: 1 2）: " garak_choices

        # 解析探測器選擇
        garak_probes=""
        for choice in $garak_choices; do
            case $choice in
                1) garak_probes="${garak_probes},promptinject" ;;
                2) garak_probes="${garak_probes},dan" ;;
                3) garak_probes="${garak_probes},encoding" ;;
                4) garak_probes="${garak_probes},malwaregen" ;;
                5) garak_probes="promptinject,dan,encoding,malwaregen"; break ;;
            esac
        done
        garak_probes=${garak_probes#,}  # 移除開頭的逗號

        if [ -z "$garak_probes" ]; then
            print_error "未選擇任何探測器，使用預設：promptinject"
            garak_probes="promptinject"
        fi

        echo ""
        print_success "已選擇探測器: $garak_probes"

        echo ""
        echo -e "${BLUE}步驟 2/2: 設定測資數量${NC}"
        echo ""
        echo -e "${YELLOW}註：Garak 會為每個探測器生成多筆測試，然後從中隨機抽樣${NC}"
        read -p "最終要抽樣幾筆測試資料？[預設: 10]: " garak_count
        garak_count=${garak_count:-10}

        echo ""
        print_info "Garak 將執行探測，並從結果中隨機抽樣 $garak_count 筆"

        echo ""
        print_info "使用 dummy 模型生成測試資料（不呼叫真實 API）"
        python -m garak \
            --model_type test \
            --model_name dummy \
            --probes "$garak_probes" \
            --report_prefix shield_quicktest

        print_success "Garak 執行完成！"

        echo -e "\n轉換為 Inspect AI 格式，並抽樣 $garak_count 筆..."
        python src/convert_garak_to_inspect.py --sample-size $garak_count

        print_success "轉換完成！"

        echo -e "\n查看生成的資料集："
        ls -lht adversarial_dataset/garak_adversarial_dataset_*.json | head -1

        echo -e "\n顯示資料集摘要："
        latest_garak=$(ls -t adversarial_dataset/garak_adversarial_dataset_*.json 2>/dev/null | head -1)
        if [ -n "$latest_garak" ]; then
            garak_count=$(cat "$latest_garak" | jq 'length')
            echo "生成測資數量: $garak_count"
            echo -e "\n探測器分佈:"
            cat "$latest_garak" | jq -r '.[].metadata.probe' | sort | uniq -c
        fi

        print_success "測試 1 完成！"
        press_enter
        ;;

    2)
        # ───────────────────────────────────────────────────────────────
        # 測試 2: FuzzyAI 獨立測試
        # ───────────────────────────────────────────────────────────────
        print_step "執行測試 2: FuzzyAI 獨立測試"

        # ═══════════════════════════════════════════════════════════════
        # 步驟 1: 選擇攻擊主題
        # ═══════════════════════════════════════════════════════════════
        echo -e "${BLUE}步驟 1/3: 選擇攻擊主題${NC}"
        echo ""
        echo "請選擇要生成的攻擊主題（可多選）："
        echo "  1) 惡意程式開發"
        echo "  2) 釣魚攻擊"
        echo "  3) 機密資料竊取"
        echo "  4) 社交工程"
        echo "  5) 權限提升"
        echo "  6) SQL注入"
        echo "  7) XSS攻擊"
        echo "  8) 自訂主題"
        echo "  9) 全部（1-7）"
        echo ""
        read -p "請輸入選項（可用空格分隔多個，例如: 1 2 3）: " topic_choices

        # 解析主題選擇
        topics_array=()
        for choice in $topic_choices; do
            case $choice in
                1) topics_array+=("惡意程式開發") ;;
                2) topics_array+=("釣魚攻擊") ;;
                3) topics_array+=("機密資料竊取") ;;
                4) topics_array+=("社交工程") ;;
                5) topics_array+=("權限提升") ;;
                6) topics_array+=("SQL注入") ;;
                7) topics_array+=("XSS攻擊") ;;
                8)
                    read -p "請輸入自訂主題（可用空格分隔多個）: " custom_topics
                    for topic in $custom_topics; do
                        topics_array+=("$topic")
                    done
                    ;;
                9)
                    topics_array=("惡意程式開發" "釣魚攻擊" "機密資料竊取" "社交工程" "權限提升" "SQL注入" "XSS攻擊")
                    break
                    ;;
            esac
        done

        # 檢查是否有選擇主題
        if [ ${#topics_array[@]} -eq 0 ]; then
            print_error "未選擇任何主題"
            press_enter
            continue
        fi

        echo ""
        print_success "已選擇 ${#topics_array[@]} 個主題: ${topics_array[*]}"

        # ═══════════════════════════════════════════════════════════════
        # 步驟 2: 設定生成數量
        # ═══════════════════════════════════════════════════════════════
        echo ""
        echo -e "${BLUE}步驟 2/3: 設定生成數量${NC}"
        echo ""
        read -p "每個主題要生成幾筆資料？[預設: 5]: " fuzzy_count
        fuzzy_count=${fuzzy_count:-5}

        total_count=$((${#topics_array[@]} * fuzzy_count))
        echo ""
        print_info "將生成總計 $total_count 筆資料 (${#topics_array[@]} 主題 × $fuzzy_count 筆)"

        # ═══════════════════════════════════════════════════════════════
        # 步驟 3: 選擇引擎
        # ═══════════════════════════════════════════════════════════════
        echo ""
        echo -e "${BLUE}步驟 3/3: 選擇 FuzzyAI 引擎${NC}"
        echo ""
        echo "請選擇 FuzzyAI 引擎："
        echo "  1) Ollama (本地免費，需要先安裝 Ollama)"
        echo "  2) NVIDIA NIM (雲端高品質，需要 API Key)"
        echo ""
        read -p "請選擇 [1-2]: " fuzzy_engine

        case $fuzzy_engine in
            1)
                # 使用 Ollama
                print_info "使用 Ollama 引擎"

                print_info "檢查 Ollama 服務..."
                if pgrep -x ollama > /dev/null; then
                    print_success "Ollama 正在運行"
                else
                    print_info "啟動 Ollama 服務..."
                    ollama serve > /dev/null 2>&1 &
                    sleep 3
                    if pgrep -x ollama > /dev/null; then
                        print_success "Ollama 已啟動"
                    else
                        print_error "Ollama 啟動失敗，請手動執行: ollama serve"
                        press_enter
                        continue
                    fi
                fi

                print_info "檢查 llama3:8b 模型..."
                if ollama list | grep -q "llama3:8b"; then
                    print_success "llama3:8b 模型已存在"
                else
                    print_info "下載 llama3:8b 模型（這可能需要幾分鐘）..."
                    ollama pull llama3:8b
                fi

                echo ""
                print_info "開始生成 $total_count 筆測試資料..."
                echo -e "${YELLOW}主題: ${topics_array[*]}${NC}"
                echo -e "${YELLOW}每主題數量: $fuzzy_count 筆${NC}"
                echo ""

                # 直接傳遞主題陣列（不要用 eval）
                python -u src/generate_fuzzyai_dataset.py \
                    --engine ollama \
                    --model llama3:8b \
                    --topics "${topics_array[@]}" \
                    --count $fuzzy_count \
                    --delay 0.5
                ;;

            2)
                # 使用 NVIDIA NIM
                print_info "使用 NVIDIA NIM 引擎"

                if [ -z "$NVIDIA_API_KEY" ]; then
                    print_error "NVIDIA_API_KEY 未設定"
                    echo ""
                    read -p "請輸入 NVIDIA API Key: " nim_key
                    if [ -z "$nim_key" ]; then
                        print_error "未輸入 API Key，取消測試"
                        press_enter
                        continue
                    fi
                    export NVIDIA_API_KEY="$nim_key"
                fi

                print_success "API Key: ${NVIDIA_API_KEY:0:10}..."

                # 計算預估時間
                estimated_time=$((total_count * 4))  # 每筆約 4 秒（3秒延遲 + 1秒處理）
                estimated_minutes=$((estimated_time / 60))

                echo ""
                echo -e "${YELLOW}⏳ 使用 NVIDIA NIM 生成測試資料...${NC}"
                echo -e "${YELLOW}   主題數量: ${#topics_array[@]} 個 (${topics_array[*]})${NC}"
                echo -e "${YELLOW}   每主題生成: $fuzzy_count 筆${NC}"
                echo -e "${YELLOW}   總計: $total_count 筆${NC}"
                echo -e "${YELLOW}   預估時間: 約 $estimated_minutes 分鐘（每個請求間隔 3 秒）${NC}"
                echo -e "${YELLOW}   進度會即時顯示，請耐心等待...${NC}"
                echo ""
                echo -e "${CYAN}[提示] 你會看到：${NC}"
                echo -e "${CYAN}  - 初始化訊息（立即顯示）${NC}"
                echo -e "${CYAN}  - 每個主題的處理進度${NC}"
                echo -e "${CYAN}  - 每個變異類型的生成進度（每 3-5 秒更新一次）${NC}"
                echo -e "${CYAN}  - 完成百分比（即時更新）${NC}"
                echo ""

                # 使用 python -u 確保無緩衝輸出（直接傳遞陣列）
                python -u src/generate_fuzzyai_dataset.py \
                    --engine nim \
                    --topics "${topics_array[@]}" \
                    --count $fuzzy_count \
                    --delay 3
                ;;

            *)
                print_error "無效的選項"
                press_enter
                continue
                ;;
        esac

        print_success "FuzzyAI 執行完成！"

        echo -e "\n查看生成的資料集："
        ls -lht adversarial_dataset/fuzzyai_adversarial_dataset_*.json | head -1

        echo -e "\n顯示資料集摘要："
        latest_fuzzy=$(ls -t adversarial_dataset/fuzzyai_adversarial_dataset_*.json 2>/dev/null | head -1)
        if [ -n "$latest_fuzzy" ]; then
            cat "$latest_fuzzy" | jq 'length' | xargs -I {} echo "生成測資數量: {}"
            echo -e "\n變異類型分佈:"
            cat "$latest_fuzzy" | jq -r '.[].metadata.mutation_type' | sort | uniq -c
        fi

        print_success "測試 2 完成！"
        press_enter
        ;;

    3)
        # ───────────────────────────────────────────────────────────────
        # 測試 3: 雙擎生成（不評估）
        # ───────────────────────────────────────────────────────────────
        print_step "執行測試 3: 雙擎生成（不評估）"

        print_info "這將執行 Garak + FuzzyAI，但不進行 Inspect AI 評估"
        echo ""

        # ═══════════════════════════════════════════════════════════════
        # 步驟 1: Garak 設定
        # ═══════════════════════════════════════════════════════════════
        echo -e "${BLUE}步驟 1/3: Garak 設定${NC}"
        echo ""
        read -p "Garak 要生成幾筆測試資料？[預設: 10]: " dual_garak_count
        dual_garak_count=${dual_garak_count:-10}

        echo ""
        print_info "Garak 將生成 $dual_garak_count 筆標準探測攻擊"

        # ═══════════════════════════════════════════════════════════════
        # 步驟 2: FuzzyAI 設定
        # ═══════════════════════════════════════════════════════════════
        echo ""
        echo -e "${BLUE}步驟 2/3: FuzzyAI 設定${NC}"
        echo ""
        read -p "FuzzyAI 每個主題生成幾筆？[預設: 5]: " dual_fuzzy_count
        dual_fuzzy_count=${dual_fuzzy_count:-5}

        echo ""
        echo "FuzzyAI 主題（請輸入主題名稱，用空格分隔）："
        echo "  範例: 惡意程式開發 釣魚攻擊 SQL注入"
        read -p "  或直接 Enter 使用預設 [惡意程式開發 機密資料竊取]: " dual_topics
        if [ -z "$dual_topics" ]; then
            dual_topics="惡意程式開發 機密資料竊取"
        fi

        echo ""
        print_info "FuzzyAI 會針對 [$dual_topics] 各生成 $dual_fuzzy_count 筆"

        # ═══════════════════════════════════════════════════════════════
        # 步驟 3: 選擇 FuzzyAI 引擎
        # ═══════════════════════════════════════════════════════════════
        echo ""
        echo -e "${BLUE}步驟 3/3: 選擇 FuzzyAI 引擎${NC}"
        echo ""
        echo "請選擇 FuzzyAI 引擎："
        echo "  1) Ollama (本地免費，需要先安裝 Ollama)"
        echo "  2) NVIDIA NIM (雲端高品質，需要 API Key)"
        echo ""
        read -p "請選擇 [1-2]: " dual_fuzzy_engine

        case $dual_fuzzy_engine in
            1)
                fuzzy_engine_name="ollama"
                fuzzy_model_name="llama3:8b"
                print_info "使用 Ollama 引擎 (llama3:8b)"
                ;;
            2)
                fuzzy_engine_name="nim"
                fuzzy_model_name="meta/llama-3.1-8b-instruct"
                print_info "使用 NVIDIA NIM 引擎"

                if [ -z "$NVIDIA_API_KEY" ]; then
                    print_error "NVIDIA_API_KEY 未設定"
                    echo ""
                    read -p "請輸入 NVIDIA API Key: " nim_key
                    if [ -z "$nim_key" ]; then
                        print_error "未輸入 API Key，取消測試"
                        press_enter
                        continue
                    fi
                    export NVIDIA_API_KEY="$nim_key"
                fi
                print_success "API Key 已設定"
                ;;
            *)
                print_error "無效的選項，使用預設: Ollama"
                fuzzy_engine_name="ollama"
                fuzzy_model_name="llama3:8b"
                ;;
        esac

        echo ""
        print_info "開始雙擎生成..."
        bash scripts/run_audit_v2.sh \
            --mode both \
            --garak-count $dual_garak_count \
            --fuzzyai-engine $fuzzy_engine_name \
            --fuzzyai-model $fuzzy_model_name \
            --fuzzyai-count $dual_fuzzy_count \
            --fuzzyai-topics "$dual_topics" \
            --skip-inspect

        print_success "雙擎生成完成！"

        echo -e "\n資料集統計："
        # 只讀取最新的檔案
        latest_garak=$(ls -t adversarial_dataset/garak_adversarial_dataset_*.json 2>/dev/null | head -1)
        latest_fuzzy=$(ls -t adversarial_dataset/fuzzyai_adversarial_dataset_*.json 2>/dev/null | head -1)

        if [ -n "$latest_garak" ]; then
            garak_count=$(jq 'length' "$latest_garak" 2>/dev/null || echo 0)
        else
            garak_count=0
        fi

        if [ -n "$latest_fuzzy" ]; then
            fuzzyai_count=$(jq 'length' "$latest_fuzzy" 2>/dev/null || echo 0)
        else
            fuzzyai_count=0
        fi

        echo "Garak 測資數量: $garak_count (來自最新檔案)"
        echo "FuzzyAI 測資數量: $fuzzyai_count (來自最新檔案)"
        echo "總計: $((garak_count + fuzzyai_count)) 筆"

        print_success "測試 3 完成！"
        press_enter
        ;;

    4)
        # ───────────────────────────────────────────────────────────────
        # 測試 4: 完整雙擎 + 評估
        # ───────────────────────────────────────────────────────────────
        print_step "執行測試 4: 完整雙擎 + Inspect AI 評估"

        print_info "⚠️  此測試將呼叫真實的 API，可能產生費用！"

        echo -e "\n檢查環境變數..."
        if [ -z "$OPENAI_API_KEY" ]; then
            print_error "OPENAI_API_KEY 未設定"
            echo -e "\n請設定環境變數："
            echo "  export OPENAI_API_KEY=\"your_api_key\""
            echo "  export OPENAI_BASE_URL=\"https://integrate.api.nvidia.com/v1\""
            echo ""
            read -p "是否現在設定？(y/n): " setup_env
            if [ "$setup_env" = "y" ]; then
                read -p "請輸入 API Key: " api_key
                export OPENAI_API_KEY="$api_key"
                read -p "請輸入 Base URL (直接 Enter 使用 NVIDIA NIM): " base_url
                if [ -z "$base_url" ]; then
                    export OPENAI_BASE_URL="https://integrate.api.nvidia.com/v1"
                else
                    export OPENAI_BASE_URL="$base_url"
                fi
            else
                print_error "取消測試"
                press_enter
                continue
            fi
        else
            print_success "API Key 已設定: ${OPENAI_API_KEY:0:10}..."
            print_success "Base URL: ${OPENAI_BASE_URL}"
        fi

        # ═══════════════════════════════════════════════════════════════
        # 步驟 1: Garak 設定
        # ═══════════════════════════════════════════════════════════════
        echo ""
        echo -e "${BLUE}步驟 1/3: Garak 設定${NC}"
        echo ""
        read -p "Garak 要生成幾筆測試資料？[預設: 10]: " full_garak_count
        full_garak_count=${full_garak_count:-10}

        echo ""
        print_info "Garak 將生成 $full_garak_count 筆標準探測攻擊"

        # ═══════════════════════════════════════════════════════════════
        # 步驟 2: FuzzyAI 設定
        # ═══════════════════════════════════════════════════════════════
        echo ""
        echo -e "${BLUE}步驟 2/3: FuzzyAI 設定${NC}"
        echo ""
        read -p "FuzzyAI 每個主題生成幾筆？[預設: 5]: " full_fuzzy_count
        full_fuzzy_count=${full_fuzzy_count:-5}

        echo ""
        echo "FuzzyAI 主題（請輸入主題名稱，用空格分隔）："
        echo "  範例: 惡意程式開發 釣魚攻擊 SQL注入"
        read -p "  或直接 Enter 使用預設 [惡意程式開發 機密資料竊取]: " full_topics
        if [ -z "$full_topics" ]; then
            full_topics="惡意程式開發 機密資料竊取"
        fi

        echo ""
        print_info "FuzzyAI 會針對 [$full_topics] 各生成 $full_fuzzy_count 筆"

        # ═══════════════════════════════════════════════════════════════
        # 步驟 3: 選擇 FuzzyAI 引擎
        # ═══════════════════════════════════════════════════════════════
        echo ""
        echo -e "${BLUE}步驟 3/3: 選擇 FuzzyAI 引擎${NC}"
        echo ""
        echo "請選擇 FuzzyAI 引擎："
        echo "  1) Ollama (本地免費，需要先安裝 Ollama)"
        echo "  2) NVIDIA NIM (雲端高品質，需要 API Key)"
        echo ""
        read -p "請選擇 [1-2]: " full_fuzzy_engine

        case $full_fuzzy_engine in
            1)
                fuzzy_engine_name="ollama"
                fuzzy_model_name="llama3:8b"
                print_info "使用 Ollama 引擎 (llama3:8b)"
                ;;
            2)
                fuzzy_engine_name="nim"
                fuzzy_model_name="meta/llama-3.1-8b-instruct"
                print_info "使用 NVIDIA NIM 引擎"

                if [ -z "$NVIDIA_API_KEY" ]; then
                    print_error "NVIDIA_API_KEY 未設定"
                    echo ""
                    read -p "請輸入 NVIDIA API Key: " nim_key
                    if [ -z "$nim_key" ]; then
                        print_error "未輸入 API Key，取消測試"
                        press_enter
                        continue
                    fi
                    export NVIDIA_API_KEY="$nim_key"
                fi
                print_success "API Key 已設定"
                ;;
            *)
                print_error "無效的選項，使用預設: Ollama"
                fuzzy_engine_name="ollama"
                fuzzy_model_name="llama3:8b"
                ;;
        esac

        # 計算總測資數量
        topic_count=$(echo $full_topics | wc -w)
        total_fuzzy=$((topic_count * full_fuzzy_count))
        total_all=$((full_garak_count + total_fuzzy))

        echo ""
        echo -e "${YELLOW}是否繼續執行完整評估？這將：${NC}"
        echo "  1. 執行 Garak 生成 $full_garak_count 筆測試資料"
        echo "  2. 執行 FuzzyAI 生成 $total_fuzzy 筆變異樣本 ($topic_count 主題 × $full_fuzzy_count 筆)"
        echo "  3. 使用 Inspect AI 評估總計 $total_all 筆資料（會產生費用）"
        echo ""
        read -p "確認執行？(y/n): " confirm

        if [ "$confirm" != "y" ]; then
            print_info "已取消"
            press_enter
            continue
        fi

        bash scripts/run_audit_v2.sh \
            --mode both \
            --garak-count $full_garak_count \
            --fuzzyai-engine $fuzzy_engine_name \
            --fuzzyai-model $fuzzy_model_name \
            --fuzzyai-count $full_fuzzy_count \
            --fuzzyai-topics "$full_topics" \
            --model openai/meta/llama-3.1-70b-instruct \
            --max-connections 1

        print_success "完整測試完成！"

        echo -e "\n查看報告："
        echo "  inspect view"
        press_enter
        ;;

    5)
        # ───────────────────────────────────────────────────────────────
        # 查看現有報告
        # ───────────────────────────────────────────────────────────────
        print_step "查看現有報告"

        echo "生成的資料集："
        ls -lht adversarial_dataset/ 2>/dev/null || echo "  無資料集"

        echo -e "\nInspect AI 報告："
        ls -lht inspect_report/ 2>/dev/null || echo "  無報告"

        echo -e "\nGarak 原始報告："
        ls -lht ~/.local/share/garak/garak_runs/ 2>/dev/null | head -5 || echo "  無報告"

        echo -e "\n${YELLOW}提示：使用 'inspect view' 查看詳細報告${NC}"
        press_enter
        ;;

    6)
        # ───────────────────────────────────────────────────────────────
        # 清理測試資料
        # ───────────────────────────────────────────────────────────────
        print_step "清理測試資料"

        echo -e "${YELLOW}警告：這將刪除所有測試資料！${NC}"
        echo "  - adversarial_dataset/*.json"
        echo "  - inspect_report/*"
        echo ""
        read -p "確認刪除？(yes/no): " confirm_delete

        if [ "$confirm_delete" = "yes" ]; then
            rm -f adversarial_dataset/*.json
            rm -f inspect_report/*
            print_success "清理完成！"
        else
            print_info "已取消"
        fi
        press_enter
        ;;

    0)
        echo ""
        print_step "感謝使用 S.H.I.E.L.D. v2.0"

        echo "下一步建議："
        echo "  1. 查看完整測試指南: cat TESTING_GUIDE.md"
        echo "  2. 查看整合文檔: cat docs/INTEGRATION_GUIDE.md"
        echo "  3. 查看快速參考: cat GARAK_QUICKREF.md 或 FUZZYAI_QUICKREF.md"
        echo "  4. 查看報告: inspect view"
        echo ""

        print_success "再見！"
        echo ""
        exit 0
        ;;

    *)
        print_error "無效的選項，請重新選擇"
        press_enter
        ;;
    esac
done
