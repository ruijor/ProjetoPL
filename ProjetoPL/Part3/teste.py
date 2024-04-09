import sys
import json

def convert_afnd_to_graphviz(afnd):
    # Inicializando o código Graphviz
    graphviz_code = 'digraph { \n'
    
    # Definindo os nós finais
    graphviz_code += '\t node [shape = doublecircle]; '
    for final_state in afnd["F"]:
        graphviz_code += final_state + '; '
    graphviz_code += '\n'
    
    # Adicionando o nó inicial
    graphviz_code += '\t node [shape = point ]; initial; \n'
    graphviz_code += '\t node [shape = circle]; \n'
    graphviz_code += '\t initial->' + afnd["q0"] + '; \n'
    
    # Adicionando transições
    for state in afnd["delta"]:
        for symbol in afnd["delta"][state]:
            next_states = afnd["delta"][state][symbol]
            for next_state in next_states:
                graphviz_code += '\t ' + state + '->' + next_state + '[label="' + symbol + '"]; \n'
    
    # Fechando o código Graphviz
    graphviz_code += '}'
    
    return graphviz_code

def convert_afnd_to_afd(afnd):
    afnd_states = afnd['Q']
    afnd_alphabet = afnd['V']
    afnd_delta = afnd['delta']
    afnd_initial_state = afnd['q0']
    afnd_final_states = afnd['F']

    # Função para fecho epsilon de um conjunto de estados
    def epsilon_closure(states):
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            if 'epsilon' in afnd_delta[state]:
                for epsilon_state in afnd_delta[state]['epsilon']:
                    if epsilon_state not in closure:
                        closure.add(epsilon_state)
                        stack.append(epsilon_state)
        return closure

    # Função para transição de um conjunto de estados por um símbolo
    def transition(states, symbol):
        result = set()
        for state in states:
            if symbol in afnd_delta[state]:
                result.update(afnd_delta[state][symbol])
        return result

    # Inicializando o AFD
    afd_states = []
    afd_delta = {}
    afd_final_states = []
    unprocessed_states = [epsilon_closure([afnd_initial_state])]
    processed_states = []

    # Processamento dos estados do AFD
    while unprocessed_states:
        current_states = unprocessed_states.pop()
        afd_states.append(current_states)
        processed_states.append(current_states)

        # Verifica se é um estado final do AFD
        for final_state in afnd_final_states:
            if final_state in current_states:
                afd_final_states.append(current_states)
                break

        # Calcula as transições do AFD para cada símbolo do alfabeto
        for symbol in afnd_alphabet:
            next_states = epsilon_closure(transition(current_states, symbol))
            if next_states:
                if next_states not in processed_states and next_states not in unprocessed_states:
                    unprocessed_states.append(next_states)

                # Convertendo as chaves para uma string antes de usar como chave no dicionário AFD
                current_states_key = ','.join(sorted(next_states))
                if current_states_key not in afd_delta:
                    afd_delta[current_states_key] = {}
                afd_delta[current_states_key][symbol] = next_states

    return {
        'Q': [list(states) for states in afd_states],
        'V': afnd_alphabet,
        'delta': afd_delta,
        'q0': list(epsilon_closure([afnd_initial_state])),
        'F': [list(states) for states in afd_final_states]
    }

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("To convert AFND to AFD: python main.py afnd.json -output afd.json")
        print("To convert AFD to Graphviz: python main.py afd.json -graphviz")
        return

    input_file = sys.argv[1]
    mode = sys.argv[2]

    if mode == '-output':
        if len(sys.argv) != 5 or sys.argv[3] != '-output':
            print("Error: Invalid arguments for AFND to AFD conversion.")
            return

        output_file = sys.argv[4]

        if not input_file.endswith('.json') or not output_file.endswith('.json'):
            print("Error: Input and output files should be in JSON format.")
            return

        try:
            with open(input_file, 'r') as file:
                afnd = json.load(file)
        except FileNotFoundError:
            print("Error: AFND file not found.")
            return
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in the AFND file.")
            return

        afd = convert_afnd_to_afd(afnd)

        try:
            with open(output_file, 'w') as file:
                json.dump(afd, file, indent=4)
            print("AFD successfully written to", output_file)
        except FileNotFoundError:
            print("Error: Output file path not found.")
            return

    elif mode == '-graphviz':
        if len(sys.argv) != 4 or sys.argv[3] != '-graphviz':
            print("Error: Invalid arguments for AFD to Graphviz conversion.")
            return

        if not input_file.endswith('.json'):
            print("Error: Input file should be in JSON format.")
            return

        try:
            with open(input_file, 'r') as file:
                afd = json.load(file)
        except FileNotFoundError:
            print("Error: AFD file not found.")
            return
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in the AFD file.")
            return

        graphviz_code = convert_afnd_to_graphviz(afd)

        print("Graphviz code successfully generated:")
        print(graphviz_code)

    else:
        print("Error: Invalid mode. Please use '-output' to convert AFND to AFD or '-graphviz' to convert AFD to Graphviz.")

if __name__ == "__main__":
    main()
