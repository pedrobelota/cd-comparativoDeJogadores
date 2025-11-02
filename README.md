## Visão Geral do Projeto

O **Comparador FBref x Transfermarkt** é uma ferramenta desenvolvida para **comparar, integrar e analisar dados de jogadores de futebol** extraídos de duas das maiores plataformas de estatísticas esportivas do mundo — [FBref](https://fbref.com) e [Transfermarkt](https://www.transfermarkt.com).

O objetivo do projeto é criar uma estrutura **modular, limpa e reutilizável**, capaz de:

- Coletar informações automaticamente das duas plataformas (via scraping e APIs);
- Unificar os dados em um formato padronizado;
- Calcular médias de desempenho e métricas agregadas por temporada e liga;
- Visualizar comparativos entre temporadas ou ligas com base em indicadores estatísticos.

Essa estrutura foi projetada para **funcionar em notebooks (Jupyter/Colab)**.

---

## Estrutura do Projeto

```

├── notebook_version/                # Versão voltada para Jupyter/Colab
| ├── Comparador_FBref_TM_com_media_liga.ipynb

├── terminal_version/                # Versão para execução em terminal (Futuro)
│   ├── comparador_fbref_tm/         # Mesmo código, com fallbacks para IPython
│   ├── main.py
│   ├── requirements.txt
│   └── notebooks/exemplo_uso.ipynb
│
└── README.md                        # Este arquivo
```

---

## Funcionalidades Principais

### Coleta de Dados 
- Leitura de tabelas do **FBref** e **Transfermarkt** via `pandas.read_html` ou `BeautifulSoup`.
- Possível uso de **Selenium** para páginas dinâmicas.
- Armazena os dados em `DataFrames` prontos para processamento.

### Processamento 
- Padroniza colunas e nomes de jogadores entre as duas fontes.
- Mescla os DataFrames em uma estrutura comparável.
- Lida com dados faltantes, tipos inconsistentes e normalizações.

### Análise 
- Calcula estatísticas descritivas e médias de liga.
- Permite comparar temporadas (ex: 2023-24 vs 2024-25).
- Identifica outliers de desempenho e variações entre temporadas.

### Visualização 
- Gera gráficos de comparação (barras, linhas, radar).
- Exporta resultados em PNG ou exibe diretamente no notebook.

### Utilitários 
- Funções auxiliares para manipulação de caminhos, logs e tratamento de erros.

## Tecnologias Utilizadas

| Categoria | Tecnologias |
|------------|-------------|
| Linguagem Principal | Python 3.10+ |
| Bibliotecas de Dados | `pandas`, `numpy` |
| Web Scraping | `requests`, `BeautifulSoup`, `selenium` |
| Visualização | `matplotlib`, `seaborn`, `plotly` |
| Ambiente Notebook | `IPython`, `Jupyter` |
| Organização | Estrutura TAD modular + README + venv + notebook |
