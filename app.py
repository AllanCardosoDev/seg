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
    page_title="CBMAM — SEGs por OBM",
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
        .badge-marco {
            background: linear-gradient(135deg, #cc0000, #ff4444);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-align: center;
            font-size: 1rem;
            font-weight: bold;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARREGAMENTO
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

# OBM
cand_obm   = ["OBM", "obm", "UNIDADE", "unidade", "LOCAL", "local", "OM", "om", "POSTO", "posto"]
col_obm    = next((c for c in cand_obm if c in colunas), colunas_txt[0] if colunas_txt else colunas[0])

# SEGs
cand_segs  = ["SEGS", "segs", "SEG", "seg", "HORAS", "horas", "TOTAL", "total", "QTD", "qtd"]
col_segs   = next((c for c in cand_segs if c in colunas), colunas_num[0] if colunas_num else colunas[-1])

# MÊS
cand_mes   = ["MES", "mes", "MÊS", "mês", "MONTH", "month", "MES_ANO", "REFERENCIA"]
col_mes    = next((c for c in cand_mes if c in colunas), None)
tem_mes    = col_mes is not None

# ─────────────────────────────────────────────
# PREPARA LISTA DE MESES E DETECTA MARÇO
# ─────────────────────────────────────────────
if tem_mes:
    df_raw[col_mes]  = df_raw[col_mes].astype(str).str.strip()
    meses_lista      = sorted(df_raw[col_mes].dropna().unique().tolist())
    # Encontra março automaticamente
    marco_val        = next(
        (m for m in meses_lista if "mar" in m.lower() or m.strip() in ["3", "03"]),
        meses_lista[0] if meses_lista else None
    )
else:
    meses_lista = []
    marco_val   = None

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("### SEGs por OBM")
    st.markdown("---")

    # ── MAPEAMENTO ────────────────────────────
    st.markdown("**⚙️ Colunas**")
    col_obm = st.selectbox(
        "📍 OBM/Unidade:",
        colunas,
        index=colunas.index(col_obm) if col_obm in colunas else 0
    )
    col_segs = st.selectbox(
        "⏱️ SEGs:",
        colunas,
        index=colunas.index(col_segs) if col_segs in colunas else 0
    )
    opcoes_mes = ["(Nenhuma)"] + colunas
    col_mes_sel = st.selectbox(
        "📅 Mês:",
        opcoes_mes,
        index=opcoes_mes.index(col_mes) if col_mes in opcoes_mes else 0
    )
    tem_mes  = col_mes_sel != "(Nenhuma)"
    col_mes  = col_mes_sel if tem_mes else None

    st.markdown("---")

    # ── FILTRO POR MÊS ────────────────────────
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
            ["📄 Mês específico", "📚 Múltiplos meses", "🗂️ Todos os meses"],
            index=0
        )

        if modo_mes == "📄 Mês específico":
            idx_default = meses_lista.index(marco_val) if marco_val in meses_lista else 0
            mes_unico   = st.selectbox("Mês:", meses_lista, index=idx_default)
            meses_ativos = [mes_unico]

        elif modo_mes == "📚 Múltiplos meses":
            default_multi = [marco_val] if marco_val else meses_lista[:1]
            meses_ativos  = st.multiselect("Meses:", meses_lista, default=default_multi)
            if not meses_ativos:
                meses_ativos = meses_lista

        else:
            meses_ativos = meses_lista
            st.info(f"✅ {len(meses_lista)} meses")

    else:
        meses_ativos = []

    st.markdown("---")

    # ── FILTRO OBM ────────────────────────────
    st.markdown("**🔍 Filtrar OBM**")
    filtro_obm = st.text_input("Buscar:")

    st.markdown("---")
    top_n = st.slider("🏆 Top N OBMs", 3, 30, 10)

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
df[col_segs] = pd.to_numeric(df[col_segs], errors="coerce")
df = df.dropna(subset=[col_segs])
df = df[df[col_segs] > 0]

if tem_mes and meses_ativos:
    df = df[df[col_mes].isin(meses_ativos)]

if filtro_obm:
    df = df[df[col_obm].astype(str).str.contains(filtro_obm, case=False, na=False)]

# DataFrame exclusivo de março
if tem_mes and marco_val:
    df_marco = df_raw.copy()
    df_marco[col_segs] = pd.to_numeric(df_marco[col_segs], errors="coerce")
    df_marco = df_marco.dropna(subset=[col_segs])
    df_marco = df_marco[df_marco[col_segs] > 0]
    df_marco = df_marco[df_marco[col_mes].astype(str) == marco_val]
else:
    df_marco = df.copy()

# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────
st.markdown('<div class="titulo">🚒 CBMAM — Quantidade de SEGs por OBM</div>', unsafe_allow_html=True)

if tem_mes and len(meses_ativos) == 1:
    is_marco = marco_val and meses_ativos[0] == marco_val
    if is_marco:
        st.markdown(
            '<div class="badge-marco">📅 MARÇO — Mês de referência principal</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(f'<div class="subtitulo">📅 {meses_ativos[0]}</div>', unsafe_allow_html=True)
elif tem_mes:
    st.markdown(f'<div class="subtitulo">📅 {", ".join(meses_ativos)}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="subtitulo">📅 Todos os registros</div>', unsafe_allow_html=True)

st.markdown("---")

if df.empty:
    st.error("Nenhum dado encontrado. Ajuste os filtros na sidebar.")
    st.stop()

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
total_segs   = int(df[col_segs].sum())
media_segs   = round(df[col_segs].mean(), 1)
total_obms   = df[col_obm].nunique()
rank_geral   = df.groupby(col_obm)[col_segs].sum()
obm_lider    = rank_geral.idxmax()
val_lider    = int(rank_geral.max())
total_marco  = int(df_marco[col_segs].sum()) if not df_marco.empty else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("⏱️ Total SEGs",        f"{total_segs:,}".replace(",", "."))
c2.metric("📅 SEGs em Março",     f"{total_marco:,}".replace(",", "."))
c3.metric("🏢 OBMs",              total_obms)
c4.metric("📊 Média por Registro",f"{media_segs:.1f}")
c5.metric("🥇 OBM Líder",         obm_lider)

st.markdown("---")

# ─────────────────────────────────────────────
# ABAS
# ─────────────────────────────────────────────
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "🏆 Ranking de OBMs",
    "📅 Março em Destaque",
    "📊 Comparativo por Mês",
    "🔥 Análise Detalhada",
    "📋 Dados Brutos"
])

