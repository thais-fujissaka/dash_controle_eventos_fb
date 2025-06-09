import streamlit as st
import pandas as pd
from utils.components import *
from streamlit_echarts import st_echarts
from utils.functions.general_functions import *
from utils.functions.parcelas import *

def kpi_card(title, value, icon, color):
    """
    Cria um card de KPI com título, valor, ícone e cor.
    """
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 20px; border-radius: 10px; display: flex; align-items: center;">
            <i class="{icon}" style="font-size: 24px; color: white; margin-right: 10px;"></i>
            <div style="color: white;">
                <h3 style="margin: 0;">{title}</h3>
                <p style="font-size: 24px;">{value}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
	

def kpi_card_propostas(valor, rgb_tupla, label, icon):
	wch_colour_box = rgb_tupla
	wch_colour_font = (255, 255, 255)
	fontsize = 36

	# Definir o ícone conforme o parâmetro
	if icon == "enviado":
		iconname = "fa-solid fa-paper-plane"
	elif icon == "confirmado":
		iconname = "fa-solid fa-check"
	elif icon == "cancelado":
		iconname = "fa-solid fa-xmark"
	elif icon == "negociacao":
		iconname = "fa-solid fa-handshake"
	else:
		iconname = "fa-solid fa-circle-info"

	sline = f"{label}"
	lnk = """<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">"""
	valor = f"{valor}"

	htmlstr = f"""
		{lnk}
		<div style='background-color: rgba({wch_colour_box[0]}, {wch_colour_box[1]}, {wch_colour_box[2]}, 1.0); 
                    color: rgba({wch_colour_font[0]}, {wch_colour_font[1]}, {wch_colour_font[2]}, 1);
                    border-radius: 7px;
					margin-bottom: 16px;
					padding: 12px 12px 0 12px;
					height: 150px;'>
            <div style='font-size: 16px; padding: 10px 14px 10px 14px;'>
			    <i class='{iconname}' style='padding: 10px 12px 0 0; font-size: 12px;'></i>
				{sline}
			</div>
            <div style="display: flex; align-items: center; justify-content: center; padding-top:10px;">
				<div style='font-size: {fontsize}px; font-weight: bold'>{valor}</div>
            </div>
        <div>
	"""
	
	st.markdown(htmlstr, unsafe_allow_html=True)
	
def kpi_card_propostas_valores(valor, rgb_tupla, label):
	wch_colour_box = rgb_tupla
	wch_colour_font = (255, 255, 255)
	fontsize = 36

	sline = f"{label}"
	lnk = """<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">"""
	valor = f"{valor}"

	htmlstr = f"""
		{lnk}
		<div style='background-color: rgba({wch_colour_box[0]}, {wch_colour_box[1]}, {wch_colour_box[2]}, 1); 
                    color: rgb({wch_colour_font[0]}, {wch_colour_font[1]}, {wch_colour_font[2]});
                    border-radius: 7px;
					margin-bottom: 16px;
					padding: 12px;
					height: 150px;'>
            <div style='font-size: 16px; padding: 10px 14px 10px 14px;'>
				{sline}
			</div>
            <div style="display: flex; align-items: center; justify-content: center; padding-top:10px">
				<div style='font-size: {fontsize}px; font-weight: bold'>R$ {valor}</div>
            </div>
        <div>
	"""
	
	st.markdown(htmlstr, unsafe_allow_html=True)
	

def cards_numero_propostas(num_leads_recebidos, num_lancadas, num_confirmadas, num_declinadas, num_em_negociacao):
	
    # N propostas lancadas no periodo
    azul = (30, 58, 138)
    verde = (34, 197, 94)
    amarelo = (234, 179, 8) 
    vermelho = (239, 68, 68)
    kpi_card_propostas(num_leads_recebidos, azul, "Nº de leads recebidos:", "leads")
    kpi_card_propostas(num_lancadas, azul, "Nº de propostas lançadas:", "enviado")
    kpi_card_propostas(num_confirmadas, verde, "Nº de propostas confirmadas:", "confirmado")
    kpi_card_propostas(num_declinadas, vermelho, "Nº de propostas declinadas:", "cancelado")
    kpi_card_propostas(num_em_negociacao, amarelo, "Nº de propostas em negociação:", "negociacao")
    
def cards_valor_propostas(valor_leads_recebidos, valor_lancadas, valor_confirmadas, valor_declinadas, valor_em_negociacao):
    azul = (30, 58, 138)
    verde = (34, 197, 94)
    amarelo = (234, 179, 8)
    vermelho = (239, 68, 68)
    kpi_card_propostas_valores(valor_leads_recebidos, azul, "Valor de leads recebidos:")
    kpi_card_propostas_valores(valor_lancadas, azul, "Valor de propostas lançadas:")
    kpi_card_propostas_valores(valor_confirmadas, verde, "Valor de propostas confirmadas:")
    kpi_card_propostas_valores(valor_declinadas, vermelho, "Valor de propostas declinadas:")
    kpi_card_propostas_valores(valor_em_negociacao, amarelo, "Valor de propostas em negociação:")
    

def calculo_numero_propostas(df_eventos, df_eventos_data_lead, ano, mes):
    """
    Calcula o número de propostas lançadas, confirmadas, declinadas e em negociação
    para o ano e mês especificados.
    """
    df_eventos['Data do Evento'] = pd.to_datetime(df_eventos['Data do Evento'])
    
    num_leads_recebidos = len(df_eventos_data_lead)
    num_lancadas = len(df_eventos)
    num_confirmadas = len(df_eventos[df_eventos['Status do Evento'] == 'Confirmado'])
    num_declinadas = len(df_eventos[df_eventos['Status do Evento'] == 'Declinado'])
    num_em_negociacao = len(df_eventos[df_eventos['Status do Evento'] == 'Em negociação'])
    
    return num_leads_recebidos, num_lancadas, num_confirmadas, num_declinadas, num_em_negociacao


