import json
import sys

def novoEstado(estados):
    # Cria um novo estado para o autômato finito não determinístico (AFND).
    novo_estado = f'q{len(estados)}' 
    estados.append(novo_estado)  # Adiciona o novo estado à lista de estados.
    return novo_estado

def processaSimbolo(simbolo, simbolos, estados, transicoes):
    # Processa um símbolo da expressão regular, criando estados de início e fim e uma transição entre eles.
    estado_inicio = novoEstado(estados)  # Cria um novo estado inicial.
    estado_fim = novoEstado(estados)  # Cria um novo estado final.
    # Adiciona uma transição com o símbolo dado entre os estados de início e fim.
    transicoes.append((estado_inicio, simbolo, estado_fim))
    # Se o símbolo ainda não estiver na lista de símbolos, adiciona-o.
    if simbolo not in simbolos:
        simbolos.append(simbolo)
    return estado_inicio, estado_fim

def processaEpsilon(estados, transicoes):
    # Processa uma transição vazia (epsilon), criando estados de início e fim e uma transição epsilon entre eles.
    estado_inicio = novoEstado(estados)  # Cria um novo estado inicial.
    estado_fim = novoEstado(estados)  # Cria um novo estado final.
    # Adiciona uma transição vazia entre os estados de início e fim.
    transicoes.append((estado_inicio, '', estado_fim))
    return estado_inicio, estado_fim

def processaAlternancia(args, estados, simbolos, transicoes):
    # Processa uma alternância (|), conectando os argumentos com transições epsilon a novos estados de início e fim.
    estado_inicio = novoEstado(estados)  # Cria um novo estado inicial.
    estado_fim = novoEstado(estados)  # Cria um novo estado final.
    # Para cada argumento na lista de argumentos:
    for arg in args:
        # Processa a expressão regular do argumento e obtém os estados de início e fim.
        inicio_arg, fim_arg = converterER(arg, estados, simbolos, transicoes)
        # Adiciona transições epsilon dos novos estados inicial e final para os estados de início e fim do argumento, respectivamente.
        transicoes.append((estado_inicio, '', inicio_arg))
        transicoes.append((fim_arg, '', estado_fim))
    return estado_inicio, estado_fim

def processaSequencia(args, estados, simbolos, transicoes):
    # Processa uma sequência, conectando cada argumento com transições epsilon, exceto o primeiro.
    inicio_seq, fim_seq = None, None
    # Para cada argumento na lista de argumentos:
    for arg in args:
        # Processa a expressão regular do argumento e obtém os estados de início e fim.
        inicio_arg, fim_arg = converterER(arg, estados, simbolos, transicoes)
        # Se for o primeiro argumento:
        if inicio_seq is None:
            inicio_seq = inicio_arg
        else:
            # Adiciona uma transição epsilon do estado final do argumento anterior para o estado inicial do argumento atual.
            transicoes.append((fim_seq, '', inicio_arg))
        fim_seq = fim_arg  # Atualiza o estado final da sequência.
    return inicio_seq, fim_seq

def processaFechamento(args, estados, simbolos, transicoes):
    # Processa o fechamento de Kleene (*), permitindo repetições do argumento.
    estado_inicio = novoEstado(estados)  # Cria um novo estado inicial.
    estado_fim = novoEstado(estados)  # Cria um novo estado final.
    # Processa a expressão regular do argumento e obtém os estados de início e fim.
    inicio_arg, fim_arg = converterER(args[0], estados, simbolos, transicoes)
    # Adiciona transições epsilon do novo estado inicial para o estado inicial do argumento,
    # do estado final do argumento para o novo estado final e do estado final do argumento para o estado inicial do argumento.
    transicoes.append((estado_inicio, '', inicio_arg))
    transicoes.append((fim_arg, '', estado_fim))
    transicoes.append((fim_arg, '', inicio_arg))
    transicoes.append((estado_inicio, '', estado_fim))
    return estado_inicio, estado_fim

