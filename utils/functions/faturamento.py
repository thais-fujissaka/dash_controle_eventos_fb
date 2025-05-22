import streamlit as st
import pandas as pd
from utils.components import *
from streamlit_echarts import st_echarts
from utils.functions.general_functions import *
from utils.functions.parcelas import *


def valores_labels_formatados(lista_valores):
    # Labels formatados
    labels = [format_brazilian(v) for v in lista_valores]

    # Dados com labels
    lista_valores_formatados = [{"value": v, "label": {"show": True, "position": "top", "color": "#000", "formatter": lbl}} for v, lbl in zip(lista_valores, labels)]

    return lista_valores_formatados


# Total de Eventos
def grafico_barras_total_eventos(df_parcelas):
    # Extrai mês e ano da coluna 'Data_Vencimento'
    df_parcelas['Mes'] = df_parcelas['Data_Vencimento'].dt.month
    df_parcelas['Ano'] = df_parcelas['Data_Vencimento'].dt.year

    # Agrupa os valores por mês e ano
    df_parcelas_agrupado = df_parcelas.groupby(['Mes', 'Ano'])['Valor_Parcela'].sum().reset_index()

    # Cria lista de meses
    meses = df_parcelas_agrupado['Mes'].unique().tolist()
    nomes_meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    nomes_meses = [nomes_meses_pt[mes - 1] for mes in meses]
    
    # Cria lista de valores
    total_eventos = df_parcelas_agrupado['Valor_Parcela'].tolist()

    # Valores e labels formatados
    total_eventos_formatados = valores_labels_formatados(total_eventos)

    # Options do grafico
    option = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": [
            {
                "type": "category",
                "data": nomes_meses,
                "boundaryGap": True,
                "axisTick": {
                    "alignWithLabel": True
                }
            }
        ],
        "yAxis": [
            {
                "type": "value"
            }
        ],
        "series": [
            {
                "name": "Faturamento de Eventos",
                "type": "bar",
                "barWidth": "60%",
                "data": total_eventos_formatados,
                "itemStyle": {
                    "color": "#FAC858"
                },
                "label": {
                "show": True,
                "position": "top",
                "color": "#000"  # cor do texto
                }
            }
        ]
    }

    # Evento de clique
    events = {
        "click": "function(params) { return params.name; }"
    }

    # Exibir gráfico com captura de clique
    mes_selecionado = st_echarts(option, events=events, height=300, width="100%", key="chart_total_eventos")
    
    # Dicionário para mapear os meses
    meses = {
        "Janeiro": "01",
        "Fevereiro": "02",
        "Março": "03",
        "Abril": "04",
        "Maio": "05",
        "Junho": "06",
        "Julho": "07",
        "Agosto": "08",
        "Setembro": "09",
        "Outubro": "10",
        "Novembro": "11",
        "Dezembro": "12"
    }
    
    # Obter o mês correspondente ao mês selecionado
    if mes_selecionado != None:
        mes_selecionado = meses[mes_selecionado]
        
        col1, col2, col3 = st.columns([1, 12, 1])
        with col2:
            df_parcelas = df_filtrar_mes(df_parcelas, 'Data_Vencimento', mes_selecionado)
            df_parcelas.drop(columns=['Mes', 'Ano', 'Total_Gazit', 'Repasse_Gazit_Bruto', 'Repasse_Gazit_Liquido'], inplace=True)
            df_parcelas = df_formata_datas_sem_horario(df_parcelas, ['Data_Vencimento', 'Data_Recebimento'])
            df_parcelas = rename_colunas_parcelas(df_parcelas)
            df_parcelas = format_columns_brazilian(df_parcelas, ['Valor Parcela', 'Valor Bruto Repasse Gazit', 'Total Locação'])
        dataframe(df_parcelas, name='Parcelas', key='total_eventos_vencimento_parcelas')
    else:
        st.markdown("Selecione um mês para visualizar as parcelas correspondentes ao faturamento do mês.")


