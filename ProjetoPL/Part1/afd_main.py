import sys
import json

# Função para carregar a definição do autômato de um arquivo JSON
def load_afd_from_json(file_path):
    with open(file_path, 'r') as file:
        afd_definition = json.load(file)
    return afd_definition


# Função para imprimir o digraph do autômato
def print_digraph(afd_definition):
    print("digraph {")
    print("node [shape = doublecircle]; " + ', '.join(afd_definition["F"]) + ";")
    print("node [shape = point]; initial;")
    print("node [shape = circle];")
    print("initial->" + afd_definition["q0"] + ";")
    for state, transitions in afd_definition["delta"].items():
        for symbol, next_state in transitions.items():
            print(state + "->" + next_state + "[label=\"" + symbol + "\"];")
    print("}")


# Função para reconhecer uma palavra no autômato
def recognize_word(afd_definition, word):
    current_state = afd_definition["q0"]
    path = [current_state]
    for symbol in word:
        if symbol not in afd_definition["V"]:
            return False, ["símbolo '" + symbol + "' não pertence ao alfabeto"]
        if symbol not in afd_definition["delta"][current_state]:
            return False, ["não há transição do estado '" + current_state + "' com o símbolo '" + symbol + "'"]
        next_state = afd_definition["delta"][current_state][symbol]
        path.append(symbol + "->" + next_state)
        current_state = next_state
    if current_state in afd_definition["F"]:
        return True, path
    else:
        return False, ["o estado '" + current_state + "' não é final"]


# Função para validar a definição do autômato
def validate_afd_definition(afd_definition):
    # Verificar se todos os estados definidos em Q estão presentes nas transições
    for state in afd_definition["Q"]:
        if state not in afd_definition["delta"]:
            raise ValueError("O estado '" + state + "' definido em Q não está presente nas transições delta.")

    # Verificar se o estado inicial (q0) está presente na definição
    if afd_definition["q0"] not in afd_definition["Q"]:
        raise ValueError("O estado inicial 'q0' não está presente na definição dos estados Q.")

    # Verificar se todos os estados finais (F) estão presentes na definição
    for final_state in afd_definition["F"]:
        if final_state not in afd_definition["Q"]:
            raise ValueError("O estado final '" + final_state + "' não está presente na definição dos estados Q.")

    # Verificar se todas as transições do delta correspondem a estados e símbolos válidos
    for state, transitions in afd_definition["delta"].items():
        if state not in afd_definition["Q"]:
            raise ValueError("O estado '" + state + "' nas transições delta não está presente na definição dos estados Q.")
        for symbol, next_state in transitions.items():
            if symbol not in afd_definition["V"]:
                raise ValueError("O símbolo '" + symbol + "' nas transições delta não está presente no alfabeto V.")
            if next_state not in afd_definition["Q"]:
                raise ValueError("O estado '" + next_state + "' nas transições delta não está presente na definição dos estados Q.")


if __name__ == "__main__":
     # Verifica se há argumentos suficientes
    if len(sys.argv) < 3:
        print("Usage: python afd-main.py <arquivo.json> [-graphviz] [-rec '<palavra>']")
        sys.exit(1)

    # Carrega a definição do autômato do arquivo JSON
    file_path = sys.argv[1]
    afd_definition = load_afd_from_json(file_path)

    # Valida a definição do autômato
    validate_afd_definition(afd_definition)

    # Imprime o digraph do autômato, se a opção -graphviz estiver presente
    if "-graphviz" in sys.argv:
        print_digraph(afd_definition)

    # Reconhece a palavra fornecida, se a opção -rec estiver presente
    if "-rec" in sys.argv:
        word_index = sys.argv.index("-rec") + 1
        word = sys.argv[word_index]
        recognized, path = recognize_word(afd_definition, word)
        if recognized:
            print("'" + word + "' é reconhecida")
            print("[caminho " + "->".join(path) + "]")
        else:
            print("'" + word + "' não é reconhecida")
            for error in path:
                print("[" + error + "]")
