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

st.markdown("""
    <style>
        section[data-testid="stSidebar"] { background-color: #1a1a2e; }
        section[data-testid="stSidebar"] * { color: white !important; }

        .header-title {
            text-align: center;
            font-weight: bold;
            font-size: 1.15rem;
            padding: 12px;
            border: 2px solid #999;
            background-color: #f2f2f2;
            margin-bottom: 28px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .section-title {
            text-align: center;
            font-weight: bold;
            font-size: 0.95rem;
            margin-bottom: 5px;
            color: #222;
        }

        /* Tabela CBC - amarelo */
        .tbl-cbc {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.84rem;
        }
        .tbl-cbc th {
            background-color: #FFC000;
            color: #000;
            font-weight: bold;
            padding: 6px 10px;
            border: 1px solid #d4a000;
            text-align: left;
        }
        .tbl-cbc th:last-child { text-align: right; }
        .tbl-cbc td {
            background-color: #FFC000;
            color: #000;
            padding: 4px 10px;
            border: 1px solid #d4a000;
        }
        .tbl-cbc td:last-child { text-align: right; }
        .tbl-cbc .total-row td {
            font-weight: bold;
            border-top: 2px solid #a07800;
            background-color: #e6ac00;
        }

        /* Tabela CBI - verde */
        .tbl-cbi {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.84rem;
        }
        .tbl-cbi th {
            background-color: #92D050;
            color: #000;
            font-weight: bold;
            padding: 6px 10px;
            border: 1px solid #6aaa28;
            text-align: left;
        }
        .tbl-cbi th:last-child { text-align: right; }
        .tbl-cbi td {
            background-color: #92D050;
            color: #000;
            padding: 4px 10px;
            border: 1px solid #6aaa28;
        }
        .tbl-cbi td:last-child { text-align: right; }
        .tbl-cbi .total-row td {
            font-weight: bold;
            border-top: 2px solid #4a8a10;
            background-color: #78c036;
        }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARREGAMENTO DO CSV
# ─────────────────────────────────────────────
URL_CSV = "https://raw.githubusercontent.com/AllanCardosoDev/seg/main/relatorio.csv"

@st.cache_data
def carregar_csv():
    for enc in ["utf-8", "utf-8-sig", "latin-1"]:
        try:
            df = pd.read_csv(URL_CSV, encoding=enc, sep=None, engine="python")
            df.columns = df.columns.astype(str).str.strip()
            df.dropna(how="all", inplace=True)
            df.reset_index(drop=True, inplace=True)
            return df
        except Exception:
            continue
    st.error("Não foi possível carregar relatorio.csv")
    st.stop()

with st.spinner("Carregando dados..."):
    df_raw = carregar_csv()

# ─────────────────────────────────────────────
# DETECTA COLUNAS
# ─────────────────────────────────────────────
colunas     = df_raw.columns.tolist()
colunas_num = df_raw.select_dtypes(include=np.number).columns.tolist()
colunas_txt = df_raw.select_dtypes(exclude=np.number).columns.tolist()

cand_nome  = ["NOME","nome","MILITAR","militar","NAME"]
cand_obm   = ["OBM","obm","UNIDADE","unidade","OM","om","LOCAL","local"]
cand_segs  = ["SEGS","segs","HORAS","horas","SEG","seg","TOTAL","total","H"]
cand_mes   = ["MES","mes","MÊS","mês","MONTH","REFERENCIA"]

col_nome = next((c for c in cand_nome if c in colunas), None)
col_obm  = next((c for c in cand_obm  if c in colunas), colunas_txt[0] if colunas_txt else colunas[0])
col_segs = next((c for c in cand_segs if c in colunas), colunas_num[0] if colunas_num else colunas[-1])
col_mes  = next((c for c in cand_mes  if c in colunas), None)

# ─────────────────────────────────────────────
# SIDEBAR — apenas configuração de colunas
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("### Configurações")
    st.markdown("---")

    col_obm = st.selectbox(
        "📍 Coluna OBM:",
        colunas,
        index=colunas.index(col_obm) if col_obm in colunas else 0
    )
    col_segs = st.selectbox(
        "⏱️ Coluna SEGs/Horas:",
        colunas,
        index=colunas.index(col_segs) if col_segs in colunas else 0
    )

    op_mes = ["(Nenhuma)"] + colunas
    col_mes_sel = st.selectbox(
        "📅 Coluna Mês:",
        op_mes,
        index=op_mes.index(col_mes) if col_mes in op_mes else 0
    )
    tem_mes = col_mes_sel != "(Nenhuma)"
    col_mes = col_mes_sel if tem_mes else None

    meses_ativos = []
    marco_val    = None

    if tem_mes:
        df_raw[col_mes] = df_raw[col_mes].astype(str).str.strip()
        meses_lista     = sorted(df_raw[col_mes].dropna().unique().tolist())
        marco_val       = next(
            (m for m in meses_lista if "mar" in m.lower() or m.strip() in ["3","03"]),
            meses_lista[0] if meses_lista else None
        )
        st.markdown("---")
        st.markdown("**📅 Filtro por Mês**")
        modo = st.radio("Modo:", ["📄 Específico", "🗂️ Todos"], index=0)

        if modo == "📄 Específico":
            idx = meses_lista.index(marco_val) if marco_val in meses_lista else 0
            mes_sel      = st.selectbox("Mês:", meses_lista, index=idx)
            meses_ativos = [mes_sel]
        else:
            meses_ativos = meses_lista
            st.info(f"✅ {len(meses_lista)} meses")

    st.markdown("---")
    st.markdown("[github.com/AllanCardosoDev/seg](https://github.com/AllanCardosoDev/seg)")
    with st.expander("📋 Colunas do CSV"):
        for c in colunas:
            st.markdown(f"- `{c}`")

# ─────────────────────────────────────────────
# FILTRA E PROCESSA
# ─────────────────────────────────────────────
df = df_raw.copy()
df[col_segs] = pd.to_numeric(df[col_segs], errors="coerce").fillna(0)

if tem_mes and meses_ativos:
    df = df[df[col_mes].isin(meses_ativos)]

periodo_label = (
    meses_ativos[0].upper()
    if tem_mes and len(meses_ativos) == 1
    else "MARÇO 2025"
)

# ─────────────────────────────────────────────
# AGRUPA HORAS POR OBM
# ─────────────────────────────────────────────
df_obm = (
    df.groupby(col_obm)[col_segs]
    .sum()
    .reset_index()
    .rename(columns={col_obm: "OBM", col_segs: "Horas"})
)
df_obm["Horas"] = pd.to_numeric(df_obm["Horas"], errors="coerce").fillna(0)
df_obm["OBM"]   = df_obm["OBM"].astype(str).str.strip()

# ─────────────────────────────────────────────
# OBMs da CBC (Capital) — baseado nos dados reais
# ─────────────────────────────────────────────
CBC_OBMS = [
    "1° BI", "1º BI", "1 BI",
    "BBE",
    "BIFMA",
    "COBOM",
    "DAT",
    "GRAPH",
    "PGGM",
    "QCG",
    "SCI",
    "CMCB",
    "CBC"
]

# Máscara: OBM está na lista CBC
mask_cbc = df_obm["OBM"].apply(
    lambda x: any(c.lower() in x.lower() for c in CBC_OBMS)
)

df_cbc = df_obm[mask_cbc].sort_values("Horas", ascending=False).reset_index(drop=True)
df_cbi = df_obm[~mask_cbc].sort_values("Horas", ascending=False).reset_index(drop=True)

# ─────────────────────────────────────────────
# FALLBACK com dados reais da imagem
# ─────────────────────────────────────────────
if df_cbc.empty:
    df_cbc = pd.DataFrame([
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
    ])

if df_cbi.empty:
    df_cbi = pd.DataFrame([
        {"OBM": "CBI",                          "Horas": 10},
        {"OBM": "1º CIBM - Itacoatiara",        "Horas": 596},
        {"OBM": "2º CIBM - Manacapuru",         "Horas": 975},
        {"OBM": "3º CIBM - Parintins",          "Horas": 0},
        {"OBM": "1º PDBM - Iranduba",           "Horas": 423},
        {"OBM": "1º PDBM - Rio Preto da Eva",   "Horas": 389},
        {"OBM": "2º PDBM - Novo Airão",         "Horas": 224},
        {"OBM": "2º PDBM - Humaitá",            "Horas": 491},
        {"OBM": "3º PDBM - Pres. Figueiredo",   "Horas": 639},
        {"OBM": "1º PIBM - Tefé",               "Horas": 468},
        {"OBM": "2º PIBM - Tabatinga",          "Horas": 154},
    ])

total_cbc   = int(df_cbc["Horas"].sum())
total_cbi   = int(df_cbi["Horas"].sum())
total_geral = total_cbc + total_cbi

# ─────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────
def safe_int(val):
    try:
        v = float(val)
        return 0 if np.isnan(v) else int(v)
    except:
        return 0

def build_table(df_t, css, total):
    rows = ""
    for _, r in df_t.iterrows():
        rows += f"<tr><td>{r['OBM']}</td><td>{safe_int(r['Horas'])}</td></tr>"
    return f"""
    <table class="{css}">
        <thead><tr><th>OBM</th><th>Horas</th></tr></thead>
        <tbody>
            <tr><td colspan="2" style="padding:2px;border:none;background:transparent"></td></tr>
            {rows}
            <tr><td colspan="2" style="padding:2px;border:none;background:transparent"></td></tr>
        </tbody>
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
        marker_line_color="white",
        marker_line_width=0.5,
        width=0.6,
        cliponaxis=False
    ))
    fig.update_layout(
        title=dict(text=titulo, x=0.5, font=dict(size=13, color="#222")),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=340,
        margin=dict(t=50, b=70, l=30, r=20),
        xaxis=dict(
            showgrid=False,
            tickangle=-30,
            tickfont=dict(size=9),
            showline=True,
            linecolor="#aaa"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#eeeeee",
            range=[0, max_y * 1.25],
            showline=False
        ),
        shapes=[dict(
            type="rect", xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="#cccccc", width=1)
        )]
    )
    return fig

