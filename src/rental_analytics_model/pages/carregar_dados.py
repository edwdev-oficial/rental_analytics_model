import streamlit as st

from rental_analytics_model.utils import loaders
from rental_analytics_model.components.arquivos_recibos import arquivos_recebidos

def show(arquivos_unicos):
    uploaded_files = loaders.load_files()
    arquivos_unicos.extend(uploaded_files)

    if arquivos_unicos:
        lista_unicos, df_valores_locacao, df_contratos = arquivos_recebidos(arquivos_unicos)
        return lista_unicos, df_valores_locacao, df_contratos
    
    return None, None, None