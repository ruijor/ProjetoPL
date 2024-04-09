import json
from validar_afd import validar_afd
from ler_afd_from_json import ler_afd_from_json
def main():
    # Chama a função para ler o arquivo JSON contendo a definição do AFD
    afd, mensagem = ler_afd_from_json("af.json")
    
    # Imprime o resultado
    print(mensagem)
    if afd:
        print("AFD carregado com sucesso:")
        print(afd)

if __name__ == "__main__":
    main()

