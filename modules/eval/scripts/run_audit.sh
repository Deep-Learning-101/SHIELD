#!/bin/bash
# 🛡️ SHIELD Phase 5 審計快速啟動腳本
#
# TonTon H.-D. Huang Ph.D.
# https://TWMAN.ORG

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_ROOT="$(dirname "$SCRIPT_DIR")"
SHIELD_ROOT="$(dirname "$(dirname "$MODULE_ROOT")")"

echo "🛡️  SHIELD Phase 5: AI 審計與合規啟動中..."
echo "📂 模組目錄: $MODULE_ROOT"
echo "📂 SHIELD 根目錄: $SHIELD_ROOT"

# 檢查虛擬環境
if [[ "$VIRTUAL_ENV" == "" ]] && [[ "$CONDA_DEFAULT_ENV" == "" ]]; then
    echo "⚠️  警告: 未偵測到 Python 虛擬環境"
    echo "請先執行以下其中一個命令："
    echo "  conda activate shield-audit-env"
    echo "  source shield-audit-env/bin/activate"
    exit 1
fi

# 切換到模組目錄
cd "$MODULE_ROOT"

# 檢查配置文件
if [[ ! -f "config/audit_config.yaml" ]]; then
    echo "❌ 配置文件不存在: config/audit_config.yaml"
    echo "請從範例文件複製："
    echo "  cp config/audit_config.example.yaml config/audit_config.yaml"
    exit 1
fi

echo "✅ 環境檢查通過"
echo ""

# 執行審計
echo "🚀 啟動 Inspect AI 審計工作流程..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

inspect eval src/shield_audit_workflow.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 審計完成！"
echo ""
echo "📊 報告位於: $SHIELD_ROOT/shared/data/audit_results/"
echo ""
echo "查看報告："
echo "  cat $SHIELD_ROOT/shared/data/audit_results/latest_summary.json"
echo ""
