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
        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARREGAMENTO DO EXCEL
# ─────────────────────────────────────────────
ARQUIVO = "1_Relatrio_GRAFICOS_3.xlsx"

@st.cache_data
def carregar_abas(arquivo):
    """Lê todas as abas do Excel e retorna um dicionário {nome_aba: DataFrame}"""
    xl = pd.ExcelFile(arquivo)
    abas = {}
    for aba in xl.sheet_names:
        try:
            df = xl.parse(aba)
            df.columns = df.columns.astype(str).str.strip()
            abas[aba] = df
        except Exception:
            pass
    return abas, xl.sheet_names


@st.cache_data
def carregar_aba_principal(arquivo, nome_aba):
    """Lê uma aba específica e faz limpeza básica"""
    df = pd.read_excel(arquivo, sheet_name=nome_aba)
    df.columns = df.columns.astype(str).str.strip()
    # Remove linhas completamente vazias
    df.dropna(how="all", inplace=True)
    return df


# ─────────────────────────────────────────────
# CARREGA ESTRUTURA DO ARQUIVO
# ─────────────────────────────────────────────
try:
    abas_dict, nomes_abas = carregar_abas(ARQUIVO)
except FileNotFoundError:
    st.error(f"❌ Arquivo '{ARQUIVO}' não encontrado. Coloque-o na mesma pasta do app.py.")
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("### Filtros do Relatório")
    st.markdown("---")

    # ── SELEÇÃO DE MÊS / ABA ──────────────────
    st.markdown("**📅 Filtro por Mês**")

    modo_mes = st.radio(
        "Modo de seleção:",
        options=["Todos os meses", "Escolher mês específico"],
        index=0
    )

    if modo_mes == "Escolher mês específico":
        mes_selecionado = st.selectbox(
            "Selecione o mês (aba do Excel):",
            options=nomes_abas
        )
        abas_ativas = [mes_selecionado]
    else:
        abas_ativas = st.multiselect(
            "Meses incluídos na análise:",
            options=nomes_abas,
            default=nomes_abas
        )
        if not abas_ativas:
            st.warning("Selecione ao menos um mês.")
            abas_ativas = [nomes_abas[0]]

    st.markdown("---")

    # ── ABA DE REFERÊNCIA PARA COLUNAS ────────
    aba_ref = abas_ativas[0]
    df_ref = abas_dict[aba_ref].copy()

    colunas_todas = df_ref.columns.tolist()
    colunas_num = df_ref.select_dtypes(include=np.number).columns.tolist()
    colunas_txt = df_ref.select_dtypes(exclude=np.number).columns.tolist()

    st.markdown("**📌 Coluna de Local/Unidade**")
    # Tenta detectar automaticamente
    candidatos_local = ["OBM", "LOCAL", "UNIDADE", "POSTO", "NOME", "obm", "local", "unidade"]
    col_local_default = next((c for c in candidatos_local if c in colunas_todas), colunas_txt[0] if colunas_txt else colunas_todas[0])
    col_local = st.selectbox(
        "Coluna de local:",
        options=colunas_txt if colunas_txt else colunas_todas,
        index=(colunas_txt.index(col_local_default) if col_local_default in colunas_txt else 0)
    )

    st.markdown("**⏱️ Coluna de SEGs/Horas**")
    candidatos_valor = ["SEGS", "HORAS", "TOTAL", "SEG", "H", "segs", "horas", "total"]
    col_valor_default = next((c for c in candidatos_valor if c in colunas_todas), colunas_num[0] if colunas_num else colunas_todas[-1])
    col_valor = st.selectbox(
        "Coluna de valor:",
        options=colunas_num if colunas_num else colunas_todas,
        index=(colunas_num.index(col_valor_default) if col_valor_default in colunas_num else 0)
    )

    st.markdown("---")
    top_n = st.slider("🏆 Top N locais no ranking", min_value=3, max_value=30, value=10)

    st.markdown("---")
    st.markdown("**📁 Arquivo**")
    st.code(ARQUIVO, language=None)
    st.markdown(f"**Abas disponíveis:** {len(nomes_abas)}")
    st.markdown(f"**Analisando:** {len(abas_ativas)} mês(es)")


# ─────────────────────────────────────────────
# CONSOLIDA DADOS DAS ABAS SELECIONADAS
# ─────────────────────────────────────────────
@st.cache_data
def consolidar_abas(arquivo, abas_ativas, col_local, col_valor):
    frames = []
    for aba in abas_ativas:
        try:
            df_tmp = pd.read_excel(arquivo, sheet_name=aba)
            df_tmp.columns = df_tmp.columns.astype(str).str.strip()
            df_tmp.dropna(how="all", inplace=True)

            if col_local in df_tmp.columns and col_valor in df_tmp.columns:
                df_tmp = df_tmp[[col_local, col_valor]].copy()
                df_tmp[col_valor] = pd.to_numeric(df_tmp[col_valor], errors="coerce")
                df_tmp.dropna(subset=[col_valor], inplace=True)
                df_tmp["Mês"] = aba
                frames.append(df_tmp)
        except Exception:
            pass

    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame()


