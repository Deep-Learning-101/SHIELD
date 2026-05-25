"""
SHIELD Core - Defense Ontology Initialization
防禦知識本體初始化模組

TonTon H.-D. Huang Ph.D.
https://TWMAN.ORG
"""

import pandas as pd
import json
import networkx as nx
import os

def build_defense_ontology(assets_path, compliance_path):
    print("🛡️ [Phase 1] 正在啟動 S.H.I.E.L.D. 防禦知識本體建置...")

    # 1. 建立一個有向圖 (Directed Graph)
    G = nx.DiGraph()
    
    # 2. 讀取並載入 IT 資產與員工節點
    print(f"📦 載入資產資料: {assets_path}")
    assets_df = pd.read_csv(assets_path)
    
    for _, row in assets_df.iterrows():
        asset_id = row['Asset_ID']
        owner = row['Owner']
        
        # 建立「伺服器」節點
        G.add_node(asset_id, 
                   type='Asset', 
                   ip=row['IP_Address'], 
                   role=row['Role'], 
                   software=row['Software'])
        
        # 建立「員工(負責人)」節點
        G.add_node(owner, 
                   type='Employee', 
                   department=row['Department'])
        
        # 建立關聯線：員工 [管理] 伺服器
        G.add_edge(owner, asset_id, relation='MANAGES')
    
    # 3. 讀取並載入合規法規節點
    print(f"📜 載入合規資料: {compliance_path}")
    with open(compliance_path, 'r', encoding='utf-8') as f:
        compliance_data = json.load(f)
        
    for rule in compliance_data:
        rule_id = rule['rule_id']
        
        # 💡 [新增] 安全地讀取 workspace_dir，若舊資料沒有此欄位則預設為 None
        workspace_dir = rule.get('workspace_dir', None)
        
        # 建立「合規條款」節點，並把 workspace_dir 存為節點屬性
        G.add_node(rule_id, 
                   type='Compliance', 
                   title=rule['title'], 
                   description=rule['description'],
                   workspace_dir=workspace_dir)  # ⬅️ 精準檢索的路徑指標
        
        # 邏輯推導：自動將伺服器與適用的法規連線
        for target_role in rule['target_roles']:
            # 尋找圖譜中符合該 Role 的所有資產
            matching_assets = [n for n, attr in G.nodes(data=True) if attr.get('type') == 'Asset' and attr.get('role') == target_role]
            
            for asset in matching_assets:
                # 建立關聯線：伺服器 [必須符合] 合規條款
                G.add_edge(asset, rule_id, relation='MUST_COMPLY_WITH')
    
    print("✅ 知識圖譜建置完成！\n")
    return G

def inspect_graph(G):
    print("🔍 [圖譜結構檢視]")
    print(f"總節點數: {G.number_of_nodes()} | 總連線數: {G.number_of_edges()}")
    
    # 測試一下圖譜的推理能力：查出 tonyd 管理的機器，以及該機器受什麼法規規範
    target_user = 'tonyd'
    print(f"\n🕵️ 針對員工 [{target_user}] 的路徑追蹤:")
    
    # 找出 tonyd 管理的資產
    managed_assets = [v for u, v, d in G.edges(data=True) if u == target_user and d['relation'] == 'MANAGES']
    
    for asset in managed_assets:
        asset_data = G.nodes[asset]
        print(f"  - 管理資產: {asset} (IP: {asset_data.get('ip')})")
        
        # 找出該資產必須遵守的法規
        compliance_rules = [v for u, v, d in G.edges(data=True) if u == asset and d['relation'] == 'MUST_COMPLY_WITH']
        for rule in compliance_rules:
            rule_data = G.nodes[rule]
            workspace = rule_data.get('workspace_dir')
            workspace_tag = f" [📁 指向 Workspace: {workspace}]" if workspace else " [無 Workspace]"
            print(f"    ⚠️ 必須遵守: {rule} - {rule_data.get('title')}{workspace_tag}")

# (供單獨測試用)
if __name__ == "__main__":
    # Monorepo 架構：調整路徑指向 shared/data
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "shared", "data")
    G = build_defense_ontology(
        os.path.join(DATA_DIR, "enterprise_assets.db"),
        os.path.join(DATA_DIR, "compliance_matrix.db")
    )
    inspect_graph(G)