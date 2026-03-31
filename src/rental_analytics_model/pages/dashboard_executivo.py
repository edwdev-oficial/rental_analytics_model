import streamlit as st
import pandas as pd
from rental_analytics_model.services.valores_locacao import load_xlsx
from rental_analytics_model.services.data_recibos import load_data_recibos
from rental_analytics_model.services.normal_itens import load_normal_itens
from rental_analytics_model.components.dashboard_executifo import show_dash
from rental_analytics_model.utils import formaters

def load_familias():
    familias = ['']
    if not st.session_state.df_recibos.empty:
        familias.extend(sorted(
            list(
                st.session_state.df_recibos[st.session_state.df_recibos['Tipo'] == 'Ferramenta']
                ['Linha']
                .unique()
            )
        ))
    elif st.session_state.df_pq_maquinas is not None and not st.session_state.df_pq_maquinas.empty:
        familias.extend(sorted(
            list(
                st.session_state.df_pq_maquinas['Linha']
                .unique()
            )
        ))        
    return familias

def load_modelos(familia):
    modelos = ['']
    if not st.session_state.df_recibos.empty:
        modelos.extend(sorted(
            list(
                st.session_state.df_recibos[st.session_state.df_recibos['Linha'] == familia]
                ['Modelo']
                .unique()
            )
        ))
    elif st.session_state.df_pq_maquinas is not None and not st.session_state.df_pq_maquinas.empty:
        modelos.extend(sorted(
            list(
                st.session_state.df_pq_maquinas[st.session_state.df_pq_maquinas['Linha'] == familia]
                ['Modelo']
                .unique()
            )
        ))        
    return modelos

def show (lista_unicos, df_pq_maquinas, df_valores_locacao, df_contratos):
    if 'df_recibos' not in st.session_state:
        st.session_state.df_recibos = pd.DataFrame()

    if not len(lista_unicos):
        st.error('Carregue os arquivos...')
        st.stop()

    df_recibos = load_data_recibos(lista_unicos, df_valores_locacao, df_contratos)
    if not df_recibos.empty:
        st.session_state.df_recibos = df_recibos

    familias = load_familias()


    familia = st.sidebar.selectbox(
        'Familia',
        familias,
        index=0
    )

    modelos = load_modelos(familia)

    modelo = st.sidebar.selectbox(
        'Modelo',
        modelos,
        index=0
    )

    show_dash(df_recibos, df_pq_maquinas, familia, modelo)

