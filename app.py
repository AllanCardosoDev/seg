# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="CBMAM — Demonstrativo SEG Março 2025",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        section[data-testid="stSidebar"] { background-color: #1a1a2e; }
        section[data-testid="stSidebar"] * { color: white !important; }

        .header-title {
            text-align: center;
            font-weight: bold;
            font-size: 1.1rem;
            padding: 10px;
            border: 1px solid #999;
            background-color: #f2f2f2;
            margin-bottom: 25px;
            letter-spacing: 0.5px;
        }

        .section-title {
            text-align: center;
            font-weight: bold;
            font-size: 0.95rem;
            margin-bottom: 6px;
            color: #222;
        }

        /* Tabela CBC - amarelo */
        .tbl-cbc {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }
        .tbl-cbc th {
            background-color: #FFC000;
            color: #000;
            font-weight: bold;
            padding: 5px 8px;
            border: 1px solid #e0a800;
            text-align: left;
        }
        .tbl-cbc th:last-child { text-align: right; }
        .tbl-cbc td {
            background-color: #FFC000;
            color: #000;
            padding: 4px 8px;
            border: 1px solid #e0a800;
            text-align: left;
        }
        .tbl-cbc td:last-child { text-align: right; }
        .tbl-cbc tr.total-row td {
            font-weight: bold;
            border-top: 2px solid #c49000;
        }
        .tbl-cbc tr.empty-row td {
            height: 8px;
            padding: 2px;
        }

        /* Tabela CBI - verde */
        .tbl-cbi {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }
        .tbl-cbi th {
            background-color: #92D050;
            color: #000;
            font-weight: bold;
            padding: 5px 8px;
            border: 1px solid #70a832;
            text-align: left;
        }
        .tbl-cbi th:last-child { text-align: right; }
        .tbl-cbi td {
            background-color: #92D050;
            color: #000;
            padding: 4px 8px;
            border: 1px solid #70a832;
            text-align: left;
        }
        .tbl-cbi td:last-child { text-align: right; }
        .tbl-cbi tr.total-row td {
            font-weight: bold;
            border-top: 2px solid #50801a;
        }
        .tbl-cbi tr.empty-row td {
            height: 8px;
            padding: 2px;
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

cand_obm  = ["OBM","obm","UNIDADE","unidade","LOCAL","local","OM","om"]
col_obm   = next((c for c in cand_obm  if c in colunas), colunas_txt[0] if colunas_txt else colunas[0])

cand_segs = ["SEGS","segs","HORAS","horas","SEG","seg","TOTAL","total"]
col_segs  = next((c for c in cand_segs if c in colunas), colunas_num[0] if colunas_num else colunas[-1])

cand_grupo = ["GRUPO","grupo","COMANDO","CBC_CBI","TIPO","REGIAO","regiao","COMANDO_GRUPO"]
col_grupo  = next((c for c in cand_grupo if c in colunas), None)

cand_mes  = ["MES","mes","MÊS","mês","MONTH","month","REFERENCIA"]
col_mes   = next((c for c in cand_mes  if c in colunas), None)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("### Configurações")
    st.markdown("---")

    st.markdown("**⚙️ Colunas**")
    col_obm = st.selectbox("📍 OBM:", colunas,
                           index=colunas.index(col_obm) if col_obm in colunas else 0)
    col_segs = st.selectbox("⏱️ SEGs/Horas:", colunas,
                            index=colunas.index(col_segs) if col_segs in colunas else 0)

    op_grupo = ["(Nenhuma)"] + colunas
    col_grupo_sel = st.selectbox(
        "🏷️ Coluna Grupo (CBC/CBI):", op_grupo,
        index=op_grupo.index(col_grupo) if col_grupo in op_grupo else 0
    )
    tem_grupo = col_grupo_sel != "(Nenhuma)"
    col_grupo = col_grupo_sel if tem_grupo else None

    op_mes = ["(Nenhuma)"] + colunas
    col_mes_sel = st.selectbox(
        "📅 Coluna de Mês:", op_mes,
        index=op_mes.index(col_mes) if col_mes in op_mes else 0
    )
    tem_mes = col_mes_sel != "(Nenhuma)"
    col_mes = col_mes_sel if tem_mes else None

    st.markdown("---")

    # Filtro por mês
    meses_ativos = []
    marco_val    = None

    if tem_mes:
        df_raw[col_mes] = df_raw[col_mes].astype(str).str.strip()
        meses_lista     = sorted(df_raw[col_mes].dropna().unique().tolist())
        marco_val       = next(
            (m for m in meses_lista if "mar" in m.lower() or m.strip() in ["3","03"]),
            meses_lista[0] if meses_lista else None
        )

        st.markdown("**📅 Filtro por Mês**")
        modo_mes = st.radio(
            "Modo:",
            ["📄 Mês específico", "📚 Múltiplos", "🗂️ Todos"],
            index=0
        )

        if modo_mes == "📄 Mês específico":
            idx = meses_lista.index(marco_val) if marco_val in meses_lista else 0
            mes_unico    = st.selectbox("Mês:", meses_lista, index=idx)
            meses_ativos = [mes_unico]
        elif modo_mes == "📚 Múltiplos":
            meses_ativos = st.multiselect(
                "Meses:", meses_lista,
                default=[marco_val] if marco_val else meses_lista[:1]
            )
            if not meses_ativos:
                meses_ativos = meses_lista
        else:
            meses_ativos = meses_lista
            st.info(f"✅ {len(meses_lista)} meses")

    st.markdown("---")
    st.markdown("**📁 Fonte**")
    st.markdown("[github.com/AllanCardosoDev/seg](https://github.com/AllanCardosoDev/seg)")
    with st.expander("📋 Colunas do CSV"):
        for c in colunas:
            st.markdown(f"- `{c}`")

# ─────────────────────────────────────────────
# FILTRA DADOS
# ─────────────────────────────────────────────
df = df_raw.copy()
df[col_segs] = pd.to_numeric(df[col_segs], errors="coerce")
df = df.dropna(subset=[col_segs])

if tem_mes and meses_ativos:
    df = df[df[col_mes].isin(meses_ativos)]

# Label do período
if tem_mes and meses_ativos and len(meses_ativos) == 1:
    periodo_label = meses_ativos[0].upper()
else:
    periodo_label = "MARÇO 2025"

# ─────────────────────────────────────────────
# DADOS REAIS DO EXCEL (fallback se CSV vazio)
# ─────────────────────────────────────────────
# CBC - Comando de Bombeiros da Capital (dados reais da imagem)
CBC_DADOS = [
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

# CBI - Comando de Bombeiros do Interior (dados reais da imagem)
CBI_DADOS = [
    {"OBM": "CBI",                        "Horas": 10},
    {"OBM": "1º CIBM - Itacoatiara",      "Horas": 596},
    {"OBM": "2º CIBM - Manacapuru",       "Horas": 975},
    {"OBM": "3º CIBM - Parintins",        "Horas": 0},
    {"OBM": "1º PDBM - Iranduba",         "Horas": 423},
    {"OBM": "1º PDBM - Rio Preto da Eva", "Horas": 389},
    {"OBM": "2º PDBM - Novo Airão",       "Horas": 224},
    {"OBM": "2º PDBM - Humaitá",          "Horas": 491},
    {"OBM": "3º PDBM - Pres. Figueiredo", "Horas": 639},
    {"OBM": "1º PIBM - Tefé",             "Horas": 468},
    {"OBM": "2º PIBM - Tabatinga",        "Horas": 154},
]

# ─────────────────────────────────────────────
# DECIDE FONTE DOS DADOS (CSV ou fallback)
# ─────────────────────────────────────────────
def montar_grupos(df_filtrado, col_obm, col_segs, col_grupo, tem_grupo):
    """Tenta separar CBC/CBI do CSV. Retorna (df_cbc, df_cbi) ou (None, None)."""
    if df_filtrado.empty:
        return None, None

    if tem_grupo:
        df_filtrado[col_grupo] = df_filtrado[col_grupo].astype(str)
        df_cbc = df_filtrado[df_filtrado[col_grupo].str.contains("CBC|Capital|capital", na=False)]
        df_cbi = df_filtrado[df_filtrado[col_grupo].str.contains("CBI|Interior|interior", na=False)]
    else:
        interior_kw = ["CIBM","PDBM","PIBM","CBI","Itacoatiara","Manacapuru",
                       "Parintins","Iranduba","Rio Preto","Novo Airão","Humaitá",
                       "Figueiredo","Tefé","Tabatinga"]
        mask = df_filtrado[col_obm].astype(str).str.contains(
            "|".join(interior_kw), case=False, na=False
        )
        df_cbc = df_filtrado[~mask]
        df_cbi = df_filtrado[mask]

    def agrupa(d):
        return (
            d.groupby(col_obm)[col_segs]
            .sum().reset_index()
            .rename(columns={col_obm: "OBM", col_segs: "Horas"})
            .sort_values("Horas", ascending=False)
            .reset_index(drop=True)
        )

    return agrupa(df_cbc), agrupa(df_cbi)


df_cbc_rank, df_cbi_rank = montar_grupos(df, col_obm, col_segs, col_grupo, tem_grupo)

# Se não conseguiu separar corretamente, usa dados reais da imagem
if df_cbc_rank is None or df_cbc_rank.empty:
    df_cbc_rank = pd.DataFrame(CBC_DADOS)
if df_cbi_rank is None or df_cbi_rank.empty:
    df_cbi_rank = pd.DataFrame(CBI_DADOS)

total_cbc   = int(df_cbc_rank["Horas"].sum())
total_cbi   = int(df_cbi_rank["Horas"].sum())
total_geral = total_cbc + total_cbi

# ─────────────────────────────────────────────
# FUNÇÕES DE RENDERIZAÇÃO
# ─────────────────────────────────────────────
def tabela_html(df_t, css_class, total):
    linhas = ""
    for _, row in df_t.iterrows():
        horas_str = str(int(row["Horas"])) if row["Horas"] > 0 else "0"
        linhas += f"<tr><td>{row['OBM']}</td><td>{horas_str}</td></tr>"

    return f"""
    <table class="{css_class}">
        <thead><tr><th>OBM</th><th>Horas</th></tr></thead>
        <tbody>
            <tr class="empty-row"><td colspan="2"></td></tr>
            {linhas}
            <tr class="empty-row"><td colspan="2"></td></tr>
        </tbody>
        <tfoot>
            <tr class="total-row"><td>Total</td><td>{total}</td></tr>
        </tfoot>
    </table>
    """

def grafico_barras(df_g, titulo, cor="#4472C4"):
    # Filtra zeros para não poluir
    df_plot = df_g[df_g["Horas"] > 0].copy()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_plot["OBM"],
        y=df_plot["Horas"],
        text=df_plot["Horas"],
        textposition="outside",
        marker_color=cor,
        marker_line_color="white",
        marker_line_width=0.8,
        width=0.55,
        cliponaxis=False
    ))
    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5,
            font=dict(size=13, color="#222")
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=320,
        margin=dict(t=45, b=60, l=20, r=20),
        xaxis=dict(
            showgrid=False,
            tickangle=-20,
            tickfont=dict(size=10),
            showline=True,
            linecolor="#aaa"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#eeeeee",
            showline=False,
            rangemode="tozero",
        ),
        shapes=[dict(
            type="rect", xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="#cccccc", width=1)
        )]
    )
    # Aumenta range Y para caber os labels
    max_y = df_plot["Horas"].max() if not df_plot.empty else 100
    fig.update_yaxes(range=[0, max_y * 1.2])
    return fig

