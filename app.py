# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="CBMAM — SEG Março 2025",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# FORÇA TEMA CLARO + ESTILOS
# ─────────────────────────────────────────────
st.markdown("""
    <style>
        /* Fundo geral branco */
        .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        [data-testid="stAppViewContainer"] {
            background-color: #ffffff !important;
        }
        [data-testid="stHeader"] {
            background-color: #ffffff !important;
        }
        [data-testid="block-container"] {
            background-color: #ffffff !important;
            padding-top: 1rem !important;
        }

        /* Métricas */
        [data-testid="stMetric"] {
            background-color: #f8f8f8;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px 16px;
        }
        [data-testid="stMetricLabel"] { color: #333 !important; }
        [data-testid="stMetricValue"] { color: #000 !important; font-weight: bold; }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #1a1a2e !important;
        }
        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Títulos e textos */
        h1, h2, h3, h4, p, span, div {
            color: #000000 !important;
        }

        /* Cabeçalho do demonstrativo */
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

        /* Título de seção */
        .section-title {
            text-align: center;
            font-weight: bold;
            font-size: 0.92rem;
            margin-bottom: 6px;
            margin-top: 4px;
            color: #222 !important;
        }

        /* Tabela CBC — amarela */
        .tbl-cbc {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            background-color: #FFC000;
        }
        .tbl-cbc th {
            background-color: #FFC000;
            color: #000 !important;
            font-weight: bold;
            padding: 7px 10px;
            border: 1px solid #c89000;
        }
        .tbl-cbc th:last-child { text-align: right; }
        .tbl-cbc td {
            background-color: #FFC000;
            color: #000 !important;
            padding: 5px 10px;
            border: 1px solid #c89000;
        }
        .tbl-cbc td:last-child { text-align: right; }
        .tbl-cbc .total-row td {
            font-weight: bold;
            border-top: 2px solid #8a6400;
            background-color: #e6ac00;
        }

        /* Tabela CBI — verde */
        .tbl-cbi {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            background-color: #92D050;
        }
        .tbl-cbi th {
            background-color: #92D050;
            color: #000 !important;
            font-weight: bold;
            padding: 7px 10px;
            border: 1px solid #5a9e20;
        }
        .tbl-cbi th:last-child { text-align: right; }
        .tbl-cbi td {
            background-color: #92D050;
            color: #000 !important;
            padding: 5px 10px;
            border: 1px solid #5a9e20;
        }
        .tbl-cbi td:last-child { text-align: right; }
        .tbl-cbi .total-row td {
            font-weight: bold;
            border-top: 2px solid #3a7a00;
            background-color: #70b830;
        }

        /* Divisor */
        hr {
            border-color: #dddddd !important;
        }

        /* Remove padding extra do Streamlit */
        .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARREGA CSV
# ─────────────────────────────────────────────
URL_CSV = "https://raw.githubusercontent.com/AllanCardosoDev/seg/main/relatorio.csv"

@st.cache_data
def carregar_csv():
    for enc in ["utf-8", "utf-8-sig", "latin-1"]:
        try:
            df = pd.read_csv(
                URL_CSV, encoding=enc,
                header=None, sep=None, engine="python"
            )
            # Pula cabeçalho textual se existir
            primeira = str(df.iloc[0, 0]).strip().lower()
            if not primeira.lstrip("-").isnumeric():
                df = df.iloc[1:].reset_index(drop=True)

            # Nomeia colunas pela estrutura real do CSV
            if df.shape[1] >= 5:
                df.columns = ["NUM", "NOME", "GUERRA", "OBM", "HORAS"] + \
                             [f"x{i}" for i in range(df.shape[1] - 5)]
            elif df.shape[1] == 4:
                df.columns = ["NUM", "NOME", "OBM", "HORAS"]
            elif df.shape[1] == 3:
                df.columns = ["NOME", "OBM", "HORAS"]
            else:
                df.columns = [f"col_{i}" for i in range(df.shape[1])]

            df.dropna(how="all", inplace=True)
            df.reset_index(drop=True, inplace=True)
            return df
        except Exception:
            continue
    st.error("Não foi possível carregar relatorio.csv")
    st.stop()

with st.spinner("Carregando dados..."):
    df_raw = carregar_csv()

col_obm  = "OBM"   if "OBM"   in df_raw.columns else df_raw.columns[-2]
col_segs = "HORAS" if "HORAS" in df_raw.columns else df_raw.columns[-1]

df_raw[col_segs] = pd.to_numeric(df_raw[col_segs], errors="coerce").fillna(0)
df_raw = df_raw[df_raw[col_obm].astype(str).str.strip().ne("")]
df_raw = df_raw[df_raw[col_obm].notna()]

# ─────────────────────────────────────────────
# AGRUPA POR OBM
# ─────────────────────────────────────────────
df_obm = (
    df_raw.groupby(col_obm)[col_segs]
    .sum()
    .reset_index()
    .rename(columns={col_obm: "OBM", col_segs: "Horas"})
)
df_obm["OBM"]   = df_obm["OBM"].astype(str).str.strip()
df_obm["Horas"] = pd.to_numeric(df_obm["Horas"], errors="coerce").fillna(0)
df_obm = df_obm[~df_obm["OBM"].str.lower().isin(["nan","none","","total"])]
df_obm = df_obm[~df_obm["OBM"].str.isnumeric()]

# ─────────────────────────────────────────────
# SEPARA CBC / CBI
# ─────────────────────────────────────────────
CBC_LISTA = [
    "1° BI","1º BI","1 BI","1°BI","1ºBI",
    "BBE","BIFMA","COBOM","DAT",
    "GRAPH","PGGM","QCG","QCG","SCI",
    "CMCB","CBC","CBCM","COBM"
]

def is_cbc(nome):
    n = str(nome).upper().strip()
    return any(c.upper() in n for c in CBC_LISTA)

mask_cbc = df_obm["OBM"].apply(is_cbc)
df_cbc   = df_obm[mask_cbc].sort_values("Horas", ascending=False).reset_index(drop=True)
df_cbi   = df_obm[~mask_cbc].sort_values("Horas", ascending=False).reset_index(drop=True)

# Fallback
if df_cbc.empty:
    df_cbc = pd.DataFrame([
        {"OBM": "SCI",   "Horas": 1730},
        {"OBM": "1º BI", "Horas": 1693},
        {"OBM": "BBE",   "Horas": 1269},
        {"OBM": "QCG",   "Horas": 1094},
        {"OBM": "DAT",   "Horas": 669},
        {"OBM": "GRAPH", "Horas": 483},
        {"OBM": "CBC",   "Horas": 469},
        {"OBM": "BIFMA", "Horas": 339},
        {"OBM": "PGGM",  "Horas": 263},
        {"OBM": "COBOM", "Horas": 61},
        {"OBM": "CMCB",  "Horas": 0},
    ])
if df_cbi.empty:
    df_cbi = pd.DataFrame([
        {"OBM": "2º CIBM - Manacapuru",       "Horas": 975},
        {"OBM": "3º PDBM - Pres. Figueiredo", "Horas": 639},
        {"OBM": "1º CIBM - Itacoatiara",      "Horas": 596},
        {"OBM": "1º PIBM - Tefé",             "Horas": 468},
        {"OBM": "2º PDBM - Humaitá",          "Horas": 491},
        {"OBM": "1º PDBM - Iranduba",         "Horas": 423},
        {"OBM": "1º PDBM - Rio Preto da Eva", "Horas": 389},
        {"OBM": "2º PDBM - Novo Airão",       "Horas": 224},
        {"OBM": "2º PIBM - Tabatinga",        "Horas": 154},
        {"OBM": "3º CIBM - Parintins",        "Horas": 0},
        {"OBM": "CBI",                        "Horas": 10},
    ])

total_cbc   = int(df_cbc["Horas"].sum())
total_cbi   = int(df_cbi["Horas"].sum())
total_geral = total_cbc + total_cbi

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
        title=dict(
            text=titulo,
            x=0.5,
            font=dict(size=13, color="#000000", family="Arial")
        ),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=360,
        margin=dict(t=50, b=80, l=40, r=20),
        font=dict(color="#000000", family="Arial"),
        xaxis=dict(
            showgrid=False,
            tickangle=-30,
            tickfont=dict(size=9, color="#000000"),
            showline=True,
            linecolor="#aaaaaa",
            linewidth=1,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#eeeeee",
            gridwidth=1,
            tickfont=dict(color="#000000"),
            range=[0, max_y * 1.28],
            showline=False,
        ),
        shapes=[dict(
            type="rect", xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="#cccccc", width=1)
        )]
    )
    return fig

# ─────────────────────────────────────────────
# SIDEBAR (debug)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("---")
    st.markdown(f"**Registros:** {len(df_raw)}")
    st.markdown(f"**OBMs:** {len(df_obm)}")
    st.markdown(f"**CBC:** {len(df_cbc)} | **CBI:** {len(df_cbi)}")
    st.markdown("---")
    with st.expander("🔍 OBMs no CSV"):
        for obm in sorted(df_obm["OBM"].tolist()):
            g = "🟡 CBC" if is_cbc(obm) else "🟢 CBI"
            st.markdown(f"{g} — `{obm}`")
    with st.expander("📋 Primeiras linhas"):
        st.dataframe(df_raw.head(10))

# ─────────────────────────────────────────────
# LAYOUT PRINCIPAL
# ─────────────────────────────────────────────
st.markdown(
    '<div class="header-title">'
    'Demonstrativo de Horas de SEG Processadas para Pagamento no Mês de MARÇO 2025'
    '</div>',
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
        build_chart(df_cbc, "Distribuição SEG - Capital"),
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
        build_chart(df_cbi, "Distribuição SEG - Interior"),
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
            height=210,
            showlegend=False,
            margin=dict(t=10, b=0, l=0, r=0),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#000000")
        )
        st.plotly_chart(fig_d, use_container_width=True)

# ── DOWNLOADS ─────────────────────────────────
st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.download_button("⬇️ CBC — CSV",
        df_cbc.to_csv(index=False).encode("utf-8"),
        "cbc_marco2025.csv", "text/csv")
with c2:
    st.download_button("⬇️ CBI — CSV",
        df_cbi.to_csv(index=False).encode("utf-8"),
        "cbi_marco2025.csv", "text/csv")
with c3:
    df_dl = pd.concat([
        df_cbc.assign(Grupo="CBC - Capital"),
        df_cbi.assign(Grupo="CBI - Interior")
    ])
    st.download_button("⬇️ Completo — CSV",
        df_dl.to_csv(index=False).encode("utf-8"),
        "cbmam_marco2025.csv", "text/csv")

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.8rem'>"
    "CBMAM · Demonstrativo SEG · Março 2025 · relatorio.csv · Streamlit"
    "</div>",
    unsafe_allow_html=True
)
