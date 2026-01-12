import xml.etree.ElementTree as ET
from pyeda.inter import *

prob_map = {}  # event_id → 確率 のマップ

# ===== XML解析関数 =====
def parse_event(event_elem):
    """<event>要素を再帰的に解析して論理式文字列を返す"""
    gate = event_elem.get("gate")
    event_id = event_elem.get("id")

    # 葉ノードの確率情報を保存
    value = event_elem.get("value")
    if value is not None and event_id is not None:
        try:
            prob_map[event_id] = float(value)
        except ValueError:
            print(f"[警告] event id={event_id} の value={value} は数値変換できませんでした")

    # 葉ノードの場合
    if gate is None:
        return event_id

    # 子ノードを再帰的に処理
    subevents = [parse_event(child) for child in event_elem.findall("event")]

    if gate.upper() == "AND":
        return "(" + " & ".join(subevents) + ")"
    elif gate.upper() == "OR":
        return "(" + " | ".join(subevents) + ")"
    else:
        raise ValueError(f"未知のゲートタイプ: {gate}")

def xml_to_formula(xml_path: str) -> str:
    """XMLファイルを解析して論理式（文字列）を生成"""
    global prob_map
    prob_map.clear()  # 前回の内容をクリア

    tree = ET.parse(xml_path)
    root = tree.getroot()

    formula = parse_event(root)
    return formula

def formula_to_dnf(formula_str):
    """論理式文字列をpyedaでDNFに変換"""
    e = expr(formula_str)
    return e.to_dnf()

if __name__ == "__main__":
    xml_file = "FTA/sample.xml"

    # XML → 論理式
    formula_str = xml_to_formula(xml_file)
    print("=== Boolean Formula ===")
    print(formula_str)

    # 論理式 → DNF
    dnf_expr = formula_to_dnf(formula_str)
    print("\n=== DNF Expression ===")
    print(dnf_expr)
