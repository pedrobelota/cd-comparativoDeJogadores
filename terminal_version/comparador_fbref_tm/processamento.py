# Módulo processamento
# Sugestão de imports comuns:
import pandas as pd
import numpy as np
import re

# ==== Trechos do notebook (seção: Utilitários (normalização, formatação, helpers)) ====

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


def is_valid_url(u: str | None) -> bool:
    return bool(re.match(r'^https?://', (u or '').strip()))

def _normalize_season(s: str) -> str:
    return re.sub(r'\s+', '', s or '')

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0)
    cols = pd.Index([str(c) for c in df.columns], dtype="object")
    seen = {}
    new_cols = []
    for c in cols:
        if c not in seen:
            seen[c] = 0
            new_cols.append(c)
        else:
            seen[c] += 1
            new_cols.append(f"{c}.{seen[c]}")
    df.columns = new_cols
    return df.rename(columns={"Competition": "Comp", "Team": "Squad", "Matches": "MP"})

def _clean_rows(df: pd.DataFrame) -> pd.DataFrame:
    if "Season" in df.columns:
        mask_hdr = df["Season"].astype(str).str.contains(r"Season|years", case=False, na=False)
        df = df.loc[~mask_hdr].copy()
        df.loc[:, "Season"] = df["Season"].astype(str).map(_normalize_season)
    return df.reset_index(drop=True)

def _pick_first_present(df, names):
    for c in names:
        if c in df.columns:
            return c
    return None

def _col_as_series(df: pd.DataFrame, col: str) -> pd.Series:
    obj = df[col]
    return obj.iloc[:, 0] if isinstance(obj, pd.DataFrame) else obj

def _fmt_by_metric(metric: str, value):
    if value is None or value == "":
        return ""
    try:
        fv = float(value)
    except Exception:
        return value
    if metric in INT_METRICS:
        return int(round(fv))
    else:
        return round(fv, 2)

# ==== Trechos do notebook (seção: Agregação (sem duplicidade de métricas)) ====

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


def aggregate_player_stats(fb_tables: dict) -> dict:
    stats = {}
    for metric, src in PREFERRED_SOURCE.items():
        df = fb_tables.get(src)
        if isinstance(df, pd.DataFrame) and not df.empty:
            alias = STAT_ALIASES.get(metric, [metric])
            col = _pick_first_present(df, alias)
            if col:
                s = _col_as_series(df, col)
                stats[metric] = pd.to_numeric(s, errors='coerce').fillna(0).sum()
        else:
            stats[metric] = 0.0

    gols, ast, minutos = stats.get("Gls", 0.0), stats.get("Ast", 0.0), stats.get("Min", 0.0)
    stats["G+A_p90"] = ((gols + ast) / minutos) * 90 if minutos > 0 else 0.0
    return stats

# ==== Trechos do notebook (seção: Exportação CSV (2 casas decimais para floats, inteiros sem casas)) ====

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


def _parse_market_value_to_eur(mv_str: str):
    if not mv_str or mv_str in ("N/A", "Erro"): return None
    s = mv_str.replace("€","").replace(",",".").strip().upper()
    try:
        if s.endswith("M"): return round(float(s[:-1]) * 1_000_000, 2)
        if s.endswith("K"): return round(float(s[:-1]) * 1_000, 2)
        return round(float(s), 2)
    except Exception:
        return None

def _num2(v, default=0.0):
    try:
        return round(float(v), 2)
    except Exception:
        return round(float(default), 2)

def build_players_dataset_rows(pname, qname,
                               p_tm, q_tm,
                               p_stats, q_stats,
                               seasons_list,
                               p_tm_url, p_fb_url,
                               q_tm_url, q_fb_url):
    collected_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    seasons = ", ".join(seasons_list)

    def row_for(name, tm, st, tm_url, fb_url):
        return {
            "player": name, "seasons": seasons,
            "source_transfermarkt": tm_url, "source_fbref_all_comps": fb_url,
            "collected_at_utc": collected_at,
            "dob": tm.get("Data de Nascimento"), "height": tm.get("Altura"),
            "current_club": tm.get("Clube Atual"), "nationality": tm.get("Nacionalidade"),
            "position": tm.get("Posição"), "market_value_eur": _parse_market_value_to_eur(tm.get("Valor de Mercado")),
            "matches": _num2(st.get("MP", 0)), "minutes": _num2(st.get("Min", 0)),
            "goals": _num2(st.get("Gls", 0)), "assists": _num2(st.get("Ast", 0)),
            "g_plus_a_per90": _num2(st.get("G+A_p90", 0)),
            "xg": _num2(st.get("xG", 0)), "xag": _num2(st.get("xAG", 0)),
            "yellow_cards": _num2(st.get("CrdY", 0)), "red_cards": _num2(st.get("CrdR", 0)),
            "tackles": _num2(st.get("Tkl", 0)), "interceptions": _num2(st.get("Int", 0)),
            "blocks": _num2(st.get("Blocks", 0)), "clearances": _num2(st.get("Clr", 0)),
            "aerials_won": _num2(st.get("AerialsWon", 0)), "pressures": _num2(st.get("Pressures", 0)),
            "errors": _num2(st.get("Err", 0)),
        }

    rows = [row_for(pname, p_tm, p_stats, p_tm_url, p_fb_url)]
    if qname and (is_valid_url(q_tm_url) or is_valid_url(q_fb_url)):
        rows.append(row_for(qname, q_tm, q_stats, q_tm_url, q_fb_url))
    return rows

def save_dataset_csv(rows, out_path="dataset_coleta_jogadores.csv"):
    df_out = pd.DataFrame(rows)

    int_cols = [
        "matches","minutes","goals","assists","yellow_cards","red_cards",
        "tackles","interceptions","blocks","clearances","aerials_won",
        "pressures","errors"
    ]
    for c in int_cols:
        if c in df_out.columns:
            df_out[c] = pd.to_numeric(df_out[c], errors="coerce").round().astype("Int64")

    float_cols = ["g_plus_a_per90","xg","xag","market_value_eur"]
    for c in float_cols:
        if c in df_out.columns:
            df_out[c] = pd.to_numeric(df_out[c], errors="coerce").round(2)

    file_exists = os.path.exists(out_path)
    df_out.to_csv(out_path, index=False, mode="a", header=not file_exists, encoding="utf-8")
    return os.path.abspath(out_path)

