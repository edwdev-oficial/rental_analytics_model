import streamlit as st
import pandas as pd

from rental_analytics_model.services.calcular_periodos import calcular_periodos_df
from rental_analytics_model.services.calcular_valor import calcular_valor

def show(
    df_pq_maquinas,
    df_valores_locacao,
    contratos
):
    st.title('Taxa de Ocupação')

    df_contratos = contratos.copy()
    df_recibos = st.session_state.df_recibos.copy()

    init_date = pd.to_datetime(st.sidebar.date_input(
        'Data Inicial',
        min_value=df_contratos['locacao'].min().date(),
        max_value=df_contratos['devolucao'].max().date(),
        value=df_contratos['locacao'].min().date()
    ))

    end_date = pd.to_datetime(st.sidebar.date_input(
        'Data Final',
        min_value=df_contratos['locacao'].min().date(),
        max_value=df_contratos['devolucao'].max().date(),
        value=df_contratos['devolucao'].max().date()
    ))

    familias = ['']
    familias.extend(df_contratos['familia'].unique())
    familia = st.sidebar.selectbox('Família', familias)

    df_contratos = df_contratos[df_contratos['familia'].str.contains(familia, case=False, na=False)].copy()

    modelos = ['']
    modelos.extend(df_contratos['modelo'].unique())
    modelo = st.sidebar.selectbox('Modelo', modelos)

    df_contratos = df_contratos[df_contratos['modelo'].str.contains(modelo, case=False, na=False)].copy()

    df_contratos = df_contratos[
        (df_contratos['devolucao'] >= init_date) &
        (df_contratos['locacao'] <= end_date)
    ].copy()

    df_contratos.reset_index(inplace=True, drop=True)

    df_contratos = calcular_periodos_df(df_contratos)

    df_contratos['valor_contrato'] = df_contratos.apply(calcular_valor, axis=1)

    with st.expander('DataFrames'):


        # ========================================================
        # region DF CONTRATOS
        # ========================================================
        with st.expander('Contratos'):

            st.dataframe(df_contratos)
            valor_total_contratos = df_contratos['valor_contrato'].sum()
            st.write(f'Valor total dos contratos: R$ {valor_total_contratos:,.2f}')
            st.divider()
        # endregion
        # ========================================================


        # ========================================================
        # region DF RECIBOS
        # ========================================================
        with st.expander('Recibos'):
            df_recibos = st.session_state.df_recibos.copy()
            df_recibos['Período'] = pd.to_datetime(df_recibos['Período']).dt.to_period('M')
            df_recibos = df_recibos[df_recibos['Linha'].str.contains(familia, case=False, na=False)].copy()
            df_recibos = df_recibos[df_recibos['Modelo'].str.contains(modelo, case=False, na=False)].copy()
            st.write('df_recibos:')
            st.write(df_recibos)
            df_valores_gf = df_recibos.groupby(['Período', 'Modelo'])[['Qt.', 'Subtotal c/imp']].sum().reset_index()
            df_valores_gf['dias_mes'] = df_valores_gf['Período'].dt.days_in_month
            df_valores_gf['dias_possíveis'] = df_valores_gf['dias_mes'] * df_valores_gf['Qt.']
            st.write('df_valores_gf:')
            st.write(df_valores_gf)
            valor_total_gf = df_valores_gf['Subtotal c/imp'].sum()
            st.write(f'Valor total dos recibos: R$ {valor_total_gf:,.2f}')
            st.divider()
        # endregion
        # ========================================================

