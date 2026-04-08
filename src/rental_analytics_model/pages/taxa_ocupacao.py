# ========================================================
# region IMPORTS
# ========================================================
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder


from rental_analytics_model.components import table
from rental_analytics_model.utils import gerar_excel
from rental_analytics_model.services.calcular_valor import calcular_valor
from rental_analytics_model.services.calcular_periodos import calcular_periodos_df
from rental_analytics_model.utils import formaters
# endregion
# ========================================================

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

    df_contratos = df_contratos[
        (df_contratos['devolucao'] >= init_date) &
        (df_contratos['locacao'] <= end_date) &
        (df_contratos['modelo'].str.contains(modelo, case=False, na=False))
    ].copy()

    df_recibos = df_recibos[
        (df_recibos['Período'] >= init_date.to_period('M')) &
        (df_recibos['Período'] <= end_date.to_period('M')) &
        (df_recibos['Linha'].str.contains(familia, case=False, na=False)) &
        (df_recibos['Modelo'].str.contains(modelo, case=False, na=False))
    ].copy()

    df_contratos.reset_index(inplace=True, drop=True)

    df_contratos = calcular_periodos_df(df_contratos)
    df_contratos['valor_contrato'] = df_contratos.apply(calcular_valor, axis=1)
    df_contratos['Período'] = df_contratos['locacao'].dt.to_period('M')
    
    # st.dataframe(df_recibos)
    # st.dataframe(df_contratos)


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

        # ========================================================
        # region VALORES DE LOCACAO
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
        # endregion
        # ========================================================

        # ========================================================
        # region RECIBOS
        # ========================================================
        with st.expander('Recibos'):
            st.dataframe(df_recibos)
            valor_total_recibos = df_recibos['Subtotal c/imp'].sum()
            st.write(f'Valor total dos Recibos: R$ {valor_total_recibos:,.2f}')
            st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region DF CALCULADO
        # ========================================================
        with st.expander('Cálculos'):
            df_calculado = df_recibos.groupby(['Período', 'Modelo'])[['Qt.', 'Subtotal c/imp']].sum().reset_index()
            df_calculado['dias_mes'] = df_calculado['Período'].dt.days_in_month
            df_calculado['dias_possíveis'] = df_calculado['dias_mes'] * df_calculado['Qt.']
            df_calculado.rename(columns={'Modelo': 'modelo'}, inplace=True)
            df_calculado = pd.merge(df_calculado, df_contratos_agrupados, on=['Período', 'modelo'], how='left')
            df_calculado.rename(columns={'dias': 'dias_loc'}, inplace=True)
            df_calculado['tx_ocupacao'] = df_calculado['dias_loc'] / df_calculado['dias_possíveis']
            df_calculado = pd.merge(df_calculado, df_valores_locacao, on=['modelo'], how='left')
            df_calculado['mix_dia'] = df_calculado['dia'] / df_calculado['dias_loc']
            df_calculado['mix_semana'] = df_calculado['semana'] * 7 / df_calculado['dias_loc']
            df_calculado['mix_quinzena'] = df_calculado['quinzena'] * 15 / df_calculado['dias_loc']
            df_calculado['mix_mes'] = df_calculado['mes'] * 30 / df_calculado['dias_loc']
            df_calculado['pot_dia'] = df_calculado['p_dia'] * df_calculado['dias_possíveis'] * df_calculado['mix_dia']
            df_calculado['pot_semana'] = df_calculado['p_semana'] * df_calculado['dias_possíveis'] * df_calculado['mix_semana'] / 7
            df_calculado['pot_quinzena'] = df_calculado['p_quinzena'] * df_calculado['dias_possíveis'] * df_calculado['mix_quinzena'] / 15
            df_calculado['pot_mes'] = df_calculado['p_mes'] * df_calculado['dias_possíveis'] * df_calculado['mix_mes'] / 30
            df_calculado['potencial'] = df_calculado['pot_dia'] + df_calculado['pot_semana'] + df_calculado['pot_quinzena'] + df_calculado['pot_mes']
            df_calculado['ocupa x potencial'] = df_calculado['tx_ocupacao'] * df_calculado['potencial']
            # df_calculado['confere'] =  df_calculado['ocupa x potencial'] == df_calculado['valor_contrato']
            df_calculado['confere'] = np.isclose(
                df_calculado['ocupa x potencial'],
                df_calculado['valor_contrato'],
                atol=0.01
            )
            df_calculado['markup'] = df_calculado['valor_contrato'] / df_calculado['Subtotal c/imp']
            df_calculado['margem'] = (df_calculado['valor_contrato'] - df_calculado['Subtotal c/imp']) / df_calculado['valor_contrato']    
            st.write('df_calculado:')
            st.write(df_calculado)
            valor_total_gf = df_calculado['Subtotal c/imp'].sum()
            st.write(f'Valor total dos Recibos de G.F.: R$ {valor_total_gf:,.2f}')
            st.divider()
            df_calculado_copia = df_calculado.copy()
            df_calculado_copia = df_calculado_copia[
                [
                    'modelo',
                    'Período',
                    'dias_mes',
                    'Qt.',
                    'dias_possíveis',
                    'dias_loc',
                    'dia',
                    'semana',
                    'quinzena',
                    'mes',
                    'tx_ocupacao',
                    'p_dia',
                    'p_semana',
                    'p_quinzena',
                    'p_mes',
                    'mix_dia',
                    'mix_semana',
                    'mix_quinzena',
                    'mix_mes',
                    'pot_dia',
                    'pot_semana',
                    'pot_quinzena',
                    'pot_mes',
                    'potencial',

                ]
            ]
            df_calculado_copia['real_dia'] = df_calculado_copia['p_dia'] * df_calculado_copia['dia']
            df_calculado_copia['real_semana'] = df_calculado_copia['p_semana'] * df_calculado_copia['semana']
            df_calculado_copia['real_quinzena'] = df_calculado_copia['p_quinzena'] * df_calculado_copia['quinzena']
            df_calculado_copia['real_mes'] = df_calculado_copia['p_mes'] * df_calculado_copia['mes']
            df_calculado_copia['real_total'] = df_calculado_copia['real_dia'] + df_calculado_copia['real_semana'] + df_calculado_copia['real_quinzena'] + df_calculado_copia['real_mes']
            df_calculado_copia['confere'] = np.isclose(
                df_calculado_copia['tx_ocupacao'] * df_calculado_copia['potencial'],
                df_calculado_copia['real_total'],
                atol=0.01
            )
            st.dataframe(df_calculado_copia)
            gerar_excel.dowload(df_calculado_copia, 'rental_analytics_model_calculos')
        # endregion
        # ========================================================

        # ========================================================
        # region BASE PARA ANALISE
        # ========================================================
        with st.expander('Base para análise'):
            df_base = df_calculado[['Período', 'modelo', 'Qt.', 'Subtotal c/imp', 'valor_contrato', 'tx_ocupacao', 'potencial', 'ocupa x potencial', 'confere', 'markup', 'margem']].copy()
            st.write('df_base:')
            st.write(df_base)

            df_base = df_base.groupby(['modelo'])[['Subtotal c/imp', 'valor_contrato', 'potencial']].sum().reset_index()
            df_base['tx_ocupacao'] = round(df_base['valor_contrato'] / df_base['potencial'], 4)
            df_base['faturamento'] = df_base['tx_ocupacao'] * df_base['potencial']
            df_base = df_base[['modelo', 'Subtotal c/imp', 'potencial', 'tx_ocupacao', 'faturamento']].copy()
            df_base.rename(columns={
                'modelo': 'Modelo',
                'Subtotal c/imp': 'Custo G.F.',
                'potencial': 'Potencial',
                'tx_ocupacao': 'Taxa de Ocupação',
                'faturamento': 'Faturamento'
            }, inplace=True)
            df_base['Ocupação'] = df_base['Taxa de Ocupação'] * 100
            df_base['Markup'] = df_base['Faturamento'] / df_base['Custo G.F.']
            df_base['Margem'] = round((df_base['Faturamento'] - df_base['Custo G.F.']) / df_base['Faturamento'] * 100, 2)
            df_base['Break Even'] = round(df_base['Custo G.F.'] / df_base['Potencial'] * 100, 2)
            st.write('df_base agrupado:')
            st.write(df_base)
        # endregion
        # ========================================================

    # ========================================================
    # region SHOW DF
    # ========================================================
    def status_ocupacao(row):
        ocup_break_even = row['Break Even']
        ocup = row['Ocupação']

        if ocup >= ocup_break_even * 2:
            return f'🟢 {ocup:.2f}%'
        elif ocup > ocup_break_even:
            return f'🟡 {ocup:.2f}%'
        else:
            return f'🔴 {ocup:.2f}%'

    df_base_show = df_base.copy()
    df_base_show['Ocupação'] = df_base_show.apply(status_ocupacao, axis=1)
    df_base_show = df_base_show[['Modelo',
        'Custo G.F.',
        'Potencial',
        'Break Even',
        'Ocupação',
        'Faturamento',
        'Markup',
        'Margem',
    ]]
    # st.table(df_base_show, border="horizontal")
    df_base_show['Custo G.F.'] = df_base_show['Custo G.F.'].map(lambda x: formaters.br_num(x, 2))
    df_base_show['Potencial'] = df_base_show['Potencial'].map(lambda x: formaters.br_num(x, 2))
    df_base_show['Break Even'] = df_base_show['Break Even'].map(lambda x: f'{formaters.br_num(x, 2)}%')
    df_base_show['Faturamento'] = df_base_show['Faturamento'].map(lambda x: formaters.br_num(x, 2))
    df_base_show['Markup'] = df_base_show['Markup'].map(lambda x: formaters.br_num(x, 1))
    df_base_show['Margem'] = df_base_show['Margem'].map(lambda x: f'{formaters.br_num(x, 2)}%')
    table.personal_table(df_base_show)
    gerar_excel.dowload(df_base_show, 'ocupacao')
    st.divider()

    df_base_total = df_base[['Custo G.F.', 'Potencial', 'Faturamento']].sum().to_frame().T
    df_base_total['Break Even'] = df_base_total['Custo G.F.'] / df_base_total['Potencial']
    df_base_total['Markup'] = df_base_total['Faturamento'] / df_base_total['Custo G.F.']
    df_base_total['Margem'] = (df_base_total['Faturamento'] - df_base_total['Custo G.F.']) / df_base_total['Faturamento']
    df_base_total['Ocupação'] = df_base_total['Faturamento'] / df_base_total['Potencial'] * 100
    df_base_total['Ocupação'] = df_base_total.apply(status_ocupacao, axis=1)

    df_base_total = df_base_total[[
        'Custo G.F.',
        'Potencial',
        'Break Even',
        'Ocupação',
        'Faturamento',
        'Markup',
        'Margem'        
    ]]

    df_exibir = df_base_total.copy()
    df_exibir['Break Even'] = df_exibir['Break Even'] * 100
    df_exibir['Margem'] = df_exibir['Margem'] * 100
    df_exibir["Custo G.F."] = df_exibir["Custo G.F."].map(lambda x: formaters.br_num(x, 2))
    df_exibir["Potencial"] = df_exibir["Potencial"].map(lambda x: formaters.br_num(x, 2))
    df_exibir["Break Even"] = df_exibir["Break Even"].map(lambda x: f'{formaters.br_num(x, 2)}%')
    df_exibir["Faturamento"] = df_exibir["Faturamento"].map(lambda x: formaters.br_num(x, 2))
    df_exibir["Markup"] = df_exibir["Markup"].map(lambda x: formaters.br_num(x, 2))
    df_exibir["Margem"] = df_exibir["Margem"].map(lambda x: f'{formaters.br_num(x, 2)}%')

    table.personal_table(df_exibir)

    # endregion
    # ========================================================



    # fig1 = px.bar(df_base, x='Modelo', y=['Potencial', 'Faturamento', 'Custo G.F.'], barmode='group')
    # st.plotly_chart(fig1, use_container_width=True)

    # df_base['tx_ocupacao_percent'] = df_base['Taxa de Ocupação'] * 100
    # fig2 = px.bar(df_base, x='Modelo', y=['tx_ocupacao_percent', 'Break Even'], barmode='group')
    # st.plotly_chart(fig2, use_container_width=True)

    # fig3 = px.scatter(
    #     df_base,
    #     x='Taxa de Ocupação',
    #     y='Break Even',
    #     text='Modelo'
    # )
    # st.plotly_chart(fig3, use_container_width=True)

    # fig4 = px.bar(df_base, x='Margem (%)', y='Modelo', orientation='h')
    # st.plotly_chart(fig4, use_container_width=True)


    # fig5 = px.scatter(
    #     df_base,
    #     x='Markup',
    #     y='Margem (%)',
    #     text='Modelo'
    # )
    # st.plotly_chart(fig5, use_container_width=True)


    # fig6 = px.bar(df_base.sort_values('Faturamento'), x='Faturamento', y='Modelo', orientation='h')
    # st.plotly_chart(fig6, use_container_width=True)

    # df_base['Eficiência'] = df_base['Faturamento'] / df_base['Potencial']
    # st.dataframe(df_base[['Modelo', 'Potencial', 'Faturamento', 'Eficiência']])

    # df_base['Gap Ocupação'] = df_base['Taxa de Ocupação'] * 100 - df_base['Break Even']
    # st.dataframe(df_base[['Modelo', 'Taxa de Ocupação', 'Break Even', 'Gap Ocupação']])