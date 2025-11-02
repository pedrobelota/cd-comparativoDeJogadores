# Módulo utils
# ==== Trechos do notebook (seção: Constantes & Configuração Global) ====

# Compatibilidade: IPython display opcional
try:
    from IPython.display import display, HTML, clear_output
except ImportError:
    def display(x): print(x)
    def HTML(x): return str(x)
    def clear_output(): pass
import re
import numpy as np
import pandas as pd


SEASONS_DEFAULT = ['2023-2024', '2024-2025']   # ajuste à vontade

FBREF_TABLE_IDS = {
    "standard":     ["stats_standard_expanded", "stats_standard_combined", "stats_standard"],
    "shooting":     ["stats_shooting_expanded", "stats_shooting_combined", "stats_shooting"],
    "passing":      ["stats_passing_expanded", "stats_passing_combined", "stats_passing"],
    "pass_types":   ["stats_passing_types_expanded", "stats_passing_types_combined", "stats_passing_types"],
    "gca":          ["stats_gca_expanded", "stats_gca_combined", "stats_gca"],
    "defense":      ["stats_defense_expanded", "stats_defense_combined", "stats_defense"],
    "possession":   ["stats_possession_expanded", "stats_possession_combined", "stats_possession"],
    "pressures":    ["stats_pressures_expanded", "stats_pressures_combined", "stats_pressures"],
    "playing_time": ["stats_playing_time_expanded", "stats_playing_time_combined", "stats_playing_time"],
    "misc":         ["stats_misc_expanded", "stats_misc_combined", "stats_misc"],
    "keeper":       ["stats_keeper_expanded", "stats_keeper_combined", "stats_keeper"],
    "keeper_adv":   ["stats_keeper_adv_expanded", "stats_keeper_adv_combined", "stats_keeper_adv"],
}

STAT_ALIASES = {
    "MP": ["MP", "Matches"],
    "Min": ["Min", "Minutes"],
    "Gls": ["Gls", "Goals"],
    "Ast": ["Ast", "Assists"],
    "xG": ["xG"],
    "xAG": ["xAG", "xA"],
    "CrdY": ["CrdY", "Yel"],
    "CrdR": ["CrdR", "Red"],
    "Tkl": ["Tkl", "Tackles"],
    "TklW": ["TklW", "Tackles Won"],
    "Int": ["Int", "Interceptions"],
    "Blocks": ["Blocks"],
    "Clr": ["Clr", "Clearances"],
    "AerialsWon": ["AerialsWon", "Aerials Won"],
    "Pressures": ["Pressures", "Press"],
    "Err": ["Err", "Errors"],
}

PREFERRED_SOURCE = {
    "MP": "standard",
    "Min": "standard",
    "Gls": "standard",
    "Ast": "standard",
    "xG": "shooting",
    "xAG": "passing",
    "CrdY": "standard",
    "CrdR": "standard",
    "Tkl": "defense",
    "TklW": "defense",
    "Int": "defense",
    "Blocks": "defense",
    "Clr": "defense",
    "AerialsWon": "defense",
    "Pressures": "pressures",
    "Err": "misc",
}

INT_METRICS = {
    "MP","Min","Gls","Ast","CrdY","CrdR",
    "Tkl","TklW","Int","Blocks","Clr","AerialsWon","Pressures","Err"
}

# ==== Trechos do notebook (seção: Execução Principal (inputs → scraping → agregação → tabela/CSV → gráficos)) ====

# Compatibilidade: IPython display opcional
try:
    from IPython.display import display, HTML, clear_output
except ImportError:
    def display(x): print(x)
    def HTML(x): return str(x)
    def clear_output(): pass
import re
import numpy as np
import pandas as pd

import pandas as pd
from IPython.display import display, HTML
from pathlib import Path

def carregar_dados_locais(nome_arquivo="liga_jogadores_completo.csv"):
    """
    Carrega o DataFrame a partir de um arquivo CSV local.
    """
    filepath = Path.cwd() / nome_arquivo
    if not filepath.exists():
        print(f"[Erro] O arquivo '{nome_arquivo}' não foi encontrado.")
        print("Por favor, execute a célula de coleta de dados primeiro para gerar o arquivo.")
        return None
    
    print(f"[OK] Carregando dados do arquivo local: {filepath.resolve()}")
    return pd.read_csv(filepath)

def analisar_medias_por_posicao(df_completo):
    """
    Filtra jogadores por posição, calcula a média e retorna um DataFrame consolidado.
    """
    if df_completo is None or df_completo.empty:
        print("[Erro] O DataFrame de entrada está vazio.")
        return

    print("--- Análise de Médias por Posição ---")
    df = df_completo[df_completo['Playing Time_Min'] >= 450].copy()

    pos_atacantes = ['FW', 'FW,MF']
    pos_meias = ['MF,FW', 'MF']
    pos_defensores = ['DF', 'DF,FW', 'DF,MF']
    pos_goleiros = ['GK']

    df_atacantes = df[df['Pos'].isin(pos_atacantes)]
    df_meias = df[df['Pos'].isin(pos_meias)]
    df_defensores = df[df['Pos'].isin(pos_defensores)]
    df_goleiros = df[df['Pos'].isin(pos_goleiros)]
    
    print(f"Jogadores analisados: {len(df_atacantes)} Atacantes, {len(df_meias)} Meias, {len(df_defensores)} Defensores, {len(df_goleiros)} Goleiros.")

    media_atacantes = df_atacantes.select_dtypes(include='number').mean()
    media_meias = df_meias.select_dtypes(include='number').mean()
    media_defensores = df_defensores.select_dtypes(include='number').mean()
    media_goleiros = df_goleiros.select_dtypes(include='number').mean()

    df_resultado = pd.DataFrame({
        'Média Atacantes': media_atacantes,
        'Média Meias': media_meias,
        'Média Defensores': media_defensores,
        'Média Goleiros': media_goleiros
    }).T

    print("\n[OK] Médias por posição calculadas com sucesso.")
    return df_resultado

#Execução Principal da Análise Local
if __name__ == '__main__':
    df_liga_completa = carregar_dados_locais()
    
    if df_liga_completa is not None:
        df_medias_posicao = analisar_medias_por_posicao(df_liga_completa)

        if df_medias_posicao is not None:
             #Dicionário mapeando nomes antigos para nomes novos
            rename_map = {
                'Performance_Gls': 'Gols',
                'Performance_Ast': 'Assist.',
                'Performance_G+A': 'G+A',
                'Expected_xG': 'xG',
                'Expected_xAG': 'xAG',
                'Playing Time_90s': '90s Jogados',
                'Tackles_Tkl': 'Desarmes'
            }
        
            #Pega apenas as colunas do mapa que existem no DataFrame
            cols_to_show = [col for col in rename_map.keys() if col in df_medias_posicao.columns]
            
            #Cria a visualização apenas com as colunas existentes
            df_view = df_medias_posicao[cols_to_show].round(2)
            
            #Renomeia usando o dicionário, o que é seguro
            df_view = df_view.rename(columns=rename_map)
            
            display(HTML(df_view.to_html(classes='dataframe', border=0)))

