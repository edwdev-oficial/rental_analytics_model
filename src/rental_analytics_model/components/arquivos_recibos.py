# ========================================================
# region IMPORTS
# ========================================================
import io
import hashlib
import pandas as pd
import streamlit as st
from src.rental_analytics_model.services.valores_locacao import load_xlsx

from rental_analytics_model.services import (
    clear_df,
    calcular_periodos
)

# endregion
# ========================================================

def arquivos_recebidos(arquivos):

    # ========================================================
    # region ARQUIVOS UNICOS
    # ========================================================
    if 'arquivos_unicos' not in st.session_state:
        st.session_state.arquivos_unicos = {}

    for file in arquivos:
        pdf_bytes = file.getvalue()
        file_hash = hashlib.md5(pdf_bytes).hexdigest()

        if file_hash not in st.session_state.arquivos_unicos:
            st.session_state.arquivos_unicos[file_hash] = file


    lista_unicos = list(st.session_state.arquivos_unicos.values())
    # endregion
    # ========================================================

    # ========================================================
    # region FATURAS GF
    # ========================================================
    pdf_files = [f for f in lista_unicos if f.type == "application/pdf"]
    if pdf_files:
        with st.expander("Faturas Gestão de Frotas"):
            abas = st.tabs([f"Recibo {pdf_files[i].name}" for i in range(len(pdf_files))])
            for aba, file in zip(abas, pdf_files):
                with aba:
                    st.pdf(file.getvalue(), height=900)
    # endregion
    # ========================================================

    # ========================================================
    # region CONTRATOS
    # ========================================================
    contratos = [f for f in lista_unicos if 'contratos' in f.name]
    df_contratos = pd.DataFrame()
    if contratos:
        with st.expander('Contratos'):
            df_contratos = load_xlsx(contratos)
            df_contratos.fillna('', inplace=True)
            st.write('df_contratos')
            st.dataframe(df_contratos)
        df_contratos = calcular_periodos.calcular_periodos_df(df_contratos)
        df_contratos['periodo'] = pd.to_datetime(df_contratos['locacao']).dt.to_period('M')
        df_contratos['dias_mes'] = df_contratos['periodo'].dt.days_in_month
    # endregion
    # ========================================================

    # ========================================================
    # region PQ_MAQUINAS
    # ========================================================
    pq_maquinas = [f for f in lista_unicos if 'pq_maquinas' in f.name]
    df_pq_maquinas = pd.DataFrame()
    if pq_maquinas:
        with st.expander('Parque de Máquinas'):
            df_pq_maquinas = load_xlsx(pq_maquinas)
            df_pq_maquinas = clear_df.clear_df_pq_maquinas(df_pq_maquinas)
            st.session_state.df_pq_maquinas = df_pq_maquinas
            st.dataframe(df_pq_maquinas)
    # endregion
    # ========================================================

    # ========================================================
    # region VALORES LOCACAO
    # ========================================================
    valores_locacao = [f for f in lista_unicos if f.name == "valores_locacao.xlsx"]
    df_valores_locacao = pd.DataFrame()
    if valores_locacao:
        with st.expander('Valores Locação'):

            df_valores_locacao = load_xlsx(valores_locacao)
            # st.write(df_valores_locacao)
            # 👇 CAPTURA O RETORNO
            df_editado = st.data_editor(
                df_valores_locacao,
                key="editor_valores_locacao"
            )

            st.session_state.df_valores_locacao = df_valores_locacao
            # st.rerun()  # Força a atualização da página para refletir as mudanças no DataFrame
            # st.write(st.session_state.df_valores_locacao) #DEBUG
            # st.session_state.df_valores_locacao = df_valores_locacao

            # 👇 BOTÃO DE SALVAR
            if not df_editado.equals(df_valores_locacao):
                df_valores_locacao = df_editado
                buffer = io.BytesIO()
                df_valores_locacao.to_excel(buffer, index=False)
                buffer.seek(0)

                st.download_button(
                    label="Baixar Excel",
                    data=buffer,
                    file_name=f"valores_locacao.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    # endregion
    # ========================================================

    # ========================================================
    # region DF AMS DASH
    # ========================================================
    data_ams_dashboard = [f for f in lista_unicos if 'ams_report_brazil' in f.name ]
    df_ams_dash = pd.DataFrame()
    if data_ams_dashboard:
        df_ams_dash = load_xlsx(data_ams_dashboard)
        with st.expander('AMS Dashboard'):
            st.write(data_ams_dashboard[0].name)
            st.dataframe(df_ams_dash)
    # endregion
    # ========================================================

    # ========================================================
    # region RETURN
    # ========================================================
    return lista_unicos, df_pq_maquinas, df_valores_locacao, df_contratos, df_ams_dash
    # endregion
    # ========================================================