# Total de Eventos - Competência
def grafico_barras_total_eventos_competencia(df_parcelas):

    # Normaliza
    df_parcelas['Categoria_Parcela'] = df_parcelas['Categoria_Parcela'].str.replace('ç', 'c')

    # Extrai mês e ano da coluna 'Data_Evento'
    df_parcelas['Mes'] = df_parcelas['Data_Evento'].dt.month
    df_parcelas['Ano'] = df_parcelas['Data_Evento'].dt.year

    # Agrupa os valores por mês e ano
    df_parcelas_agrupado = df_parcelas.groupby(['Mes', 'Ano', 'Categoria_Parcela'])['Valor_Parcela'].sum().reset_index()
    df_parcelas_agrupado['Valor_Parcela'] = df_parcelas_agrupado['Valor_Parcela'].round(2)


    # Pivotar: linhas = Mes, colunas = Categoria_Parcela, valores = soma dos valores
    df_pivot = df_parcelas_agrupado.pivot_table(
        index='Mes',
        columns='Categoria_Parcela',
        values='Valor_Parcela',
        aggfunc='sum'
    ).fillna(0).reset_index()

    # Cria lista de meses
    meses = df_pivot['Mes'].unique().tolist()
    nomes_meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    nomes_meses = [nomes_meses_pt[int(mes) - 1] for mes in meses]

    # Cria lista de valores
    total_eventos_por_competencia_AB = df_pivot.get('A&B', pd.Series([0]*len(df_pivot))).tolist()
    total_eventos_por_competencia_locacao = df_pivot.get('Locacão', pd.Series([0]*len(df_pivot))).tolist()

    # Valores e labels formatados
    total_eventos_por_competencia_AB_formatados = valores_labels_formatados(total_eventos_por_competencia_AB)
    total_eventos_por_competencia_locacao_formatados = valores_labels_formatados(total_eventos_por_competencia_locacao)

    # Options do grafico
    option = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "legend": {
            "data": [
                "A&B",
                "Locação"
            ],
            "top": "0%",   # Posição no topo do gráfico
            "left": "center",  # Centraliza a legenda horizontalmente
            "textStyle": {
                "color": "#000"  # cor do texto da legenda
            }
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": [
            {
                "type": "category",
                "data": nomes_meses,
                "boundaryGap": True,
                "axisTick": {
                    "alignWithLabel": True
                }
            }
        ],
        "yAxis": [
            {
                "type": "value"
            }
        ],
        "series": [
            {
                "name": "A&B",
                "type": "bar",
                "barWidth": "35%",
                "barGap": "5%",
                "data": total_eventos_por_competencia_AB_formatados,
                "itemStyle": {
                    "color": "#FAC858"
                },
                "label": {
                "show": True,
                "position": "top",
                "color": "#000"  # cor do texto
                }
            },
            {
                "name": "Locação",
                "type": "bar",
                "barWidth": "35%",
                "barGap": "5%",
                "data": total_eventos_por_competencia_locacao_formatados,
                "itemStyle": {
                    "color": "#5470C6"
                },
                "label": {
                "show": True,
                "position": "top",
                "color": "#000"  # cor do texto
                }
            }
        ]
    }

    # Evento de clique
    events = {
        "click": "function(params) { return params.name; }"
    }

    # Exibir gráfico com captura de clique
    mes_selecionado = st_echarts(option, events=events, height=300, width="100%", key="chart_total_eventos_competencia")

    # Dicionário para mapear os meses
    meses = {
        "Janeiro": "01",
        "Fevereiro": "02",
        "Março": "03",
        "Abril": "04",
        "Maio": "05",
        "Junho": "06",
        "Julho": "07",
        "Agosto": "08",
        "Setembro": "09",
        "Outubro": "10",
        "Novembro": "11",
        "Dezembro": "12"
    }

    # Inverter normalização
    df_parcelas['Categoria_Parcela'] = df_parcelas['Categoria_Parcela'].str.replace('Locacão', 'Locação')
    
    # Obter o mês correspondente ao mês selecionado
    if mes_selecionado != None:
        mes_selecionado = meses[mes_selecionado]
        
        col1, col2, col3 = st.columns([1, 12, 1])
        with col2:
            df_parcelas = df_filtrar_mes(df_parcelas, 'Data_Evento', mes_selecionado)
            df_parcelas.drop(columns=['Mes', 'Ano', 'Total_Gazit', 'Repasse_Gazit_Bruto', 'Repasse_Gazit_Liquido', 'Valor_Locacao_Total'], inplace=True)
            df_parcelas = df_formata_datas_sem_horario(df_parcelas, ['Data_Vencimento', 'Data_Recebimento', 'Data_Evento'])
            df_parcelas = rename_colunas_parcelas(df_parcelas)
            df_parcelas = format_columns_brazilian(df_parcelas, ['Valor Parcela', 'Valor Bruto Repasse Gazit'])
        dataframe(df_parcelas, name='Parcelas', key='total_eventos_competencia_parcelas')
    else:
        st.markdown("Selecione um mês para visualizar as parcelas correspondentes ao faturamento do mês.")

