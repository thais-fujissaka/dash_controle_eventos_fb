import streamlit as st
from streamlit.logger import get_logger
from utils.functions.general_functions import *
import pandas as pd
import mysql.connector

LOGGER = get_logger(__name__)

def mysql_connection_fb():
  mysql_config = st.secrets["mysql_fb"]

  conn_fb = mysql.connector.connect(
        host=mysql_config['host'],
        port=mysql_config['port'],
        database=mysql_config['database'],
        user=mysql_config['username'],
        password=mysql_config['password']
    )    
  return conn_fb


def execute_query(query):
    try:
        conn = mysql_connection_fb()
        cursor = conn.cursor()
        cursor.execute(query)

        # Obter nomes das colunas
        column_names = [col[0] for col in cursor.description]
  
        # Obter resultados
        result = cursor.fetchall()
  
        cursor.close()
        conn.close()  # Fechar a conexão
        return result, column_names
    except mysql.connector.Error as err:
        LOGGER.error(f"Erro ao executar query: {err}")
        return None, None


def dataframe_query(query):
  resultado, nomeColunas = execute_query(query)
  dataframe = pd.DataFrame(resultado, columns=nomeColunas)
  return dataframe


### Permissões de usuário ###

@st.cache_data
def GET_PERMISSIONS(email):
  emailStr = f"'{email}'"
  return dataframe_query(f''' 
  SELECT 
	  tg.POSICAO AS 'Permissao'
  FROM
	  ADMIN_USERS au 
	  LEFT JOIN T_GRUPO_USUARIO tgu ON au.ID = tgu.FK_USUARIO 
	  LEFT JOIN T_GRUPO tg ON tgu.FK_GRUPO = tg.id
  WHERE au.LOGIN = {emailStr}
  ''')

@st.cache_data
def GET_LOJAS_USER(email):
  emailStr = f"'{email}'"
  return dataframe_query(f'''
  SELECT 
	  te.NOME_FANTASIA AS 'Loja'
  FROM
  	ADMIN_USERS au 
	  LEFT JOIN T_USUARIOS_EMPRESAS tue ON au.ID = tue.FK_USUARIO 
	  LEFT JOIN T_EMPRESAS te ON tue.FK_EMPRESA = te.ID
	  LEFT JOIN T_LOJAS tl ON te.ID = tl.ID
  WHERE au.LOGIN = {emailStr}
  ''')

@st.cache_data
def GET_USERNAME(email):
  emailStr = f"'{email}'"
  return dataframe_query(f'''
  SELECT 
	  au.FULL_NAME AS 'Nome'
  FROM
  	ADMIN_USERS au 
  WHERE au.LOGIN = {emailStr}
  ''')


@st.cache_data
def GET_EVENTOS_PRICELESS():
   return dataframe_query(f'''
	SELECT 
		tep.ID as 'ID_Evento',
		te.NOME_FANTASIA as 'Casa',
		tee.NOME_COMPLETO as 'Comercial_Responsavel',
		tep.NOME_EVENTO as 'Nome_do_Evento',
		trec.NOME as 'Cliente',
		tep.DATA_CONTRATACAO as 'Data_Contratacao',
		tep.DATA_EVENTO as 'Data_Evento',
		tte.DESCRICAO as 'Tipo_Evento',
		tme.DESCRICAO as 'Modelo_Evento',
		tep.VALOR_TOTAL_EVENTO as 'Valor_Total',
		tep.NUM_CLIENTES as 'Num_Pessoas',
		tep.VALOR_AB as 'Valor_AB',
		tep.VALOR_LOCACAO_AROO_1 + tep.VALOR_LOCACAO_AROO_2 + tep.VALOR_LOCACAO_AROO_3 + tep.VALOR_LOCACAO_ANEXO + tep.VALOR_LOCACAO_NOTIE as 'Valor_Locacao_Total',
		tep.VALOR_LOCACAO_AROO_1 as 'Valor_Locacao_Aroo_1',
		tep.VALOR_LOCACAO_AROO_2 as 'Valor_Locacao_Aroo_2',
		tep.VALOR_LOCACAO_AROO_3 as 'Valor_Locacao_Aroo_3',
		tep.VALOR_LOCACAO_ANEXO as 'Valor_Locacao_Anexo',
		tep.VALOR_LOCACAO_NOTIE as 'Valor_Locacao_Notie',
		tep.VALOR_LOCACAO_MIRANTE as 'Valor_Locacao_Mirante',
		tep.VALOR_IMPOSTO as 'Valor_Imposto',
		tsep.DESCRICAO as 'Status_Evento',
		temd.DESCRICAO as 'Motivo_Declinio',
		tep.OBSERVACOES as 'Observacoes'
	FROM T_EVENTOS_PRICELESS tep
		LEFT JOIN T_EMPRESAS te ON (tep.FK_EMPRESA = te.ID)
		LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLIENTE trec ON (tep.FK_CLIENTE = trec.ID)
		LEFT JOIN T_STATUS_EVENTO_PRE tsep ON (tep.FK_STATUS_EVENTO = tsep.ID)
		LEFT JOIN T_EVENTOS_MOTIVOS_DECLINIO temd ON (tep.FK_MOTIVO_DECLINIO = temd.ID)
		LEFT JOIN T_TIPO_EVENTO tte ON (tep.FK_TIPO_EVENTO = tte.ID)
		LEFT JOIN T_MODELO_EVENTO tme ON (tep.FK_MODELO_EVENTO = tme.ID)
		LEFT JOIN T_EXECUTIVAS_EVENTOS tee ON (tep.FK_EXECUTIVA_EVENTOS = tee.ID)
    WHERE tep.DATA_CONTRATACAO >= '2024-01-01'
    AND tep.DATA_EVENTO >= '2024-01-01'
	''')


@st.cache_data
def GET_PARCELAS_EVENTOS_PRICELESS():
   return dataframe_query(f'''
	SELECT
		tpep.ID as 'ID_Parcela',
		tpep.FK_EVENTO_PRICELESS as 'ID_Evento',
		tep.NOME_EVENTO as 'Nome_do_Evento',
		tcep.DESCRICAO as 'Categoria_Parcela',
		tpep.VALOR_PARCELA as 'Valor_Parcela',
		tpep.DATA_VENCIMENTO_PARCELA as 'Data_Vencimento',
		tsp.DESCRICAO as 'Status_Pagamento',
		tpep.DATA_RECEBIMENTO_PARCELA as 'Data_Recebimento' 
	FROM T_PARCELAS_EVENTOS_PRICELESS tpep 
		LEFT JOIN T_EVENTOS_PRICELESS tep ON (tpep.FK_EVENTO_PRICELESS = tep.ID)
		LEFT JOIN T_STATUS_PAGAMENTO tsp ON (tpep.FK_STATUS_PAGAMENTO = tsp.ID)
		LEFT JOIN T_CATEGORIA_EVENTO_PRICELESS tcep ON (tpep.FK_CATEGORIA_PARCELA = tcep.ID)
	WHERE tpep.DATA_VENCIMENTO_PARCELA >= '2024-01-01'
    AND tpep.DATA_RECEBIMENTO_PARCELA >= '2024-01-01'
	ORDER BY tep.ID DESC, tpep.ID DESC
	''')