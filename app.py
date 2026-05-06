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
    page_title="Dashboard CBMAM - Março",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        section[data-testid="stSidebar"] { background-color: #1a1a2e; }
        section[data-testid="stSidebar"] * { color: white !important; }
        .titulo {
            color: #cc0000;
            font-size: 2rem;
            font-weight: bold;
            text-align: center;
            padding: 10px 0;
        }
        .subtitulo {
            color: #666;
            font-size: 0.95rem;
            text-align: center;
            margin-bottom: 10px;
        }
        .destaque-marco {
            background: linear-gradient(135deg, #cc0000, #ff6b6b);
            color: white;
            padding: 12px 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.1rem;
            font-weight: bold;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARREGAMENTO DO CSV
# ─────────────────────────────────────────────
URL_CSV = "https://raw.githubusercontent.com/AllanCardosoDev/seg/main/relatorio.csv"

@st.cache_data
def carregar_csv():
    for enc in ["utf-8", "latin-1", "utf-8-sig"]:
        try:
            df = pd.read_csv(URL_CSV, encoding=enc, sep=None, engine="python")
            df.columns = df.columns.astype(str).str.strip()
            df.dropna(how="all", inplace=True)
            df.reset_index(drop=True, inplace=True)
            return df
        except Exception:
            continue
    st.error("Não foi possível carregar o arquivo relatorio.csv")
    st.stop()

with st.spinner("Carregando relatorio.csv..."):
    df_raw = carregar_csv()

# ─────────────────────────────────────────────
# DETECTA COLUNAS AUTOMATICAMENTE
# ─────────────────────────────────────────────
colunas     = df_raw.columns.tolist()
colunas_num = df_raw.select_dtypes(include=np.number).columns.tolist()
colunas_txt = df_raw.select_dtypes(exclude=np.number).columns.tolist()

# Detecta coluna de MÊS
candidatos_mes   = ["MES", "MÊS", "Mes", "Mês", "mes", "mês", "MONTH", "month", "Mês/Ano", "MES/ANO"]
col_mes_auto     = next((c for c in candidatos_mes if c in colunas), None)

# Detecta coluna de LOCAL
candidatos_local = ["OBM", "LOCAL", "UNIDADE", "POSTO", "NOME", "obm", "local", "unidade", "OM", "om"]
col_local_auto   = next((c for c in candidatos_local if c in colunas),
                        colunas_txt[0] if colunas_txt else colunas[0])

# Detecta coluna de VALOR
candidatos_valor = ["SEGS", "HORAS", "TOTAL", "SEG", "segs", "horas", "total", "seg", "Segs", "Horas"]
col_valor_auto   = next((c for c in candidatos_valor if c in colunas),
                        colunas_num[0] if colunas_num else colunas[-1])

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("### Dashboard de SEGs")
    st.markdown("---")

    # ── MAPEAMENTO DE COLUNAS ─────────────────
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

    opcoes_mes = ["(Nenhuma)"] + colunas
    col_mes = st.selectbox(
        "📅 Coluna de Mês:",
        options=opcoes_mes,
        index=opcoes_mes.index(col_mes_auto) if col_mes_auto in opcoes_mes else 0
    )
    tem_mes = col_mes != "(Nenhuma)" and col_mes in df_raw.columns

    st.markdown("---")

    # ── FILTRO POR MÊS ────────────────────────
    if tem_mes:
        meses_raw        = df_raw[col_mes].dropna().unique().tolist()
        meses_disponiveis = sorted([str(m) for m in meses_raw])

        # Detecta qual valor representa março
        marco_opcoes = [m for m in meses_disponiveis
                        if "mar" in str(m).lower() or "03" in str(m) or "3" == str(m).strip()]
        marco_default = marco_opcoes[0] if marco_opcoes else (
            meses_disponiveis[0] if meses_disponiveis else None
        )

        st.markdown("**📅 Filtro por Mês**")
        modo_mes = st.radio(
            "Modo de seleção:",
            ["📄 Mês específico", "📚 Múltiplos meses", "🗂️ Todos os meses"],
            index=0
        )

        if modo_mes == "📄 Mês específico":
            idx_marco = meses_disponiveis.index(marco_default) if marco_default in meses_disponiveis else 0
            mes_escolhido = st.selectbox(
                "Selecione o mês:",
                options=meses_disponiveis,
                index=idx_marco   # março já vem pré-selecionado
            )
            meses_ativos = [mes_escolhido]

        elif modo_mes == "📚 Múltiplos meses":
            meses_ativos = st.multiselect(
                "Selecione os meses:",
                options=meses_disponiveis,
                default=[marco_default] if marco_default else meses_disponiveis[:1]
            )
            if not meses_ativos:
                meses_ativos = meses_disponiveis

        else:
            meses_ativos = meses_disponiveis
            st.info(f"✅ {len(meses_disponiveis)} meses selecionados")

    else:
        meses_ativos = []
        st.info("Coluna de mês não identificada. Todos os dados serão exibidos.")

    st.markdown("---")

    # ── OUTROS FILTROS ────────────────────────
    st.markdown("**🔍 Filtrar por Local**")
    filtro_local = st.text_input("Buscar OBM/Local:")

    st.markdown("---")
    top_n = st.slider("🏆 Top N no ranking", 3, 30, 10)

    st.markdown("---")
    st.markdown("**📁 Fonte dos dados**")
    st.markdown("[github.com/AllanCardosoDev/seg](https://github.com/AllanCardosoDev/seg)")

    with st.expander("📋 Ver colunas do CSV"):
        for c in colunas:
            st.markdown(f"- `{c}`")

# ─────────────────────────────────────────────
# APLICA FILTROS
# ─────────────────────────────────────────────
df = df_raw.copy()
df[col_mes]   = df[col_mes].astype(str) if tem_mes else df.get(col_mes, "")
df[col_valor] = pd.to_numeric(df[col_valor], errors="coerce")
df            = df.dropna(subset=[col_valor])
df            = df[df[col_valor] > 0]

# Filtro por mês
if tem_mes and meses_ativos:
    df = df[df[col_mes].isin(meses_ativos)]

# Filtro por local
if filtro_local:
    df = df[df[col_local].astype(str).str.contains(filtro_local, case=False, na=False)]

# Dados exclusivos de março (para comparativos)
df_marco = df_raw.copy()
df_marco[col_valor] = pd.to_numeric(df_marco[col_valor], errors="coerce")
df_marco = df_marco.dropna(subset=[col_valor])
df_marco = df_marco[df_marco[col_valor] > 0]
if tem_mes and marco_default:
    df_marco = df_marco[df_marco[col_mes].astype(str) == str(marco_default)]

# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────
st.markdown('<div class="titulo">🚒 CBMAM — Dashboard de SEGs</div>', unsafe_allow_html=True)

if tem_mes and len(meses_ativos) == 1:
    eh_marco = "mar" in meses_ativos[0].lower() or meses_ativos[0] == marco_default
    if eh_marco:
        st.markdown(
            '<div class="destaque-marco">📅 FOCO: MARÇO — Análise principal do mês de referência</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(f'<div class="subtitulo">📅 Mês selecionado: {meses_ativos[0]}</div>', unsafe_allow_html=True)
elif tem_mes:
    st.markdown(
        f'<div class="subtitulo">📅 Meses: {", ".join(meses_ativos)}</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown('<div class="subtitulo">📅 Todos os registros</div>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# VALIDA
# ─────────────────────────────────────────────
if df.empty:
    st.error("⚠️ Nenhum dado encontrado com os filtros aplicados. Ajuste as configurações na sidebar.")
    st.stop()

# ─────────────────────────────────────────────
# KPIs — destaque para março
# ─────────────────────────────────────────────
total_segs    = int(df[col_valor].sum())
media_segs    = round(df[col_valor].mean(), 1)
total_locais  = df[col_local].nunique()
total_linhas  = len(df)
rank_geral    = df.groupby(col_local)[col_valor].sum()
local_lider   = rank_geral.idxmax()
valor_lider   = int(rank_geral.max())

# KPIs de março para comparação
total_marco   = int(df_marco[col_valor].sum()) if not df_marco.empty else 0
locais_marco  = df_marco[col_local].nunique() if not df_marco.empty else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("⏱️ Total SEGs",     f"{total_segs:,}".replace(",", "."))
c2.metric("📅 SEGs em Março",  f"{total_marco:,}".replace(",", "."))
c3.metric("📍 Locais Únicos",  total_locais)
c4.metric("📊 Média por Reg.", f"{media_segs:.1f}")
c5.metric("🏆 Líder",          local_lider)

st.markdown("---")

# ─────────────────────────────────────────────
# ABAS
# ─────────────────────────────────────────────
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "🏆 Ranking — Quem mais precisou de SEGs",
    "📅 Março em Destaque",
    "📊 Comparativo por Mês",
    "🔥 Análise Detalhada",
    "📋 Dados Brutos"
])

# ══════════════════════════════════════════════
# ABA 1 — RANKING GERAL
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
    df_rank.index        += 1
    df_rank["% do Total"] = (df_rank["Total"] / df_rank["Total"].sum() * 100).round(1)
    top_rank              = df_rank.head(top_n)

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

    # Treemap
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

    # Funil
    st.markdown("---")
    fig_funil = go.Figure(go.Funnel(
        y=top_rank["Local"],
        x=top_rank["Total"],
        textinfo="value+percent initial",
        marker=dict(color=px.colors.sequential.Reds_r[:len(top_rank)])
    ))
    fig_funil.update_layout(title=f"Funil de Demanda — Top {top_n}", height=400)
    st.plotly_chart(fig_funil, use_container_width=True)

    # Tabela completa
    st.markdown("---")
    st.subheader("📋 Ranking Completo")
    df_exib_rank = df_rank.copy()
    df_exib_rank["Total"]      = df_exib_rank["Total"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    df_exib_rank["% do Total"] = df_exib_rank["% do Total"].astype(str) + "%"
    st.dataframe(df_exib_rank, use_container_width=True, height=350)

    st.success(
        f"🥇 **{local_lider}** foi o local com mais SEGs: "
        f"**{valor_lider:,}** ({df_rank[df_rank['Local'] == local_lider]['% do Total'].values[0]}% do total)"
        .replace(",", ".")
    )

# ══════════════════════════════════════════════
# ABA 2 — MARÇO EM DESTAQUE
# ══════════════════════════════════════════════
with aba2:
    st.markdown(
        '<div class="destaque-marco">📅 MARÇO — Análise detalhada do mês de referência</div>',
        unsafe_allow_html=True
    )

    if df_marco.empty:
        st.warning("Nenhum dado encontrado para março. Verifique a coluna de mês na sidebar.")
    else:
        # KPIs de março
        total_m   = int(df_marco[col_valor].sum())
        media_m   = round(df_marco[col_valor].mean(), 1)
        locais_m  = df_marco[col_local].nunique()
        rank_m    = df_marco.groupby(col_local)[col_valor].sum()
        lider_m   = rank_m.idxmax()
        val_lider = int(rank_m.max())

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("⏱️ Total SEGs em Março", f"{total_m:,}".replace(",", "."))
        k2.metric("📊 Média por Registro",  f"{media_m:.1f}")
        k3.metric("📍 Locais Atendidos",    locais_m)
        k4.metric("🥇 Maior Demandante",    lider_m)

        st.markdown("---")

        # Ranking de março
        df_rank_m = (
            df_marco.groupby(col_local)[col_valor]
            .sum()
            .reset_index()
            .rename(columns={col_local: "Local", col_valor: "Total"})
            .sort_values("Total", ascending=False)
            .reset_index(drop=True)
        )
        df_rank_m.index += 1
        df_rank_m["% do Mês"] = (df_rank_m["Total"] / df_rank_m["Total"].sum() * 100).round(1)

        col_m1, col_m2 = st.columns([3, 2])

        with col_m1:
            st.subheader(f"🏆 Top {top_n} em Março")
            fig_bar_m = px.bar(
                df_rank_m.head(top_n).sort_values("Total"),
                x="Total", y="Local",
                orientation="h",
                color="Total",
                color_continuous_scale="Reds",
                text="Total",
                title="Ranking de SEGs — Março"
            )
            fig_bar_m.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_bar_m.update_layout(
                height=420,
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar_m, use_container_width=True)

        with col_m2:
            st.subheader("📋 Tabela — Março")
            df_tab_m = df_rank_m.copy()
            df_tab_m["Total"]    = df_tab_m["Total"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
            df_tab_m["% do Mês"] = df_tab_m["% do Mês"].astype(str) + "%"
            st.dataframe(df_tab_m, use_container_width=True, height=420)

        st.markdown("---")

        # Treemap março
        fig_tree_m = px.treemap(
            df_rank_m,
            path=["Local"], values="Total",
            color="Total",
            color_continuous_scale="Reds",
            title="Treemap de SEGs — Março"
        )
        fig_tree_m.update_layout(height=380)
        st.plotly_chart(fig_tree_m, use_container_width=True)

        # Comparação março vs total geral (se houver outros meses)
        if tem_mes and len(meses_disponiveis) > 1:
            st.markdown("---")
            st.subheader("📊 Março vs Demais Meses")

            df_full_val = df_raw.copy()
            df_full_val[col_valor] = pd.to_numeric(df_full_val[col_valor], errors="coerce")
            df_full_val = df_full_val.dropna(subset=[col_valor])
            df_full_val = df_full_val[df_full_val[col_valor] > 0]
            df_full_val[col_mes] = df_full_val[col_mes].astype(str)

            total_por_mes = (
                df_full_val.groupby(col_mes)[col_valor]
                .sum().reset_index()
                .rename(columns={col_mes: "Mês", col_valor: "Total"})
                .sort_values("Total", ascending=False)
            )
            total_por_mes["Destaque"] = total_por_mes["Mês"].apply(
                lambda x: "🔴 Março" if "mar" in x.lower() or x == str(marco_default) else "Outros meses"
            )

            fig_comp = px.bar(
                total_por_mes,
                x="Mês", y="Total",
                color="Destaque",
                color_discrete_map={"🔴 Março": "#cc0000", "Outros meses": "#aaaaaa"},
                text="Total",
                title="Comparativo de SEGs entre Meses (Março em destaque)"
            )
            fig_comp.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_comp.update_layout(
                height=380,
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_tickangle=-30
            )
            st.plotly_chart(fig_comp, use_container_width=True)

        st.success(
            f"🥇 Em março, **{lider_m}** foi o local com maior demanda de SEGs: "
            f"**{val_lider:,}** ({df_rank_m[df_rank_m['Local'] == lider_m]['% do Mês'].values[0]}% do mês)"
            .replace(",", ".")
        )

# ══════════════════════════════════════════════
# ABA 3 — COMPARATIVO POR MÊS
# ══════════════════════════════════════════════
with aba3:
    st.subheader("📅 Comparativo entre Meses")

    if not tem_mes:
        st.info("Configure a coluna de mês na sidebar para habilitar esta análise.")
    else:
        df_full = df_raw.copy()
        df_full[col_valor] = pd.to_numeric(df_full[col_valor], errors="coerce")
        df_full = df_full.dropna(subset=[col_valor])
        df_full = df_full[df_full[col_valor] > 0]
        df_full[col_mes] = df_full[col_mes].astype(str)

        if filtro_local:
            df_full = df_full[df_full[col_local].astype(str).str.contains(filtro_local, case=False, na=False)]

        # Total por mês
        df_por_mes = (
            df_full.groupby(col_mes)[col_valor]
            .sum().reset_index()
            .rename(columns={col_mes: "Mês", col_valor: "Total"})
            .sort_values("Total", ascending=False)
        )
        df_por_mes["Destaque"] = df_por_mes["Mês"].apply(
            lambda x: "🔴 Março" if "mar" in x.lower() else "Outros"
        )

        fig_mes = px.bar(
            df_por_mes,
            x="Mês", y="Total",
            color="Destaque",
            color_discrete_map={"🔴 Março": "#cc0000", "Outros": "#888888"},
            text="Total",
            title="Total de SEGs por Mês"
        )
        fig_mes.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_mes.update_layout(
            height=380, plot_bgcolor="rgba(0,0,0,0)",
            xaxis_tickangle=-30, showlegend=True
        )
        st.plotly_chart(fig_mes, use_container_width=True)

        st.markdown("---")

        # Heatmap local × mês
        st.subheader(f"🌡️ Heatmap — Top {top_n} Locais × Meses")

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

        st.markdown("---")

        # Evolução dos top locais
        st.subheader(f"📈 Evolução Mensal — Top {top_n} Locais")

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

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        fig_hist = px.histogram(
            df, x=col_valor, nbins=30,
            color_discrete_sequence=["#cc0000"],
            title=f"Histograma — {col_valor}"
        )
        fig_hist.update_layout(height=340, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_d2:
        df_dist = (
            df.groupby(col_local)[col_valor]
            .sum().reset_index()
            .rename(columns={col_local: "Local", col_valor: "Total"})
            .sort_values("Total", ascending=False)
        )
        fig_pie2 = px.pie(
            df_dist.head(12),
            names="Local", values="Total",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Reds_r,
            title="Distribuição % por Local (Top 12)"
        )
        fig_pie2.update_traces(textinfo="percent+label")
        fig_pie2.update_layout(height=340, showlegend=False)
        st.plotly_chart(fig_pie2, use_container_width=True)

    # Boxplot
    if df.groupby(col_local).size().max() > 1:
        st.markdown("---")
        st.subheader(f"📦 Boxplot — Top {top_n} Locais")
        top_locais_box = df.groupby(col_local)[col_valor].sum().nlargest(top_n).index.tolist()
        df_box = df[df[col_local].isin(top_locais_box)]

        fig_box = px.box(
            df_box, x=col_local, y=col_valor,
            color=col_local,
            title=f"Variação de SEGs — Top {top_n} Locais"
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
        st.metric("Registros", len(df))
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
    "Dashboard CBMAM · relatorio.csv · Foco: Março · Python + Streamlit"
    "</div>",
    unsafe_allow_html=True
)
