def explore(current_node):
    print(current_node.elements())
    for node in current_node.elements():
        p, s = node
        if p.is_decision():
            explore(p)
        if s.is_decision():
            explore(s)