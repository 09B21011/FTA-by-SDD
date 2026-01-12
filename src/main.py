import subprocess
import sys
import os
import re
from pathlib import Path
from FT_to_dnf import xml_to_formula, formula_to_dnf, prob_map
from to_sdd import run_sdd_from_pyeda_obj

def main():
    os.chdir('..')
    xml_file = "./FTA/sddEx.xml"
    
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

if __name__ == "__main__":
    main()