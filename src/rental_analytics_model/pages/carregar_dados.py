import streamlit as st

from rental_analytics_model.utils import loaders
from rental_analytics_model.components.arquivos_recibos import arquivos_recebidos

def show():

    files = st.session_state.files
    uploaded_files = loaders.load_files()
    files.extend(uploaded_files)

    if files:
        lista_unicos, df_pq_maquinas, df_valores_locacao, df_contratos, df_ams_dash = arquivos_recebidos(files)
        return lista_unicos, df_pq_maquinas, df_valores_locacao, df_contratos, df_ams_dash
    
    return None, None, None, None, None