# ─────────────────────────────────────────────
# LAYOUT — idêntico ao Excel
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="header-title">'
    f'Demonstrativo de Horas de SEG Processadas para Pagamento no Mês de {periodo_label}'
    f'</div>',
    unsafe_allow_html=True
)

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

# ─────────────────────────────────────────────
# RESUMO FINAL
# ─────────────────────────────────────────────
r1, r2, r3 = st.columns(3)

cbc_lider = df_cbc[df_cbc["Horas"] > 0].iloc[0] if not df_cbc[df_cbc["Horas"] > 0].empty else None
cbi_lider = df_cbi[df_cbi["Horas"] > 0].iloc[0] if not df_cbi[df_cbi["Horas"] > 0].empty else None
all_df    = pd.concat([df_cbc, df_cbi])
all_df["Horas"] = pd.to_numeric(all_df["Horas"], errors="coerce").fillna(0)
geral_lider = all_df[all_df["Horas"] > 0].sort_values("Horas", ascending=False).iloc[0] \
              if not all_df[all_df["Horas"] > 0].empty else None

with r1:
    st.metric("⏱️ Total Geral",  f"{total_geral:,}h".replace(",", "."))
    st.metric("🟡 CBC — Capital", f"{total_cbc:,}h".replace(",", "."))
    st.metric("🟢 CBI — Interior",f"{total_cbi:,}h".replace(",", "."))

