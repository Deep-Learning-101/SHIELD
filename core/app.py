"""
SHIELD Core - Main Application
主應用程式模組

S.H.I.E.L.D. (Sovereign Heuristic Intelligence & Enterprise Logic Defense)
主權啟發式情資與企業邏輯防禦系統

TonTon H.-D. Huang Ph.D.
https://TWMAN.ORG
"""

import streamlit as st
import pandas as pd
import json
import networkx as nx
import random
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os
import time
import glob
import shutil
import requests

from google import genai
from PIL import Image

import fitz  # PyMuPDF
import opendataloader_pdf

# ==========================================
# 📁 系統目錄初始化 (修正路徑架構)
# ==========================================
# Monorepo 架構：core 模組需要引用上層的 shared 目錄
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # SHIELD/
DATA_DIR = os.path.join(BASE_DIR, "shared", "data")
ASSETS_DIR = os.path.join(BASE_DIR, "shared", "assets")
POLICIES_DIR = os.path.join(DATA_DIR, "policies")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(POLICIES_DIR, exist_ok=True)

# ==========================================
# 🚀 初始化 Gemini Client
# ==========================================
gemini_client = None
if "GOOGLE_API_KEY" in os.environ:
    gemini_client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

# ==========================================
# 📚 PageIndex & OpenDataLoader 輔助函數 (🌟已完美修復)
# ==========================================
def load_json_tree(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_tree_for_prompt(nodes_list):
    cleaned = []
    for node in nodes_list:
        clean_node = {k: v for k, v in node.items() if k != 'text'}
        if 'nodes' in node and node['nodes']:
            clean_node['nodes'] = clean_tree_for_prompt(node['nodes'])
        cleaned.append(clean_node)
    return cleaned

def extract_pages_from_tree(tree, query):
    try:
        if not gemini_client: return [1]
        
        clean_tree = clean_tree_for_prompt(tree.get('nodes', []))
        prompt = f"""
        你是一個法規目錄檢索專家。
        請根據以下文件的樹狀大綱 (JSON 格式)，找出與問題「{query}」最相關的章節，
        並回傳該章節的 page_index (數字)。
        只需回傳數字即可，如果有多個頁面請用逗號分隔。
        目錄結構：
        {json.dumps(clean_tree, ensure_ascii=False)}
        """
        
        response = gemini_client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
        )
        pages = [int(s) for s in response.text.replace(',', ' ').split() if s.isdigit()]
        return pages if pages else [1] 
    except Exception as e:
        return [1]

def find_best_pdf_and_pages(workspace_path, query):
    """🤖 [升級版] 總圖書館長：跨多份 PDF 目錄尋找最佳解答頁面"""
    import glob, json, os
    try:
        if not gemini_client: return None, [1]
        
        json_files = glob.glob(os.path.join(workspace_path, "results", "*.json"))
        if not json_files: return None, []

        library_catalog = {}
        for j_path in json_files:
            file_name = os.path.basename(j_path).replace("_structure.json", "")
            raw_tree = load_json_tree(j_path)
            structure = raw_tree.get('structure', [raw_tree])
            clean_tree = clean_tree_for_prompt(structure)
            # 這裡把圖表索引也餵給大腦
            library_catalog[file_name] = {
                "目錄": clean_tree,
                "重要圖表清單": raw_tree.get("important_assets_index", [])
            }

        # 🌟 修正點：移除 [:40000] 暴力截斷，確保 JSON 格式不破損
        catalog_str = json.dumps(library_catalog, ensure_ascii=False)
        
        prompt = f"""
        你是一位企業級的「總圖書館長」。
        以下是我們知識庫中多份文獻的樹狀大綱與圖表清單 (JSON 格式)。
        
        使用者的問題是：「{query}」
        
        請評估哪一份文件、以及其中的哪幾個頁碼 (page) 最有可能包含答案。
        請務必只回傳純粹的 JSON 格式，絕對不要包含 ```json 標記或任何其他解釋文字！
        格式如下：
        {{
            "target_file": "選出的檔案名稱 (不要附檔名)",
            "target_pages": [頁碼1, 頁碼2]
        }}
        
        文獻目錄庫：
        {catalog_str}
        """

        response = gemini_client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
        )
        
        clean_res = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(clean_res)
        
        return result.get("target_file"), result.get("target_pages", [1])
        
    except Exception as e:
        # 🚨 把錯誤印在終端機，方便除錯
        print(f"\n[Error] 總圖書館長解析失敗: {e}")
        if 'clean_res' in locals():
            print(f"[Error] Gemini 實際回傳內容: {clean_res}\n")
            
        if json_files:
            first_file = os.path.basename(json_files[0]).replace("_structure.json", "")
            return first_file, [1]
        return None, []
        
def extract_pdf_page_images(pdf_path, output_dir):
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

def build_tree_from_odl(odl_json_path, target_json_path):
    """🌟 修正版：完美轉型與結構重組"""
    with open(odl_json_path, 'r', encoding='utf-8') as f:
        odl_data = json.load(f)

    elements = odl_data.get("kids", [])
    root = {"node_id": "root", "title": "文件大綱", "page": 1, "nodes": []}
    tables_and_figures = [] 
    
    # stack 紀錄 (階層級別, 節點參考)
    stack = [(0, root)] 
    node_idx = 1
    
    def process_elements(elem_list):
        nonlocal node_idx
        for el in elem_list:
            element_type = el.get("type", "")
            page_num = el.get("page_idx", el.get("page number", 1)) 
            content = el.get("text", el.get("content", ""))
            
            if element_type == "heading":
                # 🚨 修正：增加強型別轉換與防呆
                raw_level = el.get("level", 1)
                try:
                    level = int(raw_level)
                except (ValueError, TypeError):
                    level = 1

                new_node = {
                    "node_id": f"node_{node_idx}",
                    "title": content.strip() if content else "未命名標題",
                    "page": page_num,
                    "nodes": []
                }
                node_idx += 1
                
                while stack and stack[-1][0] >= level:
                    stack.pop()
                
                if stack:
                    stack[-1][1]["nodes"].append(new_node)
                
                stack.append((level, new_node))
                
            elif element_type in ["table", "picture", "formula", "image"]:
                item_summary = content.strip()[:100] if content else f"包含重要 {element_type}"
                tables_and_figures.append({
                    "type": element_type.upper(),
                    "page": page_num,
                    "desc": item_summary
                })
            
            if "kids" in el:
                process_elements(el["kids"])

    process_elements(elements)
    
    final_tree = {
        "structure": [root],
        "important_assets_index": tables_and_figures 
    }
    with open(target_json_path, 'w', encoding='utf-8') as f:
        json.dump(final_tree, f, ensure_ascii=False, indent=2)
    
