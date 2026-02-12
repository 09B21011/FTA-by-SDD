import xml.etree.ElementTree as ET
from pyeda.inter import *

prob_map = {} 

def parse_event(event_elem):
    """<event>要素を再帰的に解析して論理式文字列を返す"""
    gate = event_elem.get("gate")
    event_id = event_elem.get("id")
    value = event_elem.get("value")
    if value is not None and event_id is not None:
        try:
            if event_id not in prob_map:
                prob_map[event_id] = float(value)
        except ValueError:
            print(f"[警告] event id={event_id} の value={value} は数値変換できませんでした")

    if gate is None:
        return event_id

    subevents = [parse_event(child) for child in event_elem.findall("event")]

    if gate.upper() == "AND":
        return "(" + " & ".join(subevents) + ")"
    elif gate.upper() == "OR":
        return "(" + " | ".join(subevents) + ")"
    else:
        raise ValueError(f"未知のゲートタイプ: {gate}")

def xml_to_formula(xml_path: str) -> str:
    """XMLファイルを解析して論理式（文字列）を生成"""
    global prob_map, custum_vtree, event_count
    prob_map.clear()

    tree = ET.parse(xml_path)
    root = tree.getroot()

    formula = parse_event(root)
    return formula

def formula_to_dnf(formula_str):
    """論理式文字列をpyedaでDNFに変換"""
    e = expr(formula_str)
    return e.to_dnf()

if __name__ == "__main__":
    xml_file = "FTA/sddEx.xml"

    # XML → 論理式
    formula_str = xml_to_formula(xml_file)
    print("=== Boolean Formula ===")
    print(formula_str)

    # 論理式 → DNF
    dnf_expr = formula_to_dnf(formula_str)
    print("\n=== DNF Expression ===")
    print(dnf_expr)