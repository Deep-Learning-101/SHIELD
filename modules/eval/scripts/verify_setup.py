#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════
S.H.I.E.L.D. 審計平台 - 安裝驗證腳本
═══════════════════════════════════════════════════════════════════════
TonTon H.-D. Huang Ph.D.
https://TWMAN.ORG
═══════════════════════════════════════════════════════════════════════
功能：驗證專案結構與配置檔案的完整性
使用方式：python scripts/verify_setup.py
═══════════════════════════════════════════════════════════════════════
"""

import os
import sys
from pathlib import Path

# 設定專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_file_exists(file_path: str, description: str) -> bool:
    """檢查檔案是否存在"""
    full_path = PROJECT_ROOT / file_path
    if full_path.exists():
        size = full_path.stat().st_size
        print(f"✓ {description}: {file_path} ({size} bytes)")
        return True
    else:
        print(f"✗ {description}: {file_path} [不存在]")
        return False


def check_yaml_syntax():
    """檢查 YAML 配置檔案語法"""
    try:
        import yaml
        config_path = PROJECT_ROOT / "config" / "audit_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"✓ YAML 配置檔案語法正確")
        print(f"  - 審計目標: {config.get('audit_target', {}).get('name', 'N/A')}")
        print(f"  - 配置區塊數量: {len(config)}")
        return True
    except ImportError:
        print(f"⚠ PyYAML 尚未安裝，跳過 YAML 語法檢查")
        return True
    except Exception as e:
        print(f"✗ YAML 配置檔案語法錯誤: {e}")
        return False


def main():
    """主驗證流程"""
    print("═" * 70)
    print("S.H.I.E.L.D. 審計平台 - 安裝驗證")
    print("═" * 70)
    print()

    results = []

    # 檢查核心檔案
    print("[1] 檢查核心檔案...")
    results.append(check_file_exists("config/audit_config.yaml", "配置檔案"))
    results.append(check_file_exists("src/shield_audit_workflow.py", "主程式"))
    results.append(check_file_exists("requirements-audit.txt", "依賴清單"))
    results.append(check_file_exists("scripts/setup_ubuntu_env.sh", "部署腳本"))
    results.append(check_file_exists(".gitignore", "Git 忽略規則"))
    results.append(check_file_exists("README.md", "專案說明文件"))
    print()

    # 檢查腳本執行權限
    print("[2] 檢查腳本權限...")
    setup_script = PROJECT_ROOT / "scripts" / "setup_ubuntu_env.sh"
    if setup_script.exists() and os.access(setup_script, os.X_OK):
        print("✓ 部署腳本具有執行權限")
        results.append(True)
    elif setup_script.exists():
        print("⚠ 部署腳本缺少執行權限（可執行: chmod +x scripts/setup_ubuntu_env.sh）")
        results.append(True)
    else:
        print("✗ 部署腳本不存在")
        results.append(False)
    print()

    # 檢查 YAML 語法
    print("[3] 檢查配置檔案語法...")
    results.append(check_yaml_syntax())
    print()

    # 檢查目錄結構
    print("[4] 檢查目錄結構...")
    required_dirs = ["config", "src", "scripts"]
    for dir_name in required_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"✓ 目錄存在: {dir_name}/")
            results.append(True)
        else:
            print(f"✗ 目錄不存在: {dir_name}/")
            results.append(False)
    print()

    # 總結
    print("═" * 70)
    success_count = sum(results)
    total_count = len(results)
    print(f"驗證完成: {success_count}/{total_count} 項檢查通過")

    if success_count == total_count:
        print("✓ 專案結構完整！可以執行部署腳本進行環境安裝。")
        print()
        print("下一步：")
        print("  1. 執行部署腳本: ./scripts/setup_ubuntu_env.sh")
        print("  2. 啟用虛擬環境: source shield-audit-env/bin/activate")
        print("  3. 測試主程式: python src/shield_audit_workflow.py")
        return 0
    else:
        print("✗ 部分檢查失敗，請修復上述問題後重新執行驗證。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