def calculo_valores_propostas(df_eventos, df_eventos_data_lead, ano, mes):
    """
    Calcula os valores das propostas lançadas, confirmadas, declinadas e em negociação
    para o ano e mês especificados.
    """
    df_eventos['Data do Evento'] = pd.to_datetime(df_eventos['Data do Evento'])
    
    valor_leads_recebidos = df_eventos_data_lead['Valor Total'].sum() if not df_eventos_data_lead.empty else 0
    valor_lancadas = df_eventos['Valor Total'].sum()
    valor_confirmadas = df_eventos[df_eventos['Status do Evento'] == 'Confirmado']['Valor Total'].sum()
    valor_declinadas = df_eventos[df_eventos['Status do Evento'] == 'Declinado']['Valor Total'].sum()
    valor_em_negociacao = df_eventos[df_eventos['Status do Evento'] == 'Em negociação']['Valor Total'].sum()
    
    return valor_leads_recebidos,valor_lancadas, valor_confirmadas, valor_declinadas, valor_em_negociacao

def grafico_pizza_num_propostas(num_confirmadas, num_declinadas, num_em_negociacao):
        
    option = {
        "tooltip": {
            "trigger": "item"
        },
        "legend": {
            "orient": "vertical",
            "left": "10%",
            "top": "center"
        },
        "series": [
            {
                "name": "Conversão de Eventos",
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
					"position": "middle",
					"formatter": "{d}%",
                    "color": "#000",
                },
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": 20,
                        "fontWeight": "bold"
                    }
                },
                "labelLine": {
                    "show": False
                },
                "data": [
                    {"value": num_confirmadas, "name": "Confirmadas", "itemStyle": {"color": "#22C55E"}},
                    {"value": num_declinadas, "name": "Declinadas", "itemStyle": {"color": "#EF4444"}},
                    {"value": num_em_negociacao, "name": "Em negociação", "itemStyle": {"color": "#EAB308"}},
                ]
            }
        ]
    }
    with st.container(border=True):
        st_echarts(option, height="300px")
		

def grafico_barras_num_propostas(df_eventos_ano):
	
    # Normaliza a coluna 'Status do Evento'
    df_eventos_ano['Status do Evento'] = df_eventos_ano['Status do Evento'].str.replace('ç', 'c')
	
    # Extrai o mês da coluna 'Data Envio Proposta'
    df_eventos_ano['Mes'] = df_eventos_ano['Data Envio Proposta'].dt.month
	
    # Agrupa os dados por ano e mês, contando o número de eventos
    df_eventos_agrupado = df_eventos_ano.groupby(['Mes', 'Status do Evento']).size().reset_index(name='Número de Eventos')

    # Cria lista de meses
    nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    # Dataframe filtrado por status do evento
    df_lancados = df_eventos_ano.groupby(['Mes']).size().reset_index(name='Número de Eventos')
    df_confirmados = df_eventos_agrupado[df_eventos_agrupado['Status do Evento'] == 'Confirmado']
    df_declinados = df_eventos_agrupado[df_eventos_agrupado['Status do Evento'] == 'Declinado']
    df_em_negociacao = df_eventos_agrupado[df_eventos_agrupado['Status do Evento'] == 'Em negociacão']

    # Cria series de valores
    serie_propostas_lancadas = [0] * 12
    serie_propostas_confirmadas = [0] * 12
    serie_propostas_declinadas = [0] * 12
    serie_propostas_em_negociacao = [0] * 12

    # Inserir numeros de propostas nas series
    if not df_lancados.empty:
        for _, row in df_lancados.iterrows():
            serie_propostas_lancadas[int(row['Mes']) - 1] = int(row['Número de Eventos'])
    if not df_confirmados.empty:
        for _, row in df_confirmados.iterrows():
            serie_propostas_confirmadas[int(row['Mes']) - 1] = int(row['Número de Eventos'])
    if not df_declinados.empty:
        for _, row in df_declinados.iterrows():
            serie_propostas_declinadas[int(row['Mes']) - 1] = int(row['Número de Eventos'])
    if not df_em_negociacao.empty:
        for _, row in df_em_negociacao.iterrows():
            serie_propostas_em_negociacao[int(row['Mes']) - 1] = int(row['Número de Eventos'])

    option = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "cross",
                "crossStyle": {"color": "#999"}
            }
        },
        "legend": {
            "data": [
                "Confirmadas", 
                "Declinadas", 
                "Em negociação",
                "Lançadas"
            ]
        },
        "xAxis": [
            {
                "type": "category",
                "data": nomes_meses,
                "axisPointer": {"type": "shadow"}
            }
        ],
        "yAxis": [
            {
                "type": "value",
                "name": "Número",
                "min": 0,
                "axisLabel": {
                    "formatter": "{value}"
                }
            }
        ],
        "series": [
            {
                "name": "Confirmadas",
                "type": "bar",
                "data": serie_propostas_confirmadas,
                "color": "#22C55E"
            },
            {
                "name": "Declinadas",
                "type": "bar",
                "data": serie_propostas_declinadas,
                "color": "#EF4444"
            },
            {
                "name": "Em negociação",
                "type": "bar",
                "data": serie_propostas_em_negociacao,
                "color": "#EAB308"
            },
            {
                "name": "Lançadas",
                "type": "line",
                "data": serie_propostas_lancadas,
                "yAxisIndex": 0,
                "color": "#1E3A8A"
            }
        ]
    }
    with st.container(border=True):
	    st_echarts(option, height="420px")