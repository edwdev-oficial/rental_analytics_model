import pandas as pd
import streamlit as st

df_precos = st.session_state.df_valores_locacao.copy()
df_precos = df_precos.set_index(df_precos.columns[0]).T

def calcular_valor(row):
    modelo = row['modelo']
    
    try:
        return (
            row['dia']      * df_precos.loc['dia', modelo] +
            row['semana']   * df_precos.loc['semana', modelo] +
            row['quinzena'] * df_precos.loc['quinzena', modelo] +
            row['mes']      * df_precos.loc['mes', modelo]
        )
    except KeyError:
        return 0    
