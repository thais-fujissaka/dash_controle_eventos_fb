import streamlit as st
import pandas as pd
from utils.queries_financeiro import *
from utils.functions.financeiro_faturamento_zigpay import *
from utils.functions.general_functions import *
from utils.components import *
from utils.user import logout

st.set_page_config(
  layout = 'wide',
  page_title = 'Faturamento Zig',
  page_icon=':moneybag:',
  initial_sidebar_state="collapsed"
)

if 'loggedIn' not in st.session_state or not st.session_state['loggedIn']:
  st.switch_page('Login.py')

def main():
  config_sidebar()
  col, col2, col3 = st.columns([6, 1, 1])
  with col:
    st.title('FATURAMENTO ZIGPAY')
  with col2:
    st.button(label="Atualizar", on_click = st.cache_data.clear)
  with col3:
    if st.button("Logout"):
      logout()
  st.divider()

  lojasComDados = preparar_dados_lojas_user_financeiro()
  data_inicio_default, data_fim_default = get_first_and_last_day_of_month()
  lojas_selecionadas, data_inicio, data_fim = criar_seletores(lojasComDados, data_inicio_default, data_fim_default)

  st.divider()

  # threading.Thread(target=config_Faturamento_zig)
  OrcamentoFaturamento = config_orcamento_faturamento(lojas_selecionadas, data_inicio, data_fim) 
  orcamfatformatado = OrcamentoFaturamento.copy()
  categorias_desejadas = ['Alimentos', 'Bebidas', 'Couvert', 'Gifts']
  soma_valor_bruto = orcamfatformatado.loc[orcamfatformatado['Categoria'].isin(categorias_desejadas), 'Valor Bruto'].sum()
  soma_valor_bruto = format_brazilian(soma_valor_bruto)
  orcamfatformatado = format_columns_brazilian(orcamfatformatado, ['Orçamento', 'Valor Bruto', 'Desconto', 'Valor Líquido', 'Faturam - Orçamento'])
  orcamfatformatado.loc[orcamfatformatado['Orçamento'] == '0,00', 'Atingimento %'] = '-'


  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 7])
    with col1:
      st.subheader("Faturamento Agregado:")
      orcamfatformatadoStyled = orcamfatformatado.style.map(highlight_values, subset=['Faturam - Orçamento'])
      st.dataframe(orcamfatformatadoStyled, width=700, hide_index=True)
      st.write(f"Soma dos Valores Brutos de Alimentos, Bebidas, Couvert e Gifts: {soma_valor_bruto}")
    with col2:
      st.subheader("Valores Líquidos:")
      Grafico_Donut(OrcamentoFaturamento)
  
  st.markdown('<div style="page-break-before: always;"></div>', unsafe_allow_html=True)

  FaturamentoZig = config_Faturamento_zig(lojas_selecionadas, data_inicio, data_fim)

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      col1, col2 = st.columns([6, 1], vertical_alignment='bottom')
      with col1:
        st.subheader("Top 10 Alimentos:")
      with col2:
        st.markdown("*Sem delivery")
      top_dez(FaturamentoZig, 'Alimentos')

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      col1, col2 = st.columns([6, 1], vertical_alignment='bottom')
      with col1:
        st.subheader("Top 10 Bebidas:")
      with col2:
        st.markdown("*Sem delivery")
      top_dez(FaturamentoZig, 'Bebidas')

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      col3, col4 = st.columns([6, 3])
      with col3:
        st.subheader("Faturamento por Categoria:")
      FaturamentoZigClasse = vendas_agrupadas_por_tipo(FaturamentoZig)

  classificacoes = obter_valores_unicos_ordenados(FaturamentoZig, 'Tipo')

  with st.container(border=True):
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      col3, col4 = st.columns([6, 3])
      with col3:
        st.subheader("Vendas de Produtos por Categoria:")
      with col4:
        classificacoes_selecionadas = st.multiselect(label='Selecione Classificações', options=classificacoes)
        FaturamentoZigClasse = filtrar_por_classe_selecionada(FaturamentoZig, 'Tipo', classificacoes_selecionadas)
      FaturamentoZigClasse = vendas_agrupadas(FaturamentoZigClasse)

  with st.container(border=True):  
    col0, col1, col2 = st.columns([1, 10, 1])
    with col1:
      st.subheader("Faturamento Por Dia:")
      st.markdown("*Sem delivery")
      faturam_por_dia(FaturamentoZig)

if __name__ == '__main__':
  main()