# Total de Eventos - Caixa
def grafico_barras_total_eventos_caixa(df_parcelas):

    # Normaliza
    df_parcelas['Categoria_Parcela'] = df_parcelas['Categoria_Parcela'].str.replace('ç', 'c')

    # Extrai mês e ano da coluna 'Data_Evento'
    df_parcelas['Mes'] = df_parcelas['Data_Recebimento'].dt.month
    df_parcelas['Ano'] = df_parcelas['Data_Recebimento'].dt.year

    # Agrupa os valores por mês e ano
    df_parcelas_agrupado = df_parcelas.groupby(['Mes', 'Ano', 'Categoria_Parcela'])['Valor_Parcela'].sum().reset_index()
    df_parcelas_agrupado['Valor_Parcela'] = df_parcelas_agrupado['Valor_Parcela'].round(2)


    # Pivotar: linhas = Mes, colunas = Categoria_Parcela, valores = soma dos valores
    df_pivot = df_parcelas_agrupado.pivot_table(
        index='Mes',
        columns='Categoria_Parcela',
        values='Valor_Parcela',
        aggfunc='sum'
    ).fillna(0).reset_index()

    # Cria lista de meses
    meses = df_pivot['Mes'].unique().tolist()
    nomes_meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    nomes_meses = [nomes_meses_pt[int(mes) - 1] for mes in meses]

    # Cria lista de valores
    total_eventos_por_recebimento_AB = df_pivot.get('A&B', pd.Series([0]*len(df_pivot))).tolist()
    total_eventos_por_recebimento_locacao = df_pivot.get('Locacão', pd.Series([0]*len(df_pivot))).tolist()

    # Valores e labels formatados
    total_eventos_por_recebimento_AB_formatados = valores_labels_formatados(total_eventos_por_recebimento_AB)
    total_eventos_por_recebimento_locacao_formatados = valores_labels_formatados(total_eventos_por_recebimento_locacao)

    # Options do grafico
    option = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "legend": {
            "data": [
                "A&B",
                "Locação"
            ],
            "top": "0%",   # Posição no topo do gráfico
            "left": "center",  # Centraliza a legenda horizontalmente
            "textStyle": {
                "color": "#000"  # cor do texto da legenda
            }
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": [
            {
                "type": "category",
                "data": nomes_meses,
                "boundaryGap": True,
                "axisTick": {
                    "alignWithLabel": True
                }
            }
        ],
        "yAxis": [
            {
                "type": "value"
            }
        ],
        "series": [
            {
                "name": "A&B",
                "type": "bar",
                "barWidth": "35%",
                "barGap": "5%",
                "data": total_eventos_por_recebimento_AB_formatados,
                "itemStyle": {
                    "color": "#FAC858"
                },
                "label": {
                "show": True,
                "position": "top",
                "color": "#000"  # cor do texto
                }
            },
            {
                "name": "Locação",
                "type": "bar",
                "barWidth": "35%",
                "barGap": "5%",
                "data": total_eventos_por_recebimento_locacao_formatados,
                "itemStyle": {
                    "color": "#5470C6"
                },
                "label": {
                "show": True,
                "position": "top",
                "color": "#000"  # cor do texto
                }
            }
        ]
    }

    # Evento de clique
    events = {
        "click": "function(params) { return params.name; }"
    }

    # Exibir gráfico com captura de clique
    mes_selecionado = st_echarts(option, events=events, height=300, width="100%", key="chart_total_eventos_recebimento")

    # Dicionário para mapear os meses
    meses = {
        "Janeiro": "01",
        "Fevereiro": "02",
        "Março": "03",
        "Abril": "04",
        "Maio": "05",
        "Junho": "06",
        "Julho": "07",
        "Agosto": "08",
        "Setembro": "09",
        "Outubro": "10",
        "Novembro": "11",
        "Dezembro": "12"
    }

    # Inverter normalização
    df_parcelas['Categoria_Parcela'] = df_parcelas['Categoria_Parcela'].str.replace('Locacão', 'Locação')
    
    # Obter o mês correspondente ao mês selecionado
    if mes_selecionado != None:
        mes_selecionado = meses[mes_selecionado]
        
        col1, col2, col3 = st.columns([1, 12, 1])
        with col2:
            df_parcelas = df_filtrar_mes(df_parcelas, 'Data_Recebimento', mes_selecionado)
            df_parcelas.drop(columns=['Mes', 'Ano', 'Total_Gazit', 'Repasse_Gazit_Bruto', 'Repasse_Gazit_Liquido', 'Valor_Locacao_Total'], inplace=True)
            df_parcelas = df_formata_datas_sem_horario(df_parcelas, ['Data_Vencimento', 'Data_Recebimento', 'Data_Evento'])
            df_parcelas = rename_colunas_parcelas(df_parcelas)
            df_parcelas = format_columns_brazilian(df_parcelas, ['Valor Parcela', 'Valor Bruto Repasse Gazit'])
        dataframe(df_parcelas, name='Parcelas', key='total_eventos_recebimento_parcelas')
    else:
        st.markdown("Selecione um mês para visualizar as parcelas correspondentes ao faturamento do mês.")

