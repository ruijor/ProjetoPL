import json
from validar_afd import validar_afd

def ler_afd_from_json(nome_arquivo):
    try:
        with open(nome_arquivo, "r") as file:
            afd_json = json.load(file)
    except FileNotFoundError:
        return None, "Arquivo não encontrado."
    except json.JSONDecodeError:
        return None, "Erro ao decodificar o JSON."

    # Validar o AFD
    valido, mensagem = validar_afd(afd_json)
    if valido:
        return afd_json, "AFD válido."
    else:
        return None, mensagem
