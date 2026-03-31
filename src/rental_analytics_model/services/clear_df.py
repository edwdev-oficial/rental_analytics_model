import pandas as pd
import streamlit as st

def clear_df_pq_maquinas(df):
    df['Qt.'] = 1
    df = df.fillna('')
    df = df[df['Status da ferramenta'] != 'Roubado']
    df['Subtotal c/imp'] = 0
    df = df[['Linha', 'Modelo', 'Qt.', 'Subtotal c/imp']]

    if st.session_state.df_valores_locacao is not None and not st.session_state.df_valores_locacao.empty:
        st.write('DEBUG - clear_df_pq_maquinas')
        st.write('DEBUG - df_valores_locacao')
        st.write(st.session_state.df_valores_locacao)
        df_valores_locacao = st.session_state.df_valores_locacao
        df = df.merge(
                df_valores_locacao[['Modelo', 'dia', 'semana', 'quinzena', 'mes']],
                on='Modelo',
                how='left'
            )

    return df