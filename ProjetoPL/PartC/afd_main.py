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
    # Define os estados finais como estados duplamente circulares
    print("node [shape = doublecircle]; " + ', '.join(["\"{}\"".format(state) for state in afd_definition["F"]]) + ";")
    # Define o estado inicial como um ponto
    print("node [shape = point]; initial;")
    # Define os estados restantes como círculos
    print("node [shape = circle];")
    # Define a transição do estado inicial
    initial_state = afd_definition["q0"][0]
    print("initial->{};".format(initial_state))
    # Define as transições entre os estados
    for state, transitions in afd_definition["delta"].items():
        for symbol, next_states in transitions.items():
            for next_state in next_states:
                print("{}->{} [label=\"{}\"];".format(state, next_state, symbol))
    print("}")



# Função para reconhecer uma palavra no autômato
def recognize_word(afd_definition, word):
    current_state = afd_definition["q0"][0]
    path = [current_state]
    for symbol in word:
        if symbol not in afd_definition["V"]:
            return False, ["símbolo '" + symbol + "' não pertence ao alfabeto"]
        if current_state not in afd_definition["delta"]:
            return False, ["estado '" + current_state + "' não tem transições definidas"]
        if symbol not in afd_definition["delta"][current_state]:
            return False, ["não há transição do estado '" + current_state + "' com o símbolo '" + symbol + "'"]
        next_state = afd_definition["delta"][current_state][symbol][0]  # Assume o primeiro estado de transição
        path.append(symbol + "->" + next_state)
        current_state = next_state
    if current_state in afd_definition["F"][0]:
        return True, path
    else:
        return False, ["o estado '" + current_state + "' não é final"]


# Função para validar a definição do autômato
def validate_afd_definition(afd_definition):
    # Verificar se todos os estados definidos em Q estão presentes nas transições
    for state_list in afd_definition["Q"]:
        for state in state_list:
            if state not in afd_definition["delta"]:
                raise ValueError("O estado '" + state + "' definido em Q não está presente nas transições delta.")

    # Verificar se o estado inicial (q0) está presente na definição
    if afd_definition["q0"][0] not in afd_definition["Q"][0]:
        raise ValueError("O estado inicial '" + afd_definition["q0"][0] + "' não está presente na definição dos estados Q.")

    # Verificar se pelo menos um dos estados finais (F) está presente na definição
    final_state_found = False
    for final_state_list in afd_definition["F"]:
        for final_state in final_state_list:
            if isinstance(final_state, str) and (final_state in afd_definition["Q"][0] or final_state in afd_definition["delta"]):
                final_state_found = True
                break
    if not final_state_found:
        raise ValueError("Pelo menos um dos estados finais não está presente na definição dos estados Q.")

    # Verificar se todas as transições do delta correspondem a estados e símbolos válidos
    for state, transitions in afd_definition["delta"].items():
        # Se o estado é composto, dividimos em componentes e verificamos se todos estão na lista de estados
        states = state.split(",")
        for s in states:
            if s not in afd_definition["Q"][0] and s not in afd_definition["delta"]:
                raise ValueError("O estado '" + s + "' nas transições delta não está presente na definição dos estados Q.")
        for symbol, next_state in transitions.items():
            if symbol not in afd_definition["V"]:
                raise ValueError("O símbolo '" + symbol + "' nas transições delta não está presente no alfabeto V.")
            for next_state_item in next_state:
                if next_state_item not in afd_definition["Q"][0] and next_state_item not in afd_definition["delta"]:
                    raise ValueError("O estado '" + next_state_item + "' nas transições delta não está presente na definição dos estados Q.")



# Verifica se há argumentos suficientes
if len(sys.argv) < 3:
    print("Usage: python afd-main.py <arquivo.json> [-graphviz] ")
    sys.exit(1)

# Carrega a definição do autômato do arquivo JSON
file_path = sys.argv[1]
afd_definition = load_afd_from_json(file_path)

# Valida a definição do autômato
validate_afd_definition(afd_definition)

# Imprime o digraph do autômato, se a opção -graphviz estiver presente
if "-graphviz" in sys.argv:
        print_digraph(afd_definition)

