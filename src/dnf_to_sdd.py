from pysdd.sdd import SddManager, Vtree
from pyeda.boolalg.expr import Variable, Complement, AndOp, OrOp

def dnf_to_str(node):
    if isinstance(node, Variable):
        return str(node)
    elif isinstance(node, AndOp):
        child_nodes = [dnf_to_str(child) for child in node.xs]
        return "(" + " & ".join(child_nodes) + ")"
    elif isinstance(node, OrOp):
        child_nodes = [dnf_to_str(child) for child in node.xs]
        return "(" + " | ".join(child_nodes) + ")"
    else:
        raise ValueError(f"Unknown node type: {type(node)}")

def run_sdd_from_pyeda_obj(pyeda_expr, formula_str):
    """
    PyEDAの式オブジェクトを直接受け取り、SDDに変換する。
    """
    print(f"Converting PyEDA object to SDD... (Type: {type(pyeda_expr)})")

    # 1. 変数集合の取得
    support_vars = sorted([str(v) for v in pyeda_expr.support])
    
    if not support_vars:
        if pyeda_expr.is_one():
            print("Formula is always TRUE")
            return None
        elif pyeda_expr.is_zero():
            print("Formula is always FALSE")
            return None

    # 2. SDDマネージャーの初期化
    var_count = len(support_vars)
    var_order = list(range(1, var_count + 1))
    
    vtree = Vtree(var_count=var_count, var_order=var_order, vtree_type="balanced")
    sdd_manager = SddManager.from_vtree(vtree)

    # 変数名とSDD変数の対応付け
    name_to_sdd_var = {name: sdd_manager.vars[i+1] for i, name in enumerate(support_vars)}

    dnf_str = dnf_to_str(pyeda_expr)
    print(dnf_str)
    """
    # 3. 再帰的に変換する内部関数
    def visit(node):
        print(node)
        # 変数
        if isinstance(node, Variable):
            print(name_to_sdd_var[str(node)])
            return name_to_sdd_var[str(node)]
        
        # 否定 (NOT)
        # PyEDAではリテラルの否定は Complement になります
        elif isinstance(node, Complement):
            return ~visit(node.inputs[0])
            
        # 論理積 (AND) -> 型は AndOp
        elif isinstance(node, AndOp):
            result = visit(node.inputs[0])
            for child in node.inputs[1:]:
                result = result & visit(child)
                print(result)
            return result
            
        # 論理和 (OR) -> 型は OrOp
        elif isinstance(node, OrOp):
            result = visit(node.inputs[0])
            for child in node.inputs[1:]:
                result = result | visit(child)
            return result
            
        # 定数
        elif node.is_one():
            return sdd_manager.true()
        elif node.is_zero():
            return sdd_manager.false()
            
        else:
            # 万が一他の型（NotOpなど）が来た場合のためのデバッグ表示
            raise ValueError(f"Unknown node type: {type(node)}")
    """
    # 変換実行
    sdd_node = eval(dnf_str, {}, name_to_sdd_var)

    with open("output/sdd.dot", "w") as out:
        print(sdd_node.dot(), file=out)
    with open("output/vtree.dot", "w") as out:
        print(vtree.dot(), file=out)
    
    print("Conversion successful.")
    # 戻り値を返す
    return sdd_node, sdd_manager, name_to_sdd_var