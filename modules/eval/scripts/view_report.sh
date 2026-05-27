#!/bin/bash
# 視覺化審計結果的專用腳本
SHIELD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$SHIELD_ROOT/modules/logs/"

echo "🌐 正在啟動審計儀表板..."
inspect view --log-dir "$OUTPUT_DIR" --host 0.0.0.0 --port 8000