def processaTransicao(args, estados, simbolos, transicoes):
    # Processa uma transição, conectando cada argumento com transições epsilon.
    inicio_trans, fim_trans = None, None
    # Para cada argumento na lista de argumentos:
    for arg in args:
        # Processa a expressão regular do argumento e obtém os estados de início e fim.
        inicio_arg, fim_arg = converterER(arg, estados, simbolos, transicoes)
        # Se for o primeiro argumento:
        if inicio_trans is None:
            inicio_trans = inicio_arg
        else:
            # Adiciona uma transição epsilon do estado final do argumento anterior para o estado inicial do argumento atual.
            transicoes.append((fim_trans, '', inicio_arg))
        fim_trans = fim_arg  # Atualiza o estado final da transição.
    return inicio_trans, fim_trans

def converterER(er, estados, simbolos, transicoes):
    # Converte a expressão regular em componentes do AFND, baseando-se no tipo de operação.
    if 'simb' in er:
        # Se a expressão for um símbolo, processa o símbolo.
        return processaSimbolo(er['simb'], simbolos, estados, transicoes)
    elif 'epsilon' in er:
        # Se a expressão for uma transição epsilon, processa a transição epsilon.
        return processaEpsilon(estados, transicoes)
    elif er['op'] == 'alt':
        # Se a expressão for uma alternância, processa a alternância.
        return processaAlternancia(er['args'], estados, simbolos, transicoes)
    elif er['op'] == 'seq':
        # Se a expressão for uma sequência, processa a sequência.
        return processaSequencia(er['args'], estados, simbolos, transicoes)
    elif er['op'] == 'kle':
        # Se a expressão for um fechamento de Kleene, processa o fechamento de Kleene.
        return processaFechamento(er['args'], estados, simbolos, transicoes)
    elif er['op'] == 'trans':
        # Se a expressão for uma transição, processa a transição.
        return processaTransicao(er['args'], estados, simbolos, transicoes)
    else:
        # Se a expressão contiver um operador inválido, levanta um erro.
        raise ValueError("Operador inválido na expressão regular")

def convertERParaAFND(expression):
    # Converte uma expressão regular (dicionário) em um AFND (dicionário).
    estados, simbolos, transicoes = [], [], []
    # Obtém os estados inicial e final do AFND a partir da expressão regular.
    inicio, fim = converterER(expression, estados, simbolos, transicoes)
    # Cria o AFND com os componentes obtidos.
    afnd = {
        'V': simbolos,  # Alfabeto do AFND.
        'Q': estados,   # Conjunto de estados do AFND.
        'delta': {estado: {} for estado in estados},  # Função de transição do AFND.
        'q0': inicio,   # Estado inicial do AFND.
        'F': [fim]      # Conjunto de estados finais do AFND.
    }
    # Preenche a função de transição do AFND com as transições obtidas.
    for transicao in transicoes:
        inicio, simbolo, fim = transicao
        if simbolo not in afnd['delta'][inicio]:
            afnd['delta'][inicio][simbolo] = []
        afnd['delta'][inicio][simbolo].append(fim)
    return afnd

# Verifica se os argumentos de linha de comando são válidos.
if len(sys.argv) != 4 or sys.argv[2] != "--output":
    print("Uso: python script.py <entrada.er.json> --output <saida.afnd.json>")
    sys.exit(1)

# Obtém o nome do arquivo de entrada e de saída dos argumentos de linha de comando.
entrada_er = sys.argv[1]
saida_afnd = sys.argv[3]

# Lê a expressão regular do arquivo de entrada.
with open(entrada_er, 'r') as f:
    expressao_regular = json.load(f)

    # Converte a expressão regular para um AFND.
    afnd = convertERParaAFND(expressao_regular)

# Escreve o AFND gerado no arquivo de saída.
with open(saida_afnd, 'w') as f:
    json.dump(afnd, f, indent=4)

# Exibe uma mensagem indicando que o AFND foi gerado com sucesso.
print(f"AFND gerado com sucesso em {saida_afnd}")
