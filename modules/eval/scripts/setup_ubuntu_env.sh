#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# S.H.I.E.L.D. 審計平台 - Ubuntu Server 環境自動化部署腳本
# ═══════════════════════════════════════════════════════════════════════
# TonTon H.-D. Huang Ph.D.
# https://TWMAN.ORG
# ═══════════════════════════════════════════════════════════════════════
# 功能:
#   1. 更新系統套件庫
#   2. 安裝 Python 3.10 虛擬環境與編譯工具鏈
#   3. 建立並啟用 Python 虛擬環境
#   4. 安裝專案依賴套件
#
# 使用方式:
#   chmod +x scripts/setup_ubuntu_env.sh
#   ./scripts/setup_ubuntu_env.sh
# ═══════════════════════════════════════════════════════════════════════

set -e  # 遇到錯誤立即退出

# ───────────────────────────────────────────────────────────────────────
# 顏色輸出定義
# ───────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# ───────────────────────────────────────────────────────────────────────
# Step 1: 系統環境檢查與更新
# ───────────────────────────────────────────────────────────────────────
log_info "開始部署 S.H.I.E.L.D. 審計平台環境..."
echo "═══════════════════════════════════════════════════════════════════════"

log_info "Step 1: 更新 APT 套件庫索引..."
sudo apt-get update -qq

log_success "APT 套件庫索引更新完成"

# ───────────────────────────────────────────────────────────────────────
# Step 2: 安裝系統依賴套件
# ───────────────────────────────────────────────────────────────────────
log_info "Step 2: 安裝 Python 虛擬環境與編譯工具..."

# 檢查 Python 3.10 是否已安裝
if ! command -v python3.10 &> /dev/null; then
    log_warning "Python 3.10 未安裝，正在安裝..."
    sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
else
    log_success "Python 3.10 已安裝 ($(python3.10 --version))"
fi

# 安裝編譯工具鏈 (某些 Python 套件需要從原始碼編譯)
log_info "安裝 build-essential 與 pip..."
sudo apt-get install -y build-essential python3-pip

log_success "系統依賴套件安裝完成"

# ───────────────────────────────────────────────────────────────────────
# Step 3: 建立 Python 虛擬環境
# ───────────────────────────────────────────────────────────────────────
log_info "Step 3: 建立 Python 虛擬環境 (shield-audit-env)..."

VENV_PATH="shield-audit-env"

if [ -d "$VENV_PATH" ]; then
    log_warning "虛擬環境已存在，跳過建立步驟"
else
    python3.10 -m venv "$VENV_PATH"
    log_success "虛擬環境建立完成: $VENV_PATH"
fi

# ───────────────────────────────────────────────────────────────────────
# Step 4: 啟用虛擬環境並安裝依賴套件
# ───────────────────────────────────────────────────────────────────────
log_info "Step 4: 安裝 Python 依賴套件..."

# 啟用虛擬環境
source "$VENV_PATH/bin/activate"

# 升級 pip 到最新版本
log_info "升級 pip 至最新版本..."
pip install --upgrade pip setuptools wheel

# 安裝專案依賴
log_info "從 requirements-audit.txt 安裝套件..."
pip install -r requirements-audit.txt

log_success "所有 Python 依賴套件安裝完成"

# ───────────────────────────────────────────────────────────────────────
# Step 5: 環境變數配置提醒
# ───────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
log_success "S.H.I.E.L.D. 審計平台環境部署完成！"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
log_info "後續步驟:"
echo "  1. 啟用虛擬環境:"
echo "     ${GREEN}source shield-audit-env/bin/activate${NC}"
echo ""
echo "  2. 設定環境變數 (如果目標 API 需要身份驗證):"
echo "     ${GREEN}export SHIELD_TARGET_API_KEY=\"your_api_key_here\"${NC}"
echo ""
echo "  3. 執行審計任務:"
echo "     ${GREEN}inspect eval src/shield_audit_workflow.py${NC}"
echo ""
echo "  4. 檢視測試模式:"
echo "     ${GREEN}python src/shield_audit_workflow.py${NC}"
echo ""
log_warning "重要提醒："
echo "  - 審計結果將包含敏感資訊，請勿將 audit_results/ 目錄推送至公開倉庫"
echo "  - 建議使用 .env 檔案管理機密環境變數"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
