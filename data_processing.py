"""
data_processing.py
Módulo para carregar, sanitizar e agregar dados da planilha BASE_Dashboard.xlsx.
Todas as funções são testáveis e comentadas para manutenção futura.
"""

import pandas as pd
import streamlit as st
from io import BytesIO


# Mapa de meses em português para geração de colunas de data legíveis
MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}


def load_excel(uploaded_file):
    """
    Carrega a planilha Excel do arquivo enviado.
    Valida presença obrigatória da aba 'BASE'.

    Args:
        uploaded_file: UploadedFile do Streamlit (ou arquivo local para testes)

    Returns:
        pd.DataFrame com dados da aba 'BASE'

    Raises:
        ValueError se aba 'BASE' não existir
    """
    try:
        # Lê todas as abas primeiro para listar disponíveis
        xls = pd.ExcelFile(uploaded_file)

        # Verifica se aba 'BASE' existe; se não, avisa o usuário
        if 'BASE' not in xls.sheet_names:
            raise ValueError(
                f"Aba 'BASE' não encontrada. Abas disponíveis: {', '.join(xls.sheet_names)}"
            )

        # Lê a aba 'BASE' retornando DataFrame
        df = pd.read_excel(uploaded_file, sheet_name='BASE')
        return df

    except Exception as e:
        raise ValueError(f"Erro ao carregar arquivo Excel: {str(e)}")


def sanitize_columns(df):
    """
    Remove espaços invisíveis (leading/trailing) nos nomes das colunas.
    Mantém nomes dos dados — apenas normaliza nomes de coluna.

    Args:
        df: pd.DataFrame

    Returns:
        pd.DataFrame com nomes de coluna limpos
    """
    # Aplica .strip() a cada nome de coluna para remover espaços extras
    df.columns = df.columns.str.strip()
    return df


def remove_totais(df):
    """
    Remove linhas de subtotais/totais que possam estar presentes no Excel.
    Descarta:
    - Linhas onde PEDIDO é nulo ou não-numérico
    - Linhas onde SEPARADOR ou CONFERENTE contêm 'total' ou 'subtotal' (case-insensitive)

    Args:
        df: pd.DataFrame

    Returns:
        pd.DataFrame filtrado (sem linhas de subtotal)
    """
    df_clean = df.copy()

    # Remove linhas onde PEDIDO é nulo
    initial_rows = len(df_clean)
    df_clean = df_clean[df_clean['PEDIDO'].notna()]

    # Converte PEDIDO para numérico; se falhar (não-numérico), transforma em NaN
    # Depois remove NaNs (linhas com PEDIDO não-numérico — provavelmente totais/labels)
    df_clean['PEDIDO'] = pd.to_numeric(df_clean['PEDIDO'], errors='coerce')
    df_clean = df_clean[df_clean['PEDIDO'].notna()]

    # Remove linhas onde SEPARADOR contém 'total' ou 'subtotal' (case-insensitive)
    df_clean = df_clean[
        ~df_clean['SEPARADOR'].str.lower().str.contains('total|subtotal', na=False, regex=True)
    ]

    # Remove linhas onde CONFERENTE contém 'total' ou 'subtotal' (case-insensitive)
    df_clean = df_clean[
        ~df_clean['CONFERENTE'].str.lower().str.contains('total|subtotal', na=False, regex=True)
    ]

    removed = initial_rows - len(df_clean)
    if removed > 0:
        st.info(f"[INFO] Removidas {removed} linhas de subtotais/totais.")

    return df_clean.reset_index(drop=True)


def coerce_quantidades(df):
    """
    Força colunas de quantidade para inteiros, tratando dados malformados.
    Usa pd.to_numeric com errors='coerce' (transforma valores inválidos em NaN)
    e preenche NaNs com 0. Depois converte para int.

    Detecta outliers extremos na coluna de conferente (valores > 1000 — suspeitosamente
    grandes, pois quantidade típica de itens por pedido é 1-100). Linhas com outliers
    são sinalizadas no info do Streamlit mas não removidas — mantém dados brutos intactos.

    Isso evita erros de tipo e distorções de soma por linhas com lixo de dados.

    Args:
        df: pd.DataFrame

    Returns:
        pd.DataFrame com QTD ITENS(separador) e QTD ITENS(conferente) como int
    """
    df_typed = df.copy()

    # Coluna de quantidade do separador: coerção + fill 0 + int
    df_typed['QTD ITENS(separador)'] = (
        pd.to_numeric(df_typed['QTD ITENS(separador)'], errors='coerce')
        .fillna(0)
        .astype(int)
    )

    # Coluna de quantidade do conferente: mesma lógica
    df_typed['QTD ITENS(conferente)'] = (
        pd.to_numeric(df_typed['QTD ITENS(conferente)'], errors='coerce')
        .fillna(0)
        .astype(int)
    )

    # Coluna PEDIDO também é numérica; converte pra int (já removemos não-numéricos antes)
    df_typed['PEDIDO'] = df_typed['PEDIDO'].astype(int)

    # Detecta outliers extremos na conferência (quantidade > 1000 é suspeita)
    # Típico: 1-100 itens/pedido; >1000 provavelmente é erro de entry ou corrupção
    outlier_count = (df_typed['QTD ITENS(conferente)'] > 1000).sum()
    if outlier_count > 0:
        st.warning(
            f"[ATENCAO] {outlier_count} registros com QTD ITENS(conferente) > 1000 "
            f"(possível erro de dados). Valores mantidos mas revisar manualmente."
        )

    return df_typed


