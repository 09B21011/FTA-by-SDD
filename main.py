import subprocess
import sys
import os
import re
from FT_to_dnf import xml_to_formula, formula_to_dnf, prob_map
from to_sdd import run_sdd_from_pyeda_obj

def render_sdd_hierarchical(dot_path, output_path):
    """
    SDDを階層構造(dot)で見やすく、かつエラーを出さずに描画するための関数。
    PySDDが出力する「rank=same」制約がGraphvizをクラッシュさせる原因のため、
    これを一時的に削除して描画する。
    """
    if not os.path.exists(dot_path):
        print(f"Warning: {dot_path} was not found.")
        return

    # 1. DOTファイルを読み込み、「rank=same」の行を削除する加工を行う
    with open(dot_path, "r") as f:
        content = f.read()

    # 正規表現で {rank=same; ... } の行を削除
    # これにより「高さの完全一致強制」がなくなり、Graphvizが柔軟に配置できるようになる
    fixed_content = re.sub(r'\{rank=same;.*\}', '', content)
    
    # 加工したDOTを一時ファイルとして保存
    temp_dot_path = dot_path.replace(".dot", "_fixed.dot")
    with open(temp_dot_path, "w") as f:
        f.write(fixed_content)

    # 2. 加工したファイルを使って dot エンジンで描画
    ext = os.path.splitext(output_path)[1][1:] # png
    cmd = [
        "dot",
        f"-T{ext}",
        "-Gsplines=line",   # 線を直線にする（曲線計算のエラー回避＆見やすさ向上）
        "-Gnodesep=0.5",    # ノード間の横幅を確保
        "-Granksep=0.8",    # 上下の階層間隔を確保
        temp_dot_path,      # 加工後のファイルを入力にする
        "-o", 
        output_path
    ]

    try:
        print(f"Rendering hierarchical SDD to {output_path}...")
        subprocess.run(cmd, check=True)
        print(f"Successfully generated: {output_path}")
        
        # 一時ファイルの削除（お好みで残してもOK）
        if os.path.exists(temp_dot_path):
            os.remove(temp_dot_path)

    except FileNotFoundError:
        print("Error: Graphviz 'dot' command not found.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while rendering: {e}")

def main():
    xml_file = "FTA/sample2.xml"
    
    # 1. XML -> 論理式文字列
    formula_str = xml_to_formula(xml_file)
    
    # 2. 文字列 -> PyEDAオブジェクト (DNF化)
    # ここで dnf_expr は既に PyEDA のオブジェクト構造を持っています
    dnf_expr = formula_to_dnf(formula_str)
    
    print("--- DNF Expression (PyEDA) ---")
    print(dnf_expr) 

    print("\n--- Probabilities ---")
    for k, v in prob_map.items():
        print(f"{k}: {v}")

    # 3. PyEDAオブジェクト -> SDD (文字列変換をスキップ！)
    # 戻り値として sddノード, マネージャ, 変数マッピングを受け取る
    result = run_sdd_from_pyeda_obj(dnf_expr)
    
    if result:
        sdd_node, mgr, var_map = result
        
        # モデルカウント (確率計算)
        wmc = sdd_node.wmc(log_mode=False)
        for name, prob in prob_map.items():
            if name in var_map:
                sdd_var = var_map[name]
                wmc.set_literal_weight(sdd_var, prob)
                wmc.set_literal_weight(-sdd_var, 1.0 - prob)
        
        print(f"\nSystem Reliability (Probability): {wmc.propagate()}")

        # --- 画像変換処理 (ここを呼び出し) ---
        print("\n--- Generating Images ---")
        
        # Vtreeは単純なのでそのままの関数でもいいですが、統一してこれを使ってもOK
        render_sdd_hierarchical("vtree.dot", "vtree.png")
        
        # SDD本番
        render_sdd_hierarchical("sdd.dot", "sdd.png")

if __name__ == "__main__":
    main()