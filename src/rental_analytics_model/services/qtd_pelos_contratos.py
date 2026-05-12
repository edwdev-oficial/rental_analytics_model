import pandas as pd
import streamlit as st

def qtd_pelos_contratos():
    st.session_state.title = 'Test Dev - Qtds Pelos Contratos'
    df_contratos = st.session_state.df_contratos.copy()

    df_ativos = (
        df_contratos
        .groupby(['patrimonio', 'familia', 'modelo'], as_index=False)
        .size()

    )
    df_ativos = (
        df_ativos
        .groupby(['familia', 'modelo'])
        .size()
        .reset_index(name='Qtd.')
    )
    return df_ativos