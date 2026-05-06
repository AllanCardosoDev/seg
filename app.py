# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard CBMAM - Relatório de Serviços",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .titulo-principal {
            color: #cc0000;
            font-size: 2.2rem;
            font-weight: bold;
            text-align: center;
            padding: 10px 0;
        }
        .subtitulo {
            color: #555;
            font-size: 1rem;
            text-align: center;
            margin-bottom: 20px;
        }
        section[data-testid="stSidebar"] {
            background-color: #1a1a2e;
        }
        section[data-testid="stSidebar"] * {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARREGAMENTO DOS DADOS VIA GITHUB
# ─────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    URL = "https://raw.githubusercontent.com/AllanCardosoDev/seg/main/relatorio.csv"

    try:
        df = pd.read_csv(URL, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(URL, encoding="latin-1")

    # Limpar nomes de colunas (espaços extras, etc.)
    df.columns = df.columns.str.strip()

    return df

# ─────────────────────────────────────────────
# CARREGA E INSPECIONA
# ─────────────────────────────────────────────
df_raw = carregar_dados()

# ─────────────────────────────────────────────
# DETECTA COLUNAS AUTOMATICAMENTE
# ─────────────────────────────────────────────
colunas = df_raw.columns.tolist()
colunas_numericas = df_raw.select_dtypes(include=np.number).columns.tolist()
colunas_texto = df_raw.select_dtypes(exclude=np.number).columns.tolist()

# Tenta identificar coluna de "local/unidade" automaticamente
col_local = None
for candidato in ["local", "unidade", "posto", "lugar", "nome", "Local", "Unidade", "Posto"]:
    if candidato in colunas:
        col_local = candidato
        break
if col_local is None and colunas_texto:
    col_local = colunas_texto[0]  # fallback: primeira coluna de texto

# Tenta identificar coluna de "segs/horas/quantidade" automaticamente
col_valor = None
for candidato in ["segs", "horas", "total", "quantidade", "seg", "Segs", "Horas", "Total"]:
    if candidato in colunas:
        col_valor = candidato
        break
if col_valor is None and colunas_numericas:
    col_valor = colunas_numericas[0]  # fallback: primeira coluna numérica

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("### Configurações do Dashboard")
    st.markdown("---")

    st.markdown("**📌 Coluna de Local/Unidade**")
    col_local = st.selectbox("Selecione a coluna de local:", colunas_texto, index=colunas_texto.index(col_local) if col_local in colunas_texto else 0)

    st.markdown("**📊 Coluna de Valor (segs/horas)**")
    col_valor = st.selectbox("Selecione a coluna de valor:", colunas_numericas, index=colunas_numericas.index(col_valor) if col_valor in colunas_numericas else 0)

    st.markdown("---")
    top_n = st.slider("🏆 Top N locais no ranking", min_value=3, max_value=30, value=10)

    # Filtro por coluna de texto adicional (se houver)
    filtros_ativos = {}
    if len(colunas_texto) > 1:
        st.markdown("---")
        st.markdown("**🔍 Filtros Adicionais**")
        for col in colunas_texto:
            if col != col_local:
                opcoes = ["Todos"] + sorted(df_raw[col].dropna().unique().tolist())
                escolha = st.selectbox(f"Filtrar por {col}:", opcoes)
                if escolha != "Todos":
                    filtros_ativos[col] = escolha

    st.markdown("---")
    st.markdown("**📁 Fonte dos dados**")
    st.markdown("[github.com/AllanCardosoDev/seg](https://github.com/AllanCardosoDev/seg)")

# ─────────────────────────────────────────────
# APLICA FILTROS
# ─────────────────────────────────────────────
df = df_raw.copy()
for col, val in filtros_ativos.items():
    df = df[df[col] == val]

# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────
st.markdown('<div class="titulo-principal">🚒 Dashboard CBMAM — Relatório de Serviços</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Análise completa dos locais que precisaram de mais SEGs</div>', unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
total_registros = len(df)
total_valor = df[col_valor].sum() if col_valor else 0
media_valor = df[col_valor].mean() if col_valor else 0
total_locais = df[col_local].nunique() if col_local else 0

if col_local and col_valor:
    local_lider = df.groupby(col_local)[col_valor].sum().idxmax()
    valor_lider = df.groupby(col_local)[col_valor].sum().max()
else:
    local_lider = "—"
    valor_lider = 0

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("📋 Total de Registros", f"{total_registros:,}".replace(",", "."))
with col2:
    st.metric("⏱️ Total Geral", f"{total_valor:,.0f}".replace(",", "."))
with col3:
    st.metric("📊 Média por Registro", f"{media_valor:.1f}")
with col4:
    st.metric("📍 Locais Únicos", total_locais)
with col5:
    st.metric("🏆 Local Líder", local_lider)

st.markdown("---")

# ─────────────────────────────────────────────
# ABAS
# ─────────────────────────────────────────────
aba1, aba2, aba3, aba4 = st.tabs([
    "🏆 Ranking de Locais",
    "📊 Distribuição",
    "🔥 Análise Detalhada",
    "📋 Dados Brutos"
])

# ══════════════════════════════════════════════
# ABA 1 — RANKING (LOCAIS QUE MAIS PRECISARAM DE SEGS)
# ══════════════════════════════════════════════
with aba1:
    st.subheader(f"🏆 Top {top_n} — Locais que Mais Precisaram de SEGs")

    if col_local and col_valor:
        df_rank = (
            df.groupby(col_local)[col_valor]
            .sum()
            .reset_index()
            .rename(columns={col_local: "Local", col_valor: "Total"})
            .sort_values("Total", ascending=False)
            .head(top_n)
            .reset_index(drop=True)
        )
        df_rank.index += 1

        col_g, col_t = st.columns([3, 2])

        with col_g:
            fig_bar = px.bar(
                df_rank,
                x="Total",
                y="Local",
                orientation="h",
                color="Total",
                color_continuous_scale="Reds",
                text="Total",
                title=f"Top {top_n} Locais por Total de SEGs",
                labels={"Total": "Total de SEGs", "Local": "Local"}
            )
            fig_bar.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside"
            )
            fig_bar.update_layout(
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
                height=450,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_t:
            st.markdown("#### 📋 Tabela de Ranking")
            df_rank_exib = df_rank.copy()
            df_rank_exib["Total"] = df_rank_exib["Total"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
            df_rank_exib["% do Total"] = (
                df.groupby(col_local)[col_valor].sum()
                .reindex(df_rank["Local"].values)
                .values / total_valor * 100
            )
            df_rank_exib["% do Total"] = df_rank_exib["% do Total"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(df_rank_exib, use_container_width=True, height=400)

        # Funil dos top locais
        st.markdown("---")
        st.subheader("📉 Funil de Demanda por Local")
        fig_funnel = go.Figure(go.Funnel(
            y=df_rank["Local"],
            x=df_rank["Total"],
            textinfo="value+percent initial",
            marker=dict(color=px.colors.sequential.Reds_r[:len(df_rank)])
        ))
        fig_funnel.update_layout(height=400)
        st.plotly_chart(fig_funnel, use_container_width=True)

    else:
        st.warning("Não foi possível identificar as colunas de local e valor. Use os filtros na sidebar.")

# ══════════════════════════════════════════════
# ABA 2 — DISTRIBUIÇÃO
# ══════════════════════════════════════════════
with aba2:
    st.subheader("📊 Distribuição de SEGs por Local")

    if col_local and col_valor:
        df_dist = (
            df.groupby(col_local)[col_valor]
            .sum()
            .reset_index()
            .rename(columns={col_local: "Local", col_valor: "Total"})
            .sort_values("Total", ascending=False)
        )

        col_p1, col_p2 = st.columns(2)

        with col_p1:
            fig_pie = px.pie(
                df_dist.head(15),
                names="Local",
                values="Total",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Reds_r,
                title="Distribuição % (Top 15 locais)"
            )
            fig_pie.update_traces(textinfo="percent+label")
            fig_pie.update_layout(height=420)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_p2:
            fig_treemap = px.treemap(
                df_dist,
                path=["Local"],
                values="Total",
                color="Total",
                color_continuous_scale="Reds",
                title="Treemap de SEGs por Local"
            )
            fig_treemap.update_layout(height=420)
            st.plotly_chart(fig_treemap, use_container_width=True)

        # Histograma de distribuição dos valores
        st.markdown("---")
        st.subheader("📈 Distribuição dos Valores de SEGs")
        fig_hist = px.histogram(
            df,
            x=col_valor,
            nbins=30,
            color_discrete_sequence=["#cc0000"],
            title=f"Histograma de {col_valor}"
        )
        fig_hist.update_layout(
            height=350,
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# ══════════════════════════════════════════════
# ABA 3 — ANÁLISE DETALHADA
# ══════════════════════════════════════════════
with aba3:
    st.subheader("🔥 Análise Detalhada por Colunas")

    # Estatísticas por local
    if col_local and col_valor:
        df_stats = (
            df.groupby(col_local)[col_valor]
            .agg(["sum", "mean", "max", "min", "count"])
            .reset_index()
            .rename(columns={
                col_local: "Local",
                "sum": "Total",
                "mean": "Média",
                "max": "Máximo",
                "min": "Mínimo",
                "count": "Registros"
            })
            .sort_values("Total", ascending=False)
        )

        for col_num in ["Total", "Média", "Máximo", "Mínimo"]:
            df_stats[col_num] = df_stats[col_num].round(2)

        st.dataframe(df_stats, use_container_width=True, height=350)

        st.markdown("---")

        # Boxplot se houver múltiplos registros por local
        if df.groupby(col_local).size().max() > 1:
            st.subheader("📦 Variação de SEGs por Local (Boxplot)")
            top_locais = df.groupby(col_local)[col_valor].sum().nlargest(top_n).index.tolist()
            df_box = df[df[col_local].isin(top_locais)]

            fig_box = px.box(
                df_box,
                x=col_local,
                y=col_valor,
                color=col_local,
                title=f"Distribuição de SEGs — Top {top_n} Locais",
                labels={col_local: "Local", col_valor: "SEGs"}
            )
            fig_box.update_layout(
                showlegend=False,
                height=420,
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_box, use_container_width=True)

    # Se tiver mais colunas numéricas, mostra correlação
    if len(colunas_numericas) > 1:
        st.markdown("---")
        st.subheader("🔗 Correlação entre Colunas Numéricas")
        corr = df[colunas_numericas].corr()
        fig_corr = px.imshow(
            corr,
            color_continuous_scale="RdBu",
            title="Matriz de Correlação",
            aspect="auto"
        )
        fig_corr.update_layout(height=400)
        st.plotly_chart(fig_corr, use_container_width=True)

# ══════════════════════════════════════════════
# ABA 4 — DADOS BRUTOS
# ══════════════════════════════════════════════
with aba4:
    st.subheader("📋 Dados Brutos — relatorio.csv")

    col_busca, col_info = st.columns([3, 1])
    with col_busca:
        busca = st.text_input("🔍 Buscar em qualquer coluna...")
    with col_info:
        st.metric("Total de linhas", len(df))

    df_exibir = df.copy()
    if busca:
        mask = df_exibir.apply(
            lambda row: row.astype(str).str.contains(busca, case=False, na=False).any(),
            axis=1
        )
        df_exibir = df_exibir[mask]
        st.caption(f"{len(df_exibir)} resultado(s) encontrado(s)")

    st.dataframe(df_exibir, use_container_width=True, height=400)

    # Download
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv = df_exibir.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Baixar dados filtrados (CSV)",
            data=csv,
            file_name="cbmam_filtrado.csv",
            mime="text/csv"
        )
    with col_dl2:
        st.markdown("**📊 Estatísticas Gerais**")
        st.dataframe(df[colunas_numericas].describe().round(2), use_container_width=True)

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.85rem'>"
    "Dashboard CBMAM · Dados: github.com/AllanCardosoDev/seg · Python + Streamlit"
    "</div>",
    unsafe_allow_html=True
)
