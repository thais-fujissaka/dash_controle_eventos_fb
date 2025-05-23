import pandas as pd
import streamlit as st
from utils.functions.date_functions import *
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from utils.functions.general_functions import *
import streamlit.components.v1 as components

def input_periodo_datas(key):
    today = get_today()
    jan_this_year = get_jan_this_year(today)
    first_day_this_month_this_year = get_first_day_this_month_this_year(today)
    last_day_this_month_this_year = get_last_day_this_month_this_year(today)

    # Inicializa o input com o mês atual
    date_input = st.date_input("Período",
                            value=(first_day_this_month_this_year, last_day_this_month_this_year),
                            min_value=jan_this_year,
                            format="DD/MM/YYYY",
                            key=key
                            )
    return date_input


def seletor_mes(key):
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

  # Obter o mês atual para defini-lo como padrão
  mes_atual_num = get_today().month
  nomes_meses = list(meses.keys())
  mes_atual_nome = nomes_meses[mes_atual_num - 1]

  # Seletor de mês
  mes = st.selectbox("Mês do vencimento", nomes_meses, index=nomes_meses.index(mes_atual_nome), key=key)

  # Obter o mês correspondente ao mês selecionado
  mes_selecionado = meses[mes]

  return mes_selecionado


def seletor_ano(ano_inicio, ano_fim, key):
   anos = list(range(ano_inicio, ano_fim + 1))
   ano = st.selectbox("Selecionar ano:", anos, key=key)
   return ano


def button_download(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Planilha")
    excel_data = output.getvalue()

    st.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name="data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def dataframe(df, name, key):
    # Detecta se está no tema escuro ou claro
    theme = st.get_option("theme.base")
    dark_mode = theme == "dark"

    # Define cores conforme o tema
    if dark_mode:
        bg_color = "#0E1117"
        text_color = "#FAFAFA"
        cell_border = "#222222"
        header_bg = "#161A2100"
    else:
        bg_color = "#FFFFFF"
        text_color = "#333333"
        cell_border = "#F0F0F0"
        header_bg = "#F9F9F900"

    # Importa a fonte Source Sans Pro do Google Fonts
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # Título estilizado sem borda, só fundo e sem margem
    st.markdown(f"""
        <h5 style='
            text-align: center;
            padding: 0.1em 0;
            margin: 0;
            background-color: {header_bg};
            color: {text_color};
            font-family: "Source Sans Pro", sans-serif;
            font-weight: 600;
        '>{name}</h5>
    """, unsafe_allow_html=True)

    # CSS customizado para grid
    st.markdown(f"""
        <style>
            .ag-theme-streamlit, .ag-root-wrapper {{
                font-family: "Source Sans Pro", sans-serif !important;
                font-size: 14px !important;
                color: {text_color} !important;
                border: 1px solid transparent !important;  /* remove borda */
                border-radius: 0 0 12px 12px !important;
                background-color: {bg_color};
                margin-top: -4px !important;  /* reduz espaço entre título e grid */
            }}
            .ag-header {{
                background-color: {header_bg} !important;
                border-bottom: 1px solid {cell_border} !important;
            }}
            .ag-root-wrapper-body {{
                border-top: none !important;
            }}
            .ag-cell {{
                border-color: {cell_border} !important;
            }}
            .ag-row-selected, .ag-row-hover {{
                background-color: #FF4B4B33 !important;  /* seleção vermelha translúcida */
            }}
            .ag-row-selected .ag-cell, .ag-row-hover .ag-cell {{
                color: #FF4B4B !important;
            }}
        </style>
    """, unsafe_allow_html=True)

    gb = GridOptionsBuilder.from_dataframe(df)

    # Configura a largura das colunas baseada no nome da coluna
    for col in df.columns:
        largura = max(100, len(col)*12)  # 12px por caractere, mínimo 100
        gb.configure_column(col, minWidth=largura)

    # Configura colunas padrão sem flex
    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        # flex=1,  # REMOVIDO para não sobrescrever largura
        minWidth=100
    )

    gb.configure_selection(
        selection_mode='multiple',
        use_checkbox=False,
        pre_selected_rows=[],
        suppressRowClickSelection=False
    )

    grid_options = gb.build()

    grid_options.update({
        "enableRangeSelection": True,
        "suppressRowClickSelection": True,
        "cellSelection": True
    })

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=False,
        key=f"aggrid_{key}",
        theme="light"
    )

    filtered_df = grid_response['data']

    return filtered_df, len(filtered_df)
