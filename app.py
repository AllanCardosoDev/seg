# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ─────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CBMAM — SEGs Março 2025",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        section[data-testid="stSidebar"] { background-color: #1a1a2e; }
        section[data-testid="stSidebar"] * { color: white !important; }

        .titulo-principal {
            font-size: 1.3rem;
            font-weight: bold;
            text-align: center;
            padding: 12px;
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            margin-bottom: 20px;
        }
        .titulo-cbc {
            font-size: 1rem;
            font-weight: bold;
            text-align: center;
            color: #333;
            margin-bottom: 6px;
        }
        .titulo-cbi {
            font-size: 1rem;
            font-weight: bold;
            text-align: center;
            color: #333;
            margin-bottom: 6px;
        }

        /* Tabela amarela CBC */
        .tabela-cbc thead tr th {
            background-color: #FFC000 !important;
            color: black !important;
            font-weight: bold;
        }
        .tabela-cbc tbody tr td {
            background-color: #FFC000 !important;
            color: black !important;
        }
        .tabela-cbc tfoot tr td {
            background-color: #FFC000 !important;
            font-weight: bold;
            color: black !important;
        }

        /* Tabela verde CBI */
        .tabela-cbi thead tr th {
            background-color: #92D050 !important;
            color: black !important;
            font-weight: bold;
        }
        .tabela-cbi tbody tr td {
            background-color: #92D050 !important;
            color: black !important;
        }
        .tabela-cbi tfoot tr td {
            background-color: #92D050 !important;
            font-weight: bold;
            color: black !important;
        }

        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 5px 10px; text-align: left; font-size: 0.88rem; }
        td:last-child, th:last-child { text-align: right; }
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

cand_obm   = ["OBM", "obm", "UNIDADE", "LOCAL", "OM", "om", "unidade", "local"]
col_obm    = next((c for c in cand_obm if c in colunas), colunas_txt[0] if colunas_txt else colunas[0])

cand_segs  = ["SEGS", "segs", "HORAS", "horas", "SEG", "TOTAL", "total"]
col_segs   = next((c for c in cand_segs if c in colunas), colunas_num[0] if colunas_num else colunas[-1])

cand_grupo = ["GRUPO", "grupo", "COMANDO", "CBC_CBI", "TIPO", "REGIAO", "regiao"]
col_grupo  = next((c for c in cand_grupo if c in colunas), None)

cand_mes   = ["MES", "mes", "MÊS", "mês", "MONTH"]
col_mes    = next((c for c in cand_mes if c in colunas), None)

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

    opcoes_grupo = ["(Nenhuma)"] + colunas
    col_grupo_sel = st.selectbox("🏷️ Coluna de Grupo (CBC/CBI):",
                                 opcoes_grupo,
                                 index=opcoes_grupo.index(col_grupo) if col_grupo in opcoes_grupo else 0)
    tem_grupo = col_grupo_sel != "(Nenhuma)"
    col_grupo = col_grupo_sel if tem_grupo else None

    opcoes_mes = ["(Nenhuma)"] + colunas
    col_mes_sel = st.selectbox("📅 Coluna de Mês:",
                               opcoes_mes,
                               index=opcoes_mes.index(col_mes) if col_mes in opcoes_mes else 0)
    tem_mes = col_mes_sel != "(Nenhuma)"
    col_mes = col_mes_sel if tem_mes else None

    st.markdown("---")

    # Filtro por mês
    if tem_mes:
        df_raw[col_mes]  = df_raw[col_mes].astype(str).str.strip()
        meses_lista      = sorted(df_raw[col_mes].dropna().unique().tolist())
        marco_val        = next(
            (m for m in meses_lista if "mar" in m.lower() or m.strip() in ["3","03"]),
            meses_lista[0] if meses_lista else None
        )

        st.markdown("**📅 Filtro por Mês**")
        modo_mes = st.radio("Modo:", ["📄 Mês específico", "📚 Múltiplos", "🗂️ Todos"], index=0)

        if modo_mes == "📄 Mês específico":
            idx = meses_lista.index(marco_val) if marco_val in meses_lista else 0
            mes_unico    = st.selectbox("Mês:", meses_lista, index=idx)
            meses_ativos = [mes_unico]
        elif modo_mes == "📚 Múltiplos":
            meses_ativos = st.multiselect("Meses:", meses_lista,
                                          default=[marco_val] if marco_val else meses_lista[:1])
            if not meses_ativos:
                meses_ativos = meses_lista
        else:
            meses_ativos = meses_lista
            st.info(f"✅ {len(meses_lista)} meses")
    else:
        meses_ativos = []
        marco_val    = None

    st.markdown("---")
    top_n = st.slider("🏆 Top N OBMs", 3, 30, 10)

    st.markdown("---")
    st.markdown("**📁 Fonte**")
    st.markdown("[github.com/AllanCardosoDev/seg](https://github.com/AllanCardosoDev/seg)")

    with st.expander("📋 Colunas do CSV"):
        for c in colunas:
            st.markdown(f"- `{c}`")

