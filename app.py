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
    page_title="Dashboard CBMAM - Horas de SEG",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        section[data-testid="stSidebar"] { background-color: #1a1a2e; }
        section[data-testid="stSidebar"] * { color: white !important; }
        .titulo { color: #cc0000; font-size: 2rem; font-weight: bold; text-align: center; }
        .subtitulo { color: #555; font-size: 0.95rem; text-align: center; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
ARQUIVO = "relatorio.csv"

# Mapeamento das abas de militares (nome da aba → mês legível)
ABAS_MILITARES = {
    "RELAÇÃO DOS MIL.": "Relação Geral",
    "MILITARES MARÇO":  "Março 2025",
    "MILITARES ABRIL":  "Abril 2025",
    "MILITARES MAIO":   "Maio 2025",
    "MILITARES MARÇO 2026": "Março 2026",
}

# Mapeamento das abas de demonstrativo (totais por OBM)
ABAS_DEMONSTRATIVO = {
    "DEMONSTRATIVO FEV":      "Fevereiro 2025",
    "DEMONSTRATIVO MARÇO":    "Março 2025",
    "DEMONSTRATIVO ABRIL":    "Abril 2025",
    "DEMONSTRATIVO MARÇO 2026": "Março 2026",
}

# ─────────────────────────────────────────────
# FUNÇÕES DE LEITURA
# ─────────────────────────────────────────────
@st.cache_data
def ler_aba_militares(arquivo, nome_aba):
    """
    Lê aba de militares. Colunas esperadas:
    Nome completo | Nome de guerra | OBM/OM | Horas
    """
    df = pd.read_excel(arquivo, sheet_name=nome_aba, header=0)
    df.columns = df.columns.astype(str).str.strip()

    # Renomeia para padrão
    cols = df.columns.tolist()
    mapa = {}
    for i, c in enumerate(cols):
        cl = c.lower()
        if i == 0 or "nome" in cl or "militar" in cl:
            mapa[c] = "NOME"
        elif "guerra" in cl or "apelido" in cl:
            mapa[c] = "GUERRA"
        elif "om" in cl or "obm" in cl or "unidade" in cl or "bi" in cl:
            mapa[c] = "OM"
        elif "hora" in cl or "hs" in cl or "h " in cl:
            mapa[c] = "HORAS"

    # Se o mapa ficou vazio, usa posicional
    if len(mapa) < 2:
        if len(cols) >= 4:
            df.columns = ["NOME", "GUERRA", "OM", "HORAS"] + list(cols[4:])
        elif len(cols) == 3:
            df.columns = ["NOME", "OM", "HORAS"]
    else:
        df = df.rename(columns=mapa)

    # Garante colunas mínimas
    for col in ["NOME", "OM", "HORAS"]:
        if col not in df.columns:
            df[col] = np.nan

    df["HORAS"] = pd.to_numeric(df["HORAS"], errors="coerce")
    df.dropna(subset=["HORAS"], inplace=True)
    df = df[df["HORAS"] > 0]

    # Remove linha de total
    if "NOME" in df.columns:
        df = df[~df["NOME"].astype(str).str.lower().str.contains("total", na=False)]

    df["OM"] = df["OM"].astype(str).str.strip()
    df["NOME"] = df["NOME"].astype(str).str.strip()
    df.reset_index(drop=True, inplace=True)
    return df


@st.cache_data
def ler_demonstrativo(arquivo, nome_aba):
    """
    Lê aba de demonstrativo (totais por OBM).
    Retorna DataFrame com colunas: OBM, HORAS, GRUPO (CBC/CBI)
    """
    df_raw = pd.read_excel(arquivo, sheet_name=nome_aba, header=None)
    registros = []
    grupo_atual = "Geral"

    for _, row in df_raw.iterrows():
        vals = [str(v).strip() for v in row.values]
        txt = " ".join(vals).lower()

        if "capital" in txt:
            grupo_atual = "CBC - Capital"
        elif "interior" in txt or "regional" in txt:
            grupo_atual = "CBI - Interior"

        # Tenta capturar linha OBM | Horas
        for i, v in enumerate(vals):
            if v.lower() in ["nan", "", "obm", "unnamed"]:
                continue
            # Procura o número na mesma linha
            for j, v2 in enumerate(vals):
                if j != i:
                    try:
                        num = float(v2.replace(",", "."))
                        if num > 0 and num < 99999 and v.lower() != "total":
                            registros.append({
                                "OBM": v,
                                "HORAS": num,
                                "GRUPO": grupo_atual
                            })
                            break
                    except:
                        pass
            break  # pega só o primeiro par válido por linha

    df_demo = pd.DataFrame(registros).drop_duplicates(subset=["OBM"])
    df_demo = df_demo[~df_demo["OBM"].str.lower().str.contains("obm|horas|nan|total|comando", na=False)]
    df_demo["HORAS"] = pd.to_numeric(df_demo["HORAS"], errors="coerce")
    df_demo.dropna(subset=["HORAS"], inplace=True)
    df_demo = df_demo[df_demo["HORAS"] > 0]
    return df_demo


@st.cache_data
def listar_abas(arquivo):
    xl = pd.ExcelFile(arquivo)
    return xl.sheet_names


# ─────────────────────────────────────────────
# CARREGA ESTRUTURA
# ─────────────────────────────────────────────
try:
    todas_abas = listar_abas(ARQUIVO)
except FileNotFoundError:
    st.error(f"❌ Arquivo '{ARQUIVO}' não encontrado na pasta do app.py.")
    st.stop()

meses_disponiveis = {v: k for k, v in ABAS_MILITARES.items() if k in todas_abas}
meses_demo_disp   = {v: k for k, v in ABAS_DEMONSTRATIVO.items() if k in todas_abas}

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚒 CBMAM")
    st.markdown("### Dashboard de SEGs")
    st.markdown("---")

    st.markdown("**📅 Filtro por Mês**")

    modo = st.radio(
        "Modo:",
        ["📄 Mês específico", "📚 Múltiplos meses", "🗂️ Todos os meses"],
        index=0
    )

    lista_meses = list(meses_disponiveis.keys())

    if modo == "📄 Mês específico":
        mes_escolhido = st.selectbox("Selecione o mês:", lista_meses)
        meses_ativos = [mes_escolhido]

    elif modo == "📚 Múltiplos meses":
        meses_ativos = st.multiselect(
            "Selecione os meses:",
            lista_meses,
            default=lista_meses[:2] if len(lista_meses) >= 2 else lista_meses
        )
        if not meses_ativos:
            meses_ativos = [lista_meses[0]]

    else:
        meses_ativos = lista_meses
        st.info(f"✅ {len(lista_meses)} meses selecionados")

    st.markdown("---")
    st.markdown("**🏆 Top N Locais**")
    top_n = st.slider("Exibir top:", 5, 20, 10)

    st.markdown("---")
    st.markdown("**🔍 Filtrar por OBM/OM**")
    filtro_obm = st.text_input("Digite parte do nome da OBM:")

# ─────────────────────────────────────────────
# CARREGA E CONSOLIDA DADOS
# ─────────────────────────────────────────────
frames = []
for mes in meses_ativos:
    nome_aba = meses_disponiveis[mes]
    try:
        df_tmp = ler_aba_militares(ARQUIVO, nome_aba)
        df_tmp["MES"] = mes
        frames.append(df_tmp)
    except Exception as e:
        st.warning(f"Erro ao ler aba '{nome_aba}': {e}")

if not frames:
    st.error("Nenhum dado carregado. Verifique as abas do arquivo.")
    st.stop()

df = pd.concat(frames, ignore_index=True)

# Aplica filtro de OBM se digitado
if filtro_obm:
    df = df[df["OM"].str.contains(filtro_obm, case=False, na=False)]

# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────
st.markdown('<div class="titulo">🚒 CBMAM — Dashboard de Horas de SEG</div>', unsafe_allow_html=True)
periodo_txt = ", ".join(meses_ativos) if len(meses_ativos) <= 3 else f"{len(meses_ativos)} meses selecionados"
st.markdown(f'<div class="subtitulo">Período: {periodo_txt} · Arquivo: {ARQUIVO}</div>', unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────
# MÉTRICAS GERAIS
# ─────────────────────────────────────────────
total_horas    = int(df["HORAS"].sum())
total_militares = df["NOME"].nunique()
total_obm      = df["OM"].nunique()
media_horas    = round(df["HORAS"].mean(), 1)

c1, c2, c3, c4 = st.columns(4)
c1.metric("⏱️ Total de Horas", f"{total_horas:,}".replace(",", "."))
c2.metric("👥 Militares Únicos", total_militares)
c3.metric("🏢 OBMs/OMs", total_obm)
c4.metric("📊 Média de Horas", media_horas)

st.markdown("---")

# ─────────────────────────────────────────────
# ABAS PRINCIPAIS
# ─────────────────────────────────────────────
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "🏆 Ranking de Locais",
    "📈 Evolução Mensal",
    "👤 Militares",
    "📋 Dados Brutos",
    "📊 Demonstrativos Oficiais"
])

# ══════════════════════════════════════════════
# ABA 1 — RANKING DE LOCAIS (quais precisaram de mais SEGs)
# ══════════════════════════════════════════════
with aba1:
    st.subheader(f"🏆 Locais que mais precisaram de SEGs — Top {top_n}")

    ranking = (
        df.groupby("OM")["HORAS"]
        .sum()
        .reset_index()
        .rename(columns={"OM": "Local", "HORAS": "Total de Horas"})
        .sort_values("Total de Horas", ascending=False)
        .reset_index(drop=True)
    )
    ranking.index += 1
    ranking["% do Total"] = (ranking["Total de Horas"] / ranking["Total de Horas"].sum() * 100).round(1)
    ranking["Posição"] = ranking.index

    top_ranking = ranking.head(top_n)

    col_g1, col_g2 = st.columns([3, 2])

    with col_g1:
        fig_bar = px.bar(
            top_ranking.sort_values("Total de Horas"),
            x="Total de Horas",
            y="Local",
            orientation="h",
            color="Total de Horas",
            color_continuous_scale="Reds",
            text="Total de Horas",
            title=f"Top {top_n} Locais — Total de Horas de SEG"
        )
        fig_bar.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_bar.update_layout(
            height=450,
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            coloraxis_showscale=False,
            yaxis_title="",
            xaxis_title="Horas"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        fig_pie = px.pie(
            top_ranking,
            names="Local",
            values="Total de Horas",
            title=f"Distribuição % — Top {top_n}",
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(height=450, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # Treemap
    fig_tree = px.treemap(
        ranking.head(20),
        path=["Local"],
        values="Total de Horas",
        color="Total de Horas",
        color_continuous_scale="Reds",
        title="Treemap — Proporção de Horas por Local (Top 20)"
    )
    fig_tree.update_layout(height=380)
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Tabela de Ranking Completo")

    st.dataframe(
        ranking[["Posição", "Local", "Total de Horas", "% do Total"]],
        use_container_width=True,
        height=350
    )

    # Destaque: 1º lugar
    primeiro = ranking.iloc[0]
    st.success(
        f"🥇 **{primeiro['Local']}** foi o local com mais horas de SEG: "
        f"**{int(primeiro['Total de Horas']):,}h** ({primeiro['% do Total']}% do total)"
    )


# ══════════════════════════════════════════════
# ABA 2 — EVOLUÇÃO MENSAL
# ══════════════════════════════════════════════
with aba2:
    st.subheader("📈 Evolução de Horas por Mês")

    if len(meses_ativos) > 1:
        # Totais por mês
        df_mensal = (
            df.groupby("MES")["HORAS"]
            .sum()
            .reset_index()
            .rename(columns={"MES": "Mês", "HORAS": "Total de Horas"})
        )
        # Mantém ordem original
        ordem = [m for m in lista_meses if m in meses_ativos]
        df_mensal["Mês"] = pd.Categorical(df_mensal["Mês"], categories=ordem, ordered=True)
        df_mensal = df_mensal.sort_values("Mês")

        fig_line = px.line(
            df_mensal,
            x="Mês", y="Total de Horas",
            markers=True,
            title="Total de Horas de SEG por Mês",
            color_discrete_sequence=["#cc0000"]
        )
        fig_line.update_traces(line_width=3, marker_size=10)
        fig_line.update_layout(height=380, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("---")

        # Por OBM e mês — heatmap
        st.subheader("🌡️ Mapa de Calor — Horas por OBM × Mês")

        pivot = df.pivot_table(
            index="OM", columns="MES", values="HORAS",
            aggfunc="sum", fill_value=0
        )
        # Filtra top OBMs
        pivot["_total"] = pivot.sum(axis=1)
        pivot = pivot.nlargest(top_n, "_total").drop(columns="_total")

        fig_heat = px.imshow(
            pivot,
            color_continuous_scale="Reds",
            title=f"Heatmap — Top {top_n} OBMs × Meses",
            aspect="auto",
            text_auto=True
        )
        fig_heat.update_layout(height=max(350, top_n * 35))
        st.plotly_chart(fig_heat, use_container_width=True)

    else:
        # Só um mês: mostra distribuição por OBM
        st.info(f"Mês selecionado: **{meses_ativos[0]}**")
        df_obm = (
            df.groupby("OM")["HORAS"]
            .sum()
            .reset_index()
            .sort_values("HORAS", ascending=False)
            .head(top_n)
        )
        fig_bar2 = px.bar(
            df_obm,
            x="OM", y="HORAS",
            color="HORAS",
            color_continuous_scale="Reds",
            title=f"Horas por OBM — {meses_ativos[0]}"
        )
        fig_bar2.update_layout(height=400, plot_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-40)
        st.plotly_chart(fig_bar2, use_container_width=True)

    # Variação entre meses
    if len(meses_ativos) >= 2:
        st.markdown("---")
        st.subheader("📊 Variação entre Meses por OBM")

        df_var = df.groupby(["MES", "OM"])["HORAS"].sum().reset_index()
        top_obms = df.groupby("OM")["HORAS"].sum().nlargest(8).index.tolist()
        df_var_top = df_var[df_var["OM"].isin(top_obms)]

        fig_multi = px.line(
            df_var_top,
            x="MES", y="HORAS", color="OM",
            markers=True,
            title="Evolução Mensal — Top 8 OBMs"
        )
        fig_multi.update_layout(height=400, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_multi, use_container_width=True)


# ══════════════════════════════════════════════
# ABA 3 — MILITARES
# ══════════════════════════════════════════════
with aba3:
    st.subheader("👤 Militares com Mais Horas de SEG")

    df_mil = (
        df.groupby(["NOME", "OM"])["HORAS"]
        .sum()
        .reset_index()
        .sort_values("HORAS", ascending=False)
        .reset_index(drop=True)
    )
    df_mil.index += 1

    col_m1, col_m2 = st.columns([2, 3])

    with col_m1:
        st.markdown(f"**Top {top_n} militares com mais horas:**")
        st.dataframe(df_mil.head(top_n)[["NOME", "OM", "HORAS"]], use_container_width=True, height=380)

    with col_m2:
        fig_mil = px.bar(
            df_mil.head(top_n).sort_values("HORAS"),
            x="HORAS", y="NOME",
            orientation="h",
            color="OM",
            title=f"Top {top_n} Militares por Horas de SEG",
            text="HORAS"
        )
        fig_mil.update_traces(textposition="outside")
        fig_mil.update_layout(
            height=450, plot_bgcolor="rgba(0,0,0,0)",
            yaxis_title="", xaxis_title="Horas"
        )
        st.plotly_chart(fig_mil, use_container_width=True)

    st.markdown("---")

    # Distribuição por OBM — quantidade de militares
    st.subheader("🏢 Militares por OBM")
    df_qtd = df.groupby("OM")["NOME"].nunique().reset_index()
    df_qtd.columns = ["OBM", "Qtd. Militares"]
    df_qtd = df_qtd.sort_values("Qtd. Militares", ascending=False).head(top_n)

    fig_qtd = px.bar(
        df_qtd,
        x="OBM", y="Qtd. Militares",
        color="Qtd. Militares",
        color_continuous_scale="Blues",
        title=f"Quantidade de Militares por OBM — Top {top_n}",
        text="Qtd. Militares"
    )
    fig_qtd.update_traces(textposition="outside")
    fig_qtd.update_layout(
        height=380, plot_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-40, coloraxis_showscale=False
    )
    st.plotly_chart(fig_qtd, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Busca de Militar")
    busca_mil = st.text_input("Pesquisar por nome:")
    if busca_mil:
        resultado = df_mil[df_mil["NOME"].str.contains(busca_mil, case=False, na=False)]
        st.dataframe(resultado, use_container_width=True)
    else:
        st.caption("Digite o nome acima para buscar.")


# ══════════════════════════════════════════════
# ABA 4 — DADOS BRUTOS
# ══════════════════════════════════════════════
with aba4:
    st.subheader("📋 Dados Brutos")

    col_b1, col_b2, col_b3 = st.columns([3, 1, 1])
    with col_b1:
        busca = st.text_input("🔍 Buscar em qualquer campo:")
    with col_b2:
        st.metric("Total de registros", len(df))
    with col_b3:
        st.metric("Total de horas", f"{int(df['HORAS'].sum()):,}".replace(",", "."))

    df_exib = df.drop(columns=["MES"], errors="ignore") if len(meses_ativos) == 1 else df.copy()

    if busca:
        mask = df_exib.apply(
            lambda r: r.astype(str).str.contains(busca, case=False, na=False).any(), axis=1
        )
        df_exib = df_exib[mask]
        st.caption(f"{len(df_exib)} resultado(s) encontrado(s)")

    st.dataframe(df_exib, use_container_width=True, height=420)

    csv = df_exib.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Baixar CSV filtrado",
        data=csv,
        file_name="cbmam_segs.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("📊 Estatísticas Descritivas")
    st.dataframe(df[["HORAS"]].describe().round(2), use_container_width=True)


# ══════════════════════════════════════════════
# ABA 5 — DEMONSTRATIVOS OFICIAIS
# ══════════════════════════════════════════════
with aba5:
    st.subheader("📊 Demonstrativos Oficiais de Horas Processadas")

    mes_demo = st.selectbox(
        "Selecione o demonstrativo:",
        list(meses_demo_disp.keys())
    )

    try:
        df_demo = ler_demonstrativo(ARQUIVO, meses_demo_disp[mes_demo])

        st.markdown(f"**{mes_demo}** — total de OBMs encontradas: {len(df_demo)}")

        col_d1, col_d2 = st.columns([2, 3])

        with col_d1:
            st.dataframe(
                df_demo[["OBM", "HORAS", "GRUPO"]].sort_values("HORAS", ascending=False),
                use_container_width=True,
                height=420
            )

        with col_d2:
            fig_demo = px.bar(
                df_demo.sort_values("HORAS", ascending=False),
                x="OBM", y="HORAS",
                color="GRUPO",
                title=f"Horas por OBM — {mes_demo}",
                text="HORAS",
                color_discrete_map={
                    "CBC - Capital": "#cc0000",
                    "CBI - Interior": "#1a6fbf",
                    "Geral": "#888"
                }
            )
            fig_demo.update_traces(textposition="outside")
            fig_demo.update_layout(
                height=450,
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_tickangle=-40
            )
            st.plotly_chart(fig_demo, use_container_width=True)

        total_demo = int(df_demo["HORAS"].sum())
        st.success(f"✅ Total de horas processadas em {mes_demo}: **{total_demo:,}h**".replace(",", "."))

    except Exception as e:
        st.warning(f"Não foi possível carregar o demonstrativo: {e}")


# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.82rem'>"
    f"Dashboard CBMAM · {ARQUIVO} · Python + Streamlit"
    "</div>",
    unsafe_allow_html=True
)
