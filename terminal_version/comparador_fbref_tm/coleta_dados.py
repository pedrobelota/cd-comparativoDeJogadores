# Módulo coleta_dados
# Sugestão de imports comuns:
import pandas as pd
import time

# ==== Trechos do notebook (seção: Instalação e Imports) ====

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


# Se precisar instalar (descomente):
# !pip install undetected-chromedriver beautifulsoup4 lxml pandas numpy matplotlib requests

import os
import re
import time
from io import StringIO
from datetime import datetime, timezone

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup, Comment
from IPython.display import display, HTML, clear_output

# ==== Trechos do notebook (seção: Scraping Transfermarkt) ====

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


def _resolve_transfermarkt_profile_url(url: str) -> str:
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "pt-BR,pt;q=0.9"}, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        link = soup.find("link", rel="canonical")
        if link and "/profil/spieler/" in (link.get("href") or ""):
            return link["href"]
        a = soup.find("a", href=re.compile(r"/profil/spieler/\d+"))
        if a and a.get("href"):
            href = a["href"]
            return href if href.startswith("http") else "https://www.transfermarkt.com.br" + href
        return url
    except Exception:
        return url

def get_transfermarkt_data(player_url: str) -> dict:
    if not is_valid_url(player_url):
        return {
            "Valor de Mercado": "N/A", "Posição": "N/A", "Nacionalidade": "N/A",
            "Clube Atual": "N/A", "Data de Nascimento": "N/A", "Altura": "N/A"
        }
    profile_url = player_url if "/profil/spieler/" in player_url else _resolve_transfermarkt_profile_url(player_url)
    try:
        r = requests.get(profile_url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "pt-BR,pt;q=0.9"}, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        market_value = "N/A"
        mv = soup.select_one("a.data-header__market-value-wrapper")
        if mv:
            txt = mv.get_text(" ", strip=True).replace("\xa0"," ").replace(",",".")
            m = re.search(r"([\d\.]+)\s*(mi\.|mil\.|M|K)", txt, flags=re.I)
            if m:
                num, unit = m.group(1), m.group(2).lower()
                market_value = f"{num}M" if unit in ("mi.","m") else f"{num}K" if unit in ("mil.","k") else num

        dob = height = position = nationality = None
        for li in soup.select(".data-header__details > ul > li"):
            t = li.get_text(" ", strip=True)
            if ("Nasc./Idade" in t) or ("Nasc." in t):
                m = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", t)
                dob = m.group(1) if m else dob
            if "Altura:" in t:
                height = t.split("Altura:")[-1].strip()
            if "Posição:" in t:
                position = t.split("Posição:")[-1].strip()
            if "Nacionalidade:" in t:
                flag = li.find("img")
                nationality = flag["title"] if flag and flag.has_attr("title") else t.split("Nacionalidade:")[-1].strip()

        current_club = None
        label = soup.find("span", string=lambda x: x and "Clube atual" in x)
        if label:
            a = label.find_next("a", title=True)
            current_club = a.get_text(strip=True) if a else None
        if not current_club:
            a = soup.select_one(".data-header__club a[title]")
            if a:
                current_club = a.get_text(strip=True)
        if not current_club:
            a = soup.find("a", href=re.compile(r"/verein/"))
            if a:
                current_club = a.get_text(strip=True)

        return {
            "Valor de Mercado": market_value or "N/A",
            "Posição": position or "N/A",
            "Nacionalidade": nationality or "N/A",
            "Clube Atual": current_club or "N/A",
            "Data de Nascimento": dob or "N/A",
            "Altura": height or "N/A",
        }
    except Exception as e:
        print(f"[Transfermarkt] Erro: {e}")
        return {
            "Valor de Mercado": "Erro", "Posição": "Erro", "Nacionalidade": "Erro",
            "Clube Atual": "Erro", "Data de Nascimento": "Erro", "Altura": "Erro"
        }

# ==== Trechos do notebook (seção: Scraping FBref (Selenium stealth headless)) ====

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


