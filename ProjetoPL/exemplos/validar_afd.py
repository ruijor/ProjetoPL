import json

def validar_afd(afd):
    # Verificar se todos os campos necessários estão presentes
    campos_necessarios = ["V", "Q", "delta", "q0", "F"]
    for campo in campos_necessarios:
        if campo not in afd:
            return False, f"Campo '{campo}' ausente na definição do AFD."

    # Verificar se os estados de transição estão corretos
    for estado, transicoes in afd["delta"].items():
        if estado not in afd["Q"]:
            return False, f"Estado '{estado}' nas transições não está presente no conjunto de estados."

        for simbolo, destino in transicoes.items():
            if simbolo not in afd["V"]:
                return False, f"Símbolo '{simbolo}' na transição de '{estado}' não está no alfabeto."
            if destino not in afd["Q"]:
                return False, f"Destino '{destino}' na transição de '{estado}' não está no conjunto de estados."

    # Verificar se o estado inicial está presente nos estados
    if afd["q0"] not in afd["Q"]:
        return False, "Estado inicial não está presente no conjunto de estados."

    # Verificar se os estados finais estão presentes nos estados
    for estado_final in afd["F"]:
        if estado_final not in afd["Q"]:
            return False, f"Estado final '{estado_final}' não está presente no conjunto de estados."

    return True, "AFD válido."
