

def gerar_dot_from_gv(gv_content):
    # Adiciona o conteúdo inicial
    dot = "digraph {\n"
    
    # Adiciona os estados finais
    dot += "\tnode [shape = doublecircle]; q2;\n"
    
    # Adiciona o estado inicial
    dot += "\tnode [shape = point]; initial;\n"
    
    # Adiciona os estados restantes
    dot += "\tnode [shape = circle];\n"
    
    # Adiciona a transição para o estado inicial
    dot += "\tinitial->q0;\n"
    
    # Adiciona as transições
    transicoes = gv_content.split(';')
    for transicao in transicoes:
        transicao = transicao.strip()
        if transicao:
            origem, destino_label = transicao.split("->")
            destino, label = destino_label.split("[label=")
            label = label.strip().strip('"')
            dot += f"\t{origem}->{destino} [label=\"{label}\"];\n"
    
    dot += "}"
    return dot