# ==========================================
# 🔌 引入 Robin 的暗網狩獵模組
# ==========================================
try:
    from search import get_search_results
    from llm import get_llm, refine_query
    from health import check_llm_health, check_search_engines, check_tor_proxy
    from scrape import scrape_multiple
except Exception as e:
    pass

# ==========================================
# 介面基本設定
# ==========================================
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #FFFFFF; }
    [data-testid="stSidebar"] img {
        border-radius: 12px; padding: 5px; background-color: white; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.5); 
    }
</style>
""", unsafe_allow_html=True)
st.set_page_config(page_title="S.H.I.E.L.D. 主權啟發式情資與企業邏輯防禦", page_icon="🛡️", layout="wide")

if "ontology_graph" not in st.session_state:
    st.session_state.ontology_graph = None
if "darkweb_results" not in st.session_state:
    st.session_state.darkweb_results = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "generated_rule" not in st.session_state:
    st.session_state.generated_rule = ""
    
# ==========================================
# 輔助函式：圖譜建置與日誌
# ==========================================
def get_local_datasets(data_dir):
    if not os.path.exists(data_dir): return []
    prefixes = set()
    for f in os.listdir(data_dir):
        if f.endswith("_assets.csv"): prefixes.add(f.replace("_assets.csv", ""))
    valid_datasets = []
    for p in prefixes:
        if os.path.exists(os.path.join(data_dir, f"{p}_compliance.json")): valid_datasets.append(p)
    return sorted(valid_datasets)

def build_defense_ontology(assets_df, compliance_rules):
    G = nx.DiGraph()
    for _, row in assets_df.iterrows():
        asset_id = str(row['Asset_ID'])
        owner = str(row['Owner'])
        G.add_node(asset_id, type='Asset', title=f"【伺服器】\nIP: {row['IP_Address']}\nOS: {row['OS']}\n軟體: {row['Software']}", color="#3498DB", ip=row['IP_Address'], software=row['Software'])  
        G.add_node(owner, type='Employee', title=f"【員工】\n部門: {row['Department']}", color="#2ECC71") 
        G.add_edge(owner, asset_id, relation='MANAGES', label='管理')
    
    for rule in compliance_rules:
        rule_id = rule['rule_id']
        workspace_dir = rule.get('workspace_dir', None)
        G.add_node(rule_id, type='Compliance', title=f"【法規 SOP】\n領域: {rule['domain']}\n說明: {rule['description']}", color="#E74C3C", workspace_dir=workspace_dir) 
        for target_role in rule['target_roles']:
            for _, asset_row in assets_df.loc[assets_df['Role'] == target_role].iterrows():
                G.add_edge(str(asset_row['Asset_ID']), rule_id, relation='MUST_COMPLY_WITH', label='必須遵守')
    return G

def generate_terminal_log(G, asset_filename, compliance_filename):
    log_text = f"🛡️ [Phase 1] 正在啟動 S.H.I.E.L.D. 防禦知識本體建置...\n"
    log_text += f"📦 載入資產資料: {asset_filename}\n📜 載入合規資料: {compliance_filename}\n✅ 知識圖譜建置完成！\n\n"
    log_text += f"🔍 [圖譜結構檢視]\n總節點數: {G.number_of_nodes()} | 總連線數: {G.number_of_edges()}\n\n"
    employees = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'Employee']
    if not employees: return log_text + f"🕵️ 查無員工資料可供抽查。\n"
    sample_size = min(len(employees), random.randint(2, 3))
    target_users = random.sample(employees, sample_size)
    for target_user in target_users:
        log_text += f"🕵️ 隨機抽查員工 [{target_user}] 的路徑追蹤:\n"
        managed_assets = [v for u, v, d in G.edges(data=True) if u == target_user and d.get('relation') == 'MANAGES']
        if not managed_assets:
            log_text += f"  (查無資料或該員工目前無管理資產)\n\n"
            continue
        for asset in managed_assets:
            asset_data = G.nodes[asset]
            software = asset_data.get('software', 'Unknown')
            ip = asset_data.get('ip', 'Unknown')
            log_text += f"  - 管理資產: {asset} ({software} @ {ip})\n"
            compliance_rules = [v for u, v, d in G.edges(data=True) if u == asset and d.get('relation') == 'MUST_COMPLY_WITH']
            for rule in compliance_rules:
                rule_data = G.nodes[rule]
                desc = rule_data.get('title', '').split('說明: ')[-1] if '說明: ' in rule_data.get('title', '') else ''
                short_desc = desc if len(desc) < 30 else desc[:28] + "..."
                log_text += f"    ⚠️ 必須遵守: {rule} ({short_desc})\n"
        log_text += "\n" 
    return log_text

def render_graph_ui(G):
    net = Network(height='600px', width='100%', directed=True, bgcolor='#1E1E1E', font_color='white')
    net.from_nx(G)
    net.repulsion(node_distance=150, central_gravity=0.2, spring_length=200, spring_strength=0.05, damping=0.09)
    net.set_options('{"interaction": {"zoomView": true, "dragView": true, "zoomSpeed": 0.3}}')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
        net.save_graph(tmp_file.name)
        with open(tmp_file.name, 'r', encoding='utf-8') as f:
            html_data = f.read()
    components.html(html_data, height=650)


# ==========================================
# 📱 Streamlit 側邊欄
# ==========================================
with st.sidebar:
    try:
        st.image(os.path.join(ASSETS_DIR, "shield-logo.jpg"), width='stretch')
    except Exception:
        pass 
        
    st.header("🛡️ S.H.I.E.L.D. 系統切換")
    
    app_mode = st.radio("🔄 選擇操作模式", ["🎯 情資防禦戰情室", "🗂️ 知識庫建檔中心", "💬 法規問答 (無向量視覺檢索)"])
    #app_mode = st.radio("🔄 選擇操作模式", ["💬 法規問答 (無向量視覺檢索)"])

    st.divider()

    selected_dataset = "--- 請選擇測試情境 ---"

    if app_mode == "🎯 情資防禦戰情室":
        st.info("💡 匯入您的資產與法規，系統將自動建置防禦知識本體。")
        
        st.subheader("🎯 載入與管理防禦情境")
        available_datasets = get_local_datasets(DATA_DIR)
        dataset_options = ["--- 請選擇測試情境 ---"] + available_datasets
        selected_dataset = st.selectbox("1. 選擇已建置的情境", dataset_options)

        with st.expander("⚙️ 管理與新增自訂情境 (CRUD)"):
            st.markdown("**🗑️ 刪除既有情境**")
            if available_datasets:
                del_ds = st.selectbox("選擇要刪除的情境", available_datasets, key="del_ds")
                if st.button("🗑️ 刪除此情境", width='stretch'):
                    try:
                        os.remove(os.path.join(DATA_DIR, f"{del_ds}_assets.csv"))
                        os.remove(os.path.join(DATA_DIR, f"{del_ds}_compliance.json"))
                        st.success("刪除成功！")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")
            else:
                st.info("目前無自訂情境。")

            st.divider()
            st.markdown("**➕ 上傳新情境**")
            new_ds_name = st.text_input("新情境名稱", placeholder="例如: corp_v2")
            up_csv = st.file_uploader("上傳 IT 資產清單 (CSV)", type=['csv'])
            up_json = st.file_uploader("上傳資安法規 SOP (JSON)", type=['json'])
            if st.button("💾 儲存新情境", type="primary", width='stretch'):
                if new_ds_name and up_csv and up_json:
                    with open(os.path.join(DATA_DIR, f"{new_ds_name}_assets.csv"), "wb") as f:
                        f.write(up_csv.getbuffer())
                    with open(os.path.join(DATA_DIR, f"{new_ds_name}_compliance.json"), "wb") as f:
                        f.write(up_json.getbuffer())
                    st.success(f"情境 {new_ds_name} 儲存成功！")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("請填寫情境名稱，並確保 CSV 與 JSON 皆已上傳。")

    st.divider()
    st.subheader("🩺 系統健康度檢測")

    if st.button("🔌 測試 LLM 連線 (Gemini)", width='stretch'):
        try:
            result = check_llm_health("gemini-2.5-flash")
            if result["status"] == "up":
                st.success("✅ 連線成功") 
            else:
                st.error("❌ 連線失敗")
        except: pass
        
    if st.button("🧅 測試 Tor 節點與暗網引擎", width='stretch'):
        with st.spinner("檢查 Tor 代理器狀態..."):
            try:
                tor_result = check_tor_proxy()
                if tor_result["status"] == "down":
                    st.error(f"❌ **Tor Proxy** — 無法連線\n\n{tor_result['error']}\n\n請確保本機端的 Tor 服務已啟動。")
                else:
                    st.success(f"✅ **Tor Proxy** — 連線成功 ({tor_result['latency_ms']}ms)")
                    with st.spinner("正在 Ping 16 個暗網搜尋引擎 (需時數秒)..."):
                        engine_results = check_search_engines()
                    up_count = sum(1 for r in engine_results if r["status"] == "up")
                    total = len(engine_results)
                    if up_count == total:
                        st.success(f"✅ **所有 {total} 個引擎皆可連線**")
                    elif up_count > 0:
                        st.warning(f"⚠️ **{up_count}/{total} 個引擎可連線**")
                    else:
                        st.error(f"❌ **0/{total} 個引擎可連線**")
                    for r in engine_results:
                        if r["status"] == "up":
                            st.markdown(f"&ensp;🟢 **{r['name']}** — {r['latency_ms']}ms")
                        else:
                            st.markdown(f"&ensp;🔴 **{r['name']}** — {r['error']}")
            except NameError:
                st.error("請確認已正確載入 health.py 模組。")

# ==========================================
# 🖥️ 主畫面路由切換
# ==========================================

# ------------------------------------------
# 模式 A：【情資防禦戰情室】 
# ------------------------------------------
if app_mode == "🎯 情資防禦戰情室":
    st.title("🛡️ Sovereign Heuristic Intelligence & Enterprise Logic Defense (S.H.I.E.L.D.)")
    st.markdown("上傳您的 IT 資產清單與合規法規，系統將自動在地端推導建立防禦知識本體 (Defense Ontology Graph)。")
    
    assets_df, compliance_rules, asset_name, compliance_name, is_data_ready = None, None, "", "", False

    try:
        if selected_dataset != "--- 請選擇測試情境 ---":
            asset_path = os.path.join(DATA_DIR, f"{selected_dataset}_assets.csv")
            compliance_path = os.path.join(DATA_DIR, f"{selected_dataset}_compliance.json")
            assets_df = pd.read_csv(asset_path)
            with open(compliance_path, 'r', encoding='utf-8') as f:
                compliance_rules = json.load(f)
            asset_name = f"{selected_dataset}_assets.csv"
            compliance_name = f"{selected_dataset}_compliance.json"
            is_data_ready = True
    except Exception as e:
        st.error(f"檔案解析發生錯誤：{e}")

    tab_phase1, tab_phase2 = st.tabs(["🕸️ [Phase 1] 企業防禦本體 (Ontology Graph)", "🕵️‍♂️ [Phase 2 & 3] 暗網狩獵與圖譜連鎖推導"])

    with tab_phase1:
        if is_data_ready:
            st.success("✅ 資料讀取成功！正在進行主權圖譜連鎖推導...")
            ontology_graph = build_defense_ontology(assets_df, compliance_rules)
            st.session_state.ontology_graph = ontology_graph
            
            col1, col2 = st.columns(2)
            col1.metric("總實體節點數 (Nodes)", ontology_graph.number_of_nodes())
            col2.metric("邏輯關聯數 (Edges)", ontology_graph.number_of_edges())
            st.divider()
            
            st.subheader("🖥️ 系統執行日誌 (System Logs)")
            terminal_output = generate_terminal_log(ontology_graph, asset_name, compliance_name)
            st.markdown(f"""<div style="background-color: #1A252C; padding: 20px; border-radius: 8px; font-family: monospace; color: #2ECC71; white-space: pre-wrap;">{terminal_output}</div>""", unsafe_allow_html=True)
            st.divider()
            st.subheader("🕸️ 企業防禦知識圖譜 (Interactive Graph)")
            render_graph_ui(ontology_graph)
        else:
            st.info("👈 請從左側面板「選擇已建置的情境」來啟動 Phase 1 系統。若無情境，請於側邊欄上傳新增。")

    with tab_phase2:
        st.markdown("### 🌐 [Phase 2] Omni-Source 暗網威脅狩獵")
        col_input, col_btn1, col_btn2, col_btn3 = st.columns([5, 2, 2, 1.5])
        with col_input: darkweb_query = st.text_input("輸入暗網追蹤關鍵字", key="dw_query")
        with col_btn1:
            st.markdown("<br>", unsafe_allow_html=True)
            real_search_btn = st.button("🚀 暗網探針", use_container_width=True)
        with col_btn2:
            st.markdown("<br>", unsafe_allow_html=True)
            demo_search_btn = st.button("🎭 暗網展示", use_container_width=True)
        with col_btn3:
            st.markdown("<br>", unsafe_allow_html=True)
            reset_btn = st.button("🔄 重置", use_container_width=True)

        # 🔄 重置分析狀態
        if reset_btn:
            st.session_state.darkweb_results = None
            st.session_state.analysis_done = False
            if "target_sw" in st.session_state:
                del st.session_state.target_sw
            if "combined_content" in st.session_state:
                del st.session_state.combined_content
            st.session_state.generated_rule = ""
            st.success("✅ 已重置分析狀態，可進行下一次搜尋")
            st.rerun()

        if real_search_btn and darkweb_query:
            # 🆕 自動重置舊狀態
            st.session_state.analysis_done = False
            st.session_state.generated_rule = ""
            if "target_sw" in st.session_state:
                del st.session_state.target_sw
            if "combined_content" in st.session_state:
                del st.session_state.combined_content

            try:
                with st.spinner("🤖 正在透過 LLM 優化搜尋提示詞..."):
                    llm = get_llm("gemini-2.5-flash")
                    refined_q = refine_query(llm, darkweb_query)
                    st.success(f"🎯 LLM 優化搜尋詞: `{refined_q}`")
                    
                with st.spinner("🧅 正在透過 Tor 節點爬取洋蔥網路情資 (約需數十秒，請確保 Tor 服務已啟動)..."):
                    raw_results = get_search_results(refined_q.replace(" ", "+"), max_workers=5)
                    if raw_results:
                        top_results = raw_results[:5]
                        with st.spinner("🕷️ 正在深入暗網網頁提取文字內容 (需時較長，請耐心等候)..."):
                            scraped_data = scrape_multiple(top_results, max_workers=5)
                            for res in top_results:
                                link = res['link']
                                res['content'] = scraped_data.get(link, "無法讀取內容或連線逾時。")
                        st.session_state.darkweb_results = top_results
                    else:
                        st.warning("⚠️ 查無結果，或所有暗網引擎皆無法連線，請確認本機 Tor Proxy 狀態。")
            except NameError:
                st.error("系統無法執行搜尋。請確認 search, llm, scrape 模組已正確引入。")
            except Exception as e:
                st.error(f"搜尋過程中發生錯誤: {e}")        
        
        # 🌟 完整保留的展示劇本
        if demo_search_btn:
            # 🆕 自動重置舊狀態
            st.session_state.analysis_done = False
            st.session_state.generated_rule = ""
            if "target_sw" in st.session_state:
                del st.session_state.target_sw
            if "combined_content" in st.session_state:
                del st.session_state.combined_content

            import random
            demo_scenarios = [
                {
                    "title": "[Selling] Bank Branch Camera Access (Taiwan)",
                    "link": "[http://camhackz555...onion/post/9912](http://camhackz555...onion/post/9912)",
                    "content": "⚠️ 駭客論壇最新發文：我們取得了一批台灣金融機構的內部監視器權限。這些設備多為 Hikvision_Firmware，且管理員未修改預設密碼。我們目前已可從遠端監看實體安全區域，售價 2 BTC。"
                },
                {
                    "title": "[Leak] Vendor HR System Database",
                    "link": "[http://breacheddata...onion/leaks/tw-bank-hr](http://breacheddata...onion/leaks/tw-bank-hr)",
                    "content": "🚨 供應鏈外洩事件：我們成功駭入某知名外包商的 Vendor_HR_System。該系統內含多家金融業員工資料。我們發現該軟體存在未修補的後門程式 (Backdoor)，目前已將 50GB 資料打包出售。"
                },
                {
                    "title": "[Exploit] SWIFT Gateway 0-day",
                    "link": "[http://exploitmarket...onion/swift-0day](http://exploitmarket...onion/swift-0day)",
                    "content": "💥 零日漏洞交易：針對 SWIFT_Alliance 閘道器系統的全新 RCE 漏洞。該漏洞允許攻擊者繞過 CSP 認證機制，直接在財務部交易室網段內執行任意代碼。附帶完整的攻擊腳本與隱蔽工具。"
                },
                {
                    "title": "🔴 APT 國家級駭客鎖定高階主管與跨國匯款閘道",
                    "content": "[Ramp APT Ransomware Forum] 釋出針對台灣某金控的初始存取權 (IAB)。已透過魚叉式釣魚取得總經理室 (IP: 172.16.1.10) 的端點控制權，並探測到可橫向移動至 SWIFT 交易網段。底價 50,000 USD。",
                    "link": "[http://exploitmarket...onion/swift-0day](http://exploitmarket...onion/swift-0day)",
                    },
                    {
                    "title": "🔴 雲端原生管線劫持與 K8s 容器勒索",
                    "content": "[LeakBase 駭客論壇] 獨家！取得目標企業開發團隊的 GitLab Runner 權限，內含最高級別的 AWS IAM Access Key。可直接控制 K8s 叢集並加密 S3 雲端備份資料桶，附贈自動化勒索腳本。",
                    "link": "[http://exploitmarket...onion/swift-0day](http://exploitmarket...onion/swift-0day)",
                    },
                    {
                    "title": "🔴 內部舊系統 0-day 漏洞與核心資料庫外洩危機",
                    "content": "[ExploitHQ] 發現目標企業的舊版應用伺服器 (Web-Server-01) 存在未公開的遠端代碼執行 (RCE) 漏洞。附上 Python 自動化攻擊腳本，可繞過防毒直取 SYSTEM 權限，並 Dump 內部 Oracle 資料庫。",
                    "link": "[http://exploitmarket...onion/swift-0day](http://exploitmarket...onion/swift-0day)",
                    }                
            ]
            selected_demo = random.choice(demo_scenarios)
            st.session_state.darkweb_results = [selected_demo]
            st.success(f"🎭 已隨機載入「展示劇本」！本次主題：{selected_demo['title']}")

        if st.session_state.darkweb_results:
            results_html = "<div style='background-color: #121212; padding: 15px; border-radius: 8px; font-family: monospace; color: #00FF41;'>"
            for i, res in enumerate(st.session_state.darkweb_results):
                results_html += f"<b>[{i+1}] {res['title']}</b><br><span style='color: #ccc;'>📄 {res.get('content', '')}</span><br><br>"
            results_html += "</div>"
            st.markdown(results_html, unsafe_allow_html=True)
            st.divider()
            
            st.markdown("### 💥 [Phase 3] 主權圖譜連鎖推導")
            if st.button("🚨 啟動 AI 提煉與圖譜連鎖推導分析", type="primary"):
                st.session_state.analysis_done = True
            
            if st.session_state.analysis_done:
                G = st.session_state.ontology_graph
                if G is None:
                    st.error("❌ 知識圖譜尚未建置！請先完成資料載入。")
                else:
                    # 🆕 每次分析都重新萃取，確保使用最新的 darkweb_results
                    with st.spinner("🤖 正在由 LLM 深度閱讀暗網內文，萃取威脅實體..."):
                        combined_content = "\n".join([res.get('content', res.get('title', '')) for res in st.session_state.darkweb_results])

                        # 從 Graph 中取得我們已知的軟體清單
                        known_software = set()
                        for n, attr in G.nodes(data=True):
                            if attr.get('type') == 'Asset' and 'software' in attr:
                                known_software.add(attr['software'])

                        extraction_prompt = f"""
你是一名資安專家。請從以下暗網情報中，找出駭客**真正意圖攻擊或利用的「軟體或系統名稱」**。

**萃取規則**：
1. 忽略廣告或無關服務（如 OnionLand Hosting, WordPress Hosting）
2. 專注尋找與 exploit, 0-day, leak, vulnerability, backdoor 相關的標的
3. **保留完整的軟體名稱**（例如：Hikvision_Firmware, SWIFT_Alliance, GitLab_Runner）
4. 若提及系統類型但無具體名稱，則返回類型名稱（如：Vendor_HR_System, Oracle_DB）
5. 若無明確攻擊標的則填 "Unknown"

**參考我們內部已知的軟體清單**（優先從這些名稱中選擇）：
{', '.join(sorted(known_software))}

請務必只輸出合法的 JSON 格式：
{{
  "target_software": "精確的軟體名稱或 Unknown"
}}

情報內容：
{combined_content[:4000]}
"""
                        try:
                            if gemini_client:
                                response = gemini_client.models.generate_content(
                                    model='gemini-2.5-flash',
                                    contents=extraction_prompt
                                )
                                clean_json_str = response.text.replace('```json', '').replace('```', '').strip()
                                dynamic_threat_entity = json.loads(clean_json_str)
                                st.session_state.target_sw = dynamic_threat_entity.get("target_software", "Unknown")
                                st.session_state.combined_content = combined_content
                            else:
                                st.error("Gemini API 未初始化！")
                                st.session_state.target_sw = "Unknown"
                        except Exception as e:
                            st.error(f"LLM 萃取失敗：{e}")
                            st.session_state.target_sw = "Unknown"

                    target_sw = st.session_state.get("target_sw", "Unknown")
                    st.success(f"✅ LLM 實體萃取完成！目標: `{target_sw}`")

                    # 🆕 改進的資產比對邏輯：使用 software 屬性並支援模糊匹配
                    def fuzzy_match_software(target_sw, asset_software):
                        """模糊匹配軟體名稱"""
                        if not target_sw or not asset_software:
                            return False

                        target_lower = target_sw.lower().replace('_', ' ').replace('-', ' ')
                        asset_lower = asset_software.lower().replace('_', ' ').replace('-', ' ')

                        # 完全匹配
                        if target_lower == asset_lower:
                            return True

                        # 包含匹配
                        if target_lower in asset_lower or asset_lower in target_lower:
                            return True

                        # 主要關鍵字匹配（例如 "SWIFT" 匹配 "SWIFT Alliance"）
                        target_parts = target_lower.split()
                        asset_parts = asset_lower.split()
                        if any(tp in asset_parts for tp in target_parts if len(tp) > 3):
                            return True

                        return False

                    impacted_assets = [
                        n for n, attr in G.nodes(data=True)
                        if attr.get('type') == 'Asset'
                        and fuzzy_match_software(target_sw, attr.get('software', ''))
                    ]
                    
                    if not impacted_assets:
                        st.info(f"ℹ️ 內部資產並未發現 `{target_sw}`，系統目前安全。")
                    else:
                        st.error(f"💥 **[系統緊急警報] 偵測到地端資產吻合暗網威脅特徵 `{target_sw}`！**")
                        st.markdown(f"**🎯 受影響資產**: `{'`, `'.join(impacted_assets)}`")

                        violated_rules_set = set()
                        for asset in impacted_assets:
                            violated_rules = [v for u, v, d in G.edges(data=True) if u == asset and d.get('relation') == 'MUST_COMPLY_WITH']
                            for rule in violated_rules: violated_rules_set.add(rule)

                        if violated_rules_set:
                            # 🌟 完整保留的 Phase 3 RAG 觸發邏輯
                            st.markdown("### 🧠 S.H.I.E.L.D. 雙引擎專家處置建議 (法規原文對齊)")
                            for rule in violated_rules_set:
                                rule_data = G.nodes[rule]
                                workspace_path = rule_data.get('workspace_dir') 
                                
                                if not workspace_path:
                                    domain_name = ""
                                    for line in rule_data.get('title', '').split('\n'):
                                        if '領域:' in line:
                                            domain_name = line.replace('領域:', '').strip()
                                            break
                                    if domain_name:
                                        guess_1 = os.path.join(POLICIES_DIR, domain_name)
                                        guess_2 = os.path.join(POLICIES_DIR, f"{domain_name}-workspace")
                                        if os.path.exists(guess_2): workspace_path = guess_2
                                        elif os.path.exists(guess_1): workspace_path = guess_1
                                            
                                if workspace_path and os.path.exists(workspace_path):
                                    json_files = glob.glob(os.path.join(workspace_path, "results", "*.json"))
                                    if not json_files: 
                                        st.warning(f"⚠️ 在 `{workspace_path}/results/` 找不到結構化 JSON 檔。")
                                        continue
                                        
                                    expert_prompt = f"根據法規 {rule} 的原文內容，針對目前遭受的 {target_sw} 威脅，請給出具體的資安應變與處置步驟。"

                                    with st.expander(f"📖 查看 {rule} 法規原文處置建議", expanded=True):
                                        with st.spinner("🤖 總圖書館長 Gemini 正在跨文獻比對最佳處置章節..."):
                                            best_pdf, target_pages = find_best_pdf_and_pages(workspace_path, expert_prompt)
                                            if not best_pdf:
                                                st.error(f"檢索失敗：在 {workspace_path} 中找不到可用的文獻目錄。")
                                                continue
                                                
                                            st.success(f"🎯 跨文獻檢索成功！鎖定文獻：`{best_pdf}.pdf` (關聯頁碼: {target_pages})")
                                            image_dir = os.path.join(workspace_path, "images", best_pdf)
                                            retrieved_images = []
                                            for p in target_pages:
                                                img_path = os.path.join(image_dir, f"page_{p}.jpg") 
                                                if os.path.exists(img_path):
                                                    retrieved_images.append(Image.open(img_path))
                                            
                                            # 避免重複生文，存在 session 裡
                                            rule_resp_key = f"resp_{rule}"
                                            if rule_resp_key not in st.session_state:
                                                if retrieved_images and gemini_client:
                                                    with st.spinner(f"👁️ 正在閱讀 {len(retrieved_images)} 頁高畫質影像並撰寫應變計畫..."):
                                                        response = gemini_client.models.generate_content(
                                                            model='gemini-2.5-flash',
                                                            contents=[expert_prompt] + retrieved_images
                                                        )
                                                        st.session_state[rule_resp_key] = response.text
                                            if rule_resp_key in st.session_state:
                                                st.markdown(st.session_state[rule_resp_key])
                                            elif not retrieved_images:
                                                st.warning(f"⚠️ 找不到對應的法規原文影像檔 (路徑: {image_dir})")
                        else:
                            st.info(f"ℹ️ 受影響資產：{', '.join(impacted_assets)}，但未找到對應的合規規則。")

                        # ==========================================
                        # ⭐ AI 主動免疫：Snort 規則生成 與 Multica 派工
                        # （移到外層，無論有無法規都要執行）
                        # ==========================================
                        st.markdown("#### 🛡️ AI 主動免疫：網路層熱修補規則生成與派工")
                        st.caption("系統正自動解析暗網駭客的攻擊手法，並轉譯為防火牆防禦規則，準備派發給 Agent 執行。")

                        if not st.session_state.generated_rule:
                            with st.spinner("🤖 正在編寫 Snort / ModSecurity 阻擋規則..."):
                                combined_content = st.session_state.get("combined_content", "")
                                rule_prompt = f"""
                                你是一名資深網路安全工程師。
                                我們的系統偵測到針對 {target_sw} 的攻擊即將發生。
                                暗網情報內容如下：
                                {combined_content[:2000]}

                                請根據情報中提及的攻擊手法，直接輸出一條有效的 Snort IDS/IPS 阻擋規則。
                                若無法判斷細節，請輸出通用型的路徑穿越或 RCE 防護規則。
                                請務必只輸出規則代碼本身，不要包含任何解釋、也不要使用 Markdown 的 ``` 符號。
                                """
                                try:
                                    if gemini_client:
                                        st.session_state.generated_rule = gemini_client.models.generate_content(
                                            model='gemini-2.5-flash',
                                            contents=rule_prompt
                                        ).text.replace('```', '').replace('snort', '').strip()
                                except Exception as e:
                                    st.error(f"⚠️ 規則生成失敗：{e}")

                        if st.session_state.generated_rule:
                            st.success("✅ 免疫規則生成完畢！")
                            st.code(st.session_state.generated_rule, language="bash")

                            st.markdown("---")
                            if st.button("🚀 傳送至 Agent Harness (Multica) 進行派工", type="primary", width='stretch'):
                                with st.spinner("正在封裝任務上下文並發送至 Multica..."):
                                    multica_url = os.environ.get("MULTICA_API_URL")
                                    multica_key = os.environ.get("MULTICA_API_KEY")
                                    multica_workspace = os.environ.get("MULTICA_WORKSPACE_ID")
                                    if not multica_url or not multica_key or not multica_workspace:
                                        st.error("⚠️ 找不到設定，請確認 .env 包含 MULTICA_API_URL, MULTICA_API_KEY 與 MULTICA_WORKSPACE_ID。")
                                    else:
                                        st.info(f"📡 正在派工至: `{multica_url}`\nWorkspace: `{multica_workspace}`")

                                        payload = {
                                            "title": f"🚨 [S.H.I.E.L.D.] {target_sw} 防禦任務",
                                            "description": f"**偵測情資**：已發現針對 {target_sw} 的威脅。\n\n**執行指令**：\n```bash\n{st.session_state.generated_rule}\n```",
                                            "priority": "high",
                                            "status": "todo",
                                            "project_id": "3c4a964a-02fa-4ab0-8af0-a4968b4fea6a"
                                        }

                                        headers = {
                                            "Authorization": f"Bearer {multica_key}",
                                            "X-Workspace-ID": multica_workspace,
                                            "Content-Type": "application/json"
                                        }

                                        try:
                                            response = requests.post(multica_url, json=payload, headers=headers)
                                            if response.status_code in [200, 201]:
                                                st.success("✅ 任務工單已成功派發！數位員工 (Agent) 即將接手進行後續審批。")
                                                st.balloons()
                                            else:
                                                st.error(f"❌ 派工失敗：伺服器回傳 {response.status_code}\n{response.text}")
                                        except Exception as e:
                                            st.error(f"❌ 連線異常：{e}")
                                        