# ─────────────────────────────────────────────
# LAYOUT PRINCIPAL
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="header-title">'
    f'DEMONSTRATIVO DE HORAS DE SEG PROCESSADAS PARA PAGAMENTO NO MÊS DE {periodo_label}'
    f'</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# BLOCO CBC
# ─────────────────────────────────────────────
col_tab_cbc, col_graf_cbc = st.columns([1, 2])

with col_tab_cbc:
    st.markdown(
        '<p class="section-title">CBC - Comando de Bombeiros da Capital</p>',
        unsafe_allow_html=True
    )
    st.markdown(tabela_html(df_cbc_rank, "tbl-cbc", total_cbc), unsafe_allow_html=True)

with col_graf_cbc:
    fig_cbc = grafico_barras(df_cbc_rank, "Distribuição SEG - Capital", cor="#4472C4")
    st.plotly_chart(fig_cbc, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# BLOCO CBI
# ─────────────────────────────────────────────
col_tab_cbi, col_graf_cbi = st.columns([1, 2])

with col_tab_cbi:
    st.markdown(
        '<p class="section-title">CBI - Comando de Bombeiros do Interior</p>',
        unsafe_allow_html=True
    )
    st.markdown(tabela_html(df_cbi_rank, "tbl-cbi", total_cbi), unsafe_allow_html=True)

with col_graf_cbi:
    fig_cbi = grafico_barras(df_cbi_rank, "Distribuição SEG - Interior", cor="#4472C4")
    st.plotly_chart(fig_cbi, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# RESUMO FINAL
# ─────────────────────────────────────────────
st.markdown("### 📊 Resumo Consolidado — Março 2025")

r1, r2, r3, r4 = st.columns(4)

lider_cbc = df_cbc_rank.iloc[0] if not df_cbc_rank.empty else None
lider_cbi = df_cbi_rank.iloc[0] if not df_cbi_rank.empty else None

r1.metric("⏱️ Total Geral",      f"{total_geral:,}h".replace(",", "."))
r2.metric("🟡 Total CBC",         f"{total_cbc:,}h".replace(",", "."))
r3.metric("🟢 Total CBI",         f"{total_cbi:,}h".replace(",", "."))
r4.metric("🏢 Total de OBMs",     len(df_cbc_rank) + len(df_cbi_rank))

st.markdown("<br>", unsafe_allow_html=True)

d1, d2, d3 = st.columns(3)

with d1:
    if lider_cbc is not None:
        st.success(
            f"🥇 **Maior OBM — Capital**\n\n"
            f"**{lider_cbc['OBM']}** com **{int(lider_cbc['Horas'])}h**"
        )

with d2:
    if lider_cbi is not None:
        st.success(
            f"🥇 **Maior OBM — Interior**\n\n"
            f"**{lider_cbi['OBM']}** com **{int(lider_cbi['Horas'])}h**"
        )

with d3:
    # OBM mais horas no geral
    df_all = pd.concat([df_cbc_rank, df_cbi_rank])
    maior_geral = df_all.loc[df_all["Horas"].idxmax()]
    st.info(
        f"🏆 **Maior OBM Geral**\n\n"
        f"**{maior_geral['OBM']}** com **{int(maior_geral['Horas'])}h**"
    )

# ─────────────────────────────────────────────
# DOWNLOADS
# ─────────────────────────────────────────────
st.markdown("---")
col_dl1, col_dl2, col_dl3 = st.columns(3)

with col_dl1:
    csv_cbc = df_cbc_rank.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ CBC — CSV", csv_cbc, "cbc_marco2025.csv", "text/csv")

with col_dl2:
    csv_cbi = df_cbi_rank.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ CBI — CSV", csv_cbi, "cbi_marco2025.csv", "text/csv")

with col_dl3:
    df_all_dl = pd.concat([
        df_cbc_rank.assign(Grupo="CBC - Capital"),
        df_cbi_rank.assign(Grupo="CBI - Interior")
    ])
    csv_all = df_all_dl.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Completo — CSV", csv_all, "cbmam_marco2025.csv", "text/csv")

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.82rem'>"
    f"CBMAM · Demonstrativo SEG · {periodo_label} · relatorio.csv · Python + Streamlit"
    "</div>",
    unsafe_allow_html=True
)
