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
    page_title="Dashboard CBMAM - SEGs",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        section[data-testid="stSidebar"] { background-color: #1a1a2e; }
        section[data-testid="stSidebar"] * { color: white !important; }
        .titulo { color: #cc0000; font-size: 2rem; font-weight: bold; text-align: center; padding: 10px 0; }
        .subtitulo { color: #666; font-size: 0.95rem; text-align: center; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARREGAMENTO DO CSV
# ─────────────────────────────────────────────
URL_CSV = "https://raw.githubusercontent.com/AllanCardosoDev/seg/main/relatorio.csv"

@st.cache_data
def carregar_csv():
    try:
        df = pd.read_csv(URL_CSV, encoding="utf-8", sep=None, engine="python")
    except Exception:
        df = pd.read_csv(URL_CSV, encoding="latin-1", sep=None, engine="python")

    # Limpa nomes de colunas
    df.columns = df.columns.astype(str).str.strip()
    # Remove linhas 100% vazias
    df.dropna(how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

with st.spinner("Carregando dados do GitHub..."):
    df_raw = carregar_csv()

# ─────────────────────────────────────────────
# DETECTA COLUNAS AUTOMATICAMENTE
# ─────────────────────────────────────────────
colunas        = df_raw.columns.tolist()
colunas_num    = df_raw.select_dtypes(include=np.number).columns.tolist()
colunas_txt    = df_raw.select_dtypes(exclude=np.number).columns.tolist()

# Coluna de MÊS — procura por "mes" ou "mês"
candidatos_mes = ["MES", "MÊS", "Mes", "Mês", "mes", "mês", "MONTH", "month"]
col_mes_auto   = next((c for c in candidatos_mes if c in colunas), None)

# Coluna de LOCAL/OBM
candidatos_local = ["OBM", "LOCAL", "UNIDADE", "POSTO", "NOME", "obm", "local", "unidade"]
col_local_auto   = next((c for c in candidatos_local if c in colunas),
                        colunas_txt[0] if colunas_txt else colunas[0])

# Coluna de VALOR (segs/horas)
candidatos_valor = ["SEGS", "HORAS", "TOTAL", "SEG", "H", "segs", "horas", "total", "seg"]
col_valor_auto   = next((c for c in candidatos_valor if c in colunas),
                        colunas_num[0] if colunas_num else colunas[-1])

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("### Configurações")
    st.markdown("---")

    # ── CONFIGURAÇÃO DE COLUNAS ───────────────
    st.markdown("**⚙️ Mapeamento de Colunas**")

    col_local = st.selectbox(
        "📍 Coluna de Local/OBM:",
        options=colunas,
        index=colunas.index(col_local_auto) if col_local_auto in colunas else 0
    )

    col_valor = st.selectbox(
        "⏱️ Coluna de SEGs/Horas:",
        options=colunas,
        index=colunas.index(col_valor_auto) if col_valor_auto in colunas else 0
    )

    # Coluna de mês (opcional)
    opcoes_mes = ["(Nenhuma)"] + colunas
    idx_mes = opcoes_mes.index(col_mes_auto) if col_mes_auto in opcoes_mes else 0
    col_mes = st.selectbox(
        "📅 Coluna de Mês (opcional):",
        options=opcoes_mes,
        index=idx_mes
    )
    tem_mes = col_mes != "(Nenhuma)" and col_mes in df_raw.columns

    st.markdown("---")

    # ── FILTRO POR MÊS ────────────────────────
    if tem_mes:
        meses_disponiveis = sorted(df_raw[col_mes].dropna().unique().tolist())

        st.markdown("**📅 Filtro por Mês**")
        modo_mes = st.radio(
            "Modo:",
            ["📄 Mês específico", "📚 Múltiplos meses", "🗂️ Todos os meses"],
            index=2
        )

        if modo_mes == "📄 Mês específico":
            mes_escolhido  = st.selectbox("Selecione o mês:", meses_disponiveis)
            meses_ativos   = [mes_escolhido]

        elif modo_mes == "📚 Múltiplos meses":
            meses_ativos = st.multiselect(
                "Selecione os meses:",
                options=meses_disponiveis,
                default=meses_disponiveis[:2] if len(meses_disponiveis) >= 2 else meses_disponiveis
            )
            if not meses_ativos:
                meses_ativos = meses_disponiveis

        else:
            meses_ativos = meses_disponiveis
            st.info(f"✅ {len(meses_disponiveis)} meses disponíveis")
    else:
        meses_ativos = []
        st.info("Nenhuma coluna de mês identificada.")

    st.markdown("---")

    # ── OUTROS FILTROS ────────────────────────
    st.markdown("**🔍 Filtro por Local**")
    filtro_local = st.text_input("Buscar OBM/Local:")

    st.markdown("---")
    top_n = st.slider("🏆 Top N no ranking", 3, 30, 10)

    st.markdown("---")
    st.markdown("**📁 Fonte**")
    st.markdown("[github.com/AllanCardosoDev/seg](https://github.com/AllanCardosoDev/seg)")

    with st.expander("📋 Colunas do CSV"):
        for c in colunas:
            st.markdown(f"- `{c}`")

# ─────────────────────────────────────────────
# APLICA FILTROS
# ─────────────────────────────────────────────
df = df_raw.copy()

# Filtro por mês
if tem_mes and meses_ativos:
    df = df[df[col_mes].isin(meses_ativos)]

# Filtro por local
if filtro_local:
    df = df[df[col_local].astype(str).str.contains(filtro_local, case=False, na=False)]

# Garante que col_valor é numérico
df[col_valor] = pd.to_numeric(df[col_valor], errors="coerce")
df = df.dropna(subset=[col_valor])
df = df[df[col_valor] > 0]

# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────
st.markdown('<div class="titulo">🚒 CBMAM — Dashboard de SEGs</div>', unsafe_allow_html=True)

if tem_mes and meses_ativos:
    if len(meses_ativos) == len(df_raw[col_mes].dropna().unique()):
        periodo = "Todos os meses"
    elif len(meses_ativos) == 1:
        periodo = f"Mês: {meses_ativos[0]}"
    else:
        periodo = f"Meses: {', '.join(str(m) for m in meses_ativos)}"
else:
    periodo = "Período completo"

st.markdown(f'<div class="subtitulo">{periodo} · relatorio.csv</div>', unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────
# VALIDA DADOS
# ─────────────────────────────────────────────
if df.empty:
    st.error("⚠️ Nenhum dado após os filtros aplicados. Ajuste as configurações na sidebar.")
    st.stop()

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
total_segs   = int(df[col_valor].sum())
media_segs   = round(df[col_valor].mean(), 1)
total_locais = df[col_local].nunique()
total_linhas = len(df)

ranking_geral = df.groupby(col_local)[col_valor].sum()
local_lider   = ranking_geral.idxmax()
valor_lider   = int(ranking_geral.max())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("⏱️ Total SEGs",     f"{total_segs:,}".replace(",", "."))
c2.metric("📊 Média por Reg.", f"{media_segs:.1f}")
c3.metric("📍 Locais Únicos",  total_locais)
c4.metric("📋 Registros",      total_linhas)
c5.metric("🏆 Líder",          local_lider)

st.markdown("---")

# ─────────────────────────────────────────────
# ABAS
# ─────────────────────────────────────────────
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "🏆 Ranking de Locais",
    "📅 Comparativo por Mês",
    "📊 Distribuição",
    "🔥 Análise Detalhada",
    "📋 Dados Brutos"
])

# ══════════════════════════════════════════════
# ABA 1 — RANKING (quais locais precisaram de mais SEGs)
# ══════════════════════════════════════════════
with aba1:
    st.subheader(f"🏆 Top {top_n} — Locais que mais precisaram de SEGs")

    df_rank = (
        df.groupby(col_local)[col_valor]
        .sum()
        .reset_index()
        .rename(columns={col_local: "Local", col_valor: "Total"})
        .sort_values("Total", ascending=False)
        .reset_index(drop=True)
    )
    df_rank.index += 1
    df_rank["% do Total"] = (df_rank["Total"] / df_rank["Total"].sum() * 100).round(1)

    top_rank = df_rank.head(top_n)

    col_g1, col_g2 = st.columns([3, 2])

    with col_g1:
        fig_bar = px.bar(
            top_rank.sort_values("Total"),
            x="Total", y="Local",
            orientation="h",
            color="Total",
            color_continuous_scale="Reds",
            text="Total",
            title=f"Top {top_n} — Total de SEGs por Local"
        )
        fig_bar.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_bar.update_layout(
            height=460,
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            yaxis_title="", xaxis_title="SEGs"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        fig_pie = px.pie(
            top_rank,
            names="Local", values="Total",
            hole=0.4,
            title=f"Distribuição % — Top {top_n}",
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(height=460, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    fig_tree = px.treemap(
        df_rank.head(20),
        path=["Local"], values="Total",
        color="Total",
        color_continuous_scale="Reds",
        title="Treemap — Proporção de SEGs por Local (Top 20)"
    )
    fig_tree.update_layout(height=380)
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Ranking Completo")
    df_rank_exib = df_rank.copy()
    df_rank_exib["Total"]     = df_rank_exib["Total"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    df_rank_exib["% do Total"] = df_rank_exib["% do Total"].astype(str) + "%"
    st.dataframe(df_rank_exib, use_container_width=True, height=350)

    st.success(
        f"🥇 **{local_lider}** foi o local com mais SEGs: "
        f"**{valor_lider:,}** ({df_rank[df_rank['Local'] == local_lider]['% do Total'].values[0]}% do total)"
        .replace(",", ".")
    )

# ══════════════════════════════════════════════
# ABA 2 — COMPARATIVO POR MÊS
# ══════════════════════════════════════════════
with aba2:
    st.subheader("📅 Comparativo por Mês")

    if not tem_mes:
        st.info("Configure a coluna de mês na sidebar para habilitar esta análise.")
    else:
        todos_meses = sorted(df_raw[col_mes].dropna().unique().tolist())

        # Garante dados de todos os meses para o comparativo (ignora filtro de mês aqui)
        df_full = df_raw.copy()
        df_full[col_valor] = pd.to_numeric(df_full[col_valor], errors="coerce")
        df_full = df_full.dropna(subset=[col_valor])
        df_full = df_full[df_full[col_valor] > 0]
        if filtro_local:
            df_full = df_full[df_full[col_local].astype(str).str.contains(filtro_local, case=False, na=False)]

        # Total por mês
        df_por_mes = (
            df_full.groupby(col_mes)[col_valor]
            .sum().reset_index()
            .rename(columns={col_mes: "Mês", col_valor: "Total"})
        )

        fig_mes = px.bar(
            df_por_mes,
            x="Mês", y="Total",
            color="Total",
            color_continuous_scale="Reds",
            text="Total",
            title="Total de SEGs por Mês"
        )
        fig_mes.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_mes.update_layout(
            height=380, plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_mes, use_container_width=True)

        st.markdown("---")

        # Evolução dos top locais por mês
        st.subheader(f"📈 Evolução dos Top {top_n} Locais por Mês")

        top_locais = df_full.groupby(col_local)[col_valor].sum().nlargest(top_n).index.tolist()
        df_evol = (
            df_full[df_full[col_local].isin(top_locais)]
            .groupby([col_mes, col_local])[col_valor]
            .sum().reset_index()
            .rename(columns={col_mes: "Mês", col_local: "Local", col_valor: "SEGs"})
        )

        fig_line = px.line(
            df_evol,
            x="Mês", y="SEGs", color="Local",
            markers=True,
            title=f"Evolução Mensal — Top {top_n} Locais"
        )
        fig_line.update_layout(height=430, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("---")

        # Heatmap Local × Mês
        st.subheader("🌡️ Mapa de Calor — Local × Mês")

        pivot = df_full.pivot_table(
            index=col_local, columns=col_mes,
            values=col_valor, aggfunc="sum", fill_value=0
        )
        pivot["_total"] = pivot.sum(axis=1)
        pivot = pivot.nlargest(top_n, "_total").drop(columns="_total")

        fig_heat = px.imshow(
            pivot,
            color_continuous_scale="Reds",
            aspect="auto",
            title=f"Heatmap SEGs — Top {top_n} Locais × Meses",
            text_auto=True
        )
        fig_heat.update_layout(height=max(350, top_n * 38))
        st.plotly_chart(fig_heat, use_container_width=True)

# ══════════════════════════════════════════════
# ABA 3 — DISTRIBUIÇÃO
# ══════════════════════════════════════════════
with aba3:
    st.subheader("📊 Distribuição de SEGs")

    df_dist = (
        df.groupby(col_local)[col_valor]
        .sum().reset_index()
        .rename(columns={col_local: "Local", col_valor: "Total"})
        .sort_values("Total", ascending=False)
    )

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        fig_pie2 = px.pie(
            df_dist.head(15),
            names="Local", values="Total",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Reds_r,
            title="% por Local (Top 15)"
        )
        fig_pie2.update_traces(textinfo="percent+label")
        fig_pie2.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig_pie2, use_container_width=True)

    with c_p2:
        fig_tree2 = px.treemap(
            df_dist,
            path=["Local"], values="Total",
            color="Total",
            color_continuous_scale="Reds",
            title="Treemap de SEGs"
        )
        fig_tree2.update_layout(height=420)
        st.plotly_chart(fig_tree2, use_container_width=True)

    st.markdown("---")
    fig_hist = px.histogram(
        df, x=col_valor, nbins=30,
        color_discrete_sequence=["#cc0000"],
        title=f"Histograma — {col_valor}"
    )
    fig_hist.update_layout(height=320, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_hist, use_container_width=True)

# ══════════════════════════════════════════════
# ABA 4 — ANÁLISE DETALHADA
# ══════════════════════════════════════════════
with aba4:
    st.subheader("🔥 Estatísticas por Local")

    df_stats = (
        df.groupby(col_local)[col_valor]
        .agg(["sum", "mean", "max", "min", "count"])
        .reset_index()
        .rename(columns={
            col_local: "Local",
            "sum": "Total", "mean": "Média",
            "max": "Máximo", "min": "Mínimo",
            "count": "Registros"
        })
        .sort_values("Total", ascending=False)
        .round(2)
    )
    st.dataframe(df_stats, use_container_width=True, height=360)

    st.markdown("---")
    if df.groupby(col_local).size().max() > 1:
        st.subheader(f"📦 Boxplot — Top {top_n} Locais")
        top_locais = df.groupby(col_local)[col_valor].sum().nlargest(top_n).index.tolist()
        df_box = df[df[col_local].isin(top_locais)]

        fig_box = px.box(
            df_box, x=col_local, y=col_valor,
            color=col_local,
            title=f"Variação de SEGs — Top {top_n} Locais",
            labels={col_local: "Local", col_valor: "SEGs"}
        )
        fig_box.update_layout(
            showlegend=False, height=420,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_tickangle=-40
        )
        st.plotly_chart(fig_box, use_container_width=True)

# ══════════════════════════════════════════════
# ABA 5 — DADOS BRUTOS
# ══════════════════════════════════════════════
with aba5:
    st.subheader("📋 Dados Brutos — relatorio.csv")

    col_b1, col_b2, col_b3 = st.columns([3, 1, 1])
    with col_b1:
        busca = st.text_input("🔍 Buscar em qualquer campo:")
    with col_b2:
        st.metric("Registros filtrados", len(df))
    with col_b3:
        st.metric("Total SEGs", f"{total_segs:,}".replace(",", "."))

    df_exib = df.copy()
    if busca:
        mask = df_exib.apply(
            lambda r: r.astype(str).str.contains(busca, case=False, na=False).any(), axis=1
        )
        df_exib = df_exib[mask]
        st.caption(f"{len(df_exib)} resultado(s) encontrado(s)")

    st.dataframe(df_exib, use_container_width=True, height=420)

    csv_bytes = df_exib.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Baixar CSV filtrado",
        data=csv_bytes,
        file_name="cbmam_filtrado.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("📊 Estatísticas Descritivas")
    st.dataframe(df[[col_valor]].describe().round(2), use_container_width=True)

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.82rem'>"
    "Dashboard CBMAM · relatorio.csv · Python + Streamlit"
    "</div>",
    unsafe_allow_html=True
)