# ─────────────────────────────────────────────
# PREPARA DADOS
# ─────────────────────────────────────────────
df = df_raw.copy()
df[col_segs] = pd.to_numeric(df[col_segs], errors="coerce")
df = df.dropna(subset=[col_segs])

if tem_mes and meses_ativos:
    df = df[df[col_mes].isin(meses_ativos)]

# Título do período
if tem_mes and len(meses_ativos) == 1:
    periodo_label = meses_ativos[0].upper()
else:
    periodo_label = "PERÍODO SELECIONADO"

# ─────────────────────────────────────────────
# SEPARA CBC E CBI
# ─────────────────────────────────────────────
# Se tiver coluna de grupo, usa ela; senão tenta detectar pelo nome da OBM
if tem_grupo:
    df[col_grupo] = df[col_grupo].astype(str).str.strip()
    cbc_keywords  = ["CBC", "Capital", "capital", "CBC - Capital"]
    cbi_keywords  = ["CBI", "Interior", "interior", "CBI - Interior"]

    df_cbc = df[df[col_grupo].str.contains("|".join(cbc_keywords), case=False, na=False)]
    df_cbi = df[df[col_grupo].str.contains("|".join(cbi_keywords), case=False, na=False)]
else:
    # Detecta pelo nome da OBM
    obms_interior  = ["CIBM", "PDBM", "PIBM", "CBI", "Itacoatiara", "Manacapuru",
                      "Parintins", "Iranduba", "Novo Airão", "Humaitá",
                      "Presidente Figueiredo", "Tefé", "Tabatinga", "Rio Preto"]
    mask_cbi = df[col_obm].astype(str).str.contains(
        "|".join(obms_interior), case=False, na=False
    )
    df_cbc = df[~mask_cbi]
    df_cbi = df[mask_cbi]

# Agrupa por OBM
def agrupar(df_g):
    return (
        df_g.groupby(col_obm)[col_segs]
        .sum()
        .reset_index()
        .rename(columns={col_obm: "OBM", col_segs: "Horas"})
        .sort_values("Horas", ascending=False)
        .reset_index(drop=True)
    )

df_cbc_rank = agrupar(df_cbc)
df_cbi_rank = agrupar(df_cbi)

total_cbc = int(df_cbc_rank["Horas"].sum())
total_cbi = int(df_cbi_rank["Horas"].sum())
total_geral = total_cbc + total_cbi

# ─────────────────────────────────────────────
# CABEÇALHO — replica estilo do Excel
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="titulo-principal">'
    f'DEMONSTRATIVO DE HORAS DE SEG PROCESSADAS PARA PAGAMENTO NO MÊS DE {periodo_label}'
    f'</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# KPIs rápidos
