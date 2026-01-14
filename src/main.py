from FT_to_dnf import xml_to_formula, formula_to_dnf, prob_map
from dnf_to_sdd import run_sdd_from_pyeda_obj

def search(current_node):
    print(current_node.elements())
    for node in current_node.elements():
        p, s = node
        #print(p, s)
        if p.is_decision():
            search(p)
        if s.is_decision():
            search(s)
    """if current_node.elements().is_decision():
        print(current_node.elements())"""

def main():
    xml_file = "./FTA/sddEx.xml"
    
    # 1. XML -> 論理式文字列
    formula_str = xml_to_formula(xml_file)
    print(formula_str)
    
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
    result = run_sdd_from_pyeda_obj(dnf_expr, formula_str)
    
    if result:
        sdd_node, mgr, var_map = result
        #print(sdd_node)
        search(sdd_node)

if __name__ == "__main__":
    main()