# ══════════════════════════════════════════════
# ABA 1 — RANKING DE OBMs
# ══════════════════════════════════════════════
with aba1:
    st.subheader(f"🏆 Top {top_n} OBMs — Maior quantidade de SEGs")

    df_rank = (
        df.groupby(col_obm)[col_segs]
        .sum()
        .reset_index()
        .rename(columns={col_obm: "OBM", col_segs: "Total SEGs"})
        .sort_values("Total SEGs", ascending=False)
        .reset_index(drop=True)
    )
    df_rank.index += 1
    df_rank["% do Total"] = (df_rank["Total SEGs"] / df_rank["Total SEGs"].sum() * 100).round(1)
    top_rank = df_rank.head(top_n)

    col_g1, col_g2 = st.columns([3, 2])

    with col_g1:
        fig_bar = px.bar(
            top_rank.sort_values("Total SEGs"),
            x="Total SEGs", y="OBM",
            orientation="h",
            color="Total SEGs",
            color_continuous_scale="Reds",
            text="Total SEGs",
            title=f"Top {top_n} OBMs — Total de SEGs"
        )
        fig_bar.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_bar.update_layout(
            height=480,
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            yaxis_title="", xaxis_title="Quantidade de SEGs"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        fig_pie = px.pie(
            top_rank,
            names="OBM", values="Total SEGs",
            hole=0.4,
            title=f"Distribuição % — Top {top_n} OBMs",
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(height=480, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # Treemap
    fig_tree = px.treemap(
        df_rank.head(20),
        path=["OBM"], values="Total SEGs",
        color="Total SEGs",
        color_continuous_scale="Reds",
        title="Treemap — Proporção de SEGs por OBM (Top 20)"
    )
    fig_tree.update_layout(height=380)
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")

    # Funil
    fig_funil = go.Figure(go.Funnel(
        y=top_rank["OBM"],
        x=top_rank["Total SEGs"],
        textinfo="value+percent initial",
        marker=dict(color=px.colors.sequential.Reds_r[:len(top_rank)])
    ))
    fig_funil.update_layout(title=f"Funil de Demanda — Top {top_n} OBMs", height=420)
    st.plotly_chart(fig_funil, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Ranking Completo por OBM")
    df_rank_exib = df_rank.copy()
    df_rank_exib["Total SEGs"]  = df_rank_exib["Total SEGs"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    df_rank_exib["% do Total"]  = df_rank_exib["% do Total"].astype(str) + "%"
    st.dataframe(df_rank_exib, use_container_width=True, height=380)

    st.success(
        f"🥇 **{obm_lider}** registrou a maior quantidade de SEGs: "
        f"**{val_lider:,}** ({df_rank[df_rank['OBM'] == obm_lider]['% do Total'].values[0]}% do total)"
        .replace(",", ".")
    )

# ══════════════════════════════════════════════
# ABA 2 — MARÇO EM DESTAQUE
# ══════════════════════════════════════════════
with aba2:
    st.markdown(
        '<div class="badge-marco">📅 MARÇO — Análise detalhada do mês de referência</div>',
        unsafe_allow_html=True
    )

    if df_marco.empty:
        st.warning("Nenhum dado de março encontrado. Verifique a coluna de mês na sidebar.")
    else:
        total_m  = int(df_marco[col_segs].sum())
        media_m  = round(df_marco[col_segs].mean(), 1)
        obms_m   = df_marco[col_obm].nunique()
        rank_m   = df_marco.groupby(col_obm)[col_segs].sum()
        lider_m  = rank_m.idxmax()
        val_m    = int(rank_m.max())

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("⏱️ Total SEGs — Março",   f"{total_m:,}".replace(",", "."))
        k2.metric("📊 Média por Registro",    f"{media_m:.1f}")
        k3.metric("🏢 OBMs com SEGs",         obms_m)
        k4.metric("🥇 OBM com Mais SEGs",     lider_m)

        st.markdown("---")

        df_rank_m = (
            df_marco.groupby(col_obm)[col_segs]
            .sum()
            .reset_index()
            .rename(columns={col_obm: "OBM", col_segs: "Total SEGs"})
            .sort_values("Total SEGs", ascending=False)
            .reset_index(drop=True)
        )
        df_rank_m.index += 1
        df_rank_m["% do Mês"] = (df_rank_m["Total SEGs"] / df_rank_m["Total SEGs"].sum() * 100).round(1)

        col_m1, col_m2 = st.columns([3, 2])

        with col_m1:
            st.subheader(f"🏆 Top {top_n} OBMs em Março")
            fig_bar_m = px.bar(
                df_rank_m.head(top_n).sort_values("Total SEGs"),
                x="Total SEGs", y="OBM",
                orientation="h",
                color="Total SEGs",
                color_continuous_scale="Reds",
                text="Total SEGs",
                title="Ranking de SEGs por OBM — Março"
            )
            fig_bar_m.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_bar_m.update_layout(
                height=440,
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                yaxis_title="", xaxis_title="SEGs"
            )
            st.plotly_chart(fig_bar_m, use_container_width=True)

        with col_m2:
            st.subheader("📋 Tabela — Março")
            df_tab_m = df_rank_m.copy()
            df_tab_m["Total SEGs"] = df_tab_m["Total SEGs"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
            df_tab_m["% do Mês"]   = df_tab_m["% do Mês"].astype(str) + "%"
            st.dataframe(df_tab_m, use_container_width=True, height=440)

        st.markdown("---")

        fig_tree_m = px.treemap(
            df_rank_m,
            path=["OBM"], values="Total SEGs",
            color="Total SEGs",
            color_continuous_scale="Reds",
            title="Treemap de SEGs por OBM — Março"
        )
        fig_tree_m.update_layout(height=380)
        st.plotly_chart(fig_tree_m, use_container_width=True)

        # Março vs demais meses
        if tem_mes and len(meses_lista) > 1:
            st.markdown("---")
            st.subheader("📊 Março vs Demais Meses")

            df_todos = df_raw.copy()
            df_todos[col_segs] = pd.to_numeric(df_todos[col_segs], errors="coerce")
            df_todos = df_todos.dropna(subset=[col_segs])
            df_todos = df_todos[df_todos[col_segs] > 0]

            totais_mes = (
                df_todos.groupby(col_mes)[col_segs]
                .sum().reset_index()
                .rename(columns={col_mes: "Mês", col_segs: "Total SEGs"})
                .sort_values("Total SEGs", ascending=False)
            )
            totais_mes["Destaque"] = totais_mes["Mês"].apply(
                lambda x: "🔴 Março" if x == marco_val else "Outros meses"
            )

            fig_comp = px.bar(
                totais_mes,
                x="Mês", y="Total SEGs",
                color="Destaque",
                color_discrete_map={"🔴 Março": "#cc0000", "Outros meses": "#aaaaaa"},
                text="Total SEGs",
                title="SEGs por Mês — Março em destaque"
            )
            fig_comp.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_comp.update_layout(
                height=380,
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_tickangle=-30
            )
            st.plotly_chart(fig_comp, use_container_width=True)

        st.success(
            f"🥇 Em março, **{lider_m}** foi a OBM com maior quantidade de SEGs: "
            f"**{val_m:,}** ({df_rank_m[df_rank_m['OBM'] == lider_m]['% do Mês'].values[0]}% do mês)"
            .replace(",", ".")
        )

# ══════════════════════════════════════════════
# ABA 3 — COMPARATIVO POR MÊS
# ══════════════════════════════════════════════
with aba3:
    st.subheader("📅 Comparativo de SEGs entre Meses")

    if not tem_mes:
        st.info("Configure a coluna de mês na sidebar para habilitar esta análise.")
    else:
        df_todos = df_raw.copy()
        df_todos[col_segs] = pd.to_numeric(df_todos[col_segs], errors="coerce")
        df_todos = df_todos.dropna(subset=[col_segs])
        df_todos = df_todos[df_todos[col_segs] > 0]
        if filtro_obm:
            df_todos = df_todos[df_todos[col_obm].astype(str).str.contains(filtro_obm, case=False, na=False)]

        # Total por mês
        totais = (
            df_todos.groupby(col_mes)[col_segs]
            .sum().reset_index()
            .rename(columns={col_mes: "Mês", col_segs: "Total SEGs"})
            .sort_values("Total SEGs", ascending=False)
        )
        totais["Destaque"] = totais["Mês"].apply(
            lambda x: "🔴 Março" if x == marco_val else "Outros"
        )

        fig_mes = px.bar(
            totais,
            x="Mês", y="Total SEGs",
            color="Destaque",
            color_discrete_map={"🔴 Março": "#cc0000", "Outros": "#888888"},
            text="Total SEGs",
            title="Total de SEGs por Mês"
        )
        fig_mes.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_mes.update_layout(
            height=380,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig_mes, use_container_width=True)

        st.markdown("---")
        st.subheader(f"🌡️ Heatmap — Top {top_n} OBMs × Meses")

        pivot = df_todos.pivot_table(
            index=col_obm, columns=col_mes,
            values=col_segs, aggfunc="sum", fill_value=0
        )
        pivot["_total"] = pivot.sum(axis=1)
        pivot = pivot.nlargest(top_n, "_total").drop(columns="_total")

        fig_heat = px.imshow(
            pivot,
            color_continuous_scale="Reds",
            aspect="auto",
            title=f"Heatmap SEGs — Top {top_n} OBMs × Meses",
            text_auto=True
        )
        fig_heat.update_layout(height=max(380, top_n * 40))
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("---")
        st.subheader(f"📈 Evolução Mensal — Top {top_n} OBMs")

        top_obms = df_todos.groupby(col_obm)[col_segs].sum().nlargest(top_n).index.tolist()
        df_evol  = (
            df_todos[df_todos[col_obm].isin(top_obms)]
            .groupby([col_mes, col_obm])[col_segs]
            .sum().reset_index()
            .rename(columns={col_mes: "Mês", col_obm: "OBM", col_segs: "SEGs"})
        )

        fig_line = px.line(
            df_evol,
            x="Mês", y="SEGs", color="OBM",
            markers=True,
            title=f"Evolução Mensal — Top {top_n} OBMs"
        )
        fig_line.update_layout(height=440, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_line, use_container_width=True)

# ══════════════════════════════════════════════
# ABA 4 — ANÁLISE DETALHADA
# ══════════════════════════════════════════════
with aba4:
    st.subheader("🔥 Estatísticas de SEGs por OBM")

    df_stats = (
        df.groupby(col_obm)[col_segs]
        .agg(["sum", "mean", "max", "min", "count"])
        .reset_index()
        .rename(columns={
            col_obm: "OBM",
            "sum": "Total SEGs", "mean": "Média",
            "max": "Máximo",    "min": "Mínimo",
            "count": "Registros"
        })
        .sort_values("Total SEGs", ascending=False)
        .round(2)
    )
    st.dataframe(df_stats, use_container_width=True, height=380)

    st.markdown("---")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        fig_hist = px.histogram(
            df, x=col_segs, nbins=30,
            color_discrete_sequence=["#cc0000"],
            title="Histograma — Distribuição de SEGs"
        )
        fig_hist.update_layout(height=340, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_d2:
        df_pie = (
            df.groupby(col_obm)[col_segs]
            .sum().reset_index()
            .sort_values(col_segs, ascending=False)
        )
        fig_pie2 = px.pie(
            df_pie.head(12),
            names=col_obm, values=col_segs,
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Reds_r,
            title="Distribuição % — Top 12 OBMs"
        )
        fig_pie2.update_traces(textinfo="percent+label")
        fig_pie2.update_layout(height=340, showlegend=False)
        st.plotly_chart(fig_pie2, use_container_width=True)

    # Boxplot
    if df.groupby(col_obm).size().max() > 1:
        st.markdown("---")
        st.subheader(f"📦 Boxplot — Top {top_n} OBMs")
        top_box = df.groupby(col_obm)[col_segs].sum().nlargest(top_n).index.tolist()
        df_box  = df[df[col_obm].isin(top_box)]

        fig_box = px.box(
            df_box, x=col_obm, y=col_segs,
            color=col_obm,
            title=f"Variação de SEGs — Top {top_n} OBMs"
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
        busca = st.text_input("🔍 Buscar:")
    with col_b2:
        st.metric("Registros", len(df))
    with col_b3:
        st.metric("Total SEGs", f"{total_segs:,}".replace(",", "."))

    df_exib = df.copy()
    if busca:
        mask    = df_exib.apply(lambda r: r.astype(str).str.contains(busca, case=False, na=False).any(), axis=1)
        df_exib = df_exib[mask]
        st.caption(f"{len(df_exib)} resultado(s)")

    st.dataframe(df_exib, use_container_width=True, height=420)

    csv_bytes = df_exib.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Baixar CSV filtrado",
        data=csv_bytes,
        file_name="cbmam_segs_obm.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("📊 Estatísticas Descritivas")
    st.dataframe(df[[col_segs]].describe().round(2), use_container_width=True)

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.82rem'>"
    "Dashboard CBMAM · SEGs por OBM · Foco: Março · relatorio.csv · Python + Streamlit"
    "</div>",
    unsafe_allow_html=True
)
