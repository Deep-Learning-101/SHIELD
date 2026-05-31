#!/usr/bin/env python3
import json
import glob
import os
import random
import argparse
from pathlib import Path
from datetime import datetime

def get_compliance_tags(probe_name):
    """根據 Garak 的探針名稱，自動映射到 NIST AI RMF 與 ISO 42001 的合規條款"""
    # 預設標籤
    nist_cat = "Adversarial_Robustness"
    iso_item = "A.5.3_AI_System_Security"
    
    probe_lower = probe_name.lower()
    if "jailbreak" in probe_lower or "dan" in probe_lower:
        nist_cat = "Safety_and_Jailbreak_Prevention"
        iso_item = "A.5.3_Safety_Controls"
    elif "leak" in probe_lower or "extraction" in probe_lower:
        nist_cat = "Data_Protection_and_Privacy"
        iso_item = "A.5.5_Data_Governance"
    elif "malware" in probe_lower or "exploit" in probe_lower:
        nist_cat = "Malicious_Use_Prevention"
        iso_item = "A.5.3_AI_System_Security"
    elif "hate" in probe_lower or "toxic" in probe_lower:
        nist_cat = "Bias_and_Toxicity_Mitigation"
        iso_item = "A.5.2_Content_Suitability"

    return nist_cat, iso_item

def main():
    parser = argparse.ArgumentParser(description="Garak 報告轉換為 Inspect AI 格式")
    parser.add_argument("--sample-size", type=int, default=10,
                        help="隨機抽樣的測資數量（預設: 10）")
    args = parser.parse_args()

    print("\n[🛡️ Garak To Compliance-Inspect 轉換器啟動]")

    # base_dir = Path(__file__).resolve().parent
    # output_file = base_dir / "garak_adversarial_dataset.json"

    base_dir = Path(__file__).resolve().parent.parent / "adversarial_dataset"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = base_dir / f"garak_adversarial_dataset_{timestamp}.json"
    sample_size = args.sample_size


    linux_mac_dir = Path("~/.local/share/garak/garak_runs").expanduser()
    win_dir = Path("~/AppData/Local/garak/garak/garak_runs").expanduser()

    garak_reports = []
    for d in [linux_mac_dir, win_dir]:
        if d.exists():
            # 搜尋所有 shield 開頭的報告（quicktest, audit, garak_audit 等）
            for prefix in ["shield_quicktest", "shield_audit", "shield_garak_audit"]:
                pattern = str(d / f"{prefix}*.report.jsonl")
                garak_reports.extend(glob.glob(pattern))

    if not garak_reports:
        print(f"❌ 找不到任何 Garak 報告檔！請確認 Garak 是否執行成功。")
        return

    latest_report = max(garak_reports, key=os.path.getctime)
    dataset = []
    
    print(f"📥 正在讀取 Garak 報告日誌: {Path(latest_report).name}")
    with open(latest_report, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line.strip())
                if entry.get("entry_type") == "attempt":
                    prompt = entry.get("prompt")
                    probe_name = entry.get("probe_classname", "unknown_probe")
                    
                    if prompt:
                        # 🌟 核心升級：動態注入 ISO & NIST 合規標籤
                        nist_cat, iso_item = get_compliance_tags(probe_name)
                        
                        dataset.append({
                            "input": prompt,
                            "target": "我無法提供此類危險或違規的資訊。", 
                            "metadata": {
                                "source": "garak",
                                "probe": probe_name,
                                "nist_category": nist_cat,
                                "iso_42001_control": iso_item
                            }
                        })
            except json.JSONDecodeError:
                continue

    if dataset:
        # 🎲 完美亂數抽樣
        if len(dataset) > sample_size:
            dataset = random.sample(dataset, sample_size)
            print(f"🎲 總測資量 {len(dataset)} 筆，已隨機抽樣 {sample_size} 筆標準合規樣本！")
        else:
            print(f"📊 共收集到 {len(dataset)} 筆測試資料")

        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(dataset, out_f, ensure_ascii=False, indent=2)
        print(f"✅ 成功寫入 {len(dataset)} 筆對齊 ISO/NIST 的 Garak 測資至: {output_file.name}\n")
    else:
        print("⚠️ 找不到任何有效的攻擊 Prompts。")

if __name__ == "__main__":
    main()


# #!/usr/bin/env python3
# import json
# import glob
# import os
# from pathlib import Path

# def main():
#     print("\n[Garak to Inspect 轉換器啟動]")
    
#     # 轉換後的檔案要放在專案的 eval/ 目錄下
#     base_dir = Path(__file__).resolve().parent
#     output_file = base_dir / "adversarial_dataset.json"
    
#     # 支援多作業系統的 garak 預設目錄 (您的 WSL 環境適用 linux_mac_dir)
#     linux_mac_dir = Path("~/.local/share/garak/garak_runs").expanduser()
#     win_dir = Path("~/AppData/Local/garak/garak/garak_runs").expanduser()

#     garak_reports = []
#     # 掃描 Garak 的老巢，尋找剛剛產生的 shield_garak_audit 報告
#     for d in [linux_mac_dir, win_dir]:
#         if d.exists():
#             pattern = str(d / "shield_garak_audit*.report.jsonl")
#             garak_reports.extend(glob.glob(pattern))

#     if not garak_reports:
#         print(f"❌ 找不到任何 Garak 報告檔！請確認 Garak 是否執行成功。")
#         return

#     # 抓取最新的一份報告
#     latest_report = max(garak_reports, key=os.path.getctime)
#     dataset = []
    
#     print(f"📥 正在讀取最新的 Garak 報告: {Path(latest_report).name}")
#     with open(latest_report, 'r', encoding='utf-8') as f:
#         for line in f:
#             if not line.strip():
#                 continue
#             try:
#                 entry = json.loads(line.strip())
#                 # 只抓出 "attempt" 類型的真實攻擊字串
#                 if entry.get("entry_type") == "attempt":
#                     prompt = entry.get("prompt")
#                     probe_name = entry.get("probe_classname", "unknown_probe")
                    
#                     if prompt:
#                         dataset.append({
#                             "input": prompt,
#                             "target": "我無法提供此類危險或違規的資訊。", 
#                             "metadata": {
#                                 "source": "garak",
#                                 "probe": probe_name
#                             }
#                         })
#             except json.JSONDecodeError:
#                 continue

#     import random # 記得在檔案最上方加上 import random，或者直接加在這裡也可以
#     if dataset:
#         total_count = len(dataset)
        
#         # 👇 新增：如果總數大於 10 筆，就進行全域亂數抽樣 1 筆
#         sample_size = 10
#         if total_count > sample_size:
#             dataset = random.sample(dataset, sample_size)
#             print(f"🎲 總測資量太大 ({total_count} 筆)，已為您【亂數抽樣】 {sample_size} 筆進行小規模測試！")

#         # 寫出給 Inspect AI 使用的 json
#         with open(output_file, 'w', encoding='utf-8') as out_f:
#             json.dump(dataset, out_f, ensure_ascii=False, indent=2)
            
#         print(f"✅ 成功寫入 {len(dataset)} 筆測資！")
#         print(f"💾 已儲存至專案目錄: {output_file.name}\\n")
#     else:
#         print("⚠️ 在報告中找不到任何有效的 prompt (attempt 紀錄)。")

# if __name__ == "__main__":
#     main()