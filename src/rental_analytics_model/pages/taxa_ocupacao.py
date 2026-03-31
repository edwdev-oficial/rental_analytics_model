import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from rental_analytics_model.services.calcular_periodos import calcular_periodos_df
from rental_analytics_model.services.calcular_valor import calcular_valor

def show(
    df_pq_maquinas,
    df_valores_locacao,
    contratos
):
    st.title('Taxa de Ocupação')

    df_contratos = contratos.copy()
    df_valores_locacao = df_valores_locacao.copy()
    df_recibos = st.session_state.df_recibos.copy()
    df_recibos['Período'] = pd.to_datetime(df_recibos['Período']).dt.to_period('M')

    init_date = pd.to_datetime(st.sidebar.date_input(
        'Data Inicial',
        min_value=df_recibos['Período'].min().start_time.date(),
        max_value=df_recibos['Período'].max().end_time.date(),
        value=df_recibos['Período'].min().start_time.date(),
    ))

    end_date = pd.to_datetime(st.sidebar.date_input(
        'Data Final',
        min_value=df_recibos['Período'].min().start_time.date(),
        max_value=df_recibos['Período'].max().end_time.date(),
        value=df_recibos['Período'].max().end_time.date()
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

    df_recibos = df_recibos[
        (df_recibos['Período'] >= init_date.to_period('M')) &
        (df_recibos['Período'] <= end_date.to_period('M'))
    ].copy()

    df_contratos.reset_index(inplace=True, drop=True)

    df_contratos = calcular_periodos_df(df_contratos)

    df_contratos['valor_contrato'] = df_contratos.apply(calcular_valor, axis=1)
    df_contratos['Período'] = df_contratos['locacao'].dt.to_period('M')

    df_contratos_agrupados = df_contratos.groupby(['Período', 'modelo'])[['dias','mes','quinzena','semana','dia','valor_contrato']].sum().reset_index()

    with st.expander('DataFrames'):

        # ========================================================
        # region DF CONTRATOS
        # ========================================================
        with st.expander('Contratos'):

            st.dataframe(df_contratos)
            valor_total_contratos = df_contratos['valor_contrato'].sum()
            st.write(f'Valor total dos contratos: R$ {valor_total_contratos:,.2f}')
            st.divider()
            st.write('df_contratos_agrupados:')
            st.dataframe(df_contratos_agrupados)
        # endregion
        # ========================================================

        with st.expander('Valores de Locação'):
            df_valores_locacao.rename(columns={
                'Modelo': 'modelo',
                'dia': 'p_dia',
                'semana': 'p_semana',
                'quinzena': 'p_quinzena',
                'mes': 'p_mes'
            }, inplace=True)
            st.dataframe(df_valores_locacao)

        # ========================================================
        # region DF RECIBOS
        # ========================================================
        with st.expander('Recibos'):
            
            df_recibos = df_recibos[df_recibos['Linha'].str.contains(familia, case=False, na=False)].copy()
            df_recibos = df_recibos[df_recibos['Modelo'].str.contains(modelo, case=False, na=False)].copy()
            st.write('df_recibos:')
            st.write(df_recibos)
            df_valores_gf = df_recibos.groupby(['Período', 'Modelo'])[['Qt.', 'Subtotal c/imp']].sum().reset_index()
            df_valores_gf['dias_mes'] = df_valores_gf['Período'].dt.days_in_month
            df_valores_gf['dias_possíveis'] = df_valores_gf['dias_mes'] * df_valores_gf['Qt.']
            df_valores_gf.rename(columns={'Modelo': 'modelo'}, inplace=True)
            df_valores_gf = pd.merge(df_valores_gf, df_contratos_agrupados, on=['Período', 'modelo'], how='left')
            df_valores_gf.rename(columns={'dias': 'dias_loc'}, inplace=True)
            df_valores_gf['tx_ocupacao'] = df_valores_gf['dias_loc'] / df_valores_gf['dias_possíveis']
            df_valores_gf = pd.merge(df_valores_gf, df_valores_locacao, on=['modelo'], how='left')
            df_valores_gf['mix_dia'] = df_valores_gf['dia'] / df_valores_gf['dias_loc']
            df_valores_gf['mix_semana'] = df_valores_gf['semana'] * 7 / df_valores_gf['dias_loc']
            df_valores_gf['mix_quinzena'] = df_valores_gf['quinzena'] * 15 / df_valores_gf['dias_loc']
            df_valores_gf['mix_mes'] = df_valores_gf['mes'] * 30 / df_valores_gf['dias_loc']
            df_valores_gf['pot_dia'] = df_valores_gf['p_dia'] * df_valores_gf['dias_possíveis'] * df_valores_gf['mix_dia']
            df_valores_gf['pot_semana'] = df_valores_gf['p_semana'] * df_valores_gf['dias_possíveis'] * df_valores_gf['mix_semana'] / 7
            df_valores_gf['pot_quinzena'] = df_valores_gf['p_quinzena'] * df_valores_gf['dias_possíveis'] * df_valores_gf['mix_quinzena'] / 15
            df_valores_gf['pot_mes'] = df_valores_gf['p_mes'] * df_valores_gf['dias_possíveis'] * df_valores_gf['mix_mes'] / 30
            df_valores_gf['potencial'] = df_valores_gf['pot_dia'] + df_valores_gf['pot_semana'] + df_valores_gf['pot_quinzena'] + df_valores_gf['pot_mes']
            df_valores_gf['ocupa x potencial'] = df_valores_gf['tx_ocupacao'] * df_valores_gf['potencial']
            # df_valores_gf['confere'] =  df_valores_gf['ocupa x potencial'] == df_valores_gf['valor_contrato']
            df_valores_gf['confere'] = np.isclose(
                df_valores_gf['ocupa x potencial'],
                df_valores_gf['valor_contrato'],
                atol=0.01
            )
            df_valores_gf['markup'] = df_valores_gf['valor_contrato'] / df_valores_gf['Subtotal c/imp']
            df_valores_gf['margem'] = (df_valores_gf['valor_contrato'] - df_valores_gf['Subtotal c/imp']) / df_valores_gf['valor_contrato']    
            st.write('df_valores_gf:')
            st.write(df_valores_gf)
            valor_total_gf = df_valores_gf['Subtotal c/imp'].sum()
            st.write(f'Valor total dos recibos: R$ {valor_total_gf:,.2f}')
            st.divider()
        # endregion
        # ========================================================

        df_base = df_valores_gf[['Período', 'modelo', 'Qt.', 'Subtotal c/imp', 'valor_contrato', 'tx_ocupacao', 'potencial', 'ocupa x potencial', 'confere', 'markup', 'margem']].copy()
        st.write('df_base:')
        st.write(df_base)

        df_base = df_base.groupby(['modelo'])[['Subtotal c/imp', 'valor_contrato', 'potencial']].sum().reset_index()
        df_base['tx_ocupacao'] = df_base['valor_contrato'] / df_base['potencial']
        df_base['faturamento'] = df_base['tx_ocupacao'] * df_base['potencial']
        df_base = df_base[['modelo', 'Subtotal c/imp', 'potencial', 'tx_ocupacao', 'faturamento']].copy()
        df_base.rename(columns={
            'modelo': 'Modelo',
            'Subtotal c/imp': 'Custo G.F.',
            'potencial': 'Potencial',
            'tx_ocupacao': 'Taxa de Ocupação',
            'faturamento': 'Faturamento'
        }, inplace=True)
        df_base['Markup'] = df_base['Faturamento'] / df_base['Custo G.F.']
        df_base['Margem (%)'] = round((df_base['Faturamento'] - df_base['Custo G.F.']) / df_base['Faturamento'] * 100, 2)
        df_base['Tx Ocupação Break Even (%)'] = round(df_base['Custo G.F.'] / df_base['Potencial'] * 100, 2)
        st.write('df_base agrupado:')
        st.write(df_base)

    fig1 = px.bar(df_base, x='Modelo', y=['Potencial', 'Faturamento', 'Custo G.F.'], barmode='group')
    st.plotly_chart(fig1, use_container_width=True)

    df_base['tx_ocupacao_percent'] = df_base['Taxa de Ocupação'] * 100
    fig2 = px.bar(df_base, x='Modelo', y=['tx_ocupacao_percent', 'Tx Ocupação Break Even (%)'], barmode='group')
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.scatter(
        df_base,
        x='Taxa de Ocupação',
        y='Tx Ocupação Break Even (%)',
        text='Modelo'
    )
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = px.bar(df_base, x='Margem (%)', y='Modelo', orientation='h')
    st.plotly_chart(fig4, use_container_width=True)


    fig5 = px.scatter(
        df_base,
        x='Markup',
        y='Margem (%)',
        text='Modelo'
    )
    st.plotly_chart(fig5, use_container_width=True)


    fig6 = px.bar(df_base.sort_values('Faturamento'), x='Faturamento', y='Modelo', orientation='h')
    st.plotly_chart(fig6, use_container_width=True)

    df_base['Eficiência'] = df_base['Faturamento'] / df_base['Potencial']
    st.dataframe(df_base[['Modelo', 'Potencial', 'Faturamento', 'Eficiência']])

    df_base['Gap Ocupação'] = df_base['Taxa de Ocupação'] * 100 - df_base['Tx Ocupação Break Even (%)']
    st.dataframe(df_base[['Modelo', 'Taxa de Ocupação', 'Tx Ocupação Break Even (%)', 'Gap Ocupação']])