def parse_datas(df):
    """
    Converte coluna DATA para datetime e gera colunas de mês/ano traduzidas para PT-BR.
    Cria:
    - DATA: datetime (valor limpo)
    - MES_NUM: número do mês (1-12)
    - MES_NOME: nome do mês em português ("Janeiro", "Fevereiro", etc)
    - ANO: ano (2026, 2027, ...)

    Args:
        df: pd.DataFrame

    Returns:
        pd.DataFrame com colunas de data expandidas
    """
    df_dates = df.copy()

    # Converte coluna DATA para datetime; erros vêm como NaT (Not a Time)
    df_dates['DATA'] = pd.to_datetime(df_dates['DATA'], errors='coerce')

    # Extrai mês e ano em novas colunas
    df_dates['MES_NUM'] = df_dates['DATA'].dt.month
    df_dates['ANO'] = df_dates['DATA'].dt.year

    # Mapeia número de mês para nome em português usando dicionário MESES_PT
    df_dates['MES_NOME'] = df_dates['MES_NUM'].map(MESES_PT)

    return df_dates


def preprocess(uploaded_file):
    """
    Orquestra todo o pipeline de limpeza e preparação de dados.
    Executa na sequência correta:
    1. Carrega Excel (aba BASE)
    2. Sanitiza nomes de coluna
    3. Remove linhas de subtotal/total
    4. Coerce quantidades para inteiros
    5. Parse e expande datas

    Args:
        uploaded_file: UploadedFile do Streamlit

    Returns:
        pd.DataFrame limpo e pronto para agregações/visualizações

    Raises:
        Lança exceção se arquivo inválido ou aba BASE ausente; caller (main.py) trata
    """
    # Etapa 1: carregar
    df = load_excel(uploaded_file)

    # Etapa 2: sanitizar nomes de coluna
    df = sanitize_columns(df)

    # Etapa 3: remover totais
    df = remove_totais(df)

    # Etapa 4: coerce quantidades
    df = coerce_quantidades(df)

    # Etapa 5: parse datas
    df = parse_datas(df)

    return df


# ============================================================================
# Funções de agregação para KPIs e gráficos
# ============================================================================

def get_kpis(df):
    """
    Calcula KPIs principais do dashboard.

    Args:
        df: pd.DataFrame processado

    Returns:
        dict com chaves:
        - total_pedidos: contagem de linhas (cada linha = 1 pedido)
        - total_itens_separados: soma de QTD ITENS(separador)
        - total_itens_conferidos: soma de QTD ITENS(conferente)
        - equipe_ativa: max entre separadores únicos e conferentes únicos
    """
    separadores_unicos = df['SEPARADOR'].nunique()
    conferentes_unicos = df['CONFERENTE'].nunique()

    return {
        'total_pedidos': len(df),
        'total_itens_separados': int(df['QTD ITENS(separador)'].sum()),
        'total_itens_conferidos': int(df['QTD ITENS(conferente)'].sum()),
        'equipe_ativa': max(separadores_unicos, conferentes_unicos),
    }


def producao_por_separador(df):
    """
    Agrega produção por SEPARADOR (quantidade de itens separados).
    Retorna DataFrame ordenado decrescente por quantidade.

    Args:
        df: pd.DataFrame processado

    Returns:
        pd.DataFrame com colunas ['SEPARADOR', 'Total Itens']
    """
    separadores = (
        df.groupby('SEPARADOR')['QTD ITENS(separador)']
        .sum()
        .reset_index()
        .rename(columns={'QTD ITENS(separador)': 'Total Itens'})
        .sort_values('Total Itens', ascending=False)
    )
    return separadores


def producao_por_conferente(df):
    """
    Agrega produção por CONFERENTE (quantidade de itens conferidos).
    Retorna DataFrame ordenado decrescente por quantidade.

    Args:
        df: pd.DataFrame processado

    Returns:
        pd.DataFrame com colunas ['CONFERENTE', 'Total Itens']
    """
    conferentes = (
        df.groupby('CONFERENTE')['QTD ITENS(conferente)']
        .sum()
        .reset_index()
        .rename(columns={'QTD ITENS(conferente)': 'Total Itens'})
        .sort_values('Total Itens', ascending=False)
    )
    return conferentes


def serie_mensal(df, coluna_qtd):
    """
    Agrupa dados por mês (MES_NUM) para criar série temporal.
    Usado para gerar sparklines nos cards de KPI.

    Args:
        df: pd.DataFrame processado
        coluna_qtd: nome da coluna de quantidade ('QTD ITENS(separador)' ou 'QTD ITENS(conferente)')

    Returns:
        pd.DataFrame com colunas ['MES_NUM', 'MES_NOME', 'Total']
    """
    serie = (
        df.groupby(['MES_NUM', 'MES_NOME'])[coluna_qtd]
        .sum()
        .reset_index()
        .rename(columns={coluna_qtd: 'Total'})
        .sort_values('MES_NUM')
    )
    return serie
