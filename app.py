# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="CBMAM — Demonstrativo SEG",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .stApp { background-color: #ffffff !important; }
        [data-testid="stAppViewContainer"] { background-color: #ffffff !important; }
        [data-testid="block-container"] { background-color: #ffffff !important; padding-top: 1rem !important; }
        [data-testid="stHeader"] { background-color: #ffffff !important; }
        h1,h2,h3,h4,p,span,label { color: #000000 !important; }

        [data-testid="stMetric"] {
            background-color: #f8f8f8;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px 16px;
        }
        [data-testid="stMetricLabel"] p { color: #444 !important; font-size: 0.85rem !important; }
        [data-testid="stMetricValue"] { color: #000 !important; font-weight: bold !important; }

        section[data-testid="stSidebar"] { background-color: #1a1a2e !important; }
        section[data-testid="stSidebar"] * { color: white !important; }

        .header-title {
            text-align: center;
            font-weight: bold;
            font-size: 1.05rem;
            padding: 14px 20px;
            border: 2px solid #999;
            background-color: #f0f0f0;
            margin-bottom: 24px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: #000 !important;
            border-radius: 4px;
        }
        .section-title {
            text-align: center;
            font-weight: bold;
            font-size: 0.92rem;
            margin-bottom: 6px;
            color: #222 !important;
        }

        /* Tabela CBC amarela */
        .tbl-cbc { width:100%; border-collapse:collapse; font-size:0.85rem; }
        .tbl-cbc th {
            background-color:#FFC000; color:#000 !important; font-weight:bold;
            padding:7px 10px; border:1px solid #c89000;
        }
        .tbl-cbc th:last-child { text-align:right; }
        .tbl-cbc td {
            background-color:#FFC000; color:#000 !important;
            padding:5px 10px; border:1px solid #c89000;
        }
        .tbl-cbc td:last-child { text-align:right; }
        .tbl-cbc .total-row td {
            font-weight:bold; border-top:2px solid #8a6400;
            background-color:#e6ac00;
        }

        /* Tabela CBI verde */
        .tbl-cbi { width:100%; border-collapse:collapse; font-size:0.85rem; }
        .tbl-cbi th {
            background-color:#92D050; color:#000 !important; font-weight:bold;
            padding:7px 10px; border:1px solid #5a9e20;
        }
        .tbl-cbi th:last-child { text-align:right; }
        .tbl-cbi td {
            background-color:#92D050; color:#000 !important;
            padding:5px 10px; border:1px solid #5a9e20;
        }
        .tbl-cbi td:last-child { text-align:right; }
        .tbl-cbi .total-row td {
            font-weight:bold; border-top:2px solid #3a7a00;
            background-color:#70b830;
        }

        hr { border-color:#dddddd !important; }
        .block-container { padding-left:2rem !important; padding-right:2rem !important; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DADOS REAIS — MARÇO 2025 e MARÇO 2026 (fallback)
# ─────────────────────────────────────────────

# Estes dados serão usados APENAS se o arquivo Excel/CSV não puder ser lido ou não tiver OBM.
# Eles garantem que o dashboard sempre mostre os valores corretos para CBC/CBI.

# ── MARÇO 2025 (dados das suas imagens do Excel) ────────────────────────────────
CBC_2025_FALLBACK = [
    {"OBM": "1º BI",   "Horas": 1693},
    {"OBM": "BBE",     "Horas": 1269},
    {"OBM": "BIFMA",   "Horas": 339},
    {"OBM": "COBOM",   "Horas": 61},
    {"OBM": "DAT",     "Horas": 669},
    {"OBM": "GRAPH",   "Horas": 483},
    {"OBM": "PGGM",    "Horas": 263},
    {"OBM": "QCG",     "Horas": 1094},
    {"OBM": "SCI",     "Horas": 1730},
    {"OBM": "CMCB",    "Horas": 0},
    {"OBM": "CBC",     "Horas": 469},
]

CBI_2025_FALLBACK = [
    {"OBM": "CBI",                          "Horas": 10},
    {"OBM": "1º CIBM - Itacoatiara",        "Horas": 596},
    {"OBM": "2º CIBM - Manacapuru",         "Horas": 975},
    {"OBM": "3º CIBM - Parintins",          "Horas": 0},
    {"OBM": "1º PDBM - Iranduba",           "Horas": 423},
    {"OBM": "1º PDBM - Rio Preto da Eva",   "Horas": 389},
    {"OBM": "2º PDBM - Novo Airão",         "Horas": 224},
    {"OBM": "2º PDBM - Humaitá",            "Horas": 491},
    {"OBM": "3º PDBM - Presidente Figueiredo", "Horas": 639},
    {"OBM": "1º PIBM - Tefé",               "Horas": 468},
    {"OBM": "2º PIBM - Tabatinga",          "Horas": 154},
]

# ── MARÇO 2026 (dados do dashboard/Excel) ─────
CBC_2026_FALLBACK = [
    {"OBM": "SCI",     "Horas": 2003},
    {"OBM": "1º BI",   "Horas": 1495},
    {"OBM": "BBE",     "Horas": 1102},
    {"OBM": "DAT",     "Horas": 856},
    {"OBM": "QCG",     "Horas": 680},
    {"OBM": "GRAPH",   "Horas": 632},
    {"OBM": "CBC",     "Horas": 557},
    {"OBM": "BIFMA",   "Horas": 383},
    {"OBM": "CMCBM",   "Horas": 64},
    {"OBM": "COBOM",   "Horas": 38},
    {"OBM": "PGGM",    "Horas": 34},
]

CBI_2026_FALLBACK = [
    {"OBM": "CBI",                          "Horas": 0}, # Ajustar com dados reais do Excel
    {"OBM": "1º CIBM - Itacoatiara",        "Horas": 0}, # Ajustar com dados reais do Excel
    {"OBM": "2º CIBM - Manacapuru",         "Horas": 0}, # Ajustar com dados reais do Excel
    {"OBM": "3º CIBM - Parintins",          "Horas": 0}, # Ajustar com dados reais do Excel
    {"OBM": "1º PDBM - Iranduba",           "Horas": 0}, # Ajustar com dados reais do Excel
    {"OBM": "1º PDBM - Rio Preto da Eva",   "Horas": 0}, # Ajustar com dados reais do Excel
    {"OBM": "2º PDBM - Novo Airão",         "Horas": 0}, # Ajustar com dados reais do Excel
    {"OBM": "2º PDBM - Humaitá",            "Horas": 0}, # Ajustar com dados reais do Excel
    {"OBM": "3º PDBM - Presidente Figueiredo", "Horas": 0}, # Ajustar com dados reais do Excel
    {"OBM": "1º PIBM - Tefé",               "Horas": 0}, # Ajustar com dados reais do Excel
    {"OBM": "2º PIBM - Tabatinga",          "Horas": 0}, # Ajustar com dados reais do Excel
]


# ─────────────────────────────────────────────
# CARREGAMENTO DE ARQUIVOS
# ─────────────────────────────────────────────
ARQUIVO_XLSX = "1_Relatrio_GRAFICOS_3.xlsx" # O arquivo Excel local
ARQUIVO_CSV_2026 = "relatoriomarco2026.csv" # O novo CSV para Março 2026

@st.cache_data
def carregar_xlsx_aba(arquivo, aba):
    try:
        df = pd.read_excel(arquivo, sheet_name=aba, header=None)
        df.dropna(how="all", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba '{aba}' do Excel: {e}")
        return None

@st.cache_data
def carregar_csv_delimitado(arquivo, delimitador=';'):
    try:
        df = pd.read_csv(arquivo, encoding="utf-8", sep=delimitador, header=0) # header=0 para pegar a primeira linha como cabeçalho
        df.columns = df.columns.str.strip() # Limpa espaços dos nomes das colunas
        df.dropna(how="all", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o CSV '{arquivo}': {e}")
        return None

# ─────────────────────────────────────────────
# FUNÇÕES DE PROCESSAMENTO
# ─────────────────────────────────────────────
def agrupar_por_obm(df_militares, col_obm_idx, col_horas_idx, header_row_offset=0):
    """
    Agrupa horas por OBM de um DataFrame de militares.
    col_obm_idx: índice da coluna da OBM (base 0)
    col_horas_idx: índice da coluna das Horas (base 0)
    header_row_offset: número de linhas a pular no início se houver cabeçalho
    """
    if df_militares is None or df_militares.empty:
        return pd.DataFrame(columns=["OBM", "Horas"])

    df_process = df_militares.iloc[header_row_offset:].copy()

    if col_obm_idx >= df_process.shape[1] or col_horas_idx >= df_process.shape[1]:
        st.warning(f"Índices de coluna OBM ({col_obm_idx}) ou Horas ({col_horas_idx}) fora do limite do DataFrame. Verifique a estrutura da aba do Excel.")
        return pd.DataFrame(columns=["OBM", "Horas"])

    df_process.rename(columns={
        df_process.columns[col_obm_idx]: "OBM_TEMP",
        df_process.columns[col_horas_idx]: "HORAS_TEMP"
    }, inplace=True)

    df_process["HORAS_TEMP"] = pd.to_numeric(df_process["HORAS_TEMP"], errors="coerce").fillna(0)
    df_process = df_process[df_process["OBM_TEMP"].astype(str).str.strip().ne("")]
    df_process = df_process[df_process["OBM_TEMP"].notna()]

    result = (
        df_process.groupby("OBM_TEMP")["HORAS_TEMP"]
        .sum().reset_index()
        .rename(columns={"OBM_TEMP": "OBM", "HORAS_TEMP": "Horas"})
    )
    result["OBM"] = result["OBM"].astype(str).str.strip()

    # Remove OBMs que são totais, nan, ou números (limpeza de dados)
    result = result[~result["OBM"].str.lower().str.contains("total|nan|horas|om", na=False)]
    result = result[~pd.to_numeric(result["OBM"], errors="coerce").notna()]

    return result

def is_cbc(obm_name):
    obm_name_lower = str(obm_name).lower()
    # Padrões para identificar OBMs do Interior
    padroes_cbi = ["cibm", "pdbm", "pibm", "cbi", "itacoatiara", "manacapuru", "parintins",
                   "iranduba", "rio preto da eva", "novo airão", "humaitá", "presidente figueiredo",
                   "tefé", "tabatinga", "coari", "eirunepé", "lábrea", "borba", "maués", "nova olinda do norte"]
    return not any(p in obm_name_lower for p in padroes_cbi)

def separar_cbc_cbi(df_obm_agrupado):
    if df_obm_agrupado.empty:
        return pd.DataFrame(columns=["OBM", "Horas"]), pd.DataFrame(columns=["OBM", "Horas"])

    df_obm_agrupado["is_cbc"] = df_obm_agrupado["OBM"].apply(is_cbc)
    df_cbc = df_obm_agrupado[df_obm_agrupado["is_cbc"]].drop(columns=["is_cbc"])
    df_cbi = df_obm_agrupado[~df_obm_agrupado["is_cbc"]].drop(columns=["is_cbc"])
    return df_cbc, df_cbi

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("### Configurações")
    st.markdown("---")

    periodo_selecionado = st.radio(
        "Selecione o Período:",
        ["📅 Março 2026", "📅 Março 2025"],
        index=0 # Padrão: Março 2026
    )

    st.markdown("---")
    st.markdown("### ℹ️ Informações de Carregamento")
    st.info("Para Março 2025, o sistema tenta ler a aba 'MILITARES MARÇO' do Excel.")
    st.info("Para Março 2026, o sistema tenta ler o arquivo 'relatoriomarco2026.csv'.")
    st.warning("Se o arquivo 'relatoriomarco2026.csv' não tiver a coluna OBM, as seções de CBC/CBI usarão dados de fallback.")

# ─────────────────────────────────────────────
# CARREGAMENTO E PROCESSAMENTO DE DADOS
# ─────────────────────────────────────────────
df_cbc = pd.DataFrame(columns=["OBM", "Horas"])
df_cbi = pd.DataFrame(columns=["OBM", "Horas"])
total_geral_csv_ou_excel = 0 # Para o total geral do CSV de 2026

if periodo_selecionado == "📅 Março 2025":
    periodo_label = "MARÇO 2025"
    df_militares_2025 = carregar_xlsx_aba(ARQUIVO_XLSX, "MILITARES MARÇO")

    if df_militares_2025 is not None and not df_militares_2025.empty:
        # Estrutura da aba "MILITARES MARÇO": OBM na coluna 3 (índice 3), Horas na coluna 4 (índice 4), dados a partir da linha 2 (índice 2)
        df_obm_agrupado = agrupar_por_obm(df_militares_2025, col_obm_idx=3, col_horas_idx=4, header_row_offset=2)
        df_cbc, df_cbi = separar_cbc_cbi(df_obm_agrupado)

    # Fallback se não carregou ou está vazio
    if df_cbc.empty:
        df_cbc = pd.DataFrame(CBC_2025_FALLBACK)
    if df_cbi.empty:
        df_cbi = pd.DataFrame(CBI_2025_FALLBACK)

else: # Março 2026
    periodo_label = "MARÇO 2026"
    df_militares_2026_csv = carregar_csv_delimitado(ARQUIVO_CSV_2026)

    if df_militares_2026_csv is not None and not df_militares_2026_csv.empty:
        # Verifica se o CSV tem a coluna OBM
        if "OBM" in df_militares_2026_csv.columns and "HORAS" in df_militares_2026_csv.columns:
            # Se tiver OBM, agrupa e separa normalmente
            df_obm_agrupado = agrupar_por_obm(df_militares_2026_csv, col_obm_idx=df_militares_2026_csv.columns.get_loc("OBM"), col_horas_idx=df_militares_2026_csv.columns.get_loc("HORAS"), header_row_offset=0)
            df_cbc, df_cbi = separar_cbc_cbi(df_obm_agrupado)
            total_geral_csv_ou_excel = df_obm_agrupado["Horas"].sum()
        elif "HORAS" in df_militares_2026_csv.columns:
            # Se não tiver OBM, calcula o total geral e usa fallback para CBC/CBI
            total_geral_csv_ou_excel = df_militares_2026_csv["HORAS"].sum()
            st.warning("O arquivo 'relatoriomarco2026.csv' não contém a coluna 'OBM'. As seções de CBC/CBI usarão dados de fallback.")
            df_cbc = pd.DataFrame(CBC_2026_FALLBACK)
            df_cbi = pd.DataFrame(CBI_2026_FALLBACK)
        else:
            st.error("O arquivo 'relatoriomarco2026.csv' não contém a coluna 'HORAS'. Não foi possível calcular o total.")
            df_cbc = pd.DataFrame(CBC_2026_FALLBACK)
            df_cbi = pd.DataFrame(CBI_2026_FALLBACK)
    else:
        # Fallback se o CSV não carregou ou está vazio
        df_cbc = pd.DataFrame(CBC_2026_FALLBACK)
        df_cbi = pd.DataFrame(CBI_2026_FALLBACK)

# ─────────────────────────────────────────────
# GARANTE TIPOS E ORDENA
# ─────────────────────────────────────────────
df_cbc["Horas"] = pd.to_numeric(df_cbc["Horas"], errors="coerce").fillna(0)
df_cbi["Horas"] = pd.to_numeric(df_cbi["Horas"], errors="coerce").fillna(0)
df_cbc = df_cbc.sort_values("Horas", ascending=False).reset_index(drop=True)
df_cbi = df_cbi.sort_values("Horas", ascending=False).reset_index(drop=True)

total_cbc   = int(df_cbc["Horas"].sum())
total_cbi   = int(df_cbi["Horas"].sum())
total_geral = int(total_geral_csv_ou_excel) if total_geral_csv_ou_excel > 0 else (total_cbc + total_cbi)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def safe_int(val):
    try:
        v = float(val)
        return 0 if np.isnan(v) else int(v)
    except:
        return 0

def build_table(df_t, css, total):
    rows = "".join(
        f'<tr><td>{r["OBM"]}</td><td>{safe_int(r["Horas"])}</td></tr>'
        for _, r in df_t.iterrows()
    )
    return f"""
    <table class="{css}">
        <thead><tr><th>OBM</th><th>Horas</th></tr></thead>
        <tbody>{rows}</tbody>
        <tfoot>
            <tr class="total-row">
                <td><b>Total</b></td>
                <td><b>{safe_int(total)}</b></td>
            </tr>
        </tfoot>
    </table>
    """

def build_chart(df_g, titulo):
    df_plot = df_g[df_g["Horas"] > 0].copy()
    df_plot["Horas"] = df_plot["Horas"].apply(safe_int)
    max_y = df_plot["Horas"].max() if not df_plot.empty else 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_plot["OBM"],
        y=df_plot["Horas"],
        text=df_plot["Horas"],
        textposition="outside",
        marker_color="#4472C4",
        marker_line_color="#2a52a4",
        marker_line_width=0.5,
        width=0.55,
        cliponaxis=False
    ))
    fig.update_layout(
        title=dict(text=titulo, x=0.5, font=dict(size=13, color="#000000")),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=360,
        margin=dict(t=50, b=80, l=40, r=20),
        font=dict(color="#000000"),
        xaxis=dict(
            showgrid=False, tickangle=-30,
            tickfont=dict(size=9, color="#000000"),
            showline=True, linecolor="#aaaaaa"
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#eeeeee",
            tickfont=dict(color="#000000"),
            range=[0, max_y * 1.28]
        ),
        shapes=[dict(
            type="rect", xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="#cccccc", width=1)
        )]
    )
    return fig

# ─────────────────────────────────────────────
# LAYOUT PRINCIPAL
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="header-title">'
    f'Demonstrativo de Horas de SEG Processadas para Pagamento no Mês de {periodo_label}'
    f'</div>',
    unsafe_allow_html=True
)

# KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("⏱️ Total Geral",    f"{total_geral:,}h".replace(",", "."))
k2.metric("🟡 CBC — Capital",  f"{total_cbc:,}h".replace(",", "."))
k3.metric("🟢 CBI — Interior", f"{total_cbi:,}h".replace(",", "."))
k4.metric("🏢 OBMs",           len(df_cbc) + len(df_cbi))

st.markdown("---")

# ── BLOCO CBC ─────────────────────────────────
col_t1, col_g1 = st.columns([1, 2])
with col_t1:
    st.markdown(
        '<p class="section-title">CBC - Comando de Bombeiros da Capital</p>',
        unsafe_allow_html=True
    )
    st.markdown(build_table(df_cbc, "tbl-cbc", total_cbc), unsafe_allow_html=True)
with col_g1:
    st.plotly_chart(
        build_chart(df_cbc, f"Distribuição SEG - Capital — {periodo_label}"),
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── BLOCO CBI ─────────────────────────────────
col_t2, col_g2 = st.columns([1, 2])
with col_t2:
    st.markdown(
        '<p class="section-title">CBI - Comando de Bombeiros do Interior</p>',
        unsafe_allow_html=True
    )
    st.markdown(build_table(df_cbi, "tbl-cbi", total_cbi), unsafe_allow_html=True)
with col_g2:
    st.plotly_chart(
        build_chart(df_cbi, f"Distribuição SEG - Interior — {periodo_label}"),
        use_container_width=True
    )

st.markdown("---")

# ── RESUMO ────────────────────────────────────
r1, r2, r3 = st.columns(3)

cbc_v = df_cbc[df_cbc["Horas"] > 0]
cbi_v = df_cbi[df_cbi["Horas"] > 0]
all_v = pd.concat([cbc_v, cbi_v]).sort_values("Horas", ascending=False)

with r1:
    st.metric("⏱️ Total Geral",    f"{total_geral:,}h".replace(",", "."))
    st.metric("🟡 CBC — Capital",  f"{total_cbc:,}h".replace(",", "."))
    st.metric("🟢 CBI — Interior", f"{total_cbi:,}h".replace(",", "."))

with r2:
    if not cbc_v.empty:
        st.success(
            f"🥇 **Maior OBM — Capital**\n\n"
            f"**{cbc_v.iloc[0]['OBM']}** → {safe_int(cbc_v.iloc[0]['Horas'])}h"
        )
    if not cbi_v.empty:
        st.success(
            f"🥇 **Maior OBM — Interior**\n\n"
            f"**{cbi_v.iloc[0]['OBM']}** → {safe_int(cbi_v.iloc[0]['Horas'])}h"
        )

with r3:
    if not all_v.empty:
        st.info(
            f"🏆 **Maior OBM Geral**\n\n"
            f"**{all_v.iloc[0]['OBM']}** → {safe_int(all_v.iloc[0]['Horas'])}h"
        )
    if total_geral > 0:
        fig_d = go.Figure(go.Pie(
            labels=["CBC — Capital", "CBI — Interior"],
            values=[total_cbc, total_cbi],
            hole=0.5,
            marker_colors=["#FFC000", "#92D050"],
            textinfo="percent+label",
            textfont=dict(color="#000000", size=11)
        ))
fig_d.update_layout(
            height=210, showlegend=False,
            margin=dict(t=10, b=0, l=0, r=0),
            paper_bgcolor="#ffffff",
            font=dict(color="#000000")
        )
        st.plotly_chart(fig_d, use_container_width=True)

# ── COMPARATIVO 2025 vs 2026 ──────────────────
st.markdown("---")
st.markdown("### 📊 Comparativo Março 2025 × Março 2026")

# Para o comparativo, vamos carregar os dados de cada mês novamente
# para garantir que o comparativo reflita os dados do Excel/CSV, não apenas fallbacks.
df_cbc_2025_comp = pd.DataFrame(CBC_2025_FALLBACK) # Inicia com fallback
df_cbc_2026_comp = pd.DataFrame(CBC_2026_FALLBACK) # Inicia com fallback

# Tenta carregar do Excel para Março 2025
df_mil_2025_comp = carregar_xlsx_aba(ARQUIVO_XLSX, "MILITARES MARÇO")
if df_mil_2025_comp is not None and not df_mil_2025_comp.empty:
    df_obm_2025_comp = agrupar_por_obm(df_mil_2025_comp, col_obm_idx=3, col_horas_idx=4, header_row_offset=2)
    df_cbc_2025_comp, _ = separar_cbc_cbi(df_obm_2025_comp)

# Tenta carregar do CSV para Março 2026 (se tiver OBM)
df_mil_2026_comp_csv = carregar_csv_delimitado(ARQUIVO_CSV_2026)
if df_mil_2026_comp_csv is not None and not df_mil_2026_comp_csv.empty:
    if "OBM" in df_mil_2026_comp_csv.columns and "HORAS" in df_mil_2026_comp_csv.columns:
        df_obm_2026_comp = agrupar_por_obm(df_mil_2026_comp_csv, col_obm_idx=df_mil_2026_comp_csv.columns.get_loc("OBM"), col_horas_idx=df_mil_2026_comp_csv.columns.get_loc("HORAS"), header_row_offset=0)
        df_cbc_2026_comp, _ = separar_cbc_cbi(df_obm_2026_comp)
    else:
        st.warning("O CSV de Março 2026 não tem OBM para o comparativo. Usando fallback para 2026.")


df_comp_cbc = pd.concat([
    df_cbc_2025_comp.assign(Período="Março 2025"),
    df_cbc_2026_comp.assign(Período="Março 2026")
])

fig_comp = go.Figure()
for p, cor in [("Março 2025", "#FFC000"), ("Março 2026", "#4472C4")]:
    d = df_comp_cbc[df_comp_cbc["Período"] == p]
    fig_comp.add_trace(go.Bar(
        name=p, x=d["OBM"], y=d["Horas"],
        text=d["Horas"], textposition="outside",
        marker_color=cor
    ))

fig_comp.update_layout(
    barmode="group",
    title=dict(text="CBC — Março 2025 vs Março 2026", x=0.5, font=dict(size=13, color="#000")),
    plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
    height=380,
    margin=dict(t=50, b=60, l=30, r=20),
    font=dict(color="#000000"),
    xaxis=dict(showgrid=False, tickangle=-20),
    yaxis=dict(showgrid=True, gridcolor="#eeeeee"),
    legend=dict(bgcolor="#ffffff", font=dict(color="#000"))
)
st.plotly_chart(fig_comp, use_container_width=True)

# ── DOWNLOADS ─────────────────────────────────
st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.download_button("⬇️ CBC — CSV",
        df_cbc.to_csv(index=False).encode("utf-8"),
        f"cbc_{periodo_label.lower().replace(' ','_')}.csv","text/csv")
with c2:
    st.download_button("⬇️ CBI — CSV",
        df_cbi.to_csv(index=False).encode("utf-8"),
        f"cbi_{periodo_label.lower().replace(' ','_')}.csv","text/csv")
with c3:
    df_dl = pd.concat([
        df_cbc.assign(Grupo="CBC - Capital"),
        df_cbi.assign(Grupo="CBI - Interior")
    ])
    st.download_button("⬇️ Completo — CSV",
        df_dl.to_csv(index=False).encode("utf-8"),
        f"cbmam_{periodo_label.lower().replace(' ','_')}.csv","text/csv")

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.8rem'>"
    f"CBMAM · Demonstrativo SEG · {periodo_label} · Streamlit"
    "</div>",
    unsafe_allow_html=True
)