# Locação

def df_fracao_locacao_espacos(df_eventos):

    # Adiciona coluna de cálculo de fração de cada espaço em relação ao valor total de locação
    # Aroo
    df_eventos['Fracao_Aroo'] = (df_eventos['Valor_Locacao_Aroo_1'] + df_eventos['Valor_Locacao_Aroo_2'] + df_eventos['Valor_Locacao_Aroo_3']) / df_eventos['Valor_Locacao_Total']
    df_eventos['Fracao_Aroo'] = df_eventos['Fracao_Aroo'].fillna(0)

    # Anexo
    df_eventos['Fracao_Anexo'] = df_eventos['Valor_Locacao_Anexo'] / df_eventos['Valor_Locacao_Total']
    df_eventos['Fracao_Anexo'] = df_eventos['Fracao_Anexo'].fillna(0)

    # Notie
    df_eventos['Fracao_Notie'] = df_eventos['Valor_Locacao_Notie'] / df_eventos['Valor_Locacao_Total']
    df_eventos['Fracao_Notie'] = df_eventos['Fracao_Notie'].fillna(0)

    # Mirante
    df_eventos['Fracao_Mirante'] = df_eventos['Valor_Locacao_Mirante'] / df_eventos['Valor_Locacao_Total']
    df_eventos['Fracao_Mirante'] = df_eventos['Fracao_Mirante'].fillna(0)

    return df_eventos

def calcula_valor_parcela_locacao_espaco(df_parcelas, df_eventos):

    df_eventos = df_fracao_locacao_espacos(df_eventos)

    # Merge df_parcelas com fracoes de cada espaço
    df_parcelas = df_parcelas.merge(df_eventos[['ID_Evento', 'Fracao_Aroo', 'Fracao_Anexo', 'Fracao_Notie', 'Fracao_Mirante']], how='left', on='ID_Evento')
    
    df_parcelas['Valor_Parcela_Aroos'] = df_parcelas['Valor_Parcela'] * df_parcelas['Fracao_Aroo']
    df_parcelas['Valor_Parcela_Anexo'] = df_parcelas['Valor_Parcela'] * df_parcelas['Fracao_Anexo']
    df_parcelas['Valor_Parcela_Notie'] = df_parcelas['Valor_Parcela'] * df_parcelas['Fracao_Notie']
    df_parcelas['Valor_Parcela_Mirante'] = df_parcelas['Valor_Parcela'] * df_parcelas['Fracao_Mirante']

    return df_parcelas