def get_fbref_tables_selenium(url: str, table_id_map: dict, headless: bool = True,
                              scroll_pause: float = 0.7, max_scroll_loops: int = 25) -> dict:
    if not is_valid_url(url):
        return {}

    import undetected_chromedriver as uc
    from selenium.webdriver.support.ui import WebDriverWait

    opts = uc.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--lang=pt-BR")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

    driver = uc.Chrome(options=opts)

    def _try_accept_consent():
        js = """
        const btns = Array.from(document.querySelectorAll('button, a, input[type="button"], input[type="submit"]'));
        const ok = btns.find(b => /accept|agree|consent|aceitar|concordo/i.test((b.textContent||b.value||'').trim()));
        if (ok) { ok.click(); return true; }
        document.documentElement.style.overflow = 'auto';
        document.body.style.overflow = 'auto';
        return false;
        """
        try:
            return bool(driver.execute_script(js))
        except Exception:
            return False

    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
        _try_accept_consent()
        time.sleep(0.8)

        last_h = 0
        loops = 0
        while True:
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            h = driver.execute_script("return document.body.scrollHeight")
            loops += 1
            if h == last_h or loops >= max_scroll_loops:
                break
            last_h = h

        html = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "lxml")
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if "<table" in c and "</table>" in c:
            frag = BeautifulSoup(c, "lxml")
            c.replace_with(frag)

    out = {}
    for name, id_variants in table_id_map.items():
        df_ok = None
        for tid in id_variants:
            holder = soup.find(id=f"div_{tid}") or soup.find(id=tid) or soup.find("table", id=tid)
            if not holder:
                continue
            table = holder if holder.name == "table" else holder.find("table", id=tid)
            if not table:
                continue
            try:
                dfs = pd.read_html(StringIO(str(table)))
                if not dfs:
                    continue
                df = dfs[0]
                df = _normalize_columns(df)
                df = _clean_rows(df)
                if "Season" in df.columns:
                    df = df[df["Season"].isin([_normalize_season(x) for x in SEASONS_DEFAULT])]
                if not df.empty:
                    df_ok = df
                    break
            except Exception:
                continue
        if df_ok is not None:
            out[name] = df_ok

    if out:
        print("[FBref] Tabelas capturadas:", {k: v.shape for k, v in out.items()})
    else:
        print("[FBref] Nenhuma tabela encontrada (confira a URL '/all_comps/').")
    return out

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


