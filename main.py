"""
main.py
Dashboard Executivo de Estoque e Operações — Tidimar Hospitalar
Tema dark nativo Plotly, estrutura modular com data_processing.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data_processing import preprocess, get_kpis, producao_por_separador, producao_por_conferente, serie_mensal


# ============================================================================
# Configuração da página Streamlit
# ============================================================================

st.set_page_config(
    page_title="Dashboard Tidimar Hospitalar",
    page_icon="[DASH]",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================*
# CSS customizado para cards estilizados em tema dark
# ============================================================================*

st.markdown("""
<style>
    /* Fundo geral e fonte */
    body {
        background-color: #0e1117;
        color: #e6edf3;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    }

    /* Remove padding padrão */
    .main {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Cards de KPI: fundo escuro, borda arredondada, sombra sutil */
    .kpi-card {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #58a6ff;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
        margin-bottom: 1rem;
    }

    .kpi-card.separador {
        border-left-color: #76C043;
    }

    .kpi-card.conferente {
        border-left-color: #005F5F;
    }

    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #e6edf3;
        margin-bottom: 0.5rem;
    }

    .kpi-label {
        font-size: 0.875rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Seções de gráficos */
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e6edf3;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #30363d;
        padding-bottom: 0.5rem;
    }

    /* Separadores entre seções */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #30363d, transparent);
        margin: 2rem 0;
    }

    /* Responsivo em mobile */
    @media (max-width: 768px) {
        .kpi-value {
            font-size: 1.75rem;
        }
        .main {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Header e Upload de arquivo
# ============================================================================

st.markdown("# Dashboard Executivo — Tidimar Hospitalar")
st.markdown(
    "**Monitoramento em tempo real** de separação e conferência de pedidos | "
    "Últimas métricas operacionais"
)

# Sidebar: upload de arquivo
with st.sidebar:
    st.header("Configuracoes")
    uploaded_file = st.file_uploader(
        "Carregar planilha (BASE_Dashboard.xlsx)",
        type=['xlsx', 'xls'],
        help="Arquivo Excel com aba 'BASE' contendo dados de pedidos"
    )

    if uploaded_file:
        st.success("✅ Arquivo carregado com sucesso!")
    else:
        st.warning("[ATENCAO] Nenhum arquivo selecionado")


# ============================================================================
# Lógica principal: carregar, processar e render
# ============================================================================

if uploaded_file is None:
    st.info(
        "=> Clique em **'Carregar planilha'** no painel esquerdo para começar.\n\n"
        "Esperado: arquivo Excel com aba chamada **'BASE'** contendo colunas: "
        "DATA, PEDIDO, SEPARADOR, QTD ITENS(separador), CONFERENTE, QTD ITENS(conferente)"
    )
    st.stop()

# Tenta processar arquivo; se falhar, mostra erro e interrompe
try:
    df = preprocess(uploaded_file)
    st.sidebar.success(f"✅ Processados {len(df)} registros")
except Exception as e:
    st.error(f"❌ Erro ao processar arquivo:\n\n{str(e)}")
    st.stop()


# ============================================================================
# Filtros (Sidebar)
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.subheader("Filtros")

# Extrai meses únicos (ordenados) e separadores/conferentes únicos
meses_unicos = sorted(df['MES_NUM'].unique())
meses_opcoes = ["Todos"] + [f"{df[df['MES_NUM'] == m]['MES_NOME'].iloc[0]}" for m in meses_unicos]

meses_selecionados = st.sidebar.multiselect(
    "Mês",
    options=meses_opcoes,
    default=["Todos"]
)

separadores_opcoes = ["Todos"] + sorted(df['SEPARADOR'].unique().tolist())
separadores_selecionados = st.sidebar.multiselect(
    "Separador",
    options=separadores_opcoes,
    default=["Todos"]
)

conferentes_opcoes = ["Todos"] + sorted(df['CONFERENTE'].unique().tolist())
conferentes_selecionados = st.sidebar.multiselect(
    "Conferente",
    options=conferentes_opcoes,
    default=["Todos"]
)

# Aplica filtros ao DataFrame
df_filtrado = df.copy()

# Filtro de mês
if "Todos" not in meses_selecionados:
    mes_nums = [
        m for m in meses_unicos
        if df[df['MES_NUM'] == m]['MES_NOME'].iloc[0] in meses_selecionados
    ]
    df_filtrado = df_filtrado[df_filtrado['MES_NUM'].isin(mes_nums)]

# Filtro de separador
if "Todos" not in separadores_selecionados:
    df_filtrado = df_filtrado[df_filtrado['SEPARADOR'].isin(separadores_selecionados)]

# Filtro de conferente
if "Todos" not in conferentes_selecionados:
    df_filtrado = df_filtrado[df_filtrado['CONFERENTE'].isin(conferentes_selecionados)]

# Mostra contagem após filtros
st.sidebar.info(f"📌 {len(df_filtrado)} registros após filtros ({len(df)} total)")


# ============================================================================
# KPIs Principais (4 Cards no topo)
# ============================================================================

st.markdown("### Indicadores Principais")

# Calcula KPIs com dados filtrados (todos os dados, incluindo outliers)
kpis = get_kpis(df_filtrado)

# Layout: 4 colunas para os 4 cards
col1, col2, col3, col4 = st.columns(4)

# Card 1: Total de Pedidos
with col1:
    # Gera mini sparkline de tendência mensal
    serie_pedidos = df_filtrado.groupby('MES_NUM').size().reset_index(name='Total')
    fig_sparkline_pedidos = go.Figure(
        data=[go.Scatter(
            x=serie_pedidos['MES_NUM'],
            y=serie_pedidos['Total'],
            mode='lines',
            line=dict(color='#58a6ff', width=2),
            fill='tozeroy',
            fillcolor='rgba(88, 166, 255, 0.1)',
            hoverinfo='skip'
        )]
    )
    fig_sparkline_pedidos.update_layout(
        height=50,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode=False
    )

    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Total de Pedidos</div>
        <div class="kpi-value">{:,}</div>
    </div>
    """.format(kpis['total_pedidos']), unsafe_allow_html=True)
    st.plotly_chart(fig_sparkline_pedidos, use_container_width=True, config={'displayModeBar': False})

# Card 2: Total Itens Separados
with col2:
    # Mini sparkline para separação
    serie_separados = df_filtrado.groupby('MES_NUM')['QTD ITENS(separador)'].sum().reset_index(name='Total')
    fig_sparkline_separados = go.Figure(
        data=[go.Scatter(
            x=serie_separados['MES_NUM'],
            y=serie_separados['Total'],
            mode='lines',
            line=dict(color='#76C043', width=2),
            fill='tozeroy',
            fillcolor='rgba(118, 192, 67, 0.1)',
            hoverinfo='skip'
        )]
    )
    fig_sparkline_separados.update_layout(
        height=50,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode=False
    )

    st.markdown("""
    <div class="kpi-card separador">
        <div class="kpi-label">Total Itens Separados</div>
        <div class="kpi-value">{:,}</div>
    </div>
    """.format(kpis['total_itens_separados']), unsafe_allow_html=True)
    st.plotly_chart(fig_sparkline_separados, use_container_width=True, config={'displayModeBar': False})

# Card 3: Total Itens Conferidos
with col3:
    # Mini sparkline para conferência
    serie_conferidos = df_filtrado.groupby('MES_NUM')['QTD ITENS(conferente)'].sum().reset_index(name='Total')
    fig_sparkline_conferidos = go.Figure(
        data=[go.Scatter(
            x=serie_conferidos['MES_NUM'],
            y=serie_conferidos['Total'],
            mode='lines',
            line=dict(color='#005F5F', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 95, 95, 0.1)',
            hoverinfo='skip'
        )]
    )
    fig_sparkline_conferidos.update_layout(
        height=50,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode=False
    )

    st.markdown("""
    <div class="kpi-card conferente">
        <div class="kpi-label">Total Itens Conferidos</div>
        <div class="kpi-value">{:,}</div>
    </div>
    """.format(kpis['total_itens_conferidos']), unsafe_allow_html=True)
    st.plotly_chart(fig_sparkline_conferidos, use_container_width=True, config={'displayModeBar': False})

# Card 4: Equipe Ativa
with col4:
    # Conta pessoas únicas (combinação separador + conferente)
    equipe_por_mes = df_filtrado.groupby('MES_NUM').apply(
        lambda x: len(x[['SEPARADOR', 'CONFERENTE']].drop_duplicates())
    ).reset_index(name='Total')

    fig_sparkline_equipe = go.Figure(
        data=[go.Scatter(
            x=equipe_por_mes['MES_NUM'],
            y=equipe_por_mes['Total'],
            mode='lines',
            line=dict(color='#58a6ff', width=2),
            fill='tozeroy',
            fillcolor='rgba(88, 166, 255, 0.1)',
            hoverinfo='skip'
        )]
    )
    fig_sparkline_equipe.update_layout(
        height=50,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode=False
    )

    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Equipe Ativa</div>
        <div class="kpi-value">{}</div>
    </div>
    """.format(kpis['equipe_ativa']), unsafe_allow_html=True)
    st.plotly_chart(fig_sparkline_equipe, use_container_width=True, config={'displayModeBar': False})


# ============================================================================
# Seção 1: Monitoramento de Separação
# ============================================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("### Monitoramento de Separacao")

prod_separador = producao_por_separador(df_filtrado)

# Cria dois gráficos em colunas lado a lado
col_sep_bar, col_sep_pie = st.columns(2)

# Gráfico 1: Barras horizontais de produção por separador (cor verde #76C043)
with col_sep_bar:
    fig_bar_sep = px.bar(
        prod_separador,
        y='SEPARADOR',
        x='Total Itens',
        orientation='h',
        title='Produção por Separador (Itens)',
        labels={'Total Itens': 'Quantidade', 'SEPARADOR': 'Separador'},
        color='Total Itens',
        color_continuous_scale=['#1f6e41', '#76C043'],  # Gradiente do verde corporativo
        text='Total Itens'  # Mostra valores nas barras
    )

    fig_bar_sep.update_layout(
        template='plotly_dark',
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title='Quantidade de Itens',
        yaxis_title='Separador',
        hovermode='closest',
        coloraxis_showscale=False
    )

    fig_bar_sep.update_traces(
        marker_line_width=0,
        textposition='outside',  # Valores fora das barras
        hovertemplate='<b>%{y}</b><br>Itens: %{x:,}<extra></extra>'
    )

    st.plotly_chart(fig_bar_sep, use_container_width=True)

# Gráfico 2: Pizza de distribuição por separador
with col_sep_pie:
    fig_pie_sep = px.pie(
        prod_separador,
        values='Total Itens',
        names='SEPARADOR',
        title='Distribuição de Separação (%)',
        color_discrete_sequence=px.colors.sequential.Greens[::-1]  # Verde ao inverso
    )

    fig_pie_sep.update_layout(
        template='plotly_dark',
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode='closest'
    )

    fig_pie_sep.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Itens: %{value:,} (%{percent})<extra></extra>'
    )

    st.plotly_chart(fig_pie_sep, use_container_width=True)