def grafico_barras_locacao_aroo(df_parcelas, df_eventos):
    # Normaliza
    df_parcelas['Categoria_Parcela'] = df_parcelas['Categoria_Parcela'].str.replace('ç', 'c')

    # Filtra pela categoria 'Locação'
    df_parcelas = (
    df_parcelas
    .loc[df_parcelas['Categoria_Parcela'] == 'Locacão']
    .copy()
    )
    
    # Calcula coluna 'Valor_Parcela_Aroos'
    df_parcelas = calcula_valor_parcela_locacao_espaco(df_parcelas, df_eventos)

    # Extrai mês e ano da coluna 'Data_Vencimento'
    df_parcelas['Mes'] = df_parcelas['Data_Vencimento'].dt.month
    df_parcelas['Ano'] = df_parcelas['Data_Vencimento'].dt.year

    # Agrupa os valores por mês e ano
    df_parcelas_agrupado = df_parcelas.groupby(['Mes', 'Ano'])['Valor_Parcela_Aroos'].sum().reset_index()

    # Cria lista de meses
    meses = df_parcelas_agrupado['Mes'].unique().tolist()
    nomes_meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    nomes_meses = [nomes_meses_pt[mes - 1] for mes in meses]
    
    # Cria lista de valores
    total_aroos = df_parcelas_agrupado['Valor_Parcela_Aroos'].tolist()

    # Valores e labels formatados
    total_aroos_formatados = valores_labels_formatados(total_aroos)
    
    # Options do grafico
    option = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": [
            {
                "type": "category",
                "data": nomes_meses,
                "boundaryGap": True,
                "axisTick": {
                    "alignWithLabel": True
                }
            }
        ],
        "yAxis": [
            {
                "type": "value"
            }
        ],
        "series": [
            {
                "name": "Faturamento de Locação Aroo",
                "type": "bar",
                "barWidth": "60%",
                "data": total_aroos_formatados,
                "itemStyle": {
                    "color": "#FAC858"
                },
                "label": {
                "show": True,
                "position": "top",
                "color": "#000"  # cor do texto
                }
            }
        ]
    }
    
    # Evento de clique
    events = {
        "click": "function(params) { return params.name; }"
    }

    # Exibir gráfico com captura de clique
    mes_selecionado = st_echarts(option, events=events, height=300, width="100%", key="chart_faturamento_aroos")
    
    # Dicionário para mapear os meses
    meses = {
        "Janeiro": "01",
        "Fevereiro": "02",
        "Março": "03",
        "Abril": "04",
        "Maio": "05",
        "Junho": "06",
        "Julho": "07",
        "Agosto": "08",
        "Setembro": "09",
        "Outubro": "10",
        "Novembro": "11",
        "Dezembro": "12"
    }
    
    
    # Obter o mês correspondente ao mês selecionado
    if mes_selecionado != None:
        mes_selecionado = meses[mes_selecionado]
        
        col1, col2, col3 = st.columns([1, 12, 1])
        with col2:
            df_parcelas = df_filtrar_mes(df_parcelas, 'Data_Vencimento', mes_selecionado)
            df_parcelas.drop(columns=['Mes', 'Ano', 'Total_Gazit', 'Repasse_Gazit_Bruto', 'Fracao_Aroo', 'Fracao_Anexo', 'Fracao_Notie', 'Fracao_Mirante','Repasse_Gazit_Liquido'], inplace=True)
            df_parcelas = df_formata_datas_sem_horario(df_parcelas, ['Data_Vencimento', 'Data_Recebimento', 'Data_Evento'])
            df_parcelas = rename_colunas_parcelas(df_parcelas)
            df_parcelas = format_columns_brazilian(df_parcelas, ['Valor Parcela', 'Valor Bruto Repasse Gazit', 'Total Locação', 'Valor Parcela Aroos', 'Valor Parcela Anexo', 'Valor Parcela Notiê', 'Valor Parcela Mirante'])
        dataframe(df_parcelas, name='Parcelas', key='faturamento_aroos_vencimento_parcelas')
    else:
        st.markdown("Selecione um mês para visualizar as parcelas correspondentes ao faturamento do mês.")



# Locação Anexo

