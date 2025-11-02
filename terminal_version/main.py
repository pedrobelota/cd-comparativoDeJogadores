import argparse
from comparador_fbref_tm import coleta_dados, processamento, analise, visualizacao

def parse_args():
    p = argparse.ArgumentParser(description='Comparador FBref x Transfermarkt (com média de liga)')
    p.add_argument('--salvar-saidas', type=str, default=None, help='Diretório para salvar resultados/figuras')
    return p.parse_args()

def main():
    args = parse_args()
    print('Pipeline base criado. Preencha o main.py com chamadas às funções dos módulos.')

if __name__ == '__main__':
    main()