df = consolidar_abas(ARQUIVO, tuple(abas_ativas), col_local, col_valor)

# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────
st.markdown('<div class="titulo-principal">🚒 Dashboard CBMAM — Relatório de Serviços</div>', unsafe_allow_html=True)

# Indica o modo ativo
if modo_mes == "Escolher mês específico":
    st.markdown(f'<div class="subtitulo">📅 Exibindo dados de: <strong>{abas_ativas[0]}</strong></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="subtitulo">📅 Período consolidado: {", ".join(abas_ativas)}</div>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# VALIDA DADOS
# ─────────────────────────────────────────────
if df.empty:
    st.error("⚠️ Nenhum dado encontrado com as colunas selecionadas. Ajuste os filtros na sidebar.")
    st.stop()

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
total_registros = len(df)
total_valor     = df[col_valor].sum()
media_valor     = df[col_valor].mean()
total_locais    = df[col_local].nunique()
df_rank_geral   = df.groupby(col_local)[col_valor].sum()
local_lider     = df_rank_geral.idxmax()
valor_lider     = df_rank_geral.max()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📋 Registros", f"{total_registros:,}".replace(",", "."))
c2.metric("⏱️ Total SEGs", f"{total_valor:,.0f}".replace(",", "."))
c3.metric("📊 Média por Reg.", f"{media_valor:.1f}")
c4.metric("📍 Locais Únicos", total_locais)
c5.metric("🏆 Líder", local_lider)

st.markdown("---")

# ─────────────────────────────────────────────
# ABAS DO DASHBOARD
# ─────────────────────────────────────────────
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "🏆 Ranking por Local",
    "📅 Comparativo por Mês",
    "📊 Distribuição",
    "🔥 Análise Detalhada",
    "📋 Dados Brutos"
])

# ══════════════════════════════════════════════
# ABA 1 — RANKING
# ══════════════════════════════════════════════
with aba1:
    st.subheader(f"🏆 Top {top_n} — Locais que Mais Precisaram de SEGs")

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
            title=f"Top {top_n} Locais — Total de SEGs",
            labels={"Total": "Total de SEGs", "Local": "Local/Unidade"}
        )
        fig_bar.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_bar.update_layout(
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
            height=460,
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_t:
        st.markdown("#### 📋 Tabela de Ranking")
        df_rank_exib = df_rank.copy()
        df_rank_exib["% do Total"] = (df_rank_exib["Total"] / total_valor * 100).round(1).astype(str) + "%"
        df_rank_exib["Total"] = df_rank_exib["Total"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
        st.dataframe(df_rank_exib, use_container_width=True, height=420)

    st.markdown("---")
    st.subheader("📉 Funil de Demanda")
    fig_funnel = go.Figure(go.Funnel(
        y=df_rank["Local"],
        x=df_rank["Total"].str.replace(".", "").astype(float) if df_rank["Total"].dtype == object else df_rank["Total"],
        textinfo="value+percent initial",
        marker=dict(color=px.colors.sequential.Reds_r[:len(df_rank)])
    ))
    fig_funnel.update_layout(height=380)
    st.plotly_chart(fig_funnel, use_container_width=True)


# ══════════════════════════════════════════════
# ABA 2 — COMPARATIVO POR MÊS
# ══════════════════════════════════════════════
with aba2:
    st.subheader("📅 Comparativo de SEGs por Mês")

    if len(abas_ativas) > 1:
        df_por_mes = (
            df.groupby("Mês")[col_valor]
            .sum()
            .reset_index()
            .rename(columns={"Mês": "Mês", col_valor: "Total"})
        )
        # Mantém a ordem original das abas
        df_por_mes["Mês"] = pd.Categorical(df_por_mes["Mês"], categories=abas_ativas, ordered=True)
        df_por_mes = df_por_mes.sort_values("Mês")

        fig_mes = px.bar(
            df_por_mes,
            x="Mês",
            y="Total",
            color="Total",
            color_continuous_scale="Reds",
            text="Total",
            title="Total de SEGs por Mês"
        )
        fig_mes.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_mes.update_layout(
            coloraxis_showscale=False,
            height=380,
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_mes, use_container_width=True)

        st.markdown("---")
        st.subheader("📈 Evolução por Local ao Longo dos Meses")

        top_locais = df.groupby(col_local)[col_valor].sum().nlargest(top_n).index.tolist()
        df_evolucao = df[df[col_local].isin(top_locais)].groupby(["Mês", col_local])[col_valor].sum().reset_index()
        df_evolucao["Mês"] = pd.Categorical(df_evolucao["Mês"], categories=abas_ativas, ordered=True)
        df_evolucao = df_evolucao.sort_values("Mês")

        fig_line = px.line(
            df_evolucao,
            x="Mês",
            y=col_valor,
            color=col_local,
            markers=True,
            title=f"Evolução dos Top {top_n} Locais por Mês",
            labels={col_valor: "Total de SEGs", col_local: "Local"}
        )
        fig_line.update_layout(height=440, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("---")
        st.subheader("🔥 Mapa de Calor — Local × Mês")

        df_heat = df.pivot_table(
            index=col_local,
            columns="Mês",
            values=col_valor,
            aggfunc="sum"
        ).fillna(0)

        fig_heat = px.imshow(
            df_heat,
            color_continuous_scale="Reds",
            aspect="auto",
            title="Intensidade de SEGs por Local e Mês",
            labels=dict(x="Mês", y="Local", color="SEGs")
        )
        fig_heat.update_layout(height=500)
        st.plotly_chart(fig_heat, use_container_width=True)

    else:
        st.info("📌 Selecione mais de um mês na sidebar (modo 'Todos os meses') para ver o comparativo entre períodos.")
        st.markdown(f"**Mês atual:** `{abas_ativas[0]}`")

        df_unico = df.groupby(col_local)[col_valor].sum().reset_index().sort_values(col_valor, ascending=False)
        fig_u = px.bar(
            df_unico.head(top_n),
            x=col_valor,
            y=col_local,
            orientation="h",
            color=col_valor,
            color_continuous_scale="Reds",
            text=col_valor,
            title=f"SEGs por Local — {abas_ativas[0]}"
        )
        fig_u.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_u.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False, height=420, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_u, use_container_width=True)


# ══════════════════════════════════════════════
# ABA 3 — DISTRIBUIÇÃO
# ══════════════════════════════════════════════
with aba3:
    st.subheader("📊 Distribuição de SEGs por Local")

    df_dist = (
        df.groupby(col_local)[col_valor]
        .sum()
        .reset_index()
        .rename(columns={col_local: "Local", col_valor: "Total"})
        .sort_values("Total", ascending=False)
    )

    c_p1, c_p2 = st.columns(2)

    with c_p1:
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

    with c_p2:
        fig_tree = px.treemap(
            df_dist,
            path=["Local"],
            values="Total",
            color="Total",
            color_continuous_scale="Reds",
            title="Treemap de SEGs por Local"
        )
        fig_tree.update_layout(height=420)
        st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")
    fig_hist = px.histogram(
        df,
        x=col_valor,
        nbins=30,
        color_discrete_sequence=["#cc0000"],
        title=f"Histograma de valores — {col_valor}"
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
            "sum": "Total",
            "mean": "Média",
            "max": "Máximo",
            "min": "Mínimo",
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
            df_box,
            x=col_local,
            y=col_valor,
            color=col_local,
            title=f"Variação de SEGs — Top {top_n} Locais",
            labels={col_local: "Local", col_valor: "SEGs"}
        )
        fig_box.update_layout(showlegend=False, height=420, plot_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-40)
        st.plotly_chart(fig_box, use_container_width=True)


# ══════════════════════════════════════════════
# ABA 5 — DADOS BRUTOS
# ══════════════════════════════════════════════
with aba5:
    st.subheader("📋 Dados Brutos")

    col_busca, col_info = st.columns([3, 1])
    with col_busca:
        busca = st.text_input("🔍 Buscar em qualquer campo...")
    with col_info:
        st.metric("Total de linhas", len(df))

    df_exib = df.copy()
    if busca:
        mask = df_exib.apply(lambda r: r.astype(str).str.contains(busca, case=False, na=False).any(), axis=1)
        df_exib = df_exib[mask]
        st.caption(f"{len(df_exib)} resultado(s)")

    st.dataframe(df_exib, use_container_width=True, height=420)

    csv_bytes = df_exib.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar dados filtrados (CSV)", data=csv_bytes, file_name="cbmam_filtrado.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("📊 Estatísticas Gerais")
    st.dataframe(df[[col_valor]].describe().round(2), use_container_width=True)

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.85rem'>"
    "Dashboard CBMAM · Python + Streamlit · Arquivo: 1_Relatrio_GRAFICOS_3.xlsx"
    "</div>",
    unsafe_allow_html=True
)