def grafico_barras_locacao_anexo(df_parcelas, df_eventos):
    # Normaliza
    df_parcelas['Categoria_Parcela'] = df_parcelas['Categoria_Parcela'].str.replace('ç', 'c')

    # Filtra pela categoria 'Locação'
    df_parcelas = (
    df_parcelas
    .loc[df_parcelas['Categoria_Parcela'] == 'Locacão']
    .copy()
    )

    df_parcelas = calcula_valor_parcela_locacao_espaco(df_parcelas, df_eventos)

    # Extrai mês e ano da coluna 'Data_Vencimento'
    df_parcelas['Mes'] = df_parcelas['Data_Vencimento'].dt.month
    df_parcelas['Ano'] = df_parcelas['Data_Vencimento'].dt.year

    # Agrupa os valores por mês e ano
    df_parcelas_agrupado = df_parcelas.groupby(['Mes', 'Ano'])['Valor_Parcela_Anexo'].sum().reset_index()

    # Cria lista de meses
    meses = df_parcelas_agrupado['Mes'].unique().tolist()
    nomes_meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    nomes_meses = [nomes_meses_pt[mes - 1] for mes in meses]
    
    # Cria lista de valores
    total_anexo = df_parcelas_agrupado['Valor_Parcela_Anexo'].tolist()

    # Valores e labels formatados
    total_anexo_formatados = valores_labels_formatados(total_anexo)

    # Options do grafico
    option = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": [
            {
                "type": "category",
                "data": nomes_meses,
                "boundaryGap": True,
                "axisTick": {
                    "alignWithLabel": True
                }
            }
        ],
        "yAxis": [
            {
                "type": "value"
            }
        ],
        "series": [
            {
                "name": "Faturamento de Locação Anexo",
                "type": "bar",
                "barWidth": "60%",
                "data": total_anexo_formatados,
                "itemStyle": {
                    "color": "#FAC858"
                },
                "label": {
                "show": True,
                "position": "top",
                "color": "#000"  # cor do texto
                }
            }
        ]
    }

    # Evento de clique
    events = {
        "click": "function(params) { return params.name; }"
    }

    # Exibir gráfico com captura de clique
    mes_selecionado = st_echarts(option, events=events, height=300, width="100%", key="chart_faturamento_anexo")
    
    # Dicionário para mapear os meses
    meses = {
        "Janeiro": "01",
        "Fevereiro": "02",
        "Março": "03",
        "Abril": "04",
        "Maio": "05",
        "Junho": "06",
        "Julho": "07",
        "Agosto": "08",
        "Setembro": "09",
        "Outubro": "10",
        "Novembro": "11",
        "Dezembro": "12"
    }
    
    # Obter o mês correspondente ao mês selecionado
    if mes_selecionado != None:
        mes_selecionado = meses[mes_selecionado]
        
        col1, col2, col3 = st.columns([1, 12, 1])
        with col2:
            df_parcelas = df_filtrar_mes(df_parcelas, 'Data_Vencimento', mes_selecionado)
            df_parcelas.drop(columns=['Mes', 'Ano', 'Total_Gazit', 'Repasse_Gazit_Bruto', 'Fracao_Aroo', 'Fracao_Anexo', 'Fracao_Notie', 'Fracao_Mirante','Repasse_Gazit_Liquido'], inplace=True)
            df_parcelas = df_formata_datas_sem_horario(df_parcelas, ['Data_Vencimento', 'Data_Recebimento', 'Data_Evento'])
            df_parcelas = rename_colunas_parcelas(df_parcelas)
            df_parcelas = format_columns_brazilian(df_parcelas, ['Valor Parcela', 'Valor Bruto Repasse Gazit', 'Total Locação', 'Valor Parcela Aroos', 'Valor Parcela Anexo', 'Valor Parcela Notiê', 'Valor Parcela Mirante'])
        dataframe(df_parcelas, name='Parcelas', key='faturamento_anexo_vencimento_parcelas')
    else:
        st.markdown("Selecione um mês para visualizar as parcelas correspondentes ao faturamento do mês.")
    

# Locação Notiê

def grafico_barras_locacao_notie(df_parcelas, df_eventos):
    # Normaliza
    df_parcelas['Categoria_Parcela'] = df_parcelas['Categoria_Parcela'].str.replace('ç', 'c')

    # Filtra pela categoria 'Locação'
    df_parcelas = (
    df_parcelas
    .loc[df_parcelas['Categoria_Parcela'] == 'Locacão']
    .copy()
    )

    df_parcelas = calcula_valor_parcela_locacao_espaco(df_parcelas, df_eventos)

    # Extrai mês e ano da coluna 'Data_Vencimento'
    df_parcelas['Mes'] = df_parcelas['Data_Vencimento'].dt.month
    df_parcelas['Ano'] = df_parcelas['Data_Vencimento'].dt.year

    # Agrupa os valores por mês e ano
    df_parcelas_agrupado = df_parcelas.groupby(['Mes', 'Ano'])['Valor_Parcela_Notie'].sum().reset_index()

    # Cria lista de meses
    meses = df_parcelas_agrupado['Mes'].unique().tolist()
    nomes_meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    nomes_meses = [nomes_meses_pt[mes - 1] for mes in meses]
    
    # Cria lista de valores
    total_notie = df_parcelas_agrupado['Valor_Parcela_Notie'].tolist()

    # Valores e labels formatados
    total_notie_formatados = valores_labels_formatados(total_notie)

    # Options do grafico
    option = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": [
            {
                "type": "category",
                "data": nomes_meses,
                "boundaryGap": True,
                "axisTick": {
                    "alignWithLabel": True
                }
            }
        ],
        "yAxis": [
            {
                "type": "value"
            }
        ],
        "series": [
            {
                "name": "Faturamento de Locação Notiê",
                "type": "bar",
                "barWidth": "60%",
                "data": total_notie_formatados,
                "itemStyle": {
                    "color": "#FAC858"
                },
                "label": {
                "show": True,
                "position": "top",
                "color": "#000"  # cor do texto
                }
            }
        ]
    }

    # Evento de clique
    events = {
        "click": "function(params) { return params.name; }"
    }

    # Exibir gráfico com captura de clique
    mes_selecionado = st_echarts(option, events=events, height=300, width="100%", key="chart_faturamento_notie")
    
    # Dicionário para mapear os meses
    meses = {
        "Janeiro": "01",
        "Fevereiro": "02",
        "Março": "03",
        "Abril": "04",
        "Maio": "05",
        "Junho": "06",
        "Julho": "07",
        "Agosto": "08",
        "Setembro": "09",
        "Outubro": "10",
        "Novembro": "11",
        "Dezembro": "12"
    }
    
    # Obter o mês correspondente ao mês selecionado
    if mes_selecionado != None:
        mes_selecionado = meses[mes_selecionado]
        
        col1, col2, col3 = st.columns([1, 12, 1])
        with col2:
            df_parcelas = df_filtrar_mes(df_parcelas, 'Data_Vencimento', mes_selecionado)
            df_parcelas.drop(columns=['Mes', 'Ano', 'Total_Gazit', 'Repasse_Gazit_Bruto', 'Fracao_Aroo', 'Fracao_Anexo', 'Fracao_Notie', 'Fracao_Mirante', 'Repasse_Gazit_Liquido'], inplace=True)
            df_parcelas = df_formata_datas_sem_horario(df_parcelas, ['Data_Vencimento', 'Data_Recebimento'])
            df_parcelas = rename_colunas_parcelas(df_parcelas)
            df_parcelas = format_columns_brazilian(df_parcelas, ['Valor Parcela', 'Valor Bruto Repasse Gazit', 'Total Locação', 'Valor Parcela Aroos', 'Valor Parcela Anexo', 'Valor Parcela Notiê', 'Valor Parcela Mirante'])
        dataframe(df_parcelas, name='Parcelas', key='faturamento_notie_vencimento_parcelas')
    else:
        st.markdown("Selecione um mês para visualizar as parcelas correspondentes ao faturamento do mês.")


