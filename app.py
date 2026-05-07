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
# DADOS REAIS — MARÇO 2025 e MARÇO 2026
# ─────────────────────────────────────────────

# ── MARÇO 2025 ────────────────────────────────
CBC_2025 = [
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

CBI_2025 = [
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
CBC_2026 = [
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

# Total CBC 2026 = 7.844h conforme dashboard
# CBI 2026 = 4.231h conforme dashboard
# Total = 12.075h

CBI_2026 = [
    {"OBM": "CBI",                          "Horas": 0},
    {"OBM": "1º CIBM - Itacoatiara",        "Horas": 0},
    {"OBM": "2º CIBM - Manacapuru",         "Horas": 0},
    {"OBM": "3º CIBM - Parintins",          "Horas": 0},
    {"OBM": "1º PDBM - Iranduba",           "Horas": 0},
    {"OBM": "1º PDBM - Rio Preto da Eva",   "Horas": 0},
    {"OBM": "2º PDBM - Novo Airão",         "Horas": 0},
    {"OBM": "2º PDBM - Humaitá",            "Horas": 0},
    {"OBM": "3º PDBM - Presidente Figueiredo", "Horas": 0},
    {"OBM": "1º PIBM - Tefé",               "Horas": 0},
    {"OBM": "2º PIBM - Tabatinga",          "Horas": 0},
]

# ─────────────────────────────────────────────
# TENTA CARREGAR DO CSV/EXCEL (dinâmico)
# ─────────────────────────────────────────────
URL_CSV = "https://raw.githubusercontent.com/AllanCardosoDev/seg/main/relatorio.csv"
ARQUIVO_XLSX = "1_Relatrio_GRAFICOS_3.xlsx"

@st.cache_data
def carregar_csv():
    for enc in ["utf-8", "utf-8-sig", "latin-1"]:
        try:
            df = pd.read_csv(URL_CSV, encoding=enc, header=None, sep=None, engine="python")
            primeira = str(df.iloc[0, 0]).strip().lower()
            if not primeira.lstrip("-").isnumeric():
                df = df.iloc[1:].reset_index(drop=True)
            if df.shape[1] >= 5:
                df.columns = ["NUM", "NOME", "GUERRA", "OBM", "HORAS"] + [f"x{i}" for i in range(df.shape[1]-5)]
            elif df.shape[1] == 4:
                df.columns = ["NUM", "NOME", "OBM", "HORAS"]
            elif df.shape[1] == 3:
                df.columns = ["NOME", "OBM", "HORAS"]
            df.dropna(how="all", inplace=True)
            df.reset_index(drop=True, inplace=True)
            return df
        except Exception:
            continue
    return None

@st.cache_data
def carregar_xlsx_aba(arquivo, aba):
    try:
        df = pd.read_excel(arquivo, sheet_name=aba, header=None)
        df.dropna(how="all", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception:
        return None

def agrupar_por_obm(df, col_obm, col_horas):
    df[col_horas] = pd.to_numeric(df[col_horas], errors="coerce").fillna(0)
    df = df[df[col_obm].astype(str).str.strip().ne("")]
    df = df[df[col_obm].notna()]
    result = (
        df.groupby(col_obm)[col_horas]
        .sum().reset_index()
        .rename(columns={col_obm: "OBM", col_horas: "Horas"})
    )
    result["OBM"] = result["OBM"].astype(str).str.strip()
    result = result[~result["OBM"].str.lower().isin(["nan","none","","total"])]
    result = result[~result["OBM"].str.isnumeric()]
    return result

CBC_LISTA = [
    "1° BI","1º BI","1 BI","BBE","BIFMA","COBOM",
    "DAT","GRAPH","PGGM","QCG","SCI","CMCB","CMCBM","CBC","CBCM"
]

def is_cbc(nome):
    n = str(nome).upper().strip()
    return any(c.upper() in n for c in CBC_LISTA)

def separar_cbc_cbi(df_obm):
    mask = df_obm["OBM"].apply(is_cbc)
    cbc  = df_obm[mask].sort_values("Horas", ascending=False).reset_index(drop=True)
    cbi  = df_obm[~mask].sort_values("Horas", ascending=False).reset_index(drop=True)
    return cbc, cbi

# ─────────────────────────────────────────────
# SIDEBAR — seleção de período
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("### Período")
    st.markdown("---")

    periodo = st.radio(
        "Selecione o mês de referência:",
        options=["📅 Março 2025", "📅 Março 2026"],
        index=1  # padrão: 2026
    )

    st.markdown("---")
    st.markdown("**📁 Fonte**")
    st.markdown("[github.com/AllanCardosoDev/seg](https://github.com/AllanCardosoDev/seg)")

# ─────────────────────────────────────────────
# CARREGA DADOS DO PERÍODO SELECIONADO
# ─────────────────────────────────────────────
if periodo == "📅 Março 2025":
    periodo_label = "MARÇO 2025"

    # Tenta carregar do CSV dinâmico
    df_csv = carregar_csv()
    if df_csv is not None and "OBM" in df_csv.columns and "HORAS" in df_csv.columns:
        df_obm_raw = agrupar_por_obm(df_csv, "OBM", "HORAS")
        df_cbc, df_cbi = separar_cbc_cbi(df_obm_raw)
        if df_cbc.empty:
            df_cbc = pd.DataFrame(CBC_2025)
        if df_cbi.empty:
            df_cbi = pd.DataFrame(CBI_2025)
    else:
        df_cbc = pd.DataFrame(CBC_2025)
        df_cbi = pd.DataFrame(CBI_2025)

else:
    periodo_label = "MARÇO 2026"

    # Tenta carregar da aba MILITARES MARÇO 3 do Excel
    df_xlsx = carregar_xlsx_aba(ARQUIVO_XLSX, "MILITARES MARÇO 3")
    if df_xlsx is not None and df_xlsx.shape[1] >= 4:
        # Nomeia colunas pela estrutura real
        if df_xlsx.shape[1] >= 5:
            df_xlsx.columns = ["NUM","NOME","GUERRA","OBM","HORAS"] + [f"x{i}" for i in range(df_xlsx.shape[1]-5)]
        else:
            df_xlsx.columns = ["NUM","NOME","OBM","HORAS"] + [f"x{i}" for i in range(df_xlsx.shape[1]-4)]

        # Pula linhas sem número válido na primeira coluna
        df_xlsx = df_xlsx[pd.to_numeric(df_xlsx["NUM"], errors="coerce").notna()]

        df_obm_raw = agrupar_por_obm(df_xlsx, "OBM", "HORAS")
        df_cbc, df_cbi = separar_cbc_cbi(df_obm_raw)

        if df_cbc.empty:
            df_cbc = pd.DataFrame(CBC_2026)
        if df_cbi.empty:
            df_cbi = pd.DataFrame(CBI_2026)
    else:
        df_cbc = pd.DataFrame(CBC_2026)
        df_cbi = pd.DataFrame(CBI_2026)

# ─────────────────────────────────────────────
# GARANTE TIPOS E ORDENA
# ─────────────────────────────────────────────
df_cbc["Horas"] = pd.to_numeric(df_cbc["Horas"], errors="coerce").fillna(0)
df_cbi["Horas"] = pd.to_numeric(df_cbi["Horas"], errors="coerce").fillna(0)
df_cbc = df_cbc.sort_values("Horas", ascending=False).reset_index(drop=True)
df_cbi = df_cbi.sort_values("Horas", ascending=False).reset_index(drop=True)

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

df_comp_cbc = pd.DataFrame([
    {"OBM": r["OBM"], "Horas": r["Horas"], "Período": "Março 2025"}
    for r in CBC_2025
] + [
    {"OBM": r["OBM"], "Horas": r["Horas"], "Período": "Março 2026"}
    for r in CBC_2026
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