# ─────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("⏱️ Total Geral de SEGs", f"{total_geral:,}".replace(",", "."))
k2.metric("🟡 CBC — Capital",        f"{total_cbc:,}".replace(",", "."))
k3.metric("🟢 CBI — Interior",       f"{total_cbi:,}".replace(",", "."))
k4.metric("🏢 Total de OBMs",        df[col_obm].nunique())

st.markdown("---")

# ─────────────────────────────────────────────
# BLOCO PRINCIPAL: tabelas + gráficos
# estilo idêntico ao print do Excel
# ─────────────────────────────────────────────

# ── LINHA 1: CBC ─────────────────────────────
col_tab_cbc, col_graf_cbc = st.columns([1, 2])

with col_tab_cbc:
    st.markdown('<div class="titulo-cbc">CBC - Comando de Bombeiros da Capital</div>',
                unsafe_allow_html=True)

    # Monta HTML da tabela amarela
    linhas_cbc = ""
    for _, row in df_cbc_rank.iterrows():
        linhas_cbc += f"<tr><td>{row['OBM']}</td><td>{int(row['Horas']):,}".replace(",", ".") + "</td></tr>"

    tabela_cbc_html = f"""
    <table class="tabela-cbc">
        <thead><tr><th>OBM</th><th>Horas</th></tr></thead>
        <tbody>{linhas_cbc}</tbody>
        <tfoot><tr><td>Total</td><td>{total_cbc:,}</td></tr></tfoot>
    </table>
    """.replace(",", ".")
    st.markdown(tabela_cbc_html, unsafe_allow_html=True)