def grafico_barras_locacao_mirante(df_parcelas, df_eventos):
    # Normaliza
    df_parcelas['Categoria_Parcela'] = df_parcelas['Categoria_Parcela'].str.replace('ç', 'c')

    # Filtra pela categoria 'Locação'
    df_parcelas = (
    df_parcelas
    .loc[df_parcelas['Categoria_Parcela'] == 'Locacão']
    .copy()
    )

    df_parcelas = calcula_valor_parcela_locacao_espaco(df_parcelas, df_eventos)

    # Extrai mês e ano da coluna 'Data_Vencimento'
    df_parcelas['Mes'] = df_parcelas['Data_Vencimento'].dt.month
    df_parcelas['Ano'] = df_parcelas['Data_Vencimento'].dt.year

    # Agrupa os valores por mês e ano
    df_parcelas_agrupado = df_parcelas.groupby(['Mes', 'Ano'])['Valor_Parcela_Mirante'].sum().reset_index()

    # Cria lista de meses
    meses = df_parcelas_agrupado['Mes'].unique().tolist()
    nomes_meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    nomes_meses = [nomes_meses_pt[mes - 1] for mes in meses]
    
    # Cria lista de valores
    total_mirante = df_parcelas_agrupado['Valor_Parcela_Mirante'].tolist()

    # Valores e labels formatados
    total_mirante_formatados = valores_labels_formatados(total_mirante)

    # Options do grafico
    option = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": [
            {
                "type": "category",
                "data": nomes_meses,
                "boundaryGap": True,
                "axisTick": {
                    "alignWithLabel": True
                }
            }
        ],
        "yAxis": [
            {
                "type": "value"
            }
        ],
        "series": [
            {
                "name": "Faturamento de Locação Mirante",
                "type": "bar",
                "barWidth": "60%",
                "data": total_mirante_formatados,
                "itemStyle": {
                    "color": "#FAC858"
                },
                "label": {
                "show": True,
                "position": "top",
                "color": "#000"  # cor do texto
                }
            }
        ]
    }

    # Evento de clique
    events = {
        "click": "function(params) { return params.name; }"
    }

    # Exibir gráfico com captura de clique
    mes_selecionado = st_echarts(option, events=events, height=300, width="100%", key="chart_faturamento_mirante")
    
    # Dicionário para mapear os meses
    meses = {
        "Janeiro": "01",
        "Fevereiro": "02",
        "Março": "03",
        "Abril": "04",
        "Maio": "05",
        "Junho": "06",
        "Julho": "07",
        "Agosto": "08",
        "Setembro": "09",
        "Outubro": "10",
        "Novembro": "11",
        "Dezembro": "12"
    }
    
    # Obter o mês correspondente ao mês selecionado
    if mes_selecionado != None:
        mes_selecionado = meses[mes_selecionado]
        
        col1, col2, col3 = st.columns([1, 12, 1])
        with col2:
            df_parcelas = df_filtrar_mes(df_parcelas, 'Data_Vencimento', mes_selecionado)
            df_parcelas.drop(columns=['Mes', 'Ano', 'Total_Gazit', 'Repasse_Gazit_Bruto', 'Fracao_Aroo', 'Fracao_Anexo', 'Fracao_Notie', 'Fracao_Mirante','Repasse_Gazit_Liquido'], inplace=True)
            df_parcelas = df_formata_datas_sem_horario(df_parcelas, ['Data_Vencimento', 'Data_Recebimento'])
            df_parcelas = rename_colunas_parcelas(df_parcelas)
            df_parcelas = format_columns_brazilian(df_parcelas, ['Valor Parcela', 'Valor Bruto Repasse Gazit', 'Total Locação', 'Valor Parcela Aroos', 'Valor Parcela Anexo', 'Valor Parcela Notiê', 'Valor Parcela Mirante'])
        dataframe(df_parcelas, name="Parcelas", key="faturamento_mirante_vencimento_parcelas")
    else:
        st.markdown("Selecione um mês para visualizar as parcelas correspondentes ao faturamento do mês.")

