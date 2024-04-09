import json
import sys
 
def novoEstado(estados):
    #Gera um novo estado e o adiciona à lista de estados.
    novo_estado = f'q{len(estados)}'
    estados.append(novo_estado)
    return novo_estado
 
def processaSimbolo(simbolo, simbolos, estados, transicoes):
   #Processa um símbolo, criando estados de início e fim e uma transição para o símbolo.
    estado_inicio = novoEstado(estados)
    estado_fim = novoEstado(estados)
    transicoes.append((estado_inicio, simbolo, estado_fim))
    if simbolo not in simbolos:
        simbolos.append(simbolo)
    return estado_inicio, estado_fim
 
def processaEpsilon(estados, transicoes):
    #Processa uma transição epsilon, criando estados de início e fim e uma transição epsilon entre eles.
    estado_inicio = novoEstado(estados)
    estado_fim = novoEstado(estados)
    transicoes.append((estado_inicio, '', estado_fim))
    return estado_inicio, estado_fim
 
def processaAlternancia(args, estados, simbolos, transicoes):
    #Processa uma alternância (|), conectando os argumentos com transições epsilon a novos estados de início e fim.
    estado_inicio = novoEstado(estados)
    estado_fim = novoEstado(estados)
    for arg in args:
        inicio_arg, fim_arg = converterER(arg, estados, simbolos, transicoes)
        transicoes.append((estado_inicio, '', inicio_arg))
        transicoes.append((fim_arg, '', estado_fim))
    return estado_inicio, estado_fim
 
def processaSequencia(args, estados, simbolos, transicoes):
   #Processa uma sequência, conectando cada argumento com transições epsilon, exceto o primeiro.
    inicio_seq, fim_seq = None, None
    for arg in args:
        inicio_arg, fim_arg = converterER(arg, estados, simbolos, transicoes)
        if inicio_seq is None:
            inicio_seq = inicio_arg
        else:
            transicoes.append((fim_seq, '', inicio_arg))
        fim_seq = fim_arg
    return inicio_seq, fim_seq
 
def processaFechamento(args, estados, simbolos, transicoes):
    #Processa o fechamento de Kleene (*), permitindo repetições do argumento.
    estado_inicio = novoEstado(estados)
    estado_fim = novoEstado(estados)
    inicio_arg, fim_arg = converterER(args[0], estados, simbolos, transicoes)
    transicoes.append((estado_inicio, '', inicio_arg))
    transicoes.append((fim_arg, '', estado_fim))
    transicoes.append((fim_arg, '', inicio_arg))
    transicoes.append((estado_inicio, '', estado_fim))
    return estado_inicio, estado_fim

def processaTransicao(args, estados, simbolos, transicoes):
    #Processa uma transição, conectando cada argumento com transições epsilon.
    inicio_trans, fim_trans = None, None
    for arg in args:
        inicio_arg, fim_arg = converterER(arg, estados, simbolos, transicoes)
        if inicio_trans is None:
            inicio_trans = inicio_arg
        else:
            transicoes.append((fim_trans, '', inicio_arg))
        fim_trans = fim_arg
    return inicio_trans, fim_trans
 
def converterER(er, estados, simbolos, transicoes):
    #Converte a expressão regular em componentes do AFND, baseando-se no tipo de operação.
    if 'simb' in er:
        return processaSimbolo(er['simb'], simbolos, estados, transicoes)
    elif er['op'] == 'alt':
        return processaAlternancia(er['args'], estados, simbolos, transicoes)
    elif er['op'] == 'seq':
        return processaSequencia(er['args'], estados, simbolos, transicoes)
    elif er['op'] == 'kle':
        return processaFechamento(er['args'], estados, simbolos, transicoes)
    elif er['op'] == 'trans':  # Adicionando a função prcTrans
        return processaTransicao(er['args'], estados, simbolos, transicoes)
    else:
        raise ValueError("Operador inválido na expressão regular")
 
def convertERParaAFND(expression):
#Converte uma expressão regular (dicionário) em um AFND (dicionário).
    estados, simbolos, transicoes = [], [], []
    inicio, fim = converterER(expression, estados, simbolos, transicoes)
    afnd = {
        'V': simbolos,
        'Q': estados,
        'delta': {estado: {} for estado in estados},
        'q0': inicio,
        'F': [fim]
    }
    for transicao in transicoes:
        inicio, simbolo, fim = transicao
        if simbolo not in afnd['delta'][inicio]:
            afnd['delta'][inicio][simbolo] = []
        afnd['delta'][inicio][simbolo].append(fim)
    return afnd

#Ponto de entrada do script; lê uma ER de um arquivo e escreve o AFND correspondente em outro.
if len(sys.argv) != 4 or sys.argv[2] != "--output":
    print("Uso: python script.py <entrada.er.json> --output <saida.afnd.json>")
    sys.exit(1)
 
entrada_er = sys.argv[1]
saida_afnd = sys.argv[3]
 
with open(entrada_er, 'r') as f:
    expressao_regular = json.load(f)
 
    afnd = convertERParaAFND(expressao_regular)
 
with open(saida_afnd, 'w') as f:
    json.dump(afnd, f, indent=4)
 
print(f"AFND gerado com sucesso em {saida_afnd}")
