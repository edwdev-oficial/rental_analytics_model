import streamlit as st
import pandas as pd
import pdfplumber
import re

from rental_analytics_model.utils.get_index import get_index
from rental_analytics_model.utils.formaters import convert_moeda_br_str_to_number
from rental_analytics_model.utils.formaters import convert_col_df_moeda_br_str_to_number
from rental_analytics_model.utils.loaders import load_normal_itens
from rental_analytics_model.services.valores_locacao import load_xlsx

def load_data_recibos(lista_unicos, df_valores_locacao):
    
    valor_total_recibos = 0
    recibos = []
    df_recibos = pd.DataFrame()

    pdf_files = [f for f in lista_unicos if f.type == "application/pdf"]

    if pdf_files:
        df_normal_itens = load_normal_itens()

        for arquivo in pdf_files:
            linhas = []
            with pdfplumber.open(arquivo) as pdf:
                for pagina in pdf.pages:
                    text = pagina.extract_text()
                    if text:
                        linhas.extend(text.splitlines())    


                # ========================================================
                # region RESUMO DOS RECIBOS
                # ========================================================
                id = linhas[get_index(linhas, 'Número cliente')].split(' ')[2]
                razao_social = linhas[get_index(linhas, 'Local Descarga')].split(',')
                remover = ['Local Descarga: Empresa', 'Local Descarga: ']
                razao_social = [x for x in razao_social if x not in remover][0].replace('Local Descarga: ', '').strip()
                recibo = linhas[get_index(linhas, 'Recibo de Aluguel')].replace('Recibo de Aluguel ', '')
                periodo = linhas[get_index(linhas, 'Período :')].replace('Período : ', '').split(' ')[0]
                valor_sem_impostos = linhas[get_index(linhas, 'Valor total com impostos BRL ') - 1]
                valor_com_impostos = linhas[get_index(linhas, 'Valor total com impostos BRL')].replace('Valor total com impostos BRL ', '')
                valor_com_impostos_float = convert_moeda_br_str_to_number(valor_com_impostos)
                valor_total_recibos += valor_com_impostos_float
                # endregion
                # ========================================================


                # ========================================================
                # region DETALHES DOS RECIBOS
                # ========================================================
                index_in = get_index(linhas, 'Hilti Fleet Premium - Gestão de Frota') + 1
                index_out = get_index(linhas, 'Valor total com impostos') - 1
                itens = linhas[index_in: index_out ]
                itens = [x for x in itens if x not in ['Extensão de Serviços para Novos Equipamentos']]

                for item in itens:

                    pattern = r'^(\d+)\s+(.*?)\s+(\d{2}/\d{4}),\s+(\d+\s+Meses)\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)$'

                    match = re.match(pattern, item)

                    if match:
                        parsed_item = {
                            'Cust_id': id,
                            'Razão Social': razao_social,
                            'Recibo nº': recibo,
                            'Período': periodo,
                            'Valor s/imp': valor_sem_impostos,
                            'Valor c/imp': valor_com_impostos,
                            'Artigo': match.group(1),
                            'Descrição': match.group(2).strip(),
                            'Data Início': match.group(3),
                            'Período de Utilização': match.group(4),
                            'Qt.': match.group(5),
                            'Mensal s/imp': match.group(6),
                            'Subtotal s/imp': match.group(7)
                        }
                        recibos.append(parsed_item)
                # endregion
                # ========================================================
        
        df_recibos = pd.DataFrame(recibos)

        # import streamlit as st
        # st.session_state.df_recibos_row = df_recibos


        df_recibos = convert_col_df_moeda_br_str_to_number(df_recibos, ['Valor s/imp', 'Valor c/imp', 'Subtotal s/imp', 'Mensal s/imp'])
        pos = df_recibos.columns.get_loc("Mensal s/imp") + 1
        df_recibos.insert(pos, "Mensal c/imp", round(df_recibos["Mensal s/imp"] / (1 - 0.0925), 2))
        df_recibos['Subtotal c/imp'] = df_recibos['Subtotal s/imp'] / (1 - 0.0925)
        df_recibos['Data Início'] = pd.to_datetime(df_recibos['Data Início'], format='%m/%Y')
        df_recibos['Qt.'] = df_recibos['Qt.'].astype(int)        

        df_recibos = df_recibos.merge(
            df_normal_itens[['Descrição', 'Tipo', 'Linha', 'Modelo']],
            on='Descrição',
            how='left'
        )

        import streamlit as st
        st.session_state.df_recibos_row = df_recibos

        df_recibos['Período'] = pd.to_datetime(df_recibos['Período'], format='%m/%Y')
        df_recibos.rename(columns={'Linha': 'familia', 'Modelo': 'modelo'}, inplace=True)
        df_recibos['periodo'] = pd.to_datetime(df_recibos['Período']).dt.to_period('M')        

        if not df_valores_locacao.empty:
            df_valores_locacao.rename(columns={'Modelo': 'modelo'}, inplace=True)
            df_recibos = df_recibos.merge(
                df_valores_locacao[['modelo', 'dia', 'semana', 'quinzena', 'mes']],
                on='modelo',
                how='left'
            )

            df_recibos = (
                df_recibos
                .groupby(['Razão Social', 'periodo', 'Tipo', 'familia', 'modelo', 'dia', 'semana', 'quinzena', 'mes'], as_index=False)
                .agg({
                    'Qt.': 'sum',
                    'Subtotal c/imp': 'sum'
                })
            )

    return df_recibos