# Alimentos e Bebidas

def grafico_barras_faturamento_AB(df_parcelas):
    # Extrai mês e ano da coluna 'Data_Vencimento'
    df_parcelas['Mes'] = df_parcelas['Data_Vencimento'].dt.month
    df_parcelas['Ano'] = df_parcelas['Data_Vencimento'].dt.year

    # Filtra pela categoria 'A&B'
    df_parcelas = (
    df_parcelas
    .loc[df_parcelas['Categoria_Parcela'] == 'A&B']
    .copy()
    )

    # Agrupa os valores por mês e ano
    df_parcelas_agrupado = df_parcelas.groupby(['Mes', 'Ano'])['Valor_Parcela'].sum().reset_index()

    # Cria lista de meses
    meses = df_parcelas_agrupado['Mes'].unique().tolist()
    nomes_meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    nomes_meses = [nomes_meses_pt[mes - 1] for mes in meses]
    
    # Cria lista de valores
    total_AB = df_parcelas_agrupado['Valor_Parcela'].tolist()

    # Valores e labels formatados
    total_AB_formatados = valores_labels_formatados(total_AB)

    # Options do grafico
    option = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow"
            }
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "containLabel": True
        },
        "xAxis": [
            {
                "type": "category",
                "data": nomes_meses,
                "boundaryGap": True,
                "axisTick": {
                    "alignWithLabel": True
                }
            }
        ],
        "yAxis": [
            {
                "type": "value"
            }
        ],
        "series": [
            {
                "name": "Faturamento de Alimentos e Bebidas",
                "type": "bar",
                "barWidth": "60%",
                "data": total_AB_formatados,
                "itemStyle": {
                    "color": "#FAC858"
                },
                "label": {
                "show": True,
                "position": "top",
                "color": "#000"  # cor do texto
                }
            }
        ]
    }

    # Evento de clique
    events = {
        "click": "function(params) { return params.name; }"
    }

    # Exibir gráfico com captura de clique
    mes_selecionado = st_echarts(option, events=events, height=300, width="100%", key="chart_faturamento_AB")
    
    # Dicionário para mapear os meses
    meses = {
        "Janeiro": "01",
        "Fevereiro": "02",
        "Março": "03",
        "Abril": "04",
        "Maio": "05",
        "Junho": "06",
        "Julho": "07",
        "Agosto": "08",
        "Setembro": "09",
        "Outubro": "10",
        "Novembro": "11",
        "Dezembro": "12"
    }
    
    # Obter o mês correspondente ao mês selecionado
    if mes_selecionado != None:
        mes_selecionado = meses[mes_selecionado]
        
        col1, col2, col3 = st.columns([1, 12, 1])
        with col2:
            df_parcelas = df_filtrar_mes(df_parcelas, 'Data_Vencimento', mes_selecionado)
            df_parcelas.drop(columns=['Mes', 'Ano', 'Total_Gazit', 'Repasse_Gazit_Bruto', 'Valor_Locacao_Total', 'Repasse_Gazit_Liquido'], inplace=True)
            df_parcelas = df_formata_datas_sem_horario(df_parcelas, ['Data_Vencimento', 'Data_Recebimento'])
            df_parcelas = rename_colunas_parcelas(df_parcelas)
            df_parcelas = format_columns_brazilian(df_parcelas, ['Valor Parcela'])
        dataframe(df_parcelas, name='Parcelas', key='faturamento_AB_vencimento_parcelas')
    else:
        st.markdown("Selecione um mês para visualizar as parcelas correspondentes ao faturamento do mês.")