# ------------------------------------------
# 模式 B：【具備 CRUD 能力的知識庫建檔中心】
# ------------------------------------------
elif app_mode == "🗂️ 知識庫建檔中心":
    st.title("🗂️ 企業級 AI 知識庫建檔中控台")
    st.markdown("使用 OpenDataLoader 核心，將法規 PDF 解析為帶有精準座標的 JSON 樹狀目錄與影像庫。")

    existing_workspaces = [d.replace("-workspace", "") for d in os.listdir(POLICIES_DIR) if os.path.isdir(os.path.join(POLICIES_DIR, d)) and d.endswith('-workspace')]
    
    st.markdown("### ⚙️ 步驟 1：選擇或建立管理領域")
    col_type, col_name = st.columns([1, 3])
    
    with col_type:
        ws_action = st.radio("操作模式", ["➕ 建立新領域", "📂 管理既有領域"], label_visibility="collapsed")
        
    workspace_name = ""
    with col_name:
        if ws_action == "➕ 建立新領域":
            workspace_name = st.text_input("輸入新領域名稱", placeholder="例如: cyber_threats_docs", label_visibility="collapsed")
        else:
            if not existing_workspaces:
                st.warning("⚠️ 目前無任何已建立的領域。請選擇「建立新領域」。")
            else:
                workspace_name = st.selectbox("選擇要管理的領域", existing_workspaces, label_visibility="collapsed")

    if workspace_name:
        final_workspace_dir = os.path.join(POLICIES_DIR, f"{workspace_name}-workspace")
        image_out_dir = os.path.join(final_workspace_dir, "images")
        results_out_dir = os.path.join(final_workspace_dir, "results")
        
        if ws_action == "📂 管理既有領域" and os.path.exists(results_out_dir):
            st.divider()
            
            col_del_1, col_del_2 = st.columns([3, 1])
            with col_del_1:
                st.markdown("### 🗑️ 管理既有文獻")
            with col_del_2:
                if st.button("🚨 刪除整個領域", type="primary", width='stretch'):
                    shutil.rmtree(final_workspace_dir)
                    st.success(f"領域 {workspace_name} 已徹底刪除！")
                    time.sleep(1)
                    st.rerun()

            existing_files = [f.replace("_structure.json", "") for f in os.listdir(results_out_dir) if f.endswith("_structure.json")]
            
            if existing_files:
                st.write(f"目前領域 `{workspace_name}` 共有 **{len(existing_files)}** 份文獻。")
                files_to_delete = st.multiselect("勾選要作廢的法規文獻 (刪除動作不可逆)", existing_files)
                
                if files_to_delete and st.button("🗑️ 永久刪除所選文獻", type="secondary"):
                    for f in files_to_delete:
                        json_path = os.path.join(results_out_dir, f"{f}_structure.json")
                        if os.path.exists(json_path): os.remove(json_path)
                        img_dir = os.path.join(image_out_dir, f)
                        if os.path.exists(img_dir): shutil.rmtree(img_dir)
                    st.success("✅ 文獻與影像庫已成功清除！")
                    time.sleep(1)
                    st.rerun() 
            else:
                st.info("此領域目前沒有任何建檔完成的文獻。")

        st.divider()
        st.markdown(f"### 📥 新增文獻至 `{workspace_name}` 領域")
        uploaded_files = st.file_uploader("上傳新的 PDF 檔案 (支援多選批次處理)", type=["pdf"], accept_multiple_files=True)

        if st.button("🚀 開始全自動極速建檔", type="primary", width='stretch'):
            if not uploaded_files:
                st.error("請至少上傳一份 PDF 檔案！")
            else:
                os.makedirs(image_out_dir, exist_ok=True)
                os.makedirs(results_out_dir, exist_ok=True)

                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_pdf_dir = os.path.join(temp_dir, "pdfs")
                    temp_odl_dir = os.path.join(temp_dir, "odl_temp")
                    os.makedirs(temp_pdf_dir)
                    os.makedirs(temp_odl_dir)

                    pdf_paths = []
                    with st.status("📥 寫入伺服器暫存區...", expanded=True) as status:
                        for uploaded_file in uploaded_files:
                            file_path = os.path.join(temp_pdf_dir, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            pdf_paths.append(file_path)
                        status.update(label="檔案寫入完成", state="complete", expanded=False)

                    with st.status("🧠 啟動 OpenDataLoader 核心進行結構萃取...", expanded=True) as status:
                        opendataloader_pdf.convert(
                            input_path=pdf_paths,
                            output_dir=temp_odl_dir,
                            format="json" 
                        )
                        status.update(label="結構萃取完成！(無 LLM 延遲)", state="complete", expanded=False)

                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    total_files = len(pdf_paths)
                    for idx, pdf_path in enumerate(pdf_paths):
                        file_name = os.path.splitext(os.path.basename(pdf_path))[0]
                        status_text.text(f"🌳 正在渲染高畫質影像並重組座標樹: {file_name} ({idx+1}/{total_files})")
                        
                        paper_image_dir = os.path.join(image_out_dir, file_name)
                        extract_pdf_page_images(pdf_path, paper_image_dir)
                        
                        odl_json_path = os.path.join(temp_odl_dir, f"{file_name}.json")
                        target_json_path = os.path.join(results_out_dir, f"{file_name}_structure.json")
                        
                        if os.path.exists(odl_json_path):
                            build_tree_from_odl(odl_json_path, target_json_path)
                        
                        progress_bar.progress((idx + 1) / total_files)
                    
                    status_text.text("✅ 批次處理完畢！")

                st.success(f"🎉 建檔大功告成！新加入的法規已成功歸檔至 `{final_workspace_dir}`。")
                time.sleep(2)
                st.rerun()

# ------------------------------------------
# 模式 C：【法規 SOP 智能問答 (視覺檢索展示)】 
# ------------------------------------------
elif app_mode == "💬 法規問答 (無向量視覺檢索)":
    st.title("💬 法規問答 (無向量視覺檢索)")
    st.markdown("此功能展示 **無向量視覺檢索 (Vectorless Visual RAG)** 技術。系統將透過 JSON 樹狀目錄定位頁碼，並讓 AI 直接閱讀原始 PDF 影像，確保表格、圖表等複雜排版資訊不遺失。")
    
    existing_workspaces = [d.replace("-workspace", "") for d in os.listdir(POLICIES_DIR) if os.path.isdir(os.path.join(POLICIES_DIR, d)) and d.endswith('-workspace')]
    
    if not existing_workspaces:
        st.warning("⚠️ 目前無任何已建檔的領域。請先至「知識庫建檔中心」建立。")
    else:
        selected_ws = st.selectbox("選擇要查詢的領域知識庫", existing_workspaces)
        workspace_path = os.path.join(POLICIES_DIR, f"{selected_ws}-workspace")
        
        user_question = st.text_input("輸入您關於法規或 SOP 的問題：", placeholder="例如：發生資料外洩時，根據通報 SOP 第一步應該通知誰？")
        
        if st.button("🔍 視覺檢索與解答", type="primary") and user_question:
            with st.spinner("🤖 總圖書館長正在檢索最相關的章節..."):
                best_pdf, target_pages = find_best_pdf_and_pages(workspace_path, user_question)
                
                if not best_pdf:
                    st.error("檢索失敗，找不到相關文獻。")
                else:
                    st.success(f"🎯 鎖定文獻：`{best_pdf}.pdf` (目標頁碼: {target_pages})")
                    
                    image_dir = os.path.join(workspace_path, "images", best_pdf)
                    retrieved_images = []
                    for p in target_pages:
                        img_path = os.path.join(image_dir, f"page_{p}.jpg") 
                        if os.path.exists(img_path):
                            retrieved_images.append(Image.open(img_path))
                    
                    if retrieved_images and gemini_client:
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.markdown("#### 📄 檢索到的原始文獻影像")
                            for img in retrieved_images:
                                st.image(img, width='stretch', caption=f"{best_pdf} - 擷取頁面")
                        
                        with col2:
                            st.markdown("#### 🤖 AI 視覺精準解答")
                            with st.spinner("👁️ 正在閱讀高畫質影像..."):
                                prompt = f"你是一位專業的法規顧問。請直接根據我提供的文獻影像，回答以下問題：\n\n問題：{user_question}"
                                try:
                                    response = gemini_client.models.generate_content(
                                        model='gemini-2.5-flash',
                                        contents=[prompt] + retrieved_images
                                    )
                                    st.info(response.text)
                                except Exception as e:
                                    st.error(f"LLM 解析失敗: {e}")
                    else:
                        st.warning("無法讀取影像檔或 Gemini API 未初始化。")