import sys
import json

# Função para converter AFND para código Graphviz
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

# Função para converter AFND para AFD
def convert_afnd_to_afd(afnd):
    # Obtendo informações do AFND
    afnd_states = afnd['Q']
    afnd_alphabet = afnd['V']
    afnd_delta = afnd['delta']
    afnd_initial_state = afnd['q0']
    afnd_final_states = afnd['F']

    # Função para fecho-épsilon
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

    # Função para transição
    def transition(states, symbol):
        result = set()
        for state in states:
            if symbol in afnd_delta[state]:
                result.update(afnd_delta[state][symbol])
        return result

    # Inicializando variáveis para o AFD
    afd_states = []
    afd_delta = {}
    afd_final_states = []
    unprocessed_states = [epsilon_closure([afnd_initial_state])]
    processed_states = []

    # Algoritmo de conversão AFND para AFD
    while unprocessed_states:
        current_states = unprocessed_states.pop()
        afd_states.append(current_states)
        processed_states.append(current_states)

        # Verificando se algum estado final do AFND está presente nos estados atuais do AFD
        for final_state in afnd_final_states:
            if final_state in current_states:
                afd_final_states.append(current_states)
                break

        # Percorrendo o alfabeto para determinar as transições do AFD
        for symbol in afnd_alphabet:
            next_states = epsilon_closure(transition(current_states, symbol))
            if next_states:
                if next_states not in processed_states and next_states not in unprocessed_states:
                    unprocessed_states.append(next_states)

                current_states_key = ','.join(sorted(next_states))
                if current_states_key not in afd_delta:
                    afd_delta[current_states_key] = {}
                afd_delta[current_states_key][symbol] = next_states

    # Retornando o AFD resultante
    return {
        'Q': [list(states) for states in afd_states],
        'V': afnd_alphabet,
        'delta': afd_delta,
        'q0': list(epsilon_closure([afnd_initial_state])),
        'F': [list(states) for states in afd_final_states]
    }

# Função principal do programa
def main():
    # Verificando os argumentos de linha de comando
    if len(sys.argv) < 3:
        print("Utilização:")
        print("Para converter AFND para Graphviz: python main.py afnd.json -graphviz")
        print("Para converter AFND para AFD: python main.py afnd.json -output afd.json")
        return

    # Obtendo o nome do arquivo AFND
    afnd_file = sys.argv[1]
    if not afnd_file.endswith('.json'):
        print("Erro: O primeiro argumento deve ser um arquivo JSON.")
        return

    # Obtendo o modo de operação
    mode = sys.argv[2]

    # Verificando o modo e executando a operação correspondente
    if mode == '-graphviz':
        try:
            with open(afnd_file, 'r') as file:
                afnd = json.load(file)
        except FileNotFoundError:
            print("Erro: Arquivo AFND não encontrado.")
            return
        except json.JSONDecodeError:
            print("Erro: Formato JSON inválido no arquivo AFND.")
            return

        graphviz_code = convert_afnd_to_graphviz(afnd)
        print(graphviz_code)

    elif mode == '-output':
        if len(sys.argv) != 4 or sys.argv[3].endswith('.json') == False:
            print("Erro: Argumentos inválidos para conversão AFND para AFD.")
            return

        afd_file = sys.argv[3]

        try:
            with open(afnd_file, 'r') as file:
                afnd = json.load(file)
        except FileNotFoundError:
            print("Erro: Arquivo AFND não encontrado.")
            return
        except json.JSONDecodeError:
            print("Erro: Formato JSON inválido no arquivo AFND.")
            return

        afd = convert_afnd_to_afd(afnd)

        # Convertendo os conjuntos de estados de 'set' para 'list'
        afd['Q'] = [list(states) for states in afd['Q']]
        for state, transitions in afd['delta'].items():
            for symbol, next_states in transitions.items():
                afd['delta'][state][symbol] = list(next_states)
        afd['q0'] = list(afd['q0'])
        afd['F'] = [list(states) for states in afd['F']]

        try:
            with open(afd_file, 'w') as file:
                json.dump(afd, file, indent=4)
            print("AFD escrito com sucesso em", afd_file)
        except FileNotFoundError:
            print("Erro: Caminho do arquivo de saída não encontrado.")
            return

    else:
        print("Erro: Modo inválido. Por favor, use '-graphviz' para gerar código Graphviz ou '-output' para converter AFND para AFD.")