# ============================================================================
# Seção 2: Monitoramento de Conferência
# ============================================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("### ✅ Monitoramento de Conferência")

prod_conferente = producao_por_conferente(df_filtrado)

# Cria dois gráficos em colunas lado a lado
col_conf_bar, col_conf_pie = st.columns(2)

# Gráfico 1: Barras horizontais de produção por conferente (cor azul/verde #005F5F)
with col_conf_bar:
    fig_bar_conf = px.bar(
        prod_conferente,
        y='CONFERENTE',
        x='Total Itens',
        orientation='h',
        title='Produção por Conferente (Itens)',
        labels={'Total Itens': 'Quantidade', 'CONFERENTE': 'Conferente'},
        color='Total Itens',
        color_continuous_scale=['#003d3d', '#005F5F'],  # Gradiente do azul/verde corporativo
        text='Total Itens'  # Mostra valores nas barras
    )

    fig_bar_conf.update_layout(
        template='plotly_dark',
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title='Quantidade de Itens',
        yaxis_title='Conferente',
        hovermode='closest',
        coloraxis_showscale=False
    )

    fig_bar_conf.update_traces(
        marker_line_width=0,
        textposition='outside',  # Valores fora das barras
        hovertemplate='<b>%{y}</b><br>Itens: %{x:,}<extra></extra>'
    )

    st.plotly_chart(fig_bar_conf, use_container_width=True)

# Gráfico 2: Pizza de distribuição por conferente
with col_conf_pie:
    fig_pie_conf = px.pie(
        prod_conferente,
        values='Total Itens',
        names='CONFERENTE',
        title='Distribuição de Conferência (%)',
        color_discrete_sequence=px.colors.sequential.Blues[::-1]  # Tons de azul
    )

    fig_pie_conf.update_layout(
        template='plotly_dark',
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode='closest'
    )

    fig_pie_conf.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Itens: %{value:,} (%{percent})<extra></extra>'
    )

    st.plotly_chart(fig_pie_conf, use_container_width=True)


# ============================================================================
# Seção 3: Tabela de dados brutos (expandível)
# ============================================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

with st.expander("📋 Ver dados brutos (filtrados)"):
    # Mostra subset de colunas relevantes para legibilidade
    cols_display = ['DATA', 'PEDIDO', 'SEPARADOR', 'QTD ITENS(separador)',
                    'CONFERENTE', 'QTD ITENS(conferente)']
    df_display = df_filtrado[cols_display].copy()
    df_display['DATA'] = df_display['DATA'].dt.strftime('%d/%m/%Y')

    st.dataframe(
        df_display,
        use_container_width=True,
        height=400
    )

    # Botão de download
    csv = df_display.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Baixar dados filtrados (CSV)",
        data=csv,
        file_name="dados_filtrados.csv",
        mime="text/csv"
    )


# ============================================================================
# Footer
# ============================================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("""
---
**Dashboard v1.0** | Tidimar Hospitalar — Operações
📧 Para dúvidas ou sugestões, contate o time de TI.
""")
