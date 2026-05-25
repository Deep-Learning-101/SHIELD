#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# S.H.I.E.L.D. 審計平台 - Conda 環境自動化部署腳本
# ═══════════════════════════════════════════════════════════════════════
# TonTon H.-D. Huang Ph.D.
# https://TWMAN.ORG
# ═══════════════════════════════════════════════════════════════════════
# 功能:
#   1. 偵測系統是否已安裝 Conda/Miniconda/Anaconda
#   2. 偵測當前是否已在 conda 環境中
#   3. 彈性選擇：使用現有環境或建立新環境
#   4. 安裝專案依賴套件
#
# 使用方式:
#   # 方式 1: 自動建立新環境
#   ./scripts/setup_conda_env.sh
#
#   # 方式 2: 先啟用現有環境，再執行腳本（會自動偵測並安裝）
#   conda activate my-existing-env
#   ./scripts/setup_conda_env.sh
#
#   # 方式 3: 指定環境名稱
#   ./scripts/setup_conda_env.sh my-custom-env
# ═══════════════════════════════════════════════════════════════════════

set -e  # 遇到錯誤立即退出

# ───────────────────────────────────────────────────────────────────────
# 顏色輸出定義
# ───────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ───────────────────────────────────────────────────────────────────────
# 輔助函數
# ───────────────────────────────────────────────────────────────────────
log_info() {
    echo -e "${BLUE}[資訊]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

log_error() {
    echo -e "${RED}[錯誤]${NC} $1"
}

log_prompt() {
    echo -e "${CYAN}[提示]${NC} $1"
}

# ───────────────────────────────────────────────────────────────────────
# Step 0: 環境偵測
# ───────────────────────────────────────────────────────────────────────
log_info "開始部署 S.H.I.E.L.D. 審計平台環境 (Conda 版本)..."
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# 預設環境名稱
DEFAULT_ENV_NAME="shield-audit-env"
TARGET_ENV_NAME="${1:-$DEFAULT_ENV_NAME}"

# 偵測 Conda 是否已安裝
log_info "Step 0: 偵測 Conda 安裝狀態..."

if ! command -v conda &> /dev/null; then
    log_error "未偵測到 Conda！"
    echo ""
    echo "請先安裝 Miniconda 或 Anaconda："
    echo "  Miniconda (推薦): https://docs.conda.io/en/latest/miniconda.html"
    echo "  Anaconda (完整版): https://www.anaconda.com/download"
    echo ""
    echo "安裝後請執行以下指令初始化 Conda："
    echo "  ${GREEN}conda init bash${NC}"
    echo "  ${GREEN}source ~/.bashrc${NC}"
    exit 1
fi

log_success "Conda 已安裝 ($(conda --version))"

# 偵測當前是否在 conda 環境中
CURRENT_CONDA_ENV="${CONDA_DEFAULT_ENV:-}"

if [ -n "$CURRENT_CONDA_ENV" ] && [ "$CURRENT_CONDA_ENV" != "base" ]; then
    log_success "偵測到當前已在 Conda 環境中: ${CYAN}$CURRENT_CONDA_ENV${NC}"
    echo ""
    log_prompt "您希望："
    echo "  ${GREEN}[1]${NC} 直接在當前環境 ($CURRENT_CONDA_ENV) 中安裝依賴套件"
    echo "  ${GREEN}[2]${NC} 建立新的 Conda 環境 ($TARGET_ENV_NAME)"
    echo ""
    read -p "請選擇 [1/2] (預設: 1): " user_choice
    user_choice=${user_choice:-1}

    if [ "$user_choice" = "1" ]; then
        TARGET_ENV_NAME="$CURRENT_CONDA_ENV"
        INSTALL_MODE="existing"
        log_info "將在現有環境 ${CYAN}$TARGET_ENV_NAME${NC} 中安裝套件"
    else
        INSTALL_MODE="new"
        log_info "將建立新環境 ${CYAN}$TARGET_ENV_NAME${NC}"
    fi
else
    # 沒有啟用 conda 環境，檢查目標環境是否已存在
    if conda env list | grep -q "^${TARGET_ENV_NAME} "; then
        log_warning "環境 ${CYAN}$TARGET_ENV_NAME${NC} 已存在"
        echo ""
        log_prompt "您希望："
        echo "  ${GREEN}[1]${NC} 使用現有環境 ($TARGET_ENV_NAME) 並更新依賴套件"
        echo "  ${GREEN}[2]${NC} 刪除舊環境並重新建立"
        echo "  ${GREEN}[3]${NC} 退出安裝"
        echo ""
        read -p "請選擇 [1/2/3] (預設: 1): " user_choice
        user_choice=${user_choice:-1}

        if [ "$user_choice" = "1" ]; then
            INSTALL_MODE="existing"
            log_info "將使用現有環境 ${CYAN}$TARGET_ENV_NAME${NC}"
        elif [ "$user_choice" = "2" ]; then
            log_warning "正在刪除舊環境..."
            conda env remove -n "$TARGET_ENV_NAME" -y
            INSTALL_MODE="new"
            log_success "舊環境已刪除"
        else
            log_info "使用者取消安裝"
            exit 0
        fi
    else
        INSTALL_MODE="new"
        log_info "將建立新環境 ${CYAN}$TARGET_ENV_NAME${NC}"
    fi
fi

echo ""

# ───────────────────────────────────────────────────────────────────────
# Step 1: 建立或啟用 Conda 環境
# ───────────────────────────────────────────────────────────────────────
if [ "$INSTALL_MODE" = "new" ]; then
    log_info "Step 1: 建立新的 Conda 環境..."
    echo ""
    log_info "正在建立環境 ${CYAN}$TARGET_ENV_NAME${NC} (Python 3.10)..."

    conda create -n "$TARGET_ENV_NAME" python=3.10 -y

    log_success "Conda 環境建立完成"
else
    log_info "Step 1: 使用現有環境 ${CYAN}$TARGET_ENV_NAME${NC}"
fi

echo ""

# ───────────────────────────────────────────────────────────────────────
# Step 2: 啟用環境並安裝依賴套件
# ───────────────────────────────────────────────────────────────────────
log_info "Step 2: 安裝 Python 依賴套件..."

# 取得 conda 的初始化腳本路徑
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

# 啟用目標環境
conda activate "$TARGET_ENV_NAME"

# 確認當前環境
ACTIVATED_ENV="${CONDA_DEFAULT_ENV:-}"
if [ "$ACTIVATED_ENV" != "$TARGET_ENV_NAME" ]; then
    log_error "環境啟用失敗！"
    echo "當前環境: $ACTIVATED_ENV"
    echo "目標環境: $TARGET_ENV_NAME"
    exit 1
fi

log_success "環境已啟用: ${CYAN}$TARGET_ENV_NAME${NC}"
echo ""

# 升級 pip 到最新版本
log_info "升級 pip 至最新版本..."
pip install --upgrade pip setuptools wheel -q

# 安裝專案依賴
log_info "從 requirements-audit.txt 安裝套件..."
echo ""

pip install -r requirements-audit.txt

log_success "所有 Python 依賴套件安裝完成"

# ───────────────────────────────────────────────────────────────────────
# Step 3: 驗證安裝
# ───────────────────────────────────────────────────────────────────────
echo ""
log_info "Step 3: 驗證關鍵套件安裝狀態..."

REQUIRED_PACKAGES=("inspect_ai" "yaml" "garak" "shap" "captum")
ALL_INSTALLED=true

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        log_success "✓ $package"
    else
        log_warning "✗ $package (安裝失敗或不可用)"
        ALL_INSTALLED=false
    fi
done

echo ""

# ───────────────────────────────────────────────────────────────────────
# Step 4: 環境資訊總結
# ───────────────────────────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════════════════"
log_success "S.H.I.E.L.D. 審計平台環境部署完成！"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
log_info "環境資訊："
echo "  • Conda 環境名稱: ${CYAN}$TARGET_ENV_NAME${NC}"
echo "  • Python 版本: $(python --version)"
echo "  • Pip 版本: $(pip --version | awk '{print $2}')"
echo ""

# ───────────────────────────────────────────────────────────────────────
# Step 5: 後續步驟指引
# ───────────────────────────────────────────────────────────────────────
log_info "後續步驟:"
echo ""

if [ "$ACTIVATED_ENV" = "$TARGET_ENV_NAME" ]; then
    log_success "環境已啟用，您可以直接執行以下指令："
    echo ""
    echo "  ${GREEN}# 設定環境變數（如果目標 API 需要身份驗證）${NC}"
    echo "  ${CYAN}export SHIELD_TARGET_API_KEY=\"your_api_key_here\"${NC}"
    echo ""
    echo "  ${GREEN}# 執行審計任務${NC}"
    echo "  ${CYAN}inspect eval src/shield_audit_workflow.py${NC}"
    echo ""
    echo "  ${GREEN}# 或檢視測試模式${NC}"
    echo "  ${CYAN}python src/shield_audit_workflow.py${NC}"
else
    echo "  ${GREEN}1. 啟用 Conda 環境:${NC}"
    echo "     ${CYAN}conda activate $TARGET_ENV_NAME${NC}"
    echo ""
    echo "  ${GREEN}2. 設定環境變數（如果目標 API 需要身份驗證）:${NC}"
    echo "     ${CYAN}export SHIELD_TARGET_API_KEY=\"your_api_key_here\"${NC}"
    echo ""
    echo "  ${GREEN}3. 執行審計任務:${NC}"
    echo "     ${CYAN}inspect eval src/shield_audit_workflow.py${NC}"
    echo ""
    echo "  ${GREEN}4. 或檢視測試模式:${NC}"
    echo "     ${CYAN}python src/shield_audit_workflow.py${NC}"
fi

echo ""
log_info "管理 Conda 環境的實用指令："
echo "  • 列出所有環境:    ${CYAN}conda env list${NC}"
echo "  • 停用當前環境:    ${CYAN}conda deactivate${NC}"
echo "  • 刪除環境:        ${CYAN}conda env remove -n $TARGET_ENV_NAME${NC}"
echo "  • 匯出環境配置:    ${CYAN}conda env export > environment.yml${NC}"
echo ""

log_warning "重要提醒："
echo "  - 審計結果將包含敏感資訊，請勿將 audit_results/ 目錄推送至公開倉庫"
echo "  - 建議使用 .env 檔案管理機密環境變數"
echo ""

if [ "$ALL_INSTALLED" = false ]; then
    log_warning "部分套件安裝驗證失敗，但這可能不影響核心功能"
    log_info "如果遇到問題，請執行: ${CYAN}conda activate $TARGET_ENV_NAME && pip install -r requirements-audit.txt${NC}"
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════════════"
