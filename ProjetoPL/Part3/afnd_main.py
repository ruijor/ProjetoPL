import sys
import json

# Função para converter um AFND em um AFD
def convert_afnd_to_afd(afnd):
    # Obtendo informações do AFND
    afnd_states = afnd['Q']  # Conjunto de estados do AFND
    afnd_alphabet = afnd['V']  # Alfabeto do AFND
    afnd_delta = afnd['delta']  # Função de transição do AFND
    afnd_initial_state = afnd['q0'] if isinstance(afnd['q0'], str) else afnd['q0'][0]  # Estado inicial do AFND
    afnd_final_states = afnd['F']  # Conjunto de estados finais do AFND

    # Função para calcular o fecho-épsilon de um conjunto de estados
    def epsilon_closure(states):
        closure = set(states)
        stack = list(states)
        # Itera até que a pilha esteja vazia
        while stack:
            state = stack.pop()
            # Verifica se existe transição epsilon a partir do estado atual
            if 'epsilon' in afnd_delta[state]:
                for epsilon_state in afnd_delta[state]['epsilon']:
                    if epsilon_state not in closure:
                        closure.add(epsilon_state)
                        stack.append(epsilon_state)
        return tuple(sorted(closure))  # Convertendo para tuple para tornar os conjuntos hashable

    # Função para calcular a transição de um conjunto de estados dado um símbolo de entrada
    def transition(states, symbol):
        result = set()
        # Itera sobre os estados atuais
        for state in states:
            # Verifica se existe transição para o símbolo atual
            if symbol in afnd_delta[state]:
                result.update(afnd_delta[state][symbol])
        return result

    # Inicializando variáveis para o AFD
    afd_states = []  # Conjunto de estados do AFD
    afd_delta = {}  # Função de transição do AFD
    afd_final_states = []  # Conjunto de estados finais do AFD
    unprocessed_states = [epsilon_closure([afnd_initial_state])]  # Estados a serem processados
    processed_states = []  # Estados já processados

    # Algoritmo de conversão AFND para AFD
    while unprocessed_states:
        current_states = unprocessed_states.pop()  # Estado atual a ser processado
        afd_states.append(current_states)  # Adiciona o estado atual ao conjunto de estados do AFD
        processed_states.append(current_states)  # Marca o estado atual como processado

        # Verificando se algum estado final do AFND está presente nos estados atuais do AFD
        for final_state in afnd_final_states:
            if final_state in current_states:
                afd_final_states.append(current_states)  # Marca o estado atual como estado final do AFD
                break

        # Percorrendo o alfabeto para determinar as transições do AFD
        for symbol in afnd_alphabet:
            next_states = epsilon_closure(transition(current_states, symbol))  # Calcula os próximos estados
            if next_states:
                # Adiciona os próximos estados à lista de estados a serem processados
                if next_states not in processed_states and next_states not in unprocessed_states:
                    unprocessed_states.append(next_states)

                current_states_key = ','.join(sorted(next_states))  # Chave para o estado atual do AFD
                if current_states_key not in afd_delta:
                    afd_delta[current_states_key] = {}
                afd_delta[current_states_key][symbol] = next_states  # Atualiza a função de transição do AFD

    # Retornando o AFD resultante
    return {
        'Q': [list(states) for states in afd_states],  # Converte os estados para listas
        'V': afnd_alphabet,  # Mantém o alfabeto
        'delta': afd_delta,  # Função de transição do AFD
        'q0': list(epsilon_closure([afnd_initial_state])),  # Converte o estado inicial para uma lista
        'F': [list(states) for states in afd_final_states]  # Converte os estados finais para listas
    }

# Função para gerar o código Graphviz a partir do AFD
def generate_graphviz(afd):
    lines = ['digraph afd {']
    lines.append('    node [shape = doublecircle]; ' + '; '.join([' '.join(states) for states in afd['F']]) + ';')
    lines.append('    node [shape = point]; qi;')
    lines.append('    node [shape = circle];')

    # Adicionando transições
    for state, transitions in afd['delta'].items():
        for symbol, next_states in transitions.items():
            for next_state in next_states:
                lines.append('    {} -> {} [label="{}"];'.format(state, next_state, symbol))
    lines.append('}')
    return '\n'.join(lines)

# Verificação de argumentos de linha de comando
if len(sys.argv) < 3:
    print("Utilização:")
    print("Para converter AFND para Graphviz: python main.py afnd.json -graphviz")
    print("Para converter AFND para AFD: python main.py afnd.json -output afd.json") 
    sys.exit()

# Obtendo o nome do arquivo AFND
afnd_file = sys.argv[1]
if not afnd_file.endswith('.json'):
    print("Erro: O primeiro argumento deve ser um arquivo JSON.")
    sys.exit()

# Obtendo o modo de operação
mode = sys.argv[2]

# Verificando o modo e executando a operação correspondente
if mode == '-graphviz':
    try:
        with open(afnd_file, 'r') as file:
            afnd = json.load(file)
    except FileNotFoundError:
        print("Erro: Arquivo AFND não encontrado.")
        sys.exit()
    except json.JSONDecodeError:
        print("Erro: Formato JSON inválido no arquivo AFND.")
        sys.exit()

    # Convertendo AFND para AFD
    afd = convert_afnd_to_afd(afnd)
    # Gerando código Graphviz
    graphviz_code = generate_graphviz(afd)
    print(graphviz_code)

elif mode == '-output':
    if len(sys.argv) != 4 or not sys.argv[3].endswith('.json'):
        print("Erro: Argumentos inválidos para conversão AFND para AFD.")
        sys.exit()

    afd_file = sys.argv[3]

    try:
        with open(afnd_file, 'r') as file:
            afnd = json.load(file)
    except FileNotFoundError:
        print("Erro: Arquivo AFND não encontrado.")
        sys.exit()
    except json.JSONDecodeError:
        print("Erro: Formato JSON inválido no arquivo AFND.")
        sys.exit()

    # Convertendo AFND para AFD
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
        sys.exit()

else:
    print("Erro: Modo inválido. Por favor, use '-graphviz' para gerar código Graphviz ou '-output' para converter AFND para AFD.")
