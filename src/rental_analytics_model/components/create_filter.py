import pandas as pd
import streamlit as st

# def create_filter(df: pd.DataFrame, coluna, tilte, sidebar= True):
#     df_use = df.copy()
#     df_use[coluna] = df_use[coluna].astype('string')
#     df_use['prefixo'] = df_use[coluna].str.extract(r'([A-Za-z]+(?:-[A-Za-z]+)?)')
#     df_use['numero'] = df_use[coluna].str.extract(r'(\d+)').astype(int)
#     df_use = df_use.sort_values(['prefixo', 'numero']).drop(columns=['prefixo', 'numero'])

#     lista = ['']
#     values = list(df_use[coluna].unique())
#     lista.extend(values)
#     if sidebar:
#         return st.sidebar.selectbox(tilte, lista)

def create_filter(df: pd.DataFrame, coluna, tilte, sidebar=True):
    df_use = df.copy()
    df_use[coluna] = df_use[coluna].astype('string')

    tem_numero = df_use[coluna].str.contains(r'\d', na=False).any()

    if tem_numero:
        df_use['prefixo'] = df_use[coluna].str.extract(r'([A-Za-z]+(?:-[A-Za-z]+)?)')[0].fillna('')
        df_use['numero'] = pd.to_numeric(
            df_use[coluna].str.extract(r'(\d+)')[0],
            errors='coerce'
        ).fillna(999999)

        df_use = df_use.sort_values(['prefixo', 'numero']).drop(columns=['prefixo', 'numero'])
    else:
        df_use = df_use.sort_values(coluna)

    lista = ['']
    values = df_use[coluna].dropna().unique().tolist()
    lista.extend(values)

    if sidebar:
        return st.sidebar.selectbox(tilte, lista)