def main():
    display(HTML("<h2>Comparação — temporadas 2023-2024 e 2024-2025</h2>"))

    p1_name = input("\nNome do jogador 1: ").strip()
    p1_tm_url = input(f"URL Transfermarkt ({p1_name}): ").strip()
    p1_fbref_url = input(f"URL FBref 'All Competitions' ({p1_name}): ").strip()

    p2_name = input("\nNome do jogador 2 (opcional): ").strip()
    p2_tm_url = input(f"URL Transfermarkt ({p2_name}) [opcional]: ").strip() if p2_name else ""
    p2_fbref_url = input(f"URL FBref 'All Competitions' ({p2_name}) [opcional]: ").strip() if p2_name else ""

    single_mode = (not p2_name) or (not is_valid_url(p2_tm_url) and not is_valid_url(p2_fbref_url))
    if single_mode:
        print("\n[Info] Modo 1 jogador.")

    # Transfermarkt
    p1_tm = get_transfermarkt_data(p1_tm_url)
    p2_tm = get_transfermarkt_data(p2_tm_url) if not single_mode else {
        "Valor de Mercado":"N/A","Posição":"N/A","Nacionalidade":"N/A",
        "Clube Atual":"N/A","Data de Nascimento":"N/A","Altura":"N/A"
    }

    # FBref
    print("\n[FBref] Coletando (Selenium stealth headless)...")
    p1_tables = get_fbref_tables_selenium(p1_fbref_url, FBREF_TABLE_IDS, headless=True)
    p2_tables = get_fbref_tables_selenium(p2_fbref_url, FBREF_TABLE_IDS, headless=True) if not single_mode else {}

    # Agregação
    p1_stats = aggregate_player_stats(p1_tables)
    p2_stats = aggregate_player_stats(p2_tables) if not single_mode else {}

    def V(metric, val):
        return _fmt_by_metric(metric, val)

    metricas = [
        "Clube Atual", "Data de Nascimento", "Altura", "Nacionalidade", "Posição", "Valor de Mercado (texto)",
        "Temporadas", "Partidas", "Minutos", "Gols", "Assistências", "G+A p/90", "xG", "xAG",
        "Amarelos", "Vermelhos", "Desarmes", "Intercepções", "Bloqueios", "Rebatidas", "Aéreos ganhos", "Pressões", "Erros"
    ]

    cols = {
        "Métrica": metricas,
        p1_name: [
            p1_tm.get('Clube Atual','-'),
            p1_tm.get('Data de Nascimento','-'),
            p1_tm.get('Altura','-'),
            p1_tm.get('Nacionalidade','-'),
            p1_tm.get('Posição','-'),
            p1_tm.get('Valor de Mercado','-'),
            ", ".join(SEASONS_DEFAULT),
            V("MP", p1_stats.get('MP',0)),
            V("Min", p1_stats.get('Min',0)),
            V("Gls", p1_stats.get('Gls',0)),
            V("Ast", p1_stats.get('Ast',0)),
            V("G+A_p90", p1_stats.get('G+A_p90',0)),
            V("xG", p1_stats.get('xG',0)),
            V("xAG", p1_stats.get('xAG',0)),
            V("CrdY", p1_stats.get('CrdY',0)),
            V("CrdR", p1_stats.get('CrdR',0)),
            V("Tkl", p1_stats.get('Tkl',0)),
            V("Int", p1_stats.get('Int',0)),
            V("Blocks", p1_stats.get('Blocks',0)),
            V("Clr", p1_stats.get('Clr',0)),
            V("AerialsWon", p1_stats.get('AerialsWon',0)),
            V("Pressures", p1_stats.get('Pressures',0)),
            V("Err", p1_stats.get('Err',0)),
        ],
    }

    if not single_mode:
        cols[p2_name] = [
            p2_tm.get('Clube Atual','-'),
            p2_tm.get('Data de Nascimento','-'),
            p2_tm.get('Altura','-'),
            p2_tm.get('Nacionalidade','-'),
            p2_tm.get('Posição','-'),
            p2_tm.get('Valor de Mercado','-'),
            ", ".join(SEASONS_DEFAULT),
            V("MP", p2_stats.get('MP',0)),
            V("Min", p2_stats.get('Min',0)),
            V("Gls", p2_stats.get('Gls',0)),
            V("Ast", p2_stats.get('Ast',0)),
            V("G+A_p90", p2_stats.get('G+A_p90',0)),
            V("xG", p2_stats.get('xG',0)),
            V("xAG", p2_stats.get('xAG',0)),
            V("CrdY", p2_stats.get('CrdY',0)),
            V("CrdR", p2_stats.get('CrdR',0)),
            V("Tkl", p2_stats.get('Tkl',0)),
            V("Int", p2_stats.get('Int',0)),
            V("Blocks", p2_stats.get('Blocks',0)),
            V("Clr", p2_stats.get('Clr',0)),
            V("AerialsWon", p2_stats.get('AerialsWon',0)),
            V("Pressures", p2_stats.get('Pressures',0)),
            V("Err", p2_stats.get('Err',0)),
        ]

    df_final = pd.DataFrame(cols).set_index('Métrica')

    player_cols = [p1_name] if single_mode else [p1_name, p2_name]

    def _highlight_max_row(s: pd.Series):
        nums = pd.to_numeric(s, errors="coerce")
        if nums.isna().all():
            return [''] * len(s)
        is_max = nums == nums.max()
        return ['background-color: #e8f6e8; font-weight: 600' if b else '' for b in is_max]

    styled_df = (df_final.style
                 .apply(_highlight_max_row, axis=1, subset=player_cols)
                 .set_properties(**{'text-align':'center','width':'260px','border':'1px solid #ccc'})
                 .set_table_styles([
                    {'selector':'th','props':[('background-color','#f2f2f2'),('font-size','14px'),('font-weight','bold'),('padding','8px')]},
                    {'selector':'th.row_heading','props':[('text-align','left'),('font-weight','bold'),('white-space','normal')]},
                    {'selector':'tr:nth-child(even)','props':[('background-color','#f9f9f9')]}
                 ])
                 .set_caption(f"<b>COMPARAÇÃO: {p1_name.upper()}{'' if single_mode else ' vs ' + p2_name.upper()}</b>"))

    clear_output(wait=True)
    display(styled_df)

    rows = build_players_dataset_rows(
        p1_name, p2_name if not single_mode else "",
        p1_tm, p2_tm if not single_mode else {},
        p1_stats, p2_stats if not single_mode else {},
        SEASONS_DEFAULT,
        p1_tm_url, p1_fbref_url,
        p2_tm_url if not single_mode else "", p2_fbref_url if not single_mode else ""
    )
    out_csv_path = save_dataset_csv(rows, out_path="dataset_coleta_jogadores.csv")
    print(f"\n[OK] Dataset salvo/atualizado em: {out_csv_path}")

    if not single_mode:
        plot_offensive_radar(p1_stats, p2_stats, p1_name, p2_name)
        plot_defensive_radar(p1_stats, p2_stats, p1_name, p2_name)
    else:
        print("\n[Info] Gráficos requerem 2 jogadores — ignorado em modo 1 jogador.")


main()

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
import time
from pathlib import Path
from io import StringIO

# Importações do Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_league_url_from_user():
    """
    Solicita e valida o link da liga do FBref.
    """
    while True:
        url = input("Digite o link da liga no FBref (ex: https://fbref.com/en/comps/12/2024-2025/stats/...): ")
        if "fbref.com" in url and "/stats/" in url:
            print(f"[OK] Link validado: {url}")
            return url
        else:
            print("\n[Erro] Link inválido. Por favor, insira um link do FBref que contenha '/stats/'. Tente novamente.")

def download_html_with_selenium(url):
    """
    Baixa o conteúdo HTML da URL fornecida usando Selenium para evitar o erro 403.
    """
    print("[INFO] Inicializando o navegador com Selenium para download seguro...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        time.sleep(3)
        html_content = driver.page_source
        print(f"[OK] Página baixada com sucesso usando Selenium: {url.split('/')[-1]}")
        return html_content
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao baixar a página com Selenium: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def collect_full_league_data(html_content, min_minutes=450):
    """
    ETAPA 1: Coleta e limpa os dados de TODOS os jogadores, criando nomes de coluna únicos.
    """
    print("\n--- ETAPA 1: Coleta de Dados de Todos os Jogadores ---")
    try:
        html_io = StringIO(html_content)
        df = pd.read_html(html_io, attrs={'id': 'stats_standard'})[0]
    except ValueError:
        print("[Erro] Tabela com id 'stats_standard' não encontrada.")
        return None

    #Lógica para achatar cabeçalhos e garantir nomes únicos.
    new_columns = []
    for col_level1, col_level2 in df.columns:
        if 'Unnamed' in col_level1:
            # Se o nível superior for "Unnamed", usa apenas o nome do nível inferior
            new_columns.append(col_level2)
        else:
            # Caso contrário, combina os dois níveis para criar um nome único e descritivo
            new_columns.append(f"{col_level1}_{col_level2}")
    
    df.columns = new_columns
    
    df = df[df['Player'] != 'Player'].copy()
    
    # Converte colunas para numérico. 
    for col in df.columns:
        if col not in ['Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Matches']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df.dropna(subset=['Playing Time_Min'], inplace=True)
    df_filtered = df[df['Playing Time_Min'] >= min_minutes].copy()
    
    print(f"[OK] Coleta concluída. Total de jogadores válidos (≥ {min_minutes} min): {len(df_filtered)}")
    
    filepath = Path.cwd() / "liga_jogadores_completo.csv"
    df_filtered.to_csv(filepath, index=False)
    print(f"[OK] DataFrame completo salvo em: {filepath.resolve()}")
    
    return df_filtered

def calculate_and_save_average(df_full_data):
    """
    ETAPA 2: Recebe o DataFrame completo e calcula a média de todas as colunas numéricas.
    """
    print("\n--- ETAPA 2: Cálculo da Média da Liga ---")
    
    df_numeric = df_full_data.select_dtypes(include='number')
    league_averages = df_numeric.mean()
    
    print("[OK] Média de todas as colunas numéricas calculada.")
    
    filepath = Path.cwd() / "liga_media_liga.csv"
    league_averages.to_frame(name='media').to_csv(filepath)
    print(f"[OK] Arquivo com a média da liga salvo em: {filepath.resolve()}")
    
    return league_averages

def main():
    """
    Orquestra o fluxo: coleta primeiro, calcula depois.
    """
    global df_comparacao
    df_comparacao = pd.DataFrame()

    league_url = get_league_url_from_user()
    html = download_html_with_selenium(league_url)
    
    if html:
        df_liga_completa = collect_full_league_data(html)
        
        if df_liga_completa is not None and not df_liga_completa.empty:
            print("\n[Visualização] 5 primeiras linhas do DataFrame coletado:")
            # Mostra as primeiras 5 linhas e as 10 primeiras colunas para não poluir a tela
            print(df_liga_completa.iloc[:, :10].head())
            
            medias = calculate_and_save_average(df_liga_completa)
            
            df_comparacao = pd.concat([df_comparacao, medias.to_frame(name='Liga (média)').T])
            print("\n[OK] Linha “Liga (média)” adicionada ao dataframe de comparação.")
            
            print("\n--- Resultado Final (DataFrame apenas com a média da liga) ---")
            # Seleciona algumas colunas-chave para uma visualização limpa
            cols_to_show = [
                'Performance_Gls', 'Performance_Ast', 'Performance_G+A',
                'Expected_xG', 'Expected_xAG', 'Playing Time_90s'
            ]
            # Filtra apenas as colunas que realmente existem no dataframe
            existing_cols_to_show = [col for col in cols_to_show if col in df_comparacao.columns]
            print(df_comparacao[existing_cols_to_show].round(2))
        else:
            print("\n[Erro Final] Nenhum dado foi coletado. O processo não pode continuar.")

if __name__ == '__main__':
    main()