with col_graf_cbc:
    st.markdown('<div class="titulo-cbc">Distribuição SEG - Capital</div>',
                unsafe_allow_html=True)

    fig_cbc = px.bar(
        df_cbc_rank,
        x="OBM",
        y="Horas",
        text="Horas",
        color_discrete_sequence=["#4472C4"]
    )
    fig_cbc.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        marker_line_color="white",
        marker_line_width=0.5
    )
    fig_cbc.update_layout(
        height=320,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        xaxis=dict(title="", tickangle=-15, showgrid=False),
        yaxis=dict(title="", showgrid=True, gridcolor="#eeeeee"),
        margin=dict(t=20, b=20, l=10, r=10),
        bargap=0.3
    )
    # Borda ao redor do gráfico
    fig_cbc.update_layout(
        shapes=[dict(
            type="rect", xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="#cccccc", width=1)
        )]
    )
    st.plotly_chart(fig_cbc, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── LINHA 2: CBI ─────────────────────────────
col_tab_cbi, col_graf_cbi = st.columns([1, 2])

with col_tab_cbi:
    st.markdown('<div class="titulo-cbi">CBI - Comando de Bombeiros do Interior</div>',
                unsafe_allow_html=True)

    linhas_cbi = ""
    for _, row in df_cbi_rank.iterrows():
        linhas_cbi += f"<tr><td>{row['OBM']}</td><td>{int(row['Horas']):,}".replace(",", ".") + "</td></tr>"

    tabela_cbi_html = f"""
    <table class="tabela-cbi">
        <thead><tr><th>OBM</th><th>Horas</th></tr></thead>
        <tbody>{linhas_cbi}</tbody>
        <tfoot><tr><td>Total</td><td>{total_cbi:,}</td></tr></tfoot>
    </table>
    """.replace(",", ".")
    st.markdown(tabela_cbi_html, unsafe_allow_html=True)

with col_graf_cbi:
    st.markdown('<div class="titulo-cbi">Distribuição SEG - Interior</div>',
                unsafe_allow_html=True)

    fig_cbi = px.bar(
        df_cbi_rank,
        x="OBM",
        y="Horas",
        text="Horas",
        color_discrete_sequence=["#4472C4"]
    )
    fig_cbi.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        marker_line_color="white",
        marker_line_width=0.5
    )
    fig_cbi.update_layout(
        height=320,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        xaxis=dict(title="", tickangle=-30, showgrid=False),
        yaxis=dict(title="", showgrid=True, gridcolor="#eeeeee"),
        margin=dict(t=20, b=20, l=10, r=10),
        bargap=0.3
    )
    fig_cbi.update_layout(
        shapes=[dict(
            type="rect", xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="#cccccc", width=1)
        )]
    )
    st.plotly_chart(fig_cbi, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# GRÁFICO COMBINADO (bônus)
# ─────────────────────────────────────────────
st.subheader("📊 Visão Geral — CBC + CBI Comparativo")

df_cbc_rank["Grupo"] = "CBC - Capital"
df_cbi_rank["Grupo"] = "CBI - Interior"
df_combined = pd.concat([df_cbc_rank, df_cbi_rank], ignore_index=True)

fig_combined = px.bar(
    df_combined,
    x="OBM",
    y="Horas",
    color="Grupo",
    text="Horas",
    barmode="group",
    color_discrete_map={
        "CBC - Capital":  "#FFC000",
        "CBI - Interior": "#92D050"
    },
    title=f"SEGs por OBM — {periodo_label}"
)
fig_combined.update_traces(texttemplate="%{text:,}", textposition="outside")
fig_combined.update_layout(
    height=400,
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(tickangle=-30),
    yaxis=dict(showgrid=True, gridcolor="#eeeeee"),
    legend_title="Comando"
)
st.plotly_chart(fig_combined, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# TABELA RESUMO FINAL
# ─────────────────────────────────────────────
st.subheader("📋 Resumo Consolidado")

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    st.markdown("**🟡 CBC — Capital**")
    df_cbc_exib = df_cbc_rank.copy()
    df_cbc_exib.index += 1
    st.dataframe(df_cbc_exib, use_container_width=True, height=320)
    st.markdown(f"**Total: {total_cbc:,}**".replace(",", "."))

with col_r2:
    st.markdown("**🟢 CBI — Interior**")
    df_cbi_exib = df_cbi_rank.copy()
    df_cbi_exib.index += 1
    st.dataframe(df_cbi_exib, use_container_width=True, height=320)
    st.markdown(f"**Total: {total_cbi:,}**".replace(",", "."))

with col_r3:
    st.markdown("**📊 Estatísticas Gerais**")
    st.metric("Total CBC + CBI",  f"{total_geral:,}".replace(",", "."))
    st.metric("Maior OBM (CBC)",
              df_cbc_rank.iloc[0]["OBM"] if not df_cbc_rank.empty else "—",
              f"{int(df_cbc_rank.iloc[0]['Horas']):,}h".replace(",", ".") if not df_cbc_rank.empty else "")
    st.metric("Maior OBM (CBI)",
              df_cbi_rank.iloc[0]["OBM"] if not df_cbi_rank.empty else "—",
              f"{int(df_cbi_rank.iloc[0]['Horas']):,}h".replace(",", ".") if not df_cbi_rank.empty else "")

    pct_cbc = round(total_cbc / total_geral * 100, 1) if total_geral > 0 else 0
    pct_cbi = round(total_cbi / total_geral * 100, 1) if total_geral > 0 else 0

    fig_donut = px.pie(
        values=[total_cbc, total_cbi],
        names=["CBC - Capital", "CBI - Interior"],
        hole=0.5,
        color_discrete_sequence=["#FFC000", "#92D050"],
        title="CBC vs CBI"
    )
    fig_donut.update_traces(textinfo="percent+label")
    fig_donut.update_layout(height=240, showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_donut, use_container_width=True)

# ─────────────────────────────────────────────
# DOWNLOAD
# ─────────────────────────────────────────────
st.markdown("---")
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    csv_cbc = df_cbc_rank.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar CBC (CSV)", csv_cbc, "cbc_marco.csv", "text/csv")
with col_dl2:
    csv_cbi = df_cbi_rank.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar CBI (CSV)", csv_cbi, "cbi_marco.csv", "text/csv")

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.82rem'>"
    f"CBMAM · Demonstrativo de SEGs · {periodo_label} · relatorio.csv · Python + Streamlit"
    "</div>",
    unsafe_allow_html=True
)
