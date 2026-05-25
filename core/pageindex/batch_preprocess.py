"""
PageIndex 批次預處理模組

TonTon H.-D. Huang Ph.D.
https://TWMAN.ORG
"""

import os
import glob
import fitz  # PyMuPDF
import json
import argparse
import opendataloader_pdf # 引入地表最強 PDF 解析器

def extract_pdf_page_images(pdf_path, output_dir):
    """將 PDF 轉為高畫質圖片供 Gemini 閱讀"""
    os.makedirs(output_dir, exist_ok=True)
    pdf_document = fitz.open(pdf_path)
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        img_path = os.path.join(output_dir, f"page_{page_number + 1}.jpg")
        with open(img_path, "wb") as f:
            f.write(pix.tobytes("jpeg"))
    pdf_document.close()

def extract_text_nodes(data, current_page=1):
    """遞迴探測：不管 JSON 結構多深，只要有 text 就全部挖出來"""
    nodes = []
    if isinstance(data, dict):
        # 1. 嘗試捕捉頁碼 (有些解析器會把 page 寫在父層)
        page_val = data.get("page") or data.get("page_number")
        if page_val:
            try:
                current_page = int(page_val)
            except:
                pass

        # 2. 尋找文字內容 (兼容不同的 Key 命名)
        text_val = data.get("text") or data.get("content") or data.get("str") or ""
        
        # 如果找到真正的文字，就把它存起來
        if text_val and str(text_val).strip():
            try:
                lvl = int(data.get("level", 1))
            except:
                lvl = 1
                
            nodes.append({
                "text": str(text_val).strip(),
                "level": lvl,
                "page": current_page
            })
            
        # 3. 繼續往下挖
        for k, v in data.items():
            nodes.extend(extract_text_nodes(v, current_page))
            
    elif isinstance(data, list):
        for item in data:
            nodes.extend(extract_text_nodes(item, current_page))
            
    return nodes

def build_tree_from_odl(odl_json_path, target_json_path):
    """將 OpenDataLoader 的 JSON 轉換成樹狀結構 (終極容錯版)"""
    with open(odl_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 💡 [終極修復] 使用遞迴提取所有文字節點
    elements = extract_text_nodes(data)

    root = {"node_id": "root", "title": "文件大綱", "nodes": []}
    stack = [(0, root)] 
    node_idx = 1

    for el in elements:
        level = el["level"]
        text = el["text"]
        page_idx = el["page"]
        
        node = {
            "node_id": f"node_{node_idx}",
            "title": text[:50] + "..." if len(text) > 50 else text,
            "text": text,
            "page_index": page_idx,
            "nodes": []
        }
        node_idx += 1

        while len(stack) > 1 and stack[-1][0] >= level:
            stack.pop()

        stack[-1][1]["nodes"].append(node)
        stack.append((level, node))

    with open(target_json_path, 'w', encoding='utf-8') as f:
        json.dump(root, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批次處理企業機密法規 PDF")
    parser.add_argument("--input_dir", required=True, help="存放 PDF 的目錄路徑")
    args = parser.parse_args()

    workspace_dir = args.input_dir 
    
    image_out_dir = os.path.join(workspace_dir, "images")
    results_out_dir = os.path.join(workspace_dir, "results")
    temp_odl_dir = os.path.join(workspace_dir, "temp_odl") 

    os.makedirs(image_out_dir, exist_ok=True)
    os.makedirs(results_out_dir, exist_ok=True)
    os.makedirs(temp_odl_dir, exist_ok=True)

    pdf_files = glob.glob(os.path.join(workspace_dir, "*.pdf"))
    if not pdf_files:
        print(f"⚠️ 在 {workspace_dir} 找不到任何 PDF 檔案！")
        exit()
    
    print("🚀 [階段 1] 正在使用 OpenDataLoader 萃取結構與座標...")
    opendataloader_pdf.convert(
        input_path=pdf_files,
        output_dir=temp_odl_dir,
        format="json"  
    )

    print("🌳 [階段 2] 正在建立座標樹狀目錄與渲染高畫質圖片...")
    for pdf_path in pdf_files:
        file_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # 維持多一層目錄，防止多份 PDF 互相覆蓋
        paper_image_dir = os.path.join(image_out_dir, file_name)
        extract_pdf_page_images(pdf_path, paper_image_dir)
        
        # 將 ODL JSON 轉為 Tree JSON
        odl_json = os.path.join(temp_odl_dir, f"{file_name}.json")
        if os.path.exists(odl_json):
            tree_json_path = os.path.join(results_out_dir, f"{file_name}_structure.json")
            build_tree_from_odl(odl_json, tree_json_path)
            print(f"✅ 成功處理：{file_name}")
            
    print(f"🎉 批次處理完成！所有圖片與目錄已存放在 {workspace_dir} 之中。")