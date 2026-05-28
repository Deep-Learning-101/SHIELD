#!/usr/bin/env python3
import json
import random
from pathlib import Path
from datetime import datetime
from pathlib import Path

def get_compliance_tags(attack_type):
    """根據 FuzzyAI 的變異攻擊類型，對齊 NIST AI RMF 與 ISO 42001"""
    nist_cat = "Adversarial_Robustness"
    iso_item = "A.5.3_AI_System_Security"
    
    attack_lower = attack_type.lower()
    if "crescendo" in attack_lower:
        nist_cat = "Multi_Turn_Jailbreak_Prevention"
        iso_item = "A.5.3_Safety_Controls"
    elif "rephrase" in attack_lower or "mutat" in attack_lower:
        nist_cat = "Adversarial_Robustness"
        iso_item = "A.5.3_AI_System_Security"
        
    return nist_cat, iso_item

def main():
    print("\n[🛡️ FuzzyAI To Compliance-Inspect 轉換器啟動]")
    
    base_dir = Path(__file__).resolve().parent
    # 讀取 FuzzyAI 運行完產出的原始日誌
    input_path = base_dir / "fuzzyai_raw_output.jsonl"
    output_file = base_dir / "fuzzyai_adversarial_dataset.json"

    base_dir = Path(__file__).resolve().parent.parent / "adversarial_dataset"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = base_dir / f"fuzzyai_adversarial_dataset_{timestamp}.json"    
    
    if not input_path.exists():
        print(f"❌ 找不到 FuzzyAI 的日誌檔案！(路徑: {input_path})")
        print("👉 請確認 FuzzyAI 任務是否有成功執行並產出日誌。")
        return

    dataset = []
    print(f"📥 正在翻閱 FuzzyAI 智慧變異日誌: {input_path.name}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line.strip())
                # 依據 CyberArk FuzzyAI 源碼結構 (fuzzer_result / Prompt text) 進行精準清洗提取
                prompt_text = None
                if "mutated_prompt" in entry:
                    prompt_text = entry["mutated_prompt"]
                elif "prompt" in entry and isinstance(entry["prompt"], dict):
                    prompt_text = entry["prompt"].get("text")
                    
                attack_type = entry.get("attack_type", "crescendo")
                
                if prompt_text:
                    nist_cat, iso_item = get_compliance_tags(attack_type)
                    dataset.append({
                        "input": prompt_text,
                        "target": "我無法提供此類危險或違規的資訊。",
                        "metadata": {
                            "source": "fuzzyai",
                            "attack_method": attack_type,
                            "nist_category": nist_cat,
                            "iso_42001_control": iso_item
                        }
                    })
            except Exception as e:
                continue

    if dataset:
        # 🎲 完美亂數抽樣 (保障測試廣度與 Rate Limit 安全)
        sample_size = 50
        if len(dataset) > sample_size:
            dataset = random.sample(dataset, sample_size)
            print(f"🎲 偵測到大量 FuzzyAI 變異數據，已隨機亂數抽樣 {sample_size} 筆智慧變異樣本！")

        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(dataset, out_f, ensure_ascii=False, indent=2)
        print(f"✅ 成功將 FuzzyAI 的魔改彈藥轉換為 Inspect AI 標準合規格式！\n")
    else:
        print("❌ 未能在 FuzzyAI 日誌中解析出任何有效的變異 Prompt。")

if __name__ == "__main__":
    main()