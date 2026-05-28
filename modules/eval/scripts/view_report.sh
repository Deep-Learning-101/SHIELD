#!/bin/bash
# 視覺化審計結果的專用腳本
SHIELD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 🌟 同步修改：讓觀看工具指向你剛剛指定的 eval/inspect_report 資料夾
OUTPUT_DIR="$SHIELD_ROOT/inspect_report"

echo "🌐 正在啟動審計儀表板..."
inspect view --log-dir "$OUTPUT_DIR" --host 0.0.0.0 --port 8000