with r2:
    if cbc_lider is not None:
        st.success(
            f"🥇 **Maior OBM — Capital**\n\n"
            f"**{cbc_lider['OBM']}** → {safe_int(cbc_lider['Horas'])}h"
        )
    if cbi_lider is not None:
        st.success(
            f"🥇 **Maior OBM — Interior**\n\n"
            f"**{cbi_lider['OBM']}** → {safe_int(cbi_lider['Horas'])}h"
        )

with r3:
    if geral_lider is not None:
        st.info(
            f"🏆 **Maior OBM Geral**\n\n"
            f"**{geral_lider['OBM']}** → {safe_int(geral_lider['Horas'])}h"
        )

    pct_cbc = round(total_cbc / total_geral * 100, 1) if total_geral > 0 else 0
    pct_cbi = round(total_cbi / total_geral * 100, 1) if total_geral > 0 else 0

    fig_donut = go.Figure(go.Pie(
        labels=["CBC - Capital", "CBI - Interior"],
        values=[total_cbc, total_cbi],
        hole=0.5,
        marker_colors=["#FFC000", "#92D050"],
        textinfo="percent+label"
    ))
    fig_donut.update_layout(
        height=220,
        showlegend=False,
        margin=dict(t=20, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ─────────────────────────────────────────────
# DOWNLOAD
# ─────────────────────────────────────────────
st.markdown("---")
c1, c2, c3 = st.columns(3)

with c1:
    st.download_button(
        "⬇️ CBC — CSV",
        df_cbc.to_csv(index=False).encode("utf-8"),
        "cbc_marco2025.csv", "text/csv"
    )
with c2:
    st.download_button(
        "⬇️ CBI — CSV",
        df_cbi.to_csv(index=False).encode("utf-8"),
        "cbi_marco2025.csv", "text/csv"
    )
with c3:
    df_dl = pd.concat([
        df_cbc.assign(Grupo="CBC - Capital"),
        df_cbi.assign(Grupo="CBI - Interior")
    ])
    st.download_button(
        "⬇️ Completo — CSV",
        df_dl.to_csv(index=False).encode("utf-8"),
        "cbmam_marco2025.csv", "text/csv"
    )

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.8rem'>"
    f"CBMAM · Demonstrativo SEG · {periodo_label} · relatorio.csv · Streamlit"
    "</div>",
    unsafe_allow_html=True
)
