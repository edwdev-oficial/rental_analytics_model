# ========================================================
# region IMPORTS
# ========================================================
import math
import json
import numpy as np
import pandas as pd
from io import BytesIO
import streamlit as st
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

from rental_analytics_model.utils import (
    loaders,
    formaters,
    gerar_excel
)
from rental_analytics_model.services.data_recibos import load_data_recibos
from rental_analytics_model.components import (
    create_filter,
    table
)

# endregion
# ========================================================

def test(session_state):

    # from rental_analytics_model.services.data_recibos import load_data_recibos
    # from rental_analytics_model.services.calcular_periodos import calcular_periodos_df
    # from rental_analytics_model.services.calculos import calcular_faturamento_frota
    # from rental_analytics_model.services.calcular_valor import calcular_valor
    # from rental_analytics_model.utils import (
    #     loaders,
    #     formaters,
    #     gerar_excel
    # )
    # from rental_analytics_model.utils import formaters

    # ========================================================
    # region TITLE
    # ========================================================
    if 'title' not in st.session_state:
        st.session_state.title = 'Teste Dev'
    st.title(st.session_state.title)
    # endregion
    # ========================================================

    # ========================================================
    # region EXPANDER SESSION.STATE
    # ========================================================
    # if show_session_state := st.sidebar.checkbox('Show session state'):
    if 'show_session_state' not in st.session_state:
        st.session_state.show_session_state = False
    if st.session_state.show_session_state:
        with st.expander('Sesseion State'):
            st.write(st.session_state)
    st.divider()
    # endregion
    # ========================================================

    # ========================================================
    # region GAUGE_GRAPH
    # ========================================================
    def gauge_graph():
        lista_unicos = session_state.files

        df_valores_locacao = session_state.df_valores_locacao.copy()
        
        df_contratos = session_state.df_contratos.copy()
        df_contratos['locacao'] = df_contratos['locacao'] + pd.DateOffset(years=1)
        df_contratos['devolucao'] = df_contratos['devolucao'] + pd.DateOffset(years=1)

        df_recibos = load_data_recibos(lista_unicos, df_valores_locacao, df_contratos)
        df_recibos['periodo_dt'] = pd.to_datetime(df_recibos['Período'], format='%m/%Y')

        min_date_recibos = df_recibos['periodo_dt'].min()
        max_date_recibos = (df_recibos['periodo_dt'].max() + pd.DateOffset(months=1)) - pd.DateOffset(days=1)

        #%% FILTROS
        df_contratos = df_contratos[
            (df_contratos['locacao'] >= min_date_recibos)
            &
            (df_contratos['locacao'] <= max_date_recibos)
        ].reset_index(drop=True)

        # st.write(f'min_date_recibos: {min_date_recibos} | max_date_recibos {max_date_recibos}')

        #%% SHOW DATAFRAMES
        st.write('Recibos G.F.')
        st.dataframe(df_recibos)
        st.divider()
        
        st.write('Valores Locação')
        st.dataframe(df_valores_locacao)
        st.divider()
        
        st.write('Contratos')
        st.dataframe(df_contratos)
        st.divider()

        #%% CÁLCULOS
        valor_total_recibos = df_recibos['Subtotal c/imp'].sum()
        valor_total_contratos = df_contratos['valor'].sum()
        margem_de_contribuicao = (valor_total_contratos - valor_total_recibos) / valor_total_contratos
        markup = (valor_total_contratos - valor_total_recibos ) / valor_total_recibos * 100
        lucro_bruto = valor_total_contratos - valor_total_recibos

        #%% RESUMO
        st.subheader('Resumo')
        st.write(f'Valor total dos recibos {formaters.format_brl(valor_total_recibos, True)}')
        st.write(f'Valor total de contratos: {formaters.format_brl(valor_total_contratos, True)}')
        st.write(f'Margem de contribuição: {round(margem_de_contribuicao * 100, 1)}%')
        st.write(f'Markup: {round(markup, 1)}')
        st.write(f'Lucro bruto: {formaters.format_brl(lucro_bruto, True)}')
        st.divider()

        #%% INSITE
        st.subheader('💡 Insites')
        st.html(f"""
            <div>
                <p>🔴 Ponto de equilíbrio total</p>
                <p>🔴 Ponto de equilíbrio por máquina</p>
            </div>
        """)

        valor_gf = st.session_state.valor_gf
        # valor_gf = 300000
        potencial_tot_faturamento = st.session_state.Potencial_faturamento
        tx_disp = st.session_state.tx_disponibilidade / 100
        st.write(f'Valor G.F.: {formaters.format_brl(valor_gf)}')
        st.write(f'Potencial total de faturamento: {formaters.format_brl(potencial_tot_faturamento)}')
        st.write(f'Taxa de disponibilidade: {tx_disp * 100}%')

        tx_ocup_mark_up = (valor_gf / potencial_tot_faturamento / tx_disp) * 100
        st.write(f'Taxa ocupação mínima para mark up: {round(tx_ocup_mark_up, 1)}%')

        col1, col2, col3, col4 = st.columns(4)


        with col1:
            tx_ocupacao = tx_ocup_mark_up

            fig = go.Figure(
                go.Indicator(
                    mode='gauge+number',
                    value=tx_ocupacao,
                    title={'text': 'Taxa de ocupação % Break Even'},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"thickness": 0.22},
                        "steps": [
                            {"range": [0, tx_ocupacao], "color": "#d2051e"},
                            {"range": [tx_ocupacao, 55], "color": "rgba(82, 79, 83, 0.2)"},
                            {"range": [55, 100], "color": "rgba(82, 79, 83, 0.6)"},
                        ],
                        "threshold": {
                            "line": {"color": "yellow", "width": 1},
                            "thickness": 0.5,
                            "value": tx_ocupacao
                        }
                    }
                )
            )

            # with st.container(border=True):
            st.plotly_chart(fig, key='gauge')
        
        
        with col2:
            tx_ocupacao = 60

            fig = go.Figure(
                go.Indicator(
                    mode='gauge+number',
                    value=tx_ocupacao,
                    title={'text': 'Taxa de ocupação % Efetiva'},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"thickness": 0.22},
                        "steps": [
                            {"range": [0, 12], "color": "#d2051e"},
                            {"range": [12, 55], "color": "rgba(82, 79, 83, 0.2)"},
                            {"range": [55, 100], "color": "rgba(82, 79, 83, 0.6)"},
                        ],
                        "threshold": {
                            "line": {"color": "yellow", "width": 1},
                            "thickness": 0.5,
                            "value": 12
                        }
                    }
                )
            )

            # with st.container(border=True):
            st.plotly_chart(fig, key='gauge2')
    
    # endregion
    # ========================================================
    # gauge_graph()

    # ========================================================
    # region TAXA_OCUPACAO
    # ========================================================
    def taxa_ocupacao(session_state):

        st.subheader('Teste Dev Indicadores Chaves', divider='red')

        @st.cache_data
        def calcular_periodos_df(df):
            
            if df.empty:
                st.warning('Carregue o arquivo contratos')
                return
                
            # garante datetime
            df['locacao'] = pd.to_datetime(df['locacao'], format='%d/%m/%Y %H:%M')
            df['devolucao'] = pd.to_datetime(df['devolucao'], format='%d/%m/%Y %H:%M')
            # df['locacao'] = pd.to_datetime(df['locacao'], errors='coerce')
            # df['devolucao'] = pd.to_datetime(df['devolucao'], errors='coerce')

            # 🔥 cálculo vetorizado (igual sua regra de calendário)
            dias_total = (
                df['devolucao'].dt.normalize() - df['locacao'].dt.normalize()
            ).dt.days

            # mínimo 1 dia
            dias_total = dias_total.clip(lower=1)

            df['dias'] = dias_total

            df['mes'] = dias_total // 30
            dias_restantes = dias_total % 30

            df['quinzena'] = dias_restantes // 15
            dias_restantes = dias_restantes % 15

            df['semana'] = dias_restantes // 7
            df['dia'] = dias_restantes % 7

            return df 

        # ========================================================
        # region RECIBOS
        # ========================================================
        df_recibos = session_state.df_recibos.copy()
        df_recibos.rename(columns={'Linha': 'familia', 'Modelo': 'modelo'}, inplace=True)
        # df_recibos = df_recibos[df_recibos['familia'] == 'Rompedor']
        df_recibos_group = (
            df_recibos
            .groupby(['periodo','familia', 'modelo'], as_index=False)
            .agg({
                'Qt.': 'sum',
                'Subtotal c/imp': 'sum'
            })
        )
        st.write('Recibos agrupados')
        st.dataframe(df_recibos_group)
        st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region VALORES LOCACAO
        # ========================================================
        
        df_valores_locacao = st.session_state.df_valores_locacao.copy()
        df_valores_locacao.rename(columns={
                'Modelo': 'modelo',
                'dia': 'p_dia',
                'semana': 'p_semana',
                'quinzena': 'p_quinzena',
                'mes': 'p_mes'
            }, inplace=True)
        st.write('Valores Locação')
        st.dataframe(df_valores_locacao)
        st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region CONTRATOS
        # ========================================================
        df_contratos = session_state.df_contratos.copy()
        df_contratos = calcular_periodos_df(df_contratos)
        df_contratos['periodo'] = pd.to_datetime(df_contratos['locacao']).dt.to_period('M')
        st.write('df_contratos')
        st.dataframe(df_contratos)
        st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region FILTER CONTRATOS
        # ========================================================

        periodos = df_contratos['periodo'].unique().tolist()
        familias = sorted(df_contratos['familia'].unique().tolist())
        modelos = sorted(df_contratos['modelo'].unique().tolist())


        periodos_selected = st.sidebar.multiselect(
            'Periodos',
            options=periodos
        )
        
        familias_selected = st.sidebar.multiselect(
            'Familias',
            options=familias
        )
        
        modelos_selected = st.sidebar.multiselect(
            'Modelos',
            options=modelos
        )

        df_contratos = df_contratos[
                (df_contratos['periodo'].isin(periodos_selected))
                &
                (df_contratos['familia'].isin(familias_selected))
                &
                (df_contratos['modelo'].isin(modelos_selected))
            ]
        

        st.write('df_contratos')
        st.dataframe(df_contratos)
        st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region FILTER CONTRATOS GROUP
        # ========================================================
        # periodos = df_contratos_group['periodo'].unique().tolist()
        # familias = sorted(df_contratos_group['familia'].unique().tolist())
        # modelos = sorted(df_contratos_group['modelo'].unique().tolist())
        # # col1, col2, col3 = st.columns(3)
        # # with col1:
        # periodos_selected = st.sidebar.multiselect(
        #     'Periodos',
        #     options=periodos
        # )
        # # with col2:
        # familias_selected = st.sidebar.multiselect(
        #     'Familias',
        #     options=familias
        # )
        # # with col3:
        # modelos_selected = st.sidebar.multiselect(
        #     'Modelos',
        #     options=modelos
        # )
        # df_contratos_group = df_contratos_group[
        #         (df_contratos_group['periodo'].isin(periodos_selected))
        #         &
        #         (df_contratos_group['familia'].isin(familias_selected))
        #         &
        #         (df_contratos_group['modelo'].isin(modelos_selected))
        #     ]        
        # endregion
        # ========================================================        

        # ========================================================
        # region DF CONTRATOS GROUP
        # ========================================================
        
        df_contratos_group = df_contratos.copy()    
        df_contratos_group = (df_contratos
            .groupby(['periodo', 'familia', 'modelo'], as_index=False)
            .agg({
                'dias': 'sum',
                'dia': 'sum',
                'quinzena': 'sum',
                'semana': 'sum',
                'mes':'sum',
            })
        )        
        df_contratos_group = pd.merge(
            df_contratos_group, 
            df_recibos_group,
            on=['periodo', 'familia', 'modelo'],
            how='left',

        )

        df_contratos_group['dias_no_periodo'] = df_contratos_group['periodo'].dt.days_in_month
        df_contratos_group['dias_possiveis'] =  df_contratos_group['dias_no_periodo'] * df_contratos_group['Qt.']
        df_contratos_group['tx_disp'] = session_state.tx_disponibilidade / 100

        df_contratos_group = pd.merge(
            df_contratos_group,
            df_valores_locacao,
            on=['modelo'],
            how='left'
        )

        df_contratos_group = (
            df_contratos_group
            .groupby(['modelo'], as_index=False)
            .agg({
                'Subtotal c/imp': 'sum',
                'dias_possiveis': 'sum',
                'dias': 'sum',
                'dia': 'sum',
                'semana': 'sum',
                'quinzena': 'sum',
                'mes': 'sum',
                'p_dia': 'mean',
                'p_semana': 'mean',
                'p_quinzena': 'mean',
                'p_mes': 'mean',
            })
        )
        df_contratos_group['Tx Ocupação'] = df_contratos_group['dias'] / df_contratos_group['dias_possiveis']
        df_contratos_group['mix_dia'] = df_contratos_group['dia'] / df_contratos_group['dias']
        df_contratos_group['mix_semana'] = df_contratos_group['semana'] * 7 / df_contratos_group['dias']
        df_contratos_group['mix_quinzena'] = df_contratos_group['quinzena'] * 15 / df_contratos_group['dias']
        df_contratos_group['mix_mes'] = df_contratos_group['mes'] * 30 / df_contratos_group['dias']
        st.write('df_contratos_group')
        st.dataframe(df_contratos_group)
        from rental_analytics_model.utils.gerar_excel import dowload
        dowload(df_contratos_group, 'df_com_tx_ocupacao')
        st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region DF CONTRATOS GROUP COM MIX MODALIDADE
        # ========================================================
        df_contratos_group2 = df_contratos_group.copy()
        df_contratos_group2['total_contratos'] = df_contratos_group2[['dia', 'semana', 'quinzena', 'mes']].sum(axis=1)
        df_contratos_group2['mix_dia'] = df_contratos_group2['dia'] / df_contratos_group2['total_contratos']
        df_contratos_group2['mix_semana'] = df_contratos_group2['semana'] / df_contratos_group2['total_contratos']
        df_contratos_group2['mix_quinzena'] = df_contratos_group2['quinzena'] / df_contratos_group2['total_contratos']
        df_contratos_group2['mix_mes'] = df_contratos_group2['mes'] / df_contratos_group2['total_contratos']        
        df_contratos_group2['sum_mix'] = (
            df_contratos_group2['mix_dia']
            +
            df_contratos_group2['mix_semana'] * 7
            +
            df_contratos_group2['mix_quinzena'] * 15
            +
            df_contratos_group2['mix_mes'] * 30
        )

        # POTENCIAL   
        df_contratos_group2['dias_possiveis/sum_mix'] = df_contratos_group2['dias_possiveis'] / df_contratos_group2['sum_mix']
        df_contratos_group2['fator_dias_pot'] = df_contratos_group2['mix_dia'] * df_contratos_group2['dias_possiveis/sum_mix']
        df_contratos_group2['fator_semanas_pot'] = df_contratos_group2['mix_semana'] * df_contratos_group2['dias_possiveis/sum_mix']
        df_contratos_group2['fator_quinzenas_pot'] = df_contratos_group2['mix_quinzena'] * df_contratos_group2['dias_possiveis/sum_mix']
        df_contratos_group2['fator_meses_pot'] = df_contratos_group2['mix_mes'] * df_contratos_group2['dias_possiveis/sum_mix']       
        df_contratos_group2['pot_dia'] = df_contratos_group2['p_dia'] * df_contratos_group2['fator_dias_pot']
        df_contratos_group2['pot_semana'] = df_contratos_group2['p_semana'] * df_contratos_group2['fator_semanas_pot']
        df_contratos_group2['pot_quinzena'] = df_contratos_group2['p_quinzena'] * df_contratos_group2['fator_quinzenas_pot']
        df_contratos_group2['pot_mes'] = df_contratos_group2['p_mes'] * df_contratos_group2['fator_meses_pot']
        df_contratos_group2['Potencial'] = df_contratos_group2[['pot_dia', 'pot_semana', 'pot_quinzena', 'pot_mes']].sum(axis=1)

        # REAL
        df_contratos_group2['dias_real/sum_mix'] = df_contratos_group2['dias'] / df_contratos_group2['sum_mix']
        df_contratos_group2['fator_dias_real'] = df_contratos_group2['mix_dia'] * df_contratos_group2['dias_real/sum_mix']
        df_contratos_group2['fator_semanas_real'] = df_contratos_group2['mix_semana'] * df_contratos_group2['dias_real/sum_mix']
        df_contratos_group2['fator_quinzenas_real'] = df_contratos_group2['mix_quinzena'] * df_contratos_group2['dias_real/sum_mix']
        df_contratos_group2['fator_meses_real'] = df_contratos_group2['mix_mes'] * df_contratos_group2['dias_real/sum_mix']
        df_contratos_group2['real_dia'] = df_contratos_group2['p_dia'] * df_contratos_group2['fator_dias_real']
        df_contratos_group2['real_semana'] = df_contratos_group2['p_semana'] * df_contratos_group2['fator_semanas_real']
        df_contratos_group2['real_quinzena'] = df_contratos_group2['p_quinzena'] * df_contratos_group2['fator_quinzenas_real']
        df_contratos_group2['real_mes'] = df_contratos_group2['p_mes'] * df_contratos_group2['fator_meses_real']
        df_contratos_group2['Faturamento'] = df_contratos_group2[['real_dia', 'real_semana', 'real_quinzena', 'real_mes']].sum(axis=1)        
        
        st.write('df_contratos_group2')
        st.dataframe(df_contratos_group2)
        st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region DF CONTRATOS GROUP COM MIX FATURAMENTO
        # ========================================================
        # df_contratos_group['mix_fat_dia'] = df_contratos_group['dia'] / df_contratos_group['dias']
        # df_contratos_group['mix_fat_semana'] = df_contratos_group['semana'] * 7 / df_contratos_group['dias']
        # df_contratos_group['mix_fat_quinzena'] = df_contratos_group['quinzena'] * 15 / df_contratos_group['dias']
        # df_contratos_group['mix_fat_mes'] = df_contratos_group['mes'] * 30 / df_contratos_group['dias']

        # df_contratos_group['pot_dia'] = df_contratos_group['p_dia'] * df_contratos_group['dias_possiveis'] * df_contratos_group['mix_fat_dia']
        # df_contratos_group['pot_semana'] = df_contratos_group['p_semana'] * df_contratos_group['dias_possiveis'] / 7 * df_contratos_group['mix_fat_semana']
        # df_contratos_group['pot_quinzena'] = df_contratos_group['p_quinzena'] * df_contratos_group['dias_possiveis'] / 15 * df_contratos_group['mix_fat_quinzena']
        # df_contratos_group['pot_mes'] = df_contratos_group['p_mes'] * df_contratos_group['dias_possiveis'] / 30 * df_contratos_group['mix_fat_mes']
        df_contratos_group['pot_dia'] = df_contratos_group['p_dia'] * df_contratos_group['dias_possiveis'] * df_contratos_group['mix_dia']
        df_contratos_group['pot_semana'] = df_contratos_group['p_semana'] * df_contratos_group['dias_possiveis'] / 7 * df_contratos_group['mix_semana']
        df_contratos_group['pot_quinzena'] = df_contratos_group['p_quinzena'] * df_contratos_group['dias_possiveis'] / 15 * df_contratos_group['mix_quinzena']
        df_contratos_group['pot_mes'] = df_contratos_group['p_mes'] * df_contratos_group['dias_possiveis'] / 30 * df_contratos_group['mix_mes']
        df_contratos_group['Potencial'] = df_contratos_group[['pot_dia', 'pot_semana', 'pot_quinzena', 'pot_mes']].sum(axis=1)

        df_contratos_group['real_dia'] = df_contratos_group['dia'] * df_contratos_group['p_dia']
        df_contratos_group['real_semana'] = df_contratos_group['semana'] * df_contratos_group['p_semana']
        df_contratos_group['real_quinzena'] = df_contratos_group['quinzena'] * df_contratos_group['p_quinzena']
        df_contratos_group['real_mes'] = df_contratos_group['mes'] * df_contratos_group['p_mes']
        df_contratos_group['Faturamento'] = df_contratos_group[['real_dia', 'real_semana', 'real_quinzena', 'real_mes']].sum(axis=1)


        
        df_contratos_group.rename(columns={'Subtotal c/imp': 'Custo G.F.'}, inplace=True)
        st.write('df_contratos_group3')
        st.write(df_contratos_group)
        st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region STATUS OCUPAÇÃO
        # ========================================================
        def status_ocupacao(row):
            ocup_break_even = row['Break Even']
            ocup = row['Tx Ocupação']

            if ocup >= ocup_break_even * 2:
                return f'🟢 {ocup:.2f}%'
            elif ocup > ocup_break_even:
                return f'🟡 {ocup:.2f}%'
            else:
                return f'🔴 {ocup:.2f}%'
        # endregion
        # ========================================================

        # ========================================================
        # region RESULTADOS
        # ========================================================
        df_resultados = df_contratos_group.copy()
        df_resultados['Modelo'] = df_resultados['modelo']
        df_resultados['Break Even'] = df_resultados['Custo G.F.'] / df_resultados['Potencial'] * 100
        df_resultados['Markup'] = df_resultados['Faturamento'] / df_resultados['Custo G.F.']
        df_resultados['Margem'] = (df_resultados['Faturamento'] - df_resultados['Custo G.F.']) / df_resultados['Faturamento'] * 100
        df_resultados['Tx Ocupação'] = df_resultados['Tx Ocupação'] * 100
        df_resultados['Tx Ocupação'] = df_resultados.apply(status_ocupacao, axis=1)
        df_resultados['Custo G.F.'] = df_resultados['Custo G.F.'].map(lambda x: formaters.br_num(x, 2))
        df_resultados['Potencial'] = df_resultados['Potencial'].map(lambda x: formaters.br_num(x, 2))
        df_resultados['Break Even'] = df_resultados['Break Even'].map(lambda x: f'{formaters.br_num(x, 2)}%')
        df_resultados['Faturamento'] = df_resultados['Faturamento'].map(lambda x: formaters.br_num(x, 2))
        df_resultados['Markup'] = df_resultados['Markup'].map(lambda x: f'{formaters.br_num(x, 2)}%')
        df_resultados['Margem'] = df_resultados['Margem'].map(lambda x: f'{formaters.br_num(x, 2)}%')
        df_resultados = df_resultados[[
            'Modelo',
            'Custo G.F.',
            'Potencial',
            'Break Even',
            'Tx Ocupação',
            'Faturamento',
            'Markup',
            'Margem'
        ]]
        from rental_analytics_model.components import table
        st.subheader('Resultados')
        table.personal_table(df_resultados)
        st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region CALCULO POTENCIAL TOTAL
        # ========================================================
        df_pot_total = df_contratos_group[[
            'Custo G.F.',
            'dias_possiveis',
            'dias',
            'dia',
            'semana',
            'quinzena',
            'mes'
        ]].sum(skipna=True).to_frame().T
        df_pot_total['Tx Ocupação'] = df_pot_total['dias'] / df_pot_total['dias_possiveis']
        df_pot_total['preco_dia'] = df_contratos_group['p_dia'].mean()
        df_pot_total['preco_semana'] = df_contratos_group['p_semana'].mean()
        df_pot_total['preco_quinzena'] = df_contratos_group['p_quinzena'].mean()
        df_pot_total['preco_mes'] = df_contratos_group['p_mes'].mean()
        df_pot_total['mix_fat_dia'] = df_pot_total['dia'] / df_pot_total['dias']
        df_pot_total['mix_fat_semana'] = df_pot_total['semana'] * 7 / df_pot_total['dias']
        df_pot_total['mix_fat_quinzena'] = df_pot_total['quinzena'] * 15 / df_pot_total['dias']
        df_pot_total['mix_fat_mes'] = df_pot_total['mes'] * 30 / df_pot_total['dias']
        df_pot_total['pot_dia'] = df_pot_total['preco_dia'] * df_pot_total['dias_possiveis'] * df_pot_total['mix_fat_dia'] 
        df_pot_total['pot_semana'] = df_pot_total['preco_semana'] * df_pot_total['dias_possiveis'] / 7 * df_pot_total['mix_fat_semana'] 
        df_pot_total['pot_quinzena'] = df_pot_total['preco_quinzena'] * df_pot_total['dias_possiveis'] / 15 * df_pot_total['mix_fat_quinzena'] 
        df_pot_total['pot_mes'] = df_pot_total['preco_mes'] * df_pot_total['dias_possiveis'] / 30 * df_pot_total['mix_fat_mes'] 
        df_pot_total['Potencial'] = df_pot_total[['pot_dia', 'pot_semana', 'pot_quinzena', 'pot_mes']].sum(axis=1)
        df_pot_total['Faturamento'] = df_pot_total['Potencial'] * df_pot_total['Tx Ocupação']
        st.write('df_pot_total')
        st.dataframe(df_pot_total)
        st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region RESUMO E DF EXIBIR RESUMO
        # ========================================================
        df_resumo = df_pot_total[['Custo G.F.', 'Potencial', 'Tx Ocupação', 'Faturamento']].sum(skipna=True).to_frame().T
        df_resumo['Markup'] = df_resumo['Faturamento'] / df_resumo['Custo G.F.']
        df_resumo['Margem'] = (df_resumo['Faturamento'] - df_resumo['Custo G.F.']) / df_resumo['Faturamento'] * 100
        df_exibir = df_resumo.copy()
        df_exibir["Tx Ocupação"] = df_exibir["Tx Ocupação"] * 100
        df_exibir['Break Even'] = df_exibir['Custo G.F.'] / df_exibir['Potencial'] * 100
        df_exibir['Tx Ocupação'] = df_exibir.apply(status_ocupacao, axis=1)
        df_exibir["Break Even"] = df_exibir["Break Even"].map(lambda x: f'{formaters.br_num(x, 2)}%')
        df_exibir["Margem"] = df_exibir["Margem"].map(lambda x: f'{formaters.br_num(x, 2)}%')
        # df_exibir["Tx Ocupação"] = df_exibir["Tx Ocupação"].map(lambda x: f'{formaters.br_num(x, 2)}%')
        df_exibir['Custo G.F.'] = df_exibir['Custo G.F.'].map(lambda x: formaters.br_num(x, 2))
        df_exibir['Markup'] = df_exibir['Markup'].map(lambda x: formaters.br_num(x, 2))
        df_exibir['Potencial'] = df_exibir['Potencial'].map(lambda x: formaters.br_num(x, 2))
        df_exibir['Faturamento'] = df_exibir['Faturamento'].map(lambda x: formaters.br_num(x, 2))
        df_exibir = df_exibir[['Custo G.F.', 'Potencial', 'Break Even', 'Tx Ocupação', 'Faturamento', 'Markup', 'Margem' ]]

        st.subheader('Resultados Agrupados')
        table.personal_table(df_exibir)
        st.divider()
        # endregion
        # ========================================================

    # endregion
    # ========================================================
    # taxa_ocupacao(session_state)


    # ========================================================
    # region INDICADORES CHAVES
    # ========================================================
    def indicadores_chaves():

        from rental_analytics_model.components import table, multi_select_persist
        from rental_analytics_model.utils.gerar_excel import dowload
        from rental_analytics_model.services import calcular_indicadores_chave_m2, filter
        from rental_analytics_model.services.calcular_periodos import calcular_periodos_df

        # ========================================================
        # region SUBHEADER E SESSION STATE
        # ========================================================
        st.session_state.title = 'Test Dev - Indicadores Chaves'

        # endregion
        # ========================================================

        # ========================================================
        # region RECIBOS, CONTRATOS, VALORES LOCACAO
        # ========================================================
        session_state = st.session_state
        df_recibos = session_state.df_recibos.copy()
        df_contratos = session_state.df_contratos.copy()
        df_valores_locacao = session_state.df_valores_locacao.copy()
        # endregion
        # ========================================================

        # ========================================================
        # region RECIBOS
        # ========================================================
        periodos = multi_select_persist.multiselect_persist('Períodos', list(df_recibos['periodo'].unique()), 'key_periodo', True)
        df_recibos = filter.filter(df_recibos, 'periodo', periodos)
        familias = multi_select_persist.multiselect_persist('Familias', list(df_recibos['familia'].unique()), 'key_familia', True)
        df_recibos = filter.filter(df_recibos, 'familia', familias)
        modelos = multi_select_persist.multiselect_persist('Modelos', list(df_recibos['modelo'].unique()), 'key_modelo', True)
        df_recibos = filter.filter(df_recibos, 'modelo', modelos)
        
        if df_recibos.empty:
            st.warning('Não há dados de recibos para exibir os indicadores chaves.')
            return
        df_recibos.rename(columns={'Linha': 'familia', 'Modelo': 'modelo'}, inplace=True)
        df_recibos_group = (
            df_recibos
            .groupby(['periodo','familia', 'modelo'], as_index=False)
            .agg({
                'Qt.': 'sum',
                'Subtotal c/imp': 'sum'
            })
        )
        df_recibos_group['acc'] = df_recibos_group['Subtotal c/imp'].cumsum()
        # endregion
        # ========================================================

        # ========================================================
        # region CONTRATOS
        # ========================================================
        df_contratos = filter.filter(df=df_contratos, column='periodo', lista=periodos )
        df_contratos = filter.filter(df=df_contratos, column='modelo', lista=modelos )
        if df_contratos.empty:
            st.warning('Não há dados de contratos para exibir os indicadores chaves.')
            return
        df_contratos['periodo'] = pd.to_datetime(df_contratos['locacao']).dt.to_period('M')
        df_contratos['dias_mes'] = df_contratos['periodo'].dt.days_in_month
        df_contratos = calcular_periodos_df(df_contratos)
        # endregion
        # ========================================================

        # ========================================================
        # region VALORES LOCACAO
        # ========================================================
        # df_valores_locacao = st.session_state.df_valores_locacao.copy()
        if df_valores_locacao.empty and 'valor' not in df_contratos.columns:
            st.warning('Não há dados de valores locação para exibir os indicadores chaves.')
            return             
        df_valores_locacao.rename(columns={
                'Modelo': 'modelo',
                'dia': 'p_dia',
                'semana': 'p_semana',
                'quinzena': 'p_quinzena',
                'mes': 'p_mes'
            }, inplace=True)
        # endregion
        # ========================================================

        # ========================================================
        # region CONTRATOS MERGE VALORES
        # ========================================================
        df_contratos_valores = pd.merge(
                df_contratos,
                df_valores_locacao,
                on=['modelo'],
                how='left'
        )
        df_contratos_valores['fat_dia'] = df_contratos_valores['dia'] * df_contratos_valores['p_dia']
        df_contratos_valores['fat_semana'] = df_contratos_valores['semana'] * df_contratos_valores['p_semana']
        df_contratos_valores['fat_quinzena'] = df_contratos_valores['quinzena'] * df_contratos_valores['p_quinzena']
        df_contratos_valores['fat_mes'] = df_contratos_valores['mes'] * df_contratos_valores['p_mes']
        df_contratos_valores['valor'] = df_contratos_valores[['fat_dia', 'fat_semana', 'fat_quinzena', 'fat_mes']].sum(axis=1)
        # endregion
        # ========================================================

        # ========================================================
        # region CONTRATOS VALORES SHOW
        # ========================================================
        df_contratos_valores_show = df_contratos_valores[[
            'numero_contrato',
            'patrimonio',
            'familia',
            'marca',
            'modelo',
            'locacao',
            'devolucao',
            'valor'
        ]]
        df_contratos_valores_show['valor_acumulado'] = df_contratos_valores_show['valor'].cumsum()
        # endregion
        # ========================================================
        # ========================================================
        # region DF CONTRATOS GROUP AND MERGE WITH DF RECIBOS GROUP
        # ========================================================
        df_contratos_group = df_contratos.copy()    
        df_contratos_group = (df_contratos
            .groupby(['periodo', 'dias_mes', 'familia', 'modelo'], as_index=False)
            .agg({
                'dias': 'sum',
                'dia': 'sum',
                'quinzena': 'sum',
                'semana': 'sum',
                'mes':'sum',
                # 'valor': 'sum'
            })
        )
        # st.stop()

        df_contratos_group = pd.merge(
            df_contratos_group, 
            df_recibos_group,
            on=['periodo', 'familia', 'modelo'],
            how='outer',
        )


        df_contratos_group['dias_no_periodo'] = df_contratos_group['periodo'].dt.days_in_month
        df_contratos_group['dias_possiveis'] =  df_contratos_group['dias_no_periodo'] * df_contratos_group['Qt.']
        if 'tx_disponibilidade' not in st.session_state:
                st.session_state.tx_disponibilidade = 100
        df_contratos_group['tx_disp'] = session_state.tx_disponibilidade / 100

        df_contratos_group['dias'] = df_contratos_group['dias'].fillna(0)
        df_contratos_group['dia'] = df_contratos_group['dia'].fillna(0)
        df_contratos_group['semana'] = df_contratos_group['semana'].fillna(0)
        df_contratos_group['quinzena'] = df_contratos_group['quinzena'].fillna(0)
        df_contratos_group['mes'] = df_contratos_group['mes'].fillna(0)
        # endregion
        # ========================================================

        # ========================================================
        # region DF CONTRATOS GROUP MERGE VALORES LOCAÇÃO
        # ========================================================
        if df_valores_locacao.empty and 'valor' not in df_contratos.columns:
                st.warning('Não há dados de valores de locações para exibir os indicadores chaves')
                return
        
        # with st.expander('df_valores_locacao'):
        #     st.dataframe(df_valores_locacao)

        if not df_valores_locacao.empty:
            df_contratos_group = pd.merge(
                df_contratos_group,
                df_valores_locacao,
                on=['modelo'],
                how='left'
            )

            df_contratos_group_merge_valores = (
                df_contratos_group
                .groupby(['periodo', 'dias_no_periodo', 'familia', 'modelo'], as_index=False)
                .agg({
                    'Qt.': 'sum',
                    'Subtotal c/imp': 'sum',
                    'dias_possiveis': 'sum',
                    'dias': 'sum',
                    'dia': 'sum',
                    'semana': 'sum',
                    'quinzena': 'sum',
                    'mes': 'sum',
                    'p_dia': 'mean',
                    'p_semana': 'mean',
                    'p_quinzena': 'mean',
                    'p_mes': 'mean',
                })
            )

            # with st.expander('Contratos agrupados com valores locação'):
            #     st.dataframe(df_contratos_group)

        
        df_contratos_group_merge_valores['tx_ocupacao'] = df_contratos_group_merge_valores['dias'] / df_contratos_group_merge_valores['dias_possiveis']
        
        df_contratos_group_merge_valores['total_contratos'] = df_contratos_group_merge_valores[['dia', 'semana', 'quinzena', 'mes']].sum(axis=1)
        
        df_contratos_group_merge_valores['mix_dia'] = (df_contratos_group_merge_valores['dia'] / df_contratos_group_merge_valores['total_contratos']).fillna(0)
        
        df_contratos_group_merge_valores['mix_semana'] = (df_contratos_group_merge_valores['semana'] / df_contratos_group_merge_valores['total_contratos']).fillna(0)
                
        df_contratos_group_merge_valores['mix_quinzena'] = (df_contratos_group_merge_valores['quinzena'] / df_contratos_group_merge_valores['total_contratos']).fillna(0)

        df_contratos_group_merge_valores['mix_mes'] = (df_contratos_group_merge_valores['mes'] / df_contratos_group_merge_valores['total_contratos']).fillna(0)

        # with st.expander('Conferir dados'):
        #     st.write('dias')
        #     st.write(df_contratos_group[['periodo', 'modelo', 'dias']])
        #     st.write('total_contratos')
        #     st.write(df_contratos_group[['periodo', 'modelo', 'total_contratos']])
        #     st.write('mix_dia')
        #     st.write(df_contratos_group[['periodo', 'modelo', 'dia', 'total_contratos', 'mix_dia']])
        #     st.write('mix_semana')
        #     st.write(df_contratos_group[['periodo', 'modelo', 'semana', 'total_contratos', 'mix_semana']])
        #     st.write('mix_quinzena')
        #     st.write(df_contratos_group[['periodo', 'modelo', 'quinzena', 'total_contratos', 'mix_quinzena']])
        #     st.write('mix_mes')
        #     st.write(df_contratos_group[['periodo', 'modelo', 'mes', 'total_contratos', 'mix_mes']])
        # endregion
        # ========================================================

        # ========================================================
        # region EXPANDER
        # ========================================================
        if st.toggle('Show Details'):
            with st.expander('RECIBOS'):
                st.dataframe(df_recibos_group)
                custo_gf = df_recibos_group['Subtotal c/imp'].sum()
                st.write(f'Custo G.F. c/ impostos: {formaters.br_num(custo_gf)}')        
            with st.expander('VALORES LOCACAO'):
                st.dataframe(df_valores_locacao)
            with st.expander('CONTRATOS MERGE VALORES'):
                st.dataframe(df_contratos_valores)
            with st.expander('CONTRATOS VALORES SHOW'):
                st.dataframe(df_contratos_valores_show)
            with st.expander('CONTRATOS GROUP AND MERGE WITH DF RECIBOS GROUP'):
                st.dataframe(df_contratos_group)
            with st.expander('CONTRATOS GROUP MERGE VALORES LOCAÇÃO'):
                st.dataframe(df_contratos_group_merge_valores)
        # endregion
        # ========================================================           

        # ========================================================
        # region DF CONTRATOS CALCULAR
        # ========================================================
        df_contratos_calcular = df_contratos_group_merge_valores.copy()
        df_contratos_calcular.rename(columns={'dias_no_periodo': 'dias_mes'}, inplace=True)
        df_contratos_calcular = df_contratos_calcular[[
            'familia',
            'modelo',
            'Subtotal c/imp',
            'periodo',
            'Qt.',
            'dias_mes',
            'tx_ocupacao',
            'mix_dia',
            'mix_semana',
            'mix_quinzena',
            'mix_mes',
            'p_dia',
            'p_semana',
            'p_quinzena',
            'p_mes',
            'dias_possiveis',
        ]]
        df_contratos_calcular.insert(df_contratos_calcular.columns.get_loc('tx_ocupacao'), 'tx_disp', 1)
        # with st.expander('df_contratos_calcular'):
        #     st.dataframe(df_contratos_calcular)
        # endregion
        # ========================================================

        # ========================================================
        # region DF CALCULADO
        # ========================================================
        # df_calculado, df_total = calcular_indicadores_chave.calc(df_contratos_calcular)

        df_check, df_check_group, df_calculado, df_total = calcular_indicadores_chave_m2.calc(df_contratos_calcular)

        # st.write('df_check')
        # st.dataframe(df_check)
        # st.write(f'Potencial total: {formaters.br_num(df_check['pot_total'].sum())}')
        # dowload(df_check, 'df_check')
        # st.write('df_check_group')
        # st.dataframe(df_check_group)

        df_calculado['prefixo'] = df_calculado['Modelo'].str.extract(r'([A-Za-z]+(?:-[A-Za-z]+)?)')
        df_calculado['numero'] = df_calculado['Modelo'].str.extract(r'(\d+)').astype(int)
        df_calculado = df_calculado.sort_values(['prefixo', 'numero']).drop(columns=['prefixo', 'numero'])
        # endregion
        # ========================================================

        # ========================================================
        # region SHOW
        # ========================================================
        table.personal_table(df_total)
        with st.expander('Detalhes'):
            table.personal_table(df_calculado)
            dowload(df_calculado, 'contratos_calcular')
        # endregion
        # ========================================================

    # endregion
    # ========================================================
    indicadores_chaves()

    # ========================================================
    # region Qtd pelos contratos
    # ========================================================
    def qtd_pelos_contratos():
        st.session_state.title = 'Test Dev - Qtds Pelos Contratos'
        df_contratos = st.session_state.df_contratos.copy()
        st.dataframe(df_contratos)

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


        st.dataframe(df_ativos)

    # endregion
    # ========================================================
    # qtd_pelos_contratos()

    # ========================================================
    # region STREAMLIT ECHARTS
    # ========================================================
    def streamlit_echarts():
        st.session_state.title = 'Test Dev Streamlit Echarts'
    # endregion
    # ========================================================
    # streamlit_echarts()

    # ========================================================
    # region CONFERE RECIBOS
    # ========================================================
    def confere_recibos():

        df_recibos = st.session_state.df_recibos.copy()

        st.dataframe(df_recibos)

        # recibo = create_filter.create_filter(df=df_recibos, coluna='Recibo nº', tilte='Recibo nº')
        # if recibo: df_recibos = df_recibos[df_recibos['Recibo nº'] == recibo]
        # tipo = create_filter.create_filter(df=df_recibos, coluna='Tipo', tilte='tipo')
        # if tipo: df_recibos = df_recibos[df_recibos['Tipo'] == tipo]
        familia = create_filter.create_filter(df=df_recibos, coluna='familia', tilte='Familia')
        if familia: df_recibos = df_recibos[df_recibos['familia'] == familia].reset_index(drop=True)
        modelo = create_filter.create_filter(df=df_recibos, coluna='modelo', tilte='Modelo')
        if modelo: df_recibos = df_recibos[df_recibos['modelo'] == modelo]
        # descricao  = create_filter.create_filter(df=df_recibos, coluna='Descrição', tilte='Descrição')
        # if descricao: df_recibos = df_recibos[df_recibos['Descrição'] == descricao]
    
        # df_recibos['Acc_sem_imp'] = df_recibos['Subtotal s/imp'].cumsum()
        df_recibos['Acc_com_imp'] = df_recibos['Subtotal c/imp'].cumsum()

        st.dataframe(df_recibos)
        total_com_imp = df_recibos['Subtotal c/imp'].sum()
        st.write(f'Total com impostos: {formaters.br_num(total_com_imp)}')
        # table.personal_table(df_recibos)
        # total_com_imp = df_recibos['Subtotal c/imp'].sum()
        # st.write(f'Total com impostos: {formaters.br_num(total_com_imp)}')
        # gerar_excel.dowload(df=df_recibos, name='df_recibos')

        df_group = df_recibos.groupby(['familia', 'modelo'], as_index=False).agg({'Qt.': 'sum', 'Subtotal c/imp': 'sum'})
        st.dataframe(df_group)

    # endregion
    # ========================================================
    # confere_recibos()

    # ========================================================
    # region SIMULADOR
    # ========================================================
    def simulador(sessiton_state):
        st.subheader('Indicadores Chaves', divider='red')

        # ========================================================
        # region DF RECIBOS
        # ========================================================
        df_recibos = session_state.df_recibos.copy()
        df_recibos.rename(columns={'Linha': 'familia', 'Modelo': 'modelo'}, inplace=True)
        # df_recibos = df_recibos[df_recibos['familia'] == 'Rompedor']
        df_recibos['periodo'] = pd.to_datetime(df_recibos['Período']).dt.to_period('M')
        df_recibos_group = (
            df_recibos
            .groupby(['periodo','familia', 'modelo'], as_index=False)
            .agg({
                'Qt.': 'sum',
                'Subtotal c/imp': 'sum'
            })
        )
        # st.write('Recibos agrupados')
        # st.dataframe(df_recibos_group)
        # st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region DF VALORES LOCACAO
        # ========================================================        
        df_valores_locacao = st.session_state.df_valores_locacao.copy()
        df_valores_locacao.rename(columns={
                'Modelo': 'modelo',
                'dia': 'p_dia',
                'semana': 'p_semana',
                'quinzena': 'p_quinzena',
                'mes': 'p_mes'
            }, inplace=True)
        # st.write('Valores Locação')
        # st.dataframe(df_valores_locacao)
        # st.divider()
        # endregion
        # ========================================================        

        # ========================================================
        # region DF CONTRATOS
        # ========================================================
        df_contratos = st.session_state.df_contratos.copy()
        df_contratos['periodo'] = pd.to_datetime(df_contratos['locacao']).dt.to_period('M')
        df_contratos['dias_mes'] = df_contratos['periodo'].dt.days_in_month
        df_contratos = calcular_periodos_df(df_contratos)
        # st.dataframe(df_contratos)
        # endregion
        # ========================================================

        # ========================================================
        # region FILTER CONTRATOS
        # ========================================================
        periodos = df_contratos['periodo'].unique().tolist()
        familias = sorted(df_contratos['familia'].unique().tolist())
        modelos = sorted(df_contratos['modelo'].unique().tolist())


        periodos_selected = st.sidebar.multiselect(
            'Periodos',
            options=periodos
        )
        
        familias_selected = st.sidebar.multiselect(
            'Familias',
            options=familias
        )
        
        modelos_selected = st.sidebar.multiselect(
            'Modelos',
            options=modelos
        )

        df_contratos = df_contratos[
                (df_contratos['periodo'].isin(periodos_selected))
                &
                (df_contratos['familia'].isin(familias_selected))
                &
                (df_contratos['modelo'].isin(modelos_selected))
            ]
        # endregion
        # ========================================================

        # region DF CONTRATOS GROUP
        # ========================================================
        df_contratos_group = df_contratos.copy()    
        df_contratos_group = (df_contratos
            .groupby(['periodo', 'dias_mes', 'familia', 'modelo'], as_index=False)
            .agg({
                'dias': 'sum',
                'dia': 'sum',
                'quinzena': 'sum',
                'semana': 'sum',
                'mes':'sum',
            })
        )


        df_contratos_group = pd.merge(
            df_contratos_group, 
            df_recibos_group,
            on=['periodo', 'familia', 'modelo'],
            how='left',

        )


        df_contratos_group['dias_no_periodo'] = df_contratos_group['periodo'].dt.days_in_month
        df_contratos_group['dias_possiveis'] =  df_contratos_group['dias_no_periodo'] * df_contratos_group['Qt.']
        df_contratos_group['tx_disp'] = session_state.tx_disponibilidade / 100

        df_contratos_group = pd.merge(
            df_contratos_group,
            df_valores_locacao,
            on=['modelo'],
            how='left'
        )


        df_contratos_group = (
            df_contratos_group
            .groupby(['periodo', 'dias_mes', 'modelo'], as_index=False)
            .agg({
                'Qt.': 'sum',
                'Subtotal c/imp': 'sum',
                'dias_possiveis': 'sum',
                'dias': 'sum',
                'dia': 'sum',
                'semana': 'sum',
                'quinzena': 'sum',
                'mes': 'sum',
                'p_dia': 'mean',
                'p_semana': 'mean',
                'p_quinzena': 'mean',
                'p_mes': 'mean',
            })
        )


        df_contratos_group['tx_ocupacao'] = df_contratos_group['dias'] / df_contratos_group['dias_possiveis']
        df_contratos_group['total_contratos'] = df_contratos_group[['dia', 'semana', 'quinzena', 'mes']].sum(axis=1)
        df_contratos_group['mix_dia'] = df_contratos_group['dia'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_semana'] = df_contratos_group['semana'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_quinzena'] = df_contratos_group['quinzena'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_mes'] = df_contratos_group['mes'] / df_contratos_group['total_contratos']
        # st.dataframe(df_contratos_group)
        # endregion
        # ========================================================        

        # ========================================================
        # region DF CALCULAR
        # ========================================================
        df_contratos_calcular = df_contratos_group.copy()
        df_contratos_calcular = df_contratos_calcular[[
            'modelo',
            'Subtotal c/imp',
            'periodo',
            'Qt.',
            'dias_mes',
            'tx_ocupacao',
            'mix_dia',
            'mix_semana',
            'mix_quinzena',
            'mix_mes',
            'p_dia',
            'p_semana',
            'p_quinzena',
            'p_mes',
            'dias_possiveis',
        ]]

        df_contratos_calcular.insert(df_contratos_calcular.columns.get_loc('tx_ocupacao'), 'tx_disp', 1)

        from rental_analytics_model.services import calcular_indicadores_chave

        df_calculado, df_total = calcular_indicadores_chave.calc(df_contratos_calcular)

        from rental_analytics_model.components import table
        table.personal_table(df_calculado)
        # from rental_analytics_model.utils.gerar_excel import dowload
        gerar_excel.dowload(df_contratos_calcular, 'contratos_calcular')

        st.divider()
        table.personal_table(df_total)
        # endregion
        # ========================================================

    # endregion
    # ========================================================
    # simulador(session_state)

    # ========================================================
    # region FILTER_TEST
    # ========================================================
    def filter_test():
        
        itens = [
            {'name': 'abc'},
            {'name': 'abcd'},
            {'name': 'abcde'},
        ]

        itens_filter = [i for i in itens if 'abcd' in i['name']]
        if itens_filter:
            st.write(itens_filter)

    # endregion
    # ========================================================
    # filter_test()

    # ========================================================
    # region PREPARAR_CONTRATOS
    # ========================================================

    # @st.cache_data
    # def gerar_excel(df):
    #     import io
    #     buffer = io.BytesIO()
    #     df.to_excel(buffer, index=False)
    #     buffer.seek(0)
    #     return buffer

  

    def converter_coluna_datetime(col):
        col = col.astype("string").str.strip()

        # remove vazios
        amostra = col[col.notna() & (col != "")]
        
        if amostra.empty:
            return pd.to_datetime(col, errors="coerce")

        primeiro_valor = amostra.iloc[0]

        formatos_possiveis = [
            "%d-%m-%Y",
            "%d-%m-%Y %H:%M",
            "%d-%m-%Y %H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
        ]

        formato_detectado = None

        for fmt in formatos_possiveis:
            try:
                pd.to_datetime(primeiro_valor, format=fmt)
                formato_detectado = fmt
                break
            except (ValueError, TypeError):
                continue

        if formato_detectado is None:
            raise ValueError(f"Formato de data não reconhecido: {primeiro_valor}")

        return pd.to_datetime(col, format=formato_detectado, errors="coerce")

    def preparar_contratos():
        df_contratos = st.session_state.df_contratos
        df_contratos = df_contratos.fillna('')
        df_contratos['familia'] = 'Rompedor'
        df_contratos.rename(columns={
            'Contrato': 'numero_contrato',
            'NumPat': 'patrimonio',
            'DescPat': 'modelo',
            'VlTotalFaturado': 'valor',
            'VlTotalSemDesc': 'valor',
            'QTDE_DIAS': 'dias_no_periodo_original'
        }, inplace=True)
        
        # # para os contratos da mil máquinas
        # df_contratos['marca'] = 'Hilti'

        # para os contratos da lorenzon
        df_contratos['marca'] = np.where(
            df_contratos['modelo'].str.contains('HILTI', case=False, na=False),
            'Hilti',
            'Outros'
        )
        df_contratos[['locacao', 'devolucao']] = df_contratos['PeriodoItem'].str.split(' a ', expand=True)

        df_contratos['modelo'] = df_contratos['modelo'].str.replace('hilti', '', case=False)
        df_contratos['modelo'] = df_contratos['modelo'].str.replace('rompedor', '', case=False)
        df_contratos['modelo'] = df_contratos['modelo'].str.replace(' ', '', case=False)
        df_contratos['locacao'] = df_contratos['locacao'].astype(str)
        df_contratos['devolucao'] = df_contratos['devolucao'].astype(str)
        df_contratos['locacao'] = df_contratos['locacao'].str.replace('/', '-')
        df_contratos['devolucao'] = df_contratos['devolucao'].str.replace('/', '-')
        df_contratos['locacao'] = converter_coluna_datetime(df_contratos['locacao'])
        df_contratos['devolucao'] = converter_coluna_datetime(df_contratos['devolucao'])
        df_contratos['numero_contrato'] = df_contratos['numero_contrato'].astype(str)
        # df_contratos['locacao'] = df_contratos['locacao'].replace('/', '-')
        # df_contratos = df_contratos[['numero_contrato', 'patrimonio', 'familia', 'marca', 'modelo', 'locacao', 'devolucao', 'dias_no_periodo_original', 'valor']].fillna('')

        # df_contratos = df_contratos[
        #     pd.to_datetime(df_contratos['locacao'], format='%d/%m/%Y %H:%M') < pd.to_datetime(df_contratos['devolucao'], format='%d/%m/%Y %H:%M')
        # ]

        df_contratos = df_contratos[['numero_contrato', 'patrimonio', 'familia', 'marca', 'modelo', 'locacao', 'devolucao', 'valor']]

        st.dataframe(df_contratos)
        gerar_excel.dowload(df_contratos, 'df_contratos')
        # buffer = gerar_excel(df_contratos)
        # st.download_button(
        #     label="Baixar Excel",
        #     data=buffer,
        #     file_name="contratos.xlsx"
        # )
    # endregion
    # ========================================================
    # preparar_contratos()

    # ========================================================
    # region INCLUIR PERÍODOS
    # ========================================================
    @st.cache_data
    def calcular_periodos_df(df):
        
        if df.empty:
            st.warning('Carregue o arquivo contratos')
            return
            
        # garante datetime
        df['locacao'] = pd.to_datetime(df['locacao'], format='%d/%m/%Y %H:%M')
        df['devolucao'] = pd.to_datetime(df['devolucao'], format='%d/%m/%Y %H:%M')
        # df['locacao'] = pd.to_datetime(df['locacao'], errors='coerce')
        # df['devolucao'] = pd.to_datetime(df['devolucao'], errors='coerce')

        # 🔥 cálculo vetorizado (igual sua regra de calendário)
        dias_total = (
            df['devolucao'].dt.normalize() - df['locacao'].dt.normalize()
        ).dt.days

        # mínimo 1 dia
        dias_total = dias_total.clip(lower=1)

        df['dias'] = dias_total

        df['mes'] = dias_total // 30
        dias_restantes = dias_total % 30

        df['quinzena'] = dias_restantes // 15
        dias_restantes = dias_restantes % 15

        df['semana'] = dias_restantes // 7
        df['dia'] = dias_restantes % 7

        return df 

    def incluir_periodos():
        df_contratos = st.session_state.df_contratos

        df = df_contratos.copy() 
        df_periodo = calcular_periodos_df(df)
        # df_periodo = df_periodo[['numero_contrato', 'patrimonio', 'familia', 'marca', 'modelo', 'locacao', 'devolucao', 'dias', 'mes', 'quinzena', 'semana', 'dia', 'valor']]
        df_periodo = df_periodo[['numero_contrato', 'patrimonio', 'familia', 'marca', 'modelo', 'locacao', 'devolucao', 'dias', 'mes', 'quinzena', 'semana', 'dia']]
        df_periodo = df_periodo.fillna('')
        st.dataframe(df_periodo)
        st.write(f'Dias: {df_periodo['dias'].sum()}')
    # endregion
    # ========================================================
    # incluir_periodos()

    # ========================================================
    # region ST.TABLE
    # ========================================================
    def st_table():
        product_data = pd.DataFrame({
            "Product": [
                ":material/devices: Widget Pro",
                ":material/smart_toy: Smart Device",
                ":material/inventory: Premium Kit",
            ],
            "Category": [":blue[Electronics]", ":green[IoT]", ":violet[Bundle]"],
            "Stock": ["🟢 Full", "🟡 Low", "🔴 Empty"],
            "Units sold": [1247, 892, 654],
            "Revenue": [125000, 89000, 98000],
        })
        st.table(product_data, border="horizontal")
        # from rental_analytics_model.utils import gerar_excel
        gerar_excel.dowload(product_data, 'product_data')        
    # endregion
    # ========================================================
    # st_table()

    # ========================================================
    # region CALC_MEDIA_POTENCIAL
    # ========================================================
    def calc_media_potencial():
        
        df = pd.DataFrame({
            'dias_possiveis': [2108, 1904],
            'dias_loc': [1275, 879],
            'locacoes_diarias': [214,134],
            'p_dia': [160, 160],
        })

        df['mix_dia'] = df['locacoes_diarias'] / df['dias_loc']
        df['pot_dia'] = df['mix_dia'] * df['p_dia'] * df['dias_possiveis']
        df['peso'] = df['p_dia'] * df['dias_possiveis']


        st.dataframe(df)
        total_1 = df['pot_dia'].sum()
        st.write(f'total_1: {total_1:,.2f}')


        peso_total = df['peso'].sum()
        taxa_pond = (df['mix_dia'] * df['peso']).sum() / peso_total

        total_2 = taxa_pond * peso_total
        st.write(f'total_2: {total_2:,.2f}')

        st.write(f'total_1 == total_2', f'✅{total_1 == total_2}' )  # ✅ True        

        # mix_dia_ponderado = (df['mix_dia'] * df['peso']).sum() / df['peso'].sum()
        # Potencial = df['pot_dia'].sum()

        # st.write('Taxa ponderada:', mix_dia_ponderado)
        # st.write(f'{Potencial:,.2f}')


    # endregion
    # ========================================================
    # calc_media_potencial()

    # ========================================================
    # region RECIBOS GF
    # ========================================================
    def recibos_gf():
        
        # ========================================================
        # region STATUS OCUPAÇÃO
        # ========================================================
        def status_ocupacao(row):
            ocup_break_even = row['Break Even (ocupação)']
            ocup = row['Ocupação']

            if ocup >= ocup_break_even * 2:
                return f'🟢 {ocup:.2f}%'
            elif ocup > ocup_break_even:
                return f'🟡 {ocup:.2f}%'
            else:
                return f'🔴 {ocup:.2f}%'
        # endregion
        # ========================================================

        # ========================================================
        # region AMS DASH - CUSTO REPARAÇÕES
        # ========================================================
        df_ams_dash = st.session_state.df_ams_dash.copy()

        # ids_cc_brasilia = [
        #         '26165724',
        #         '21713020',
        #         '27803016',
        #         '30232699',
        #         '31713069',
        #         '26165731',
        #         '26165735',
        #         '30040310',
        #         '30229844',
        #         '22016941',
        #         '27805502',
        #         '26165732',
        #         '21715560'
        #     ]
        # for id in listids:
        #     st.write(id)

        ids =  st.sidebar.text_area('ids')
        list_ids = ids.split('\n')
        # st.write(list_ids)

        pattern = '|'.join(list_ids)

        if not df_ams_dash.empty:
            df_ams_dash = df_ams_dash[
                (df_ams_dash['Cliente'].str.contains(pattern, case=False, na=False))
                # (df_ams_dash['Cliente'].str.contains('VALPARAISO'))
                &
                (df_ams_dash['Nome do Material'].str.contains('700'))
            ].reset_index()
            custo_reparacoes = df_ams_dash['Pagado pelo Cliente'].sum()
            
            # st.subheader('df_ams_dash', divider='red')
            # st.dataframe(df_ams_dash)
            # st.write(f'Custo das reparações: {formaters.br_num(custo_reparacoes, 2)}')
            # from rental_analytics_model.utils import gerar_excel
            # gerar_excel.dowload(df_ams_dash, 'custo_reparos_cc_brasilia_2025')
        # endregion
        # ========================================================

            # ========================================================
            # region RECIBOS
            # ========================================================
            # st.subheader('Recibos', divider='red')
            df = st.session_state.df_recibos.copy()
            if not df.empty:
                df['Período'] = pd.to_datetime(df['Período'])
                df = df[df['Período'] <= pd.to_datetime('2025-12-31')]
                # df = df[df['Período'] >= pd.to_datetime('2026-01-01')]
                df = df[df['Descrição'].str.contains('700')]
                # st.dataframe(df)
                custo_gf = df['Subtotal c/imp'].sum()
                # st.write(f'Total dos contratos: {custo_reparações:,.2f}')

                # df_group_modelo = df.groupby(['Descrição'])['Qt.'].sum().reset_index()
                df_group_modelo = (
                    df
                    .groupby(['Período', 'Modelo'])
                    .agg({
                        'Qt.': 'sum',
                        'Subtotal c/imp': 'sum'
                    })
                    .reset_index()
                )
                # st.dataframe(df_group_modelo)
                # endregion
                # ========================================================

                qtd_total = 111
                qtd_gf = 47
                qtd_proprios = qtd_total-qtd_gf
                tx_disponibilidade = (100 - 6.9 - 7.4) / 100
                tx_ocupacao = 55.2 / 100
                faturamento = 956842.42
                faturamento_por_maquina = faturamento / qtd_total
                faturamento_gf = faturamento_por_maquina * qtd_gf
                custo_depreciacao = qtd_proprios * 9500 / 5
                # custo_total = custo_gf + custo_depreciacao + custo_reparacoes
                custo_total = custo_gf + custo_reparacoes
                markup = faturamento / custo_total
                lucro_bruto = (faturamento - custo_total) / faturamento
                potencial = faturamento / tx_ocupacao / tx_disponibilidade
                pot_disp = potencial * tx_disponibilidade
                pot_ocup = pot_disp * tx_disponibilidade
                ocupacao_break_even = custo_total / (potencial * tx_disponibilidade)
                break_even = custo_total / pot_ocup
                margem = (faturamento - custo_total) / faturamento

                result = {
                    'qtd_total': qtd_total,
                    'qtd_proprios': qtd_proprios,
                    'qtd_gf': qtd_gf,
                    'tx_disponibilidade': tx_disponibilidade,
                    'tx_ocupacao': tx_ocupacao,
                    'faturamento': faturamento,
                    'faturamento_por_maquina': faturamento_por_maquina,
                    'faturamento_gf': faturamento_gf,
                    'custo_gf': custo_gf,
                    'custo_reparações': custo_reparacoes,
                    'custo_depreciacao': custo_depreciacao,
                    'custo_total': custo_total,
                    'makup': markup,
                    'lucro_bruto': lucro_bruto
                }

                # st.write(result)

                data_show = {
                    'Modelo': 'TE-700',
                    'Custo (G.F. + Reparações)': custo_total,
                    'Faturamento': faturamento,
                    'Potencial': potencial,
                    'Disponibilidade': tx_disponibilidade,
                    'Ocupação': tx_ocupacao,
                    'Break Even (ocupação)': ocupacao_break_even
                }

                data_show = {
                    'Modelo': 'TE-700',
                    'Custo total (G.F. + Reparações)': custo_total,
                    'Potencial total': potencial,
                    'Disponibilidade': tx_disponibilidade,
                    'Potencial (ocupação 100%)': pot_ocup,
                    'Break Even (ocupação)': break_even,
                    'Ocupação': tx_ocupacao * 100,
                    'Faturamento': faturamento,
                    'Markup': markup,
                    'Margem': margem * 100
                }

                # st.write(data_show)

                df_data_show = pd.DataFrame([data_show])
                df_data_show['Ocupação'] = df_data_show.apply(status_ocupacao, axis=1)
                df_data_show['Custo total (G.F. + Reparações)'] = df_data_show['Custo total (G.F. + Reparações)'].map(lambda x: formaters.br_num(x, 2))
                df_data_show['Potencial total'] = df_data_show['Potencial total'].map(lambda x: formaters.br_num(x, 2))
                df_data_show['Disponibilidade'] = df_data_show['Disponibilidade'].map(lambda x: f'{formaters.br_num(x, 2)}%')
                df_data_show['Potencial (ocupação 100%)'] = df_data_show['Potencial (ocupação 100%)'].map(lambda x: formaters.br_num(x, 2))
                df_data_show['Break Even (ocupação)'] = df_data_show['Break Even (ocupação)'].map(lambda x: f'{formaters.br_num(x, 2)}%')
                df_data_show['Faturamento'] = df_data_show['Faturamento'].map(lambda x: formaters.br_num(x, 2))
                df_data_show['Markup'] = df_data_show['Markup'].map(lambda x: formaters.br_num(x, 2))
                df_data_show['Margem'] = df_data_show['Margem'].map(lambda x: f'{formaters.br_num(x, 2)}%')

                from rental_analytics_model.components import table
                table.personal_table(df_data_show)


            # # df_group_periodo = df.groupby('Período')['Subtotal c/imp'].sum()
            # df_group_periodo = (
            #     df
            #     .groupby('Período', as_index=False)['Subtotal c/imp']
            #     .sum()
            # )

            # df_group_periodo = df_group_periodo.sort_values('Período')

            # fig = px.bar(
            #     df_group_periodo,
            #     x='Período',
            #     y='Subtotal c/imp',
            #     text='Subtotal c/imp',
            #     title='Valor G.F. por Período'
            # )

            # fig.update_layout(
            #     xaxis=dict(tickformat="%m/%Y"),
            #     yaxis_tickprefix='R$ '
            # )

            # fig.update_traces(
            #     texttemplate='%{text:,.0f}',
            #     textposition='outside'
            # )


            # st.plotly_chart(fig)

    # endregion
    # ========================================================
    # recibos_gf()

    # ========================================================
    # region CRIAR NORMAL ITENS
    # ========================================================
    def criar_normal_itens():
        st.subheader('Normal Itens')
        df = st.session_state.df_recibos.copy()
        df = df[df['Tipo'].isna() ]
        if df.empty:
            st.warning('Nenhuma descrição sem Tipo, Linha e Modelo')
            return
        st.dataframe(df)
        descricoes = df['Descrição'].dropna().astype(str).sort_values().unique().tolist()
        # st.write(descricoes)
        df = loaders.load_normal_itens()

        descricao_selected = st.selectbox('Descrição', descricoes)
        tipo = st.selectbox('Tipo', ['Ferramenta', 'Acessório'])
        linha = st.text_input('Linha')
        modelo = st.text_input('Modelo')

        df_new = pd.DataFrame([{
            'Descrição': descricao_selected,
            'Tipo': tipo,
            'Linha': linha,
            'Modelo': modelo
        }])

        # st.dataframe(df_new)
        if modelo != '':
            df = pd.concat([df, df_new], axis=0, ignore_index=True)

        st.dataframe(df)
        if st.button('Salvar'):
            BASE_DIR = Path(__file__).parents[3]
            df.to_json(BASE_DIR/'data'/'normal_itens.json', orient='records', force_ascii=False, indent=4)
            st.success('Arquivo salvo com sucesso!')
    # endregion
    # ========================================================
    # criar_normal_itens()

    # ========================================================
    # region TABLE STYLE
    # ========================================================
    def table_estyle():

        from rental_analytics_model.utils import formaters
        from rental_analytics_model.components import table

        df = pd.DataFrame({
            "Custo G.F.": [551782.6777],
            "Potencial": [3124556.9794],
            "Break Even": [0.1766],
            "Ocupação": ["🟢 0.35%"],
            "Faturamento": [1104977.1572],
            "Markup": [2.0026],
            "Margem": [0.5006],
        })

        df['Margem'] = df['Margem'] * 100

        df_exibir = df.copy()
        df_exibir["Custo G.F."] = df_exibir["Custo G.F."].map(lambda x: formaters.br_num(x, 2))
        df_exibir["Potencial"] = df_exibir["Potencial"].map(lambda x: formaters.br_num(x, 2))
        df_exibir["Break Even"] = df_exibir["Break Even"].map(lambda x: formaters.br_num(x, 4))
        df_exibir["Faturamento"] = df_exibir["Faturamento"].map(lambda x: formaters.br_num(x, 2))
        df_exibir["Markup"] = df_exibir["Markup"].map(lambda x: formaters.br_num(x, 1))
        df_exibir["Margem"] = df_exibir["Margem"].map(lambda x: f'{formaters.br_num(x, 2)} %')


        table.personal_table(df_exibir)


    # endregion
    # ========================================================
    # table_estyle()

    # ========================================================
    # region AMS DASHBOARD
    # ========================================================
    def ams_dashboard():
        st.subheader('ams_dashboard', divider='red')
        df_ams_dash = st.session_state.df_ams_dash.copy()

        ids = [
                '26165724',
                '21713020',
                '27803016',
                '30232699',
                '31713069',
                '26165731',
                '26165735',
                '30040310',
                '30229844',
                '22016941',
                '27805502',
                '26165732',
                '21715560'
            ]

        pattern = '|'.join(ids)

        df_ams_dash = df_ams_dash[
            (df_ams_dash['Cliente'].str.contains(pattern, case=False, na=False))
            # (df_ams_dash['Cliente'].str.contains('VALPARAISO'))
            &
            (df_ams_dash['Nome do Material'].str.contains('700'))
        ].reset_index()
        st.dataframe(df_ams_dash)
        total_cust = df_ams_dash['Pagado pelo Cliente'].sum()
        st.write(f'Custo das reparações: {formaters.br_num(total_cust, 2)}')
    # endregion
    # ========================================================
    # ams_dashboard()

    # ========================================================
    # region CALC POTENCIAL
    # ========================================================
    def calc_potencial():

        from rental_analytics_model.services.calcular_periodos import calcular_periodos_df
        from rental_analytics_model.services import calcular_indicadores_chave

        st.sidebar.subheader('', divider='red')

        # 1. Obter os contratos
        df_contratos = st.session_state.df_contratos.copy()
        # df_contratos['periodo'] = pd.to_datetime(df_contratos['locacao']).dt.to_period('M')
        # df_contratos['dias_mes'] = df_contratos['periodo'].dt.days_in_month
        # df_contratos = calcular_periodos_df(df_contratos)
        # df_contratos 
        st.write('df_contratos')
        st.write(df_contratos)

        st.write(df_contratos['modelo'].unique())

        # 1. Obtem o df_recibos_group agrupado por perio, familia e modelo com
        # as quantidades totais de cada.
        # =========================================================================================
        df_recibos = st.session_state.df_recibos.copy()

        if df_recibos.empty:
            st.warning('Não há dados de recibos para exibir os indicadores chaves.')
            st.stop()
        st.write('df_recibos')
        st.write(df_recibos)

        # # df_recibos.rename(columns={'Linha': 'familia', 'Modelo': 'modelo'}, inplace=True)
        # # df_recibos['periodo'] = pd.to_datetime(df_recibos['Período']).dt.to_period('M')
        # # df_recibos_group = (
        # #     df_recibos
        # #     .groupby(['periodo','familia', 'modelo'], as_index=False)
        # #     .agg({
        # #         'Qt.': 'sum',
        # #         'Subtotal c/imp': 'sum'
        # #     })
        # # )
        # st.write('df_recibos_group')
        # st.dataframe(df_recibos_group)

        # 2. Obtem o df_contratos com os períodos calculados
        # =========================================================================================
        # df_contratos = st.session_state.df_contratos.copy()
        # if df_contratos.empty:
        #     st.warning('Não há dados de contratos para exibir os indicadores chaves.')
        #     st.stop()
        # df_contratos['periodo'] = pd.to_datetime(df_contratos['locacao']).dt.to_period('M')
        # df_contratos['dias_mes'] = df_contratos['periodo'].dt.days_in_month
        # df_contratos = calcular_periodos_df(df_contratos)
        # st.write('df_contratos')
        # st.write(df_contratos)

        # 3. Obtem o df_valores_locacao
        # =========================================================================================
        df_valores_locacao = st.session_state.df_valores_locacao.copy()
        if df_valores_locacao.empty and 'valor' not in df_contratos.columns:
            st.warning('Não há dados de valores locação para exibir os indicadores chaves.')
            return             
        df_valores_locacao.rename(columns={
                'Modelo': 'modelo',
                'dia': 'p_dia',
                'semana': 'p_semana',
                'quinzena': 'p_quinzena',
                'mes': 'p_mes'
            }, inplace=True)
        st.write('df_valores_locacao')
        st.write(df_valores_locacao)

        # 4. Obtem os valores de locação através da união df_contratos e df_valores_locacao
        #  criando o df_contratos_valores
        # =========================================================================================
        df_contratos_valores = df_contratos.copy()
        df_contratos_valores = pd.merge(
             df_contratos_valores,
             df_valores_locacao,
             on=['modelo'],
             how='left'
        )
        df_contratos_valores['fat_dia'] = df_contratos_valores['dia'] * df_contratos_valores['p_dia']
        df_contratos_valores['fat_semana'] = df_contratos_valores['semana'] * df_contratos_valores['p_semana']
        df_contratos_valores['fat_quinzena'] = df_contratos_valores['quinzena'] * df_contratos_valores['p_quinzena']
        df_contratos_valores['fat_mes'] = df_contratos_valores['mes'] * df_contratos_valores['p_mes']
        df_contratos_valores['valor'] = df_contratos_valores[['fat_dia', 'fat_semana', 'fat_quinzena', 'fat_mes']].sum(axis=1)        
        # st.write('df_contratos_valores')
        # st.dataframe(df_contratos_valores)
        df_contratos_valores_show = df_contratos_valores[[
            'numero_contrato',
            'patrimonio',
            'familia',
            'marca',
            'modelo',
            'locacao',
            'devolucao',
            'valor'
        ]]        
        st.write('df_contratos_valores_show')        
        st.write(df_contratos_valores_show)

        # 5. Não sei por que se cria um novo df_contratos_group a partir do df_contratos
        # =========================================================================================
        df_contratos_group = df_contratos.copy()    
        df_contratos_group = (
            df_contratos
            .groupby(['periodo', 'dias_mes', 'familia', 'modelo'], as_index=False)
            .agg({
                'dias': 'sum',
                'dia': 'sum',
                'quinzena': 'sum',
                'semana': 'sum',
                'mes':'sum',
                'valor': 'sum'
            })
        )
        st.write('df_contratos_group')        
        st.write(df_contratos_group)
        

        # 6. E também não entendi por que agora usa-se o df_contratos_group novo
        # =========================================================================================
        df_contratos_group = pd.merge(
            df_contratos_group, 
            df_recibos,
            on=['periodo', 'familia', 'modelo'],
            how='left',
        )


        # df_contratos_group['dias_no_periodo'] = df_contratos_group['periodo'].dt.days_in_month
        df_contratos_group['dias_possiveis'] =  df_contratos_group['dias_mes'] * df_contratos_group['Qt.']
        if 'tx_disponibilidade' not in st.session_state:
              st.session_state.tx_disponibilidade = 100
        df_contratos_group['tx_disp'] = session_state.tx_disponibilidade / 100

        if df_valores_locacao.empty and 'valor' not in df_contratos.columns:
              st.warning('Não há dados de valores de locações para exibir os indicadores chaves')
              return
        if not df_valores_locacao.empty:
            df_contratos_group = pd.merge(
                df_contratos_group,
                df_valores_locacao,
                on=['modelo'],
                how='left'
            )

            df_contratos_group = (
                df_contratos_group
                .groupby(['periodo', 'dias_mes', 'familia', 'modelo'], as_index=False)
                .agg({
                    'Qt.': 'sum',
                    'Subtotal c/imp': 'sum',
                    'dias_possiveis': 'sum',
                    'dias': 'sum',
                    'dia': 'sum',
                    'semana': 'sum',
                    'quinzena': 'sum',
                    'mes': 'sum',
                    'p_dia': 'mean',
                    'p_semana': 'mean',
                    'p_quinzena': 'mean',
                    'p_mes': 'mean',
                })
            )

        df_contratos_group['tx_ocupacao'] = df_contratos_group['dias'] / df_contratos_group['dias_possiveis']
        df_contratos_group['total_contratos'] = df_contratos_group[['dia', 'semana', 'quinzena', 'mes']].sum(axis=1)
        df_contratos_group['mix_dia'] = df_contratos_group['dia'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_semana'] = df_contratos_group['semana'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_quinzena'] = df_contratos_group['quinzena'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_mes'] = df_contratos_group['mes'] / df_contratos_group['total_contratos']
        st.write('df_contratos_group denovo')        
        st.write(df_contratos_group)

        # st.write('df_contratos_group')
        # st.write(df_contratos_group)

        df_contratos_calcular = df_contratos_group.copy()
        df_contratos_calcular = df_contratos_calcular[[
            'familia',
            'modelo',
            'Subtotal c/imp',
            'periodo',
            'Qt.',
            'dias_mes',
            'tx_ocupacao',
            'mix_dia',
            'mix_semana',
            'mix_quinzena',
            'mix_mes',
            'p_dia',
            'p_semana',
            'p_quinzena',
            'p_mes',
            'dias_possiveis',
        ]]
        df_contratos_calcular.insert(df_contratos_calcular.columns.get_loc('tx_ocupacao'), 'tx_disp', 1)
        st.write('df_contratos_calcular')
        st.write(df_contratos_calcular)

        familia = create_filter.create_filter(df_contratos_calcular, 'familia', 'Familia')
        if familia:
            df_contratos_calcular = df_contratos_calcular[df_contratos_calcular['familia'] == familia]

        modelo = create_filter.create_filter(df_contratos_calcular, 'modelo', 'Modelo')
        if modelo:
            df_contratos_calcular = df_contratos_calcular[df_contratos_calcular['modelo'] == modelo]            



        df_calculado, df_total = calcular_indicadores_chave.calc(df_contratos_calcular)

        st.write('df_calculado')
        st.write(df_calculado)

        st.write('df_total')
        st.write(df_total)
        st.stop()


    # endregion
    # ========================================================
    # calc_potencial()

    # ========================================================
    # region INCLUIR FAMILIA MODELO
    # ========================================================
    def incluir_familia_modelo():

        from rental_analytics_model.services import rental_analytics_services as service
        from rental_analytics_model.utils.loaders import loaders
        from collections import defaultdict
        from pathlib import Path
        import json

        def identificar_familia_modelo(df_raw):
            return service.identificar_familia_modelo(
                df=df_raw,
                coluna_texto="Nome do Material",
                familias_modelos=st.session_state.familias,
                enviar_nulos=True
            ).reset_index(drop=True)

        df_raw = st.session_state.df_ams_dash.copy()
        df_raw['Custo de Reparos'] = df_raw['Custo de Reparos'].fillna(0) 
        df_raw['Pagado pelo Cliente'] = df_raw['Pagado pelo Cliente'].fillna(0)
        df_raw['Economia'] = df_raw['Economia'].fillna(0)
        df_raw = service.normalizar_material(df_raw)

        if "familias" not in st.session_state:
            st.session_state.familias = loaders('modelos', 'json')

        st.session_state.df_resultado = identificar_familia_modelo(df_raw)

        df_unicos = pd.DataFrame(
            sorted(st.session_state.df_resultado['Nome do Material'].dropna().unique()),
            columns=['Nome do Material']
        )
        st.dataframe(df_unicos)

        modelos = defaultdict(list, loaders('modelos', 'json'))

        familias = ['']
        familias.extend(sorted(modelos.keys()))
        familia_selected = st.selectbox('Selecionar familia', familias)
        familia = st.text_input('Familia', value=familia_selected)
        modelo = st.text_input('Modelo')

        if st.button('Salvar'):
            if not familia or not modelo:
                st.warning('Informe a família e o modelo')
                st.stop()

            path_file = Path(__file__).resolve().parents[1] / "assets" / "modelos.json"

            if modelo.lower() not in modelos[familia.lower()]:
                modelos[familia.lower()].append(modelo.lower())

                with open(path_file, 'w', encoding='utf-8') as f:
                    json.dump(dict(modelos), f, indent=4, ensure_ascii=False)

                st.session_state.familias = loaders('modelos', 'json')
                st.success('Modelo salvo com sucesso')
                st.rerun()
            else:
                st.info('Esse modelo já existe nessa família')        

    # endregion
    # ========================================================        
    # incluir_familia_modelo()

    # ========================================================
    # region ESTUDO GERAL AMS
    # ========================================================
    def estudo_geral_ams(df: pd.DataFrame):

        import calendar
        from dateutil.relativedelta import relativedelta
        from datetime import timedelta
        from rental_analytics_model.constants.rental_analytics_constantes import MODELOS_ROMPEDOR_VALIDOS
        from rental_analytics_model.utils import formaters
        from rental_analytics_model.services import processar_reparos

        def data_venda(idade_frac):
            data_relatorio = pd.to_datetime('2026-04-11')
            dias = (idade_frac * 365.25).round().astype(int)
            return data_relatorio - pd.to_timedelta(dias, unit='D')       

        df = df.copy()
        df = df[
            (df['modelo'].isin(MODELOS_ROMPEDOR_VALIDOS))
        ]

        df.rename(columns={
            'Número de Série': 'serie',
            'Idade em Anos': 'idade_frac',
            'ano_reparo': 'ano_relatorio',
            '# Notif.': 'falhas',
            '# Reparos': 'reparos',
            'Custo de Reparos': 'custo_reparos',
            'Pagado pelo Cliente': 'custo_cliente',
            'Economia': 'custo_hilti',
        }, inplace=True)
        df['data_venda'] = data_venda(df['idade_frac'])

        df = df[['familia', 'modelo', 'serie', 'data_venda', 'ano_relatorio', 'falhas', 'reparos', 'custo_reparos']]
        df.sort_values(['data_venda', 'serie', 'ano_relatorio'], inplace=True)
        df = df.reset_index(drop=True)

        resultado = processar_reparos.processar_reparos_json(df)

        df_metricas = resultado['df_metricas']
        st.dataframe(df_metricas)

        fig = px.line(
            df_metricas,
            x="idade_int",
            y="falhas_por_maquina",
            color="modelo",
            markers=True,
            title="Falhas por máquina por idade"
        )
        st.plotly_chart(fig)

        # st.dataframe(df)

        # df_group = (
        #     df
        #     .groupby(['modelo'])
        #     .agg({
        #         'falhas': 'sum',
        #         'reparos': 'sum'
        #     })
        # ).reset_index()
        # df_group['orcamentos_recusados'] = df_group['falhas'] - df_group['reparos']

        # st.dataframe(df_group)
        # qtd_falhas = df_group['falhas'].sum()
        # qtd_reparos = df_group['reparos'].sum()
        # recusados = qtd_falhas - qtd_reparos
        # percent_recusados = recusados / qtd_falhas * 100
        # st.write(f"""
        #     {qtd_falhas} falhas | 
        #     {qtd_reparos} reparos | 
        #     recusados {recusados} | 
        #     {formaters.br_num(percent_recusados, 2)}%
        # """)

        # if st.button('Salvar'):
        #     df.to_json(
        #         'reparos.json',
        #         date_format='iso',
        #         indent=4,
        #         orient='records',
        #         index=False
        #     )
    # endregion
    # ========================================================

    # ========================================================
    # region FILTROS DEPENDENTES WITH AMS REPORT BRAZIL
    # ========================================================
    def filtro_dependentes():

        from rental_analytics_model.components.indicadores_chave_filters import (
            render_filtros_sidebar_dependentes
        )
        from rental_analytics_model.components.rental_analytics_views import (
            render_bloco_filtro_reparos
        )
        from rental_analytics_model.services import rental_analytics_services as service
        from rental_analytics_model.utils.loaders import loaders
        # from rental_analytics_model.utils.gerar_excel import dowload

        def identificar_familia_modelo(df_raw):
            if "familias" not in st.session_state:
                st.session_state.familias = loaders('modelos', 'json')

            return service.identificar_familia_modelo(
                df=df_raw,
                coluna_texto="Nome do Material",
                familias_modelos=st.session_state.familias,
            ).reset_index(drop=True)
        
        df_raw = st.session_state.df_ams_dash.copy()

        df_raw = service.normalizar_material(df_raw)
        # st.write('df_raw')
        # st.dataframe(df_raw)
        # st.write(f'{df_raw.shape[0]} linhas {df_raw.shape[1]} colunas')
        # st.divider()
        
        df_identificado = identificar_familia_modelo(df_raw)

        # estudo_geral_ams(df_identificado)

        # st.write('df_identificado')
        # st.dataframe(df_identificado)
        # st.write(f'{df_identificado.shape[0]} linhas {df_identificado.shape[1]} colunas')
        # st.divider()


        df_vips = loaders('vips', 'xlsx')
        # # st.write('df_vips')
        # # st.dataframe(df_vips)
        # # st.write(f'{df_vips.shape[0]} linhas {df_vips.shape[1]} colunas')
        # # st.divider()

        df_base = service.preparar_base_filtro(
            df_resultado=df_identificado,
            df_vips_excel=df_vips
        )

        # # st.write('df_base')
        # # st.dataframe(df_base)
        # # st.write(f'{df_base.shape[0]} linhas {df_base.shape[1]} colunas')
        # # st.divider()

        # # --------------------------------------------------
        # # FILTROS ENCADEADOS
        # # --------------------------------------------------

        filtros_selecionados = render_filtros_sidebar_dependentes(service, df_base)

        # # # st.write(filtros_selecionados)

        df_filtrado = service.aplicar_filtros(
            df=df_base,
            **filtros_selecionados
        )
        estudo_geral_ams(df_filtrado)
        # st.write('df_filtrado')
        # st.dataframe(df_filtrado)
        # st.write(f'{df_filtrado.shape[0]} linhas {df_filtrado.shape[1]} colunas')
        # st.divider()

        # df_filter = service.preparar_df_filter(df_filtrado)

        # render_bloco_filtro_reparos(df_filter=df_filter, filtros=filtros_selecionados)

        # df_group_idade = service.agrupar_por_idade(df_filter)

        # st.divider()
        # st.write('df_group_idade')
        # st.write(f'df_reparações Qtd linhas: {df_group_idade.shape[0]} | Qtd colunas: {df_group_idade.shape[1]}')
        # st.dataframe(df_group_idade)
        # dowload(df_group_idade, 'analizar_medias_reparacoes')
        # st.divider()

        # # ok, mensagem = service.validar_df_group_idade(df_group_idade=df_group_idade)
        # # if not ok:
        # #     st.warning(mensagem)
        # #     return

        # # df_taxa = service.calcular_taxa_falha(df_group_idade)
        # # st.write('df_taxa')
        # # st.write(f'df_reparações Qtd linhas: {df_taxa.shape[0]} | Qtd colunas: {df_taxa.shape[1]}')
        # # st.dataframe(df_taxa)


    # endregion
    # ========================================================
    # filtro_dependentes()

    # ========================================================
    # region JOIN AMS REPORT BRAZIL
    # ========================================================
    def join_ams_report():
        
        # from rental_analytics_model.utils.gerar_excel import dowload

        files = list(st.session_state.arquivos_unicos.values())
        reports = [f for f in files if 'ams_report_brazil' in f.name ]

        # reports = reports[8:]
        df = pd.DataFrame()

        for report in reports:
            ano_reparo = report.name.split('_')[3].replace('.xlsx', '')
            df_atual = pd.read_excel(report)
            df_atual['ano_reparo'] = ano_reparo
            df = pd.concat([df, df_atual])

        df = df[
            (df['Cliente'] != 'Total' )
            &
            (~df['Cliente'].str.contains('Filtros', case=False, na=False))
            &
            (~df['Cliente'].isna())
        ].reset_index(drop=True)

        st.dataframe(df)
        gerar_excel.dowload(df, 'ams_report_brazil_total')

    # endregion
    # ========================================================
    # join_ams_report()

    # ========================================================
    # region READ AMS DASHBOARD SP
    # ========================================================
    def read_ams_dashboard_sap():

        from rental_analytics_model.services.processar_reparos import (
            processar_base_reparacoes,
            gerar_curva_coorte
        )
        from rental_analytics_model.services.previsao import (
            prever_curva_modelo
        )
        # from rental_analytics_model.utils import (formaters)

        @st.cache_data
        def carregar_dados(file_bytes, sheet_name: str = 'dados_consolidados'):
            xlsx = pd.ExcelFile(file_bytes)

            if 'dados_consolidados_teste' not in xlsx.sheet_names:
                return None

            return pd.read_excel(file_bytes, sheet_name='dados_consolidados')

        arquivos_unicos = list(st.session_state.arquivos_unicos.values())

        file = [f for f in arquivos_unicos if 'G_GMRRPCOPA' in f.name]
        if not file:
            st.warning('Sem arquivos para carregar')
            return

        file_obj = file[0]
        df = carregar_dados(file_obj.getvalue())

        st.dataframe(df)

        # ========================================================
        # region DADOS ROW PARA TESTES
        # ========================================================
        # with st.expander('Dados row'):
        #     df_row = df.copy()
        #     df_row['Covered by Customer'] = df_row['Covered by Customer'].fillna(0) 
        #     df_row['Covered by Hilti'] = df_row['Covered by Hilti'].fillna(0)
        #     df_row['Covered by Customer_acumulado'] = df_row['Covered by Customer'].cumsum() 
        #     df_row['Covered by Hilti_acumulado'] = df_row['Covered by Hilti'].cumsum()
        #     df_row['Covered by Hilti + Customer Acumulado'] = df_row['Covered by Hilti'].cumsum() + df_row['Covered by Customer'].cumsum()
        #     st.dataframe(df_row)
        #     df_row_with_cust = df_row[
        #         (df_row['Covered by Customer'] > 0)
        #         |
        #         (df_row['Covered by Hilti'] > 0)

        #     ].reset_index()
        #     st.dataframe(df_row_with_cust)
        #     df_row_without_cust = df_row[
        #         (df_row['Covered by Customer'] == 0)
        #         &
        #         (df_row['Covered by Hilti'] == 0)

        #     ].reset_index()
        #     df_row_without_cust['Covered by Customer_acumulado'] = df_row_without_cust['Covered by Customer'].cumsum() 
        #     df_row_without_cust['Covered by Hilti_acumulado'] = df_row_without_cust['Covered by Hilti'].cumsum()            
        #     st.dataframe(df_row_without_cust)
        #     qtd_maquinas = len(list(df_row['(n) Serial Number'].unique()))
        #     st.write(f'{qtd_maquinas} máquinas')
        # endregion
        # ========================================================

        df.rename(columns={
            '(n) Serial Number': 'serie',
            'Tool Type': 'modelo',
            'Tool Age in months (Delivery)': 'idade_meses',
            'Notif. Completion Date': 'data_reparacao',
            'Covered by Customer': 'custo_cliente',
            'Covered by Hilti': 'custo_hilti'
            # ''
        }, inplace=True)
            
        df['custo_reparacao'] = (df['custo_cliente'] + df['custo_hilti']) * 1.4
        
        df = df[['serie', 'modelo', 'idade_meses', 'data_reparacao', 'custo_reparacao']]

        mapa = {
            'TE 500': 'TE-500',
            'TE 500-AVR': 'TE-500',
            'TE 700-AVR': 'TE-700',
            'TE 800-AVR': 'TE-800',
            'TE 1000-AVR': 'TE-1000',
            'TE 2000-AVR': 'TE-2000',
            'TE 3000-AVR': 'TE-3000',
        }
            
        df['modelo'] = df['modelo'].map(mapa).fillna(df['modelo'])
        df['custo_reparacao'] = df['custo_reparacao'].fillna(0)

        df['data_reparacao'] = pd.to_datetime(df['data_reparacao'])

        # st.dataframe(df)
        # if st.button('Salvar'):
        #     df.to_json(
        #         'reparacoes_ams.json',
        #         date_format='iso',
        #         indent=4,
        #         orient='records',
        #         index=False
        #     )
        # st.divider()
        # df_qtds = df['modelo'].value_counts()
        # st.write(df_qtds)


        # ========================================================
        # region FILTER MODELO
        # ========================================================
        modelos = ['']
        values = list(df['modelo'].unique())
        modelos.extend(values)
        modelo = st.sidebar.selectbox('Modelo', modelos)
        df = df[df['modelo'].str.contains(modelo)]
        # endregion
        # ========================================================


        df_limpo, df_metricas_idade, df_intervalos, df_modelos = processar_base_reparacoes(df)            
        st.subheader('df_limpo', divider='red')
        st.dataframe(df_limpo)


        # ========================================================
        # region ANALISE SÉRIES
        # ========================================================
        # st.subheader('Análise Séries', divider='red')
        # # df_limpo = df_limpo[df_limpo['custo_reparacao'] > 300]
        # # df_limpo = df_limpo[df_limpo['idade_int'] == 4]
        # df_series = df_limpo.copy()
        # series_count = df_series['serie'].value_counts()
        # df_count = series_count.reset_index()
        # df_count.columns = ['serie', 'count']
        # series = ['']
        # values = list(df_count['serie'].unique())
        # series.extend(values)
        # serie = st.sidebar.selectbox('Série', series)
        # if serie:
        #     df_series = df_series[df_series['serie'] == serie].reset_index()
        # st.dataframe(df_series)
        # total_cust_reparacao = df_series['custo_reparacao'].sum()
        # st.write(f'Custo total das reparações: {formaters.br_num(total_cust_reparacao)}')
        # qtd_reparacoes = len(df_series)
        # st.write(f'Qtd reparações {qtd_reparacoes}')
        # valor_medio_reparacao = total_cust_reparacao / qtd_reparacoes
        # st.write(formaters.br_num(valor_medio_reparacao))
        # df_series['reparacoes'] = 1
        # df_series_group = (
        #     df_series
        #     .groupby(['serie', 'idade_int'])
        #     .agg({
        #         'reparacoes': 'count',
        #         'custo_reparacao': 'sum'
        #     })
        #     .reset_index()
        # )
        # df_series_group['custo_medio'] = df_series_group['custo_reparacao'] / df_series_group['reparacoes']
        # st.dataframe(df_series_group)
        # endregion
        # ========================================================


        resultado = gerar_curva_coorte(
            df_limpo=df_limpo,
            idade_coorte_min=10,
            min_maquinas_por_idade=20,
            janela_suavizacao=3,
        )

        st.subheader('Resultado', divider='red')

        with st.expander('Resultado'):
            st.write(resultado)

        df_metricas = resultado["df_metricas"]

        st.subheader('📊 Gráfico de probabilidade de falha', divider='red')
        fig = px.scatter(
            df_metricas,
            x="idade_int",
            y="prob_falha",
            title="TE-500 - Probabilidade de falha por idade"
        )

        fig.add_scatter(
            x=df_metricas["idade_int"],
            y=df_metricas["prob_falha_suavizada"],
            mode="lines",
            name="Prob. suavizada"
        )

        st.plotly_chart(fig)

        st.subheader('📊 Gráfico de Reparações Por Máquina', divider='red')
        fig = px.scatter(
            df_metricas,
            x="idade_int",
            y="reparacoes_por_maquina",
            title="TE-500 - Reparações por máquina exposta"
        )

        fig.add_scatter(
            x=df_metricas["idade_int"],
            y=df_metricas["reparacoes_suavizada"],
            mode="lines",
            name="Reparações suavizadas"
        )

        st.plotly_chart(fig)

        st.subheader('📊 Gráfico da base por idade', divider='red')
        fig = px.bar(
            df_metricas,
            x="idade_int",
            y="maquinas",
            title="TE-500 - Máquinas expostas por idade"
        )

        st.plotly_chart(fig)

        # ========================================================
        # region 🔎 Prever probabilidade de falha
        # ========================================================
        resultado_pred = prever_curva_modelo(
            df_metricas=df_metricas,
            modelo=modelo,
            alvo="prob_falha_suavizada",
            grau_polinomio=2,
            idade_max_previsao=15,
            clip_lower=0
        )

        df_modelo = resultado_pred["df_modelo"]
        df_pred = resultado_pred["df_pred"]
        st.subheader('🔎 Prever probabilidade de falha', divider='red')
        fig = px.scatter(
            df_modelo,
            x="idade_int",
            y="prob_falha_suavizada",
            title="TE-500 - Probabilidade de falha: real vs previsão"
        )

        fig.add_scatter(
            x=df_pred["idade_int"],
            y=df_pred["valor_previsto"],
            mode="lines",
            name="Previsão"
        )
        st.plotly_chart(fig)
        # endregion
        # ========================================================

        # ========================================================
        # region FUNÇÃO PARA PLOTAR
        # ========================================================
        def plotar_previsao(
            df_modelo: pd.DataFrame,
            df_pred: pd.DataFrame,
            y_real: str,
            titulo: str,
            nome_prev="Previsão"
        ):
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df_modelo["idade_int"],
                y=df_modelo[y_real],
                mode="markers",
                name="Real"
            ))

            fig.add_trace(go.Scatter(
                x=df_pred["idade_int"],
                y=df_pred["valor_previsto"],
                mode="lines",
                name=nome_prev
            ))

            fig.update_layout(
                title=titulo,
                xaxis_title="Idade (anos)",
                yaxis_title=y_real
            )

            return fig
        # endregion
        # ========================================================

        # ========================================================
        # region 🔎 Prever reparações por máquina
        # ========================================================
        st.subheader('🔎 Prever reparações por máquina', divider='red')
        resultado_pred_rep = prever_curva_modelo(
            df_metricas=df_metricas,
            modelo=modelo,
            alvo="reparacoes_suavizada",
            grau_polinomio=2,
            idade_max_previsao=15,
            clip_lower=0
        )
        df_modelo_rep = resultado_pred_rep["df_modelo"]
        df_pred_rep = resultado_pred_rep["df_pred"]        
        st.dataframe(df_pred_rep.head())
        fig = plotar_previsao(
            df_modelo=df_modelo_rep,
            df_pred=df_pred_rep,
            y_real="reparacoes_suavizada",
            titulo=f"{modelo} - Reparações por máquina: real vs previsão"
        )
        st.plotly_chart(fig)       
        # endregion
        # ========================================================

        # ========================================================
        # region 🔎 Prever custo por máquina
        # ========================================================
        st.subheader('🔎 Prever custo por máquina', divider='red')
        resultado_pred_custo = prever_curva_modelo(
            df_metricas=df_metricas,
            modelo=modelo,
            alvo="custo_suavizado",
            grau_polinomio=2,
            idade_max_previsao=15,
            clip_lower=0
        )

        df_modelo_custo = resultado_pred_custo["df_modelo"]
        df_pred_custo = resultado_pred_custo["df_pred"]
        st.dataframe(df_pred_custo.head())
        fig = plotar_previsao(
            df_modelo=df_modelo_custo,
            df_pred=df_pred_custo,
            y_real="custo_suavizado",
            titulo=f"{modelo} - Custo por máquina: real vs previsão"
        )
        st.plotly_chart(fig)
        
        # endregion
        # ========================================================

        st.subheader('df_metricas_idade', divider='red')
        st.write('df_metricas_idade')
        st.dataframe(df_metricas_idade)


        st.subheader('df_idade', divider='red')
        df_idade = df_metricas_idade.copy()

        df_idade = df_idade.sort_values(["modelo", "idade_int"])

        df_idade["falhas_suavizada"] = (
            df_idade.groupby("modelo")["reparacoes_por_maquina"]
            .transform(lambda x: x.rolling(3, min_periods=1, center=True).mean())
        )

        st.write('df_idade - (incluindo a coluna falhas_suavisadas)')
        st.dataframe(df_idade)

        fig = px.line(
            df_idade,
            x="idade_int",
            y=["reparacoes_por_maquina", "falhas_suavizada"],
            color="modelo",
            markers=True,
            title="Falhas por idade (original vs suavizada)"
        )

        st.plotly_chart(fig)

        # df_prob
        # ========================================================
        st.subheader('df_prob v.1', divider='red')
        st.write('df_prob')
        df_limpo["teve_falha"] = 1

        df_prob = (
            df_limpo.groupby(["modelo", "idade_int"])
            .agg(
                maquinas=("serie", "nunique"),
                maquinas_com_falha=("teve_falha", "sum")
            )
            .reset_index()
        )

        df_prob["prob_falha"] = (
            df_prob["maquinas_com_falha"] / df_prob["maquinas"]
        )

        st.dataframe(df_prob)



        # df_lifecycle para fazer df_prob V.2
        # ========================================================
        st.subheader('df_prob V.2', divider='red')
        st.write('df_prob')
        df_obs = (
            df_limpo.groupby(["serie", "modelo"])
            .agg(
                idade_max=("idade_int", "max")
            )
            .reset_index()
        )

        registros = []

        for _, row in df_obs.iterrows():
            for idade in range(row["idade_max"] + 1):
                registros.append({
                    "serie": row["serie"],
                    "modelo": row["modelo"],
                    "idade_int": idade
                })

        df_exposicao = pd.DataFrame(registros)

        df_falhas = df_limpo.copy()

        df_falhas["teve_falha"] = 1

        df_falhas = df_falhas.groupby(
            ["serie", "modelo", "idade_int"],
            as_index=False
        ).agg(
            teve_falha=("teve_falha", "max")
        )

        df_lifecycle = df_exposicao.merge(
            df_falhas,
            on=["serie", "modelo", "idade_int"],
            how="left"
        )

        df_lifecycle["teve_falha"] = df_lifecycle["teve_falha"].fillna(0)

        df_prob = (
            df_lifecycle.groupby(["modelo", "idade_int"])
            .agg(
                maquinas=("serie", "nunique"),
                maquinas_com_falha=("teve_falha", "sum")
            )
            .reset_index()
        )

        df_prob["prob_falha"] = (
            df_prob["maquinas_com_falha"] / df_prob["maquinas"]
        )

        st.dataframe(df_prob)

        fig2 = px.line(
            df_prob,
            x="idade_int",
            y="prob_falha",
            color="modelo",
            markers=True,
            title="Probabilidade de falha por idade"
        )

        st.plotly_chart(fig2)

        st.subheader('Modelo preditivo simples', divider='red')
        # 🔹 3. Modelo preditivo simples
        # Agora você transforma isso em previsão.
        # 🎯 Objetivo
        # Prever:
        # falhas futuras
        # custo futuro
        # 🔧 Modelo simples (regressão linear)
        # Preparar dados
        df_model = df_idade.copy()
        df_model = df_model.dropna(subset=["falhas_suavizada"])

        # Treinar modelo
        from sklearn.linear_model import LinearRegression

        X = df_model[["idade_int"]]
        y = df_model["falhas_suavizada"]

        model = LinearRegression()
        model.fit(X, y)

        # Previsão
        idades_futuras = np.arange(0, 15).reshape(-1, 1)

        pred = model.predict(idades_futuras)

        # 📊 Plot previsão
        df_pred = pd.DataFrame({
            "idade_int": idades_futuras.flatten(),
            "falhas_previstas": pred
        })

        fig3 = px.line(df_model, x="idade_int", y="falhas_suavizada", title="Falhas reais vs previstas")

        fig3.add_scatter(
            x=df_pred["idade_int"],
            y=df_pred["falhas_previstas"],
            mode="lines",
            name="Previsão"
        )

        st.plotly_chart(fig3)
        # ⚠️ Limitação

        # Linear é simples demais — geralmente a curva é:

        # lenta no começo
        # cresce no meio
        # explode no final

        # 👉 então melhor usar:

        # 🔥 Versão melhor (polinomial)
        st.subheader('🔥 Versão melhor (polinomial)', divider='red')
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.pipeline import make_pipeline

        for modelo in df_idade['modelo'].unique():

            st.subheader(modelo, divider='red')

            df_model = df_idade[df_idade["modelo"] == modelo]
            # 🔎 Interpretação direta da linha abaixo
            # Remove todas as linhas do DataFrame onde a coluna "falhas_suavizada" está com valor NaN (nulo).
            # Retorna um novo DataFrame sem essas linhas.
            # Você está sobrescrevendo o original (df_model).        
            df_model = df_model.dropna(subset=["idade_int", "falhas_suavizada"])
            
            st.dataframe(df_model)

            X = df_model[["idade_int"]]   # precisa ser DataFrame (não série)
            y = df_model["falhas_suavizada"]

            model = make_pipeline(
                # PolynomialFeatures(degree=2),
                PolynomialFeatures(degree=2, include_bias=False),
                LinearRegression()
            )        

            model.fit(X, y)

            idades_futuras = np.arange(0, 15).reshape(-1, 1)

            pred = model.predict(idades_futuras)
            pred = np.clip(pred, 0, None)

            df_pred = pd.DataFrame({
                "idade_int": idades_futuras.flatten(),
                "falhas_previstas": pred
            })

            st.dataframe(df_pred)

            fig4 = px.scatter(
                df_model,
                x="idade_int",
                y="falhas_suavizada",
                title="Falhas reais vs previsão"
            )

            fig4.add_scatter(
                x=df_pred["idade_int"],
                y=df_pred["falhas_previstas"],
                mode="lines",
                name="Previsão"
            )

            fig4.update_layout(
                xaxis_title="Idade (anos)",
                yaxis_title="Falhas",
                legend_title="Legenda"
            )

            st.plotly_chart(fig4)

            fig4 = px.scatter(
                df_model,
                x="idade_int",
                y="falhas_suavizada",
                title=f"{modelo} - Falhas reais vs previsão"
            )

            fig4.add_scatter(
                x=df_pred["idade_int"],
                y=df_pred["falhas_previstas"],
                mode="lines",
                name="Previsão"
            )

            fig4.update_layout(
                xaxis_title="Idade (anos)",
                yaxis_title="Falhas"
            )

            st.plotly_chart(fig4, use_container_width=True)

        st.subheader('Prova Real', divider='red')
        fig = px.bar(
            df_metricas_idade,
            x="idade_int",
            y="maquinas",
            title="Máquinas por idade"
        )

        st.plotly_chart(fig)

        # 🧠 Interpretação

        # Agora você consegue:

        # prever falhas aos 6, 7, 8 anos
        # projetar custo futuro
        # antecipar problema da frota

        # 🔥 Insight mais importante

        # Agora você tem 3 camadas:

        # 1. Real (dados)
        # falhas por idade
        # 2. Tendência
        # curva suavizada
        # 3. Futuro
        # previsão
        # 🚀 Próximo passo natural

        # Se quiser evoluir ainda mais (nível bem alto):

        # encontrar ponto ótimo de troca
        # calcular:
        # custo acumulado
        # falha acumulada
        # custo marginal

        # 👉 isso responde:

        # “com quantos anos devo substituir a máquina?”

        # ✔️ Resumo

        # Você agora tem:

        # curva limpa (suavizada)
        # risco real (% de falha)
        # previsão futura

        # 👉 isso já é nível engenharia de confiabilidade básica

        # Se quiser, próximo passo eu monto:

        # 👉 função única que retorna tudo isso pronto (df + gráficos)
        # 👉 ou direto uma página Streamlit com esses 3 blocos integrados

        # Qual caminho quer seguir?


    # endregion
    # ========================================================
    # read_ams_dashboard_sap()

    # ========================================================
    # region Machine Learning
    # ========================================================
    def machine_lerning():
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import mean_squared_error

        # # st.title('Machine Learning')
        # st.session_state.title = 'Machine Learning'

        # df = pd.DataFrame({
        #     'x': [1, 2, 3, 4, 5],
        #     'y': [2, 4, 6, 8, 10],
        #     # 'y': [2, 5, 7, 9, 11],
        # })

        # # df['y'] = 2 * df['x'] ** 2

        # st.dataframe(df)

        # x = df[['x']]
        # y = df['y']

        # model = LinearRegression()
    
        # model.fit(x, y)

        # x_value = st.number_input('Novo valor para x')

        # resultado = model.predict([[x_value]])

        # st.write(f'Previsão para x = {x_value} ➡️ {resultado[0]}')
        # st.write("Coeficiente (a):", model.coef_[0])
        # st.write("Intercepto (b):", model.intercept_)
        
        # st.latex(r'''
        # MSE = \frac{1}{n} \sum_{i=1}^{n} (y_{real,i} - y_{previsto,i})^2
        # ''')        

        # # previsões para todos os pontos
        # y_pred = model.predict(x)

        # # cálculo do erro
        # mse = mean_squared_error(y, y_pred)

        # st.write('mse', mse)

        st.title("Cálculo de MSE (Erro Quadrático Médio)")

        st.write("Digite os valores separados por vírgula:")

        # Inputs
        y_real_input = st.text_input("Valores reais (y_real)", "1, 2, 3, 4, 5")
        y_prev_input = st.text_input("Valores previstos (y_previsto)", "1.1, 1.9, 3.2, 3.8, 5.1")

        def parse_input(texto):
            try:
                return np.array([float(x.strip()) for x in texto.split(",")])
            except:
                return None

        y_real = parse_input(y_real_input)
        y_prev = parse_input(y_prev_input)

        if y_real is not None and y_prev is not None:

            if len(y_real) != len(y_prev):
                st.error("As listas precisam ter o mesmo tamanho.")
            else:
                # cálculo do MSE
                mse = np.mean((y_real - y_prev) ** 2)

                st.subheader("Resultado")
                st.write(f"MSE = {mse:.4f}")

                # mostrar passo a passo
                st.subheader("Detalhamento")
                erros = y_real - y_prev
                erros_quad = erros ** 2

                st.write("Erros:", erros)
                st.write("Erros ao quadrado:", erros_quad)
                st.write('Somatorio de Erros ao quadrado', [erros_quad][0].mean())
    
    # endregion
    # ========================================================
    # machine_lerning()

    # ========================================================
    # region NORMALIZAR ITENS
    # ========================================================
    def normalizar_itens(df_repair=None):
        df_normal_itens = loaders.load_normal_itens()
        st.dataframe(df_normal_itens)
    # endregion
    # ========================================================
    # normalizar_itens()

    # ========================================================
    # region TRATA DADOS AMS DASHBOARD
    # ========================================================
    def repair_cc_sorocaba():
    # Baixa os dados do AMS Dashboard selecionando os anos separadamente
    # Nomeia os arquivos com o ano do reparo
    # Carrega todos os arquivos
    # Insere UF manualmente
    # Insera Tipo, Linha e Modelo manualmente
    # Salva o novo arquivo tratado

        st.subheader('Repair CC Sorocaba')

        # ========================================================
        # region OBTER DADOS E DF_REPAIR
        # ========================================================
        @st.cache_data(show_spinner="Carregando arquivos...")
        def carregar_excel(file_bytes):
            return pd.read_excel(BytesIO(file_bytes))                

        arquivos = st.session_state.arquivos_unicos.items()

        dfs = []

        if arquivos:
            for key, file in arquivos:
                df = carregar_excel(file.getvalue()) # 👈 aqui
                name_file = file.name.split('_')[3].replace(".xlsx", "")
                df['ano_reparo'] = name_file
                dfs.append(df)

        df_repair = pd.concat(dfs, ignore_index=True)

        df_repair = df_repair[
            (df_repair['Cliente'] != 'Total')
            &
            (~df_repair['Cliente'].str.contains('Filtros', case=False, na=False))
            &
            (~df_repair['Cliente'].isna())
        ].reset_index(drop=True)
        split = df_repair['Cliente'].str.split(' - ', n=1, expand=True)
        df_repair.insert(0, 'Id', split[0].str.strip())
        df_repair.insert(1, 'Razão Social', split[1].str.strip())
        df_repair.drop(columns=['Cliente'], inplace=True)
        df_repair.rename(columns={
            'Pagado pelo Cliente': 'Pago pelo Cliente',
            'Economia': 'Custo Hilti'
        }, inplace=True)

        cols = ['Custo de Reparos', 'Pago pelo Cliente', 'Custo Hilti']
        df_repair[cols] = df_repair[cols] * 1.4   

        df_unidades = pd.DataFrame({
            'Razão Social': df_repair['Razão Social'].unique()
        })
        df_unidades.insert(0, 'UF', '')
        with st.expander('UFs'):
            df_editado =  st.data_editor(df_unidades)

        df_repair = df_repair.merge(
            df_editado,
            on='Razão Social',
            how='left'
        )


        df_descricoes = df_repair['Nome do Material'].unique()
        df_descricoes = pd.DataFrame({
            'Nome do Material': df_descricoes
        })
        df_descricoes.insert(1, 'Tipo', '')
        df_descricoes.insert(2, 'Linha', '')
        df_descricoes.insert(3, 'Modelo', '')
        with st.expander('Modelos'):
            df_descricoes_editado = st.data_editor(df_descricoes)

        df_repair = df_repair.merge(
            df_descricoes_editado,
            on='Nome do Material',
            how='left'
        )

        # endregion
        # ========================================================            



        # ========================================================
        # region SHOW DF_REPAIR
        # ========================================================
        st.dataframe(df_repair)
        total = df_repair['Custo de Reparos'].sum()
        st.write(f'Custo total de reparos: {formaters.br_num(total)}')        
        if st.button('Gerar Excel'):
            gerar_excel.dowload(df_repair, 'repair_cc_sorocaba')
        # endregion
        # ========================================================

    # endregion
    # ========================================================
    # repair_cc_sorocaba()

    # ========================================================
    # region ANALISA OS DADOS AMS DASHBOARD 
    # ========================================================
    def analisa_dados_ams_dashboard():
    # Os dados podem já existir ou serem obtidos em :
    # TRATA DADOS AMS DASHBOARD
     
        # ========================================================
        # region CARREGAR DADOS
        # ========================================================
        @st.cache_data(show_spinner="Carregando arquivos...")
        def carregar_excel(file_bytes):
            return pd.read_excel(BytesIO(file_bytes))

        arquivos = st.session_state.arquivos_unicos.items()

        dfs = []

        if arquivos:
            for key, file in arquivos:
                df = carregar_excel(file.getvalue()) # 👈 aqui
                dfs.append(df)

        df_repair = pd.concat(dfs, ignore_index=True)
        df_repair.rename(columns={'Linha': 'Familia'}, inplace=True)
        df_repair.insert(0, 'Cliente', 'CC Brasilia')
        # endregion
        # ========================================================

        # ========================================================
        # region FILTROS
        # ========================================================
        
        ufs = ['']
        values = list(df_repair['UF'].unique())
        ufs.extend(values)
        uf = st.sidebar.selectbox('UF', ufs)
        if uf:
            df_repair = df_repair[df_repair['UF'] == uf]

        anos = ['']
        values = list(df_repair['ano_reparo'].unique())
        anos.extend(values)
        anos_selected = st.sidebar.multiselect('Ano Reparo', anos)
        if anos_selected:
            df_repair = df_repair[df_repair['ano_reparo'].isin(anos_selected)]            

        tipos = ['']
        values = list(df_repair['Tipo'].unique())
        tipos.extend(values)
        tipo = st.sidebar.selectbox('Tipo', tipos)
        if tipo:
            df_repair = df_repair[df_repair['Tipo'] == tipo]

        familias = ['']
        values = list(df_repair['Familia'].unique())
        familias.extend(values)
        familias_selected = st.sidebar.multiselect('Familia', familias)
        if familias_selected:
            df_repair = df_repair[df_repair['Familia'].isin(familias_selected)]

        modelos = ['']
        values = list(df_repair['Modelo'].unique())
        modelos.extend(values)
        modelo = st.sidebar.selectbox('Modelo', modelos)
        if modelo:
            df_repair = df_repair[df_repair['Modelo'] == modelo]

        # endregion
        # ========================================================        

        # ========================================================
        # region SHOW DF_REPAIR
        # ========================================================
        st.dataframe(df_repair)
        total = df_repair['Custo de Reparos'].sum()
        st.write(f'Custo total de reparos: {formaters.br_num(total)}')
        gerar_excel.dowload(df_repair, 'ams_dashboard_cc_sorocaba_2026_04_27')   
        # endregion
        # ========================================================

        # ========================================================
        # region GRÁFICOS
        # ========================================================
        df_plot = (
            df_repair
            .groupby('ano_reparo', as_index=False)
            ['Custo de Reparos']
            .sum()
        )            

        fig = px.bar(
            df_plot,
            x='ano_reparo',
            y='Custo de Reparos',
            title='Custo de Reparos por Ano',
            text='Custo de Reparos',
            color_discrete_sequence=['#d2051e']  # 👈 cor da barra
        )
        fig.update_traces(
            texttemplate='R$ %{text:,.0f}',
            textposition='outside',
            hovertemplate='Ano: %{x}<br>Total: R$ %{y:,.2f}<extra></extra>'
        )
        fig.update_layout(
            yaxis_tickprefix="R$ ",
            xaxis_title="Ano",
            yaxis_title="Custo Total"
        )        

        st.plotly_chart(fig)
        # endregion
        # ========================================================        


    # endregion
    # ========================================================
    # analisa_dados_ams_dashboard()


    ## ========================================================
    # region DF_RECIBOS_ROW
    # ========================================================
    def df_recibos_row():
        st.subheader('DF Recibos Row')
        df = st.session_state.df_recibos_row.copy()
        st.dataframe(df)

        df_razao_social = pd.DataFrame(df['Razão Social'].unique(), columns=['Razão Social'])
        df_razao_social.insert(1, 'UF', '')
        with st.expander('UFs'):
            df_razao_social_editado = st.data_editor(df_razao_social)

        df = df.merge(
            df_razao_social_editado,
            on='Razão Social',
            how='left'
        )

        UFs = ['']
        values = list(df['UF'].unique())
        UFs.extend(values)
        UF = st.sidebar.multiselect('UF', UFs)
        if UF:
            df = df[df['UF'].isin(UF)]

        df['ano'] = df['Período'].dt.year.astype(str)
        anos = ['']
        values = list(df['ano'].unique())
        anos.extend(values)
        ano = st.sidebar.multiselect('Ano', anos)
        if ano:
            df = df[df['ano'].isin(ano)]

        periodos = ['']
        values = list(df['Período'].unique())
        periodos.extend(values)
        periodo = st.sidebar.multiselect('Período', periodos)
        if periodo:
            df = df[df['Período'].isin(periodo)]        

        familias = ['']
        values = list(df['familia'].unique())
        familias.extend(values)
        familia = st.sidebar.multiselect('Familia', familias)
        if familia:
            df = df[df['familia'].isin(familia)]

        modelos = ['']
        values = list(df['modelo'].unique())
        modelos.extend(values)
        modelo = st.sidebar.multiselect('Modelo', modelos)
        if modelo:
            df = df[df['modelo'].isin(modelo)]

        st.dataframe(df)
        total = df['Subtotal c/imp'].sum()
        st.write(f'Total: {formaters.br_num(total)}')
        gerar_excel.dowload(df, 'df_recibos_row_sorocaba_2026_04_27')
    # endregion
    # ========================================================
    # df_recibos_row()

    # ========================================================
    # region ANALISE VIABILIDADE G.F.
    # ========================================================

    def analise_viabilidade_gf():
        st.set_page_config(page_title="Compra vs Gestão de Frotas", layout="wide")


        def taxa_mensal(taxa_anual):
            return (1 + taxa_anual) ** (1 / 12) - 1


        def saldo_com_retiradas(valor_inicial, retirada_mensal, taxa_anual, meses):
            i = taxa_mensal(taxa_anual)

            saldo = valor_inicial
            historico = []

            for mes in range(1, meses + 1):
                saldo *= (1 + i)
                saldo -= retirada_mensal

                historico.append({
                    "Mês": mes,
                    "Saldo": saldo
                })

            return saldo, pd.DataFrame(historico)


        def brl(valor):
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


        st.title("Simulador: Compra vs Gestão de Frotas")

        st.sidebar.header("Parâmetros principais")

        valor_maquina = st.sidebar.number_input(
            "Valor unitário da máquina",
            min_value=0.0,
            value=8746.79,
            step=100.0
        )

        qtd_maquinas = st.sidebar.number_input(
            "Quantidade de máquinas",
            min_value=1,
            value=50,
            step=1
        )

        taxa_anual_pct = st.sidebar.slider(
            "Taxa anual da aplicação (%)",
            min_value=0.0,
            max_value=25.0,
            value=10.0,
            step=0.5
        )

        taxa_anual = taxa_anual_pct / 100

        meses_gf = st.sidebar.slider(
            "Prazo Gestão de Frotas (meses)",
            min_value=1,
            max_value=60,
            value=48,
            step=1
        )

        meses_compra = st.sidebar.slider(
            "Prazo de pagamento da compra (meses)",
            min_value=1,
            max_value=60,
            value=15,
            step=1
        )

        parcela_compra = st.sidebar.number_input(
            "Parcela mensal da compra",
            min_value=0.0,
            value=29155.97,
            step=100.0
        )

        mensalidade_gf_unitaria = st.sidebar.number_input(
            "Mensalidade G.F. por máquina",
            min_value=0.0,
            value=381.21,
            step=10.0
        )

        st.sidebar.header("Premissas econômicas")

        valor_residual_pct = st.sidebar.slider(
            "Valor residual da compra (%)",
            min_value=0,
            max_value=80,
            value=30,
            step=1
        ) / 100

        custo_reparo_mensal = st.sidebar.slider(
            "Custo mensal de reparos evitado pela G.F.",
            min_value=0,
            max_value=50000,
            value=5000,
            step=500
        )

        custo_parada_mensal = st.sidebar.slider(
            "Custo mensal de paradas evitado pela G.F.",
            min_value=0,
            max_value=50000,
            value=3000,
            step=500
        )

        perda_roubo_mensal = st.sidebar.slider(
            "Perda mensal estimada por roubo/sinistro",
            min_value=0,
            max_value=50000,
            value=1500,
            step=500
        )


        valor_compra_total = valor_maquina * qtd_maquinas
        mensalidade_gf_total = mensalidade_gf_unitaria * qtd_maquinas
        valor_contrato_gf = mensalidade_gf_total * meses_gf


        saldo_compra, df_compra = saldo_com_retiradas(
            valor_inicial=valor_compra_total,
            retirada_mensal=parcela_compra,
            taxa_anual=taxa_anual,
            meses=meses_compra
        )

        valor_residual = valor_compra_total * valor_residual_pct

        custo_reparos_total = custo_reparo_mensal * meses_gf
        custo_paradas_total = custo_parada_mensal * meses_gf
        perdas_roubo_total = perda_roubo_mensal * meses_gf

        resultado_compra = (
            saldo_compra
            + valor_residual
            - custo_reparos_total
            - custo_paradas_total
            - perdas_roubo_total
        )


        saldo_gf, df_gf = saldo_com_retiradas(
            valor_inicial=valor_contrato_gf,
            retirada_mensal=mensalidade_gf_total,
            taxa_anual=taxa_anual,
            meses=meses_gf
        )

        economia_reparos_total = custo_reparos_total
        economia_paradas_total = custo_paradas_total
        economia_roubo_total = perdas_roubo_total

        resultado_gf = (
            saldo_gf
            # + economia_reparos_total
            # + economia_paradas_total
            # + economia_roubo_total
        )

        ganho_liquido_gf = resultado_gf - resultado_compra


        st.subheader("Resumo dos cenários")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Resultado Econômico Compra", brl(resultado_compra))

        with col2:
            st.metric("Resultado Econômico G.F.", brl(resultado_gf))

        with col3:
            st.metric("Ganho Líquido da G.F.", brl(ganho_liquido_gf))


        st.divider()

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric("Valor total da compra", brl(valor_compra_total))
            st.metric("Saldo financeiro compra", brl(saldo_compra))
            st.metric("Valor residual estimado", brl(valor_residual))

        with col_b:
            st.metric("Valor contrato G.F.", brl(valor_contrato_gf))
            st.metric("Mensalidade total G.F.", brl(mensalidade_gf_total))
            st.metric("Saldo financeiro G.F.", brl(saldo_gf))

        with col_c:
            st.metric("Economia total com reparos", brl(economia_reparos_total))
            st.metric("Economia total com paradas", brl(economia_paradas_total))
            st.metric("Proteção contra perdas", brl(economia_roubo_total))


        st.divider()

        df_resultado = pd.DataFrame([
            {
                "Cenário": "Compra",
                "Saldo Financeiro": saldo_compra,
                "Valor Residual": valor_residual,
                "Reparos/Paradas/Perdas": -(custo_reparos_total + custo_paradas_total + perdas_roubo_total),
                "Resultado Econômico": resultado_compra
            },
            {
                "Cenário": "Gestão de Frotas",
                "Saldo Financeiro": saldo_gf,
                "Valor Residual": 0,
                "Reparos/Paradas/Perdas": 0, #economia_reparos_total + economia_paradas_total + economia_roubo_total,
                "Resultado Econômico": resultado_gf
            }
        ])

        st.subheader("Tabela comparativa")

        st.dataframe(
            df_resultado.style.format({
                "Saldo Financeiro": lambda x: brl(x),
                "Valor Residual": lambda x: brl(x),
                "Reparos/Paradas/Perdas": lambda x: brl(x),
                "Resultado Econômico": lambda x: brl(x),
            }),
            hide_index=True,
            use_container_width=True
        )


        st.subheader("Comparação do Resultado Econômico")

        fig_bar = px.bar(
            df_resultado,
            x="Cenário",
            y="Resultado Econômico",
            text="Resultado Econômico",
            title="Resultado Econômico Final por Cenário"
        )

        fig_bar.update_traces(
            texttemplate="R$ %{text:,.2f}",
            textposition="outside"
        )

        fig_bar.update_layout(
            yaxis_title="Resultado Econômico",
            xaxis_title=None
        )

        st.plotly_chart(fig_bar, use_container_width=True)


        st.subheader("Evolução do saldo financeiro")

        df_compra["Cenário"] = "Compra"
        df_gf["Cenário"] = "Gestão de Frotas"

        df_fluxo = pd.concat([df_compra, df_gf], ignore_index=True)

        fig_line = px.line(
            df_fluxo,
            x="Mês",
            y="Saldo",
            color="Cenário",
            markers=True,
            title="Saldo da Aplicação ao Longo do Tempo"
        )

        st.plotly_chart(fig_line, use_container_width=True)


        st.subheader("Break-even simplificado")

        custo_operacional_total = custo_reparos_total + custo_paradas_total + perdas_roubo_total

        break_even_mensal = max(0, resultado_compra - saldo_gf) / meses_gf

        col_be1, col_be2 = st.columns(2)

        with col_be1:
            st.metric(
                "Custo operacional total considerado",
                brl(custo_operacional_total)
            )

        with col_be2:
            st.metric(
                "Economia mensal necessária para G.F. empatar",
                brl(break_even_mensal)
            )


        st.caption(
            "Observação: este modelo considera valor financeiro final, valor residual, reparos, paradas e perdas. "
            "Ele não substitui uma análise contábil completa, mas já permite comparar compra e Gestão de Frotas de forma econômica."
        )    
    # endregion
    # ========================================================
    # analise_viabilidade_gf()

    # ========================================================
    # region COMPOR MIX ADIÇÃO GF
    # ========================================================
    def compor_mix_adicao_gf(show_session_state=False, sheet = 0):
        if show_session_state:
            st.session_state.show_session_state = show_session_state

        @st.cache_data(show_spinner="Carregando arquivos...")
        def carregar_excel(file_bytes, sheet_name=0):
            return pd.read_excel(BytesIO(file_bytes), sheet_name=sheet_name)

        arquivos = st.session_state.arquivos_unicos.items()

        dfs = []

        if arquivos:
            for key, file in arquivos:
                df = carregar_excel(file.getvalue(), sheet_name=sheet) # 👈 aqui
                dfs.append(df)
        
        if dfs:
            df_mix_row = pd.concat(dfs, ignore_index=True)

            cliente = create_filter.create_filter(df_mix_row, 'Cliente', 'Cliente')
            if cliente:
                df_mix_row = df_mix_row[df_mix_row['Cliente'] == cliente]

            with st.expander('DF Mix Row - Original'):
                st.subheader('DF Mix Row')
                st.dataframe(df_mix_row)


            if not sheet:
                st.write('Não foi passado nome da planilha')                
                df_mix = df_mix_row.copy()

                # # forma 1 - usando loop (menos elegante)
                # # clientes = list(df_mix['Cliente'].unique())
                # # df_mix[clientes] = pd.get_dummies(df_mix['Cliente']).mul(df_mix['Qtd'], axis=0)

                # forma 2 - usando join (mais elegante)
                df_mix = df_mix.join(
                    pd.get_dummies(df_mix['Cliente']).mul(df_mix['Qtd'], axis=0)
                )

                df_mix.drop(columns=['Cliente', 'Qtd'], inplace=True)

                df_mix = df_mix.groupby(['linha', 'modelo'], as_index=False).sum()

                st.subheader('Mix de Adição G.F.')
                st.dataframe(df_mix)
                total_maquinas = df_mix.drop(columns=['linha', 'modelo']).sum().sum()
                st.write(f'Total de máquinas: {formaters.br_num(total_maquinas)}')

                df_sugestao_mix = df_mix.copy()
                if 'CC Brasilia' in df_sugestao_mix.columns and 'CC Sorocaba' in df_sugestao_mix.columns:
                    max_vals = df_sugestao_mix[['CC Brasilia', 'CC Sorocaba']].max(axis=1)

                    df_sugestao_mix['CC Brasilia'] = max_vals
                    df_sugestao_mix['CC Sorocaba'] = max_vals

                df_sugestao_mix.loc[df_sugestao_mix['modelo'] == 'TE-700', 'modelo'] = 'TE-600'

                st.subheader('Sugestão de Mix')
                st.dataframe(df_sugestao_mix)
                total_sugestao = df_sugestao_mix.drop(columns=['linha', 'modelo']).sum().sum()
                st.write(f'Total de máquinas na sugestão: {formaters.br_num(total_sugestao)}')
                if st.button('Salvar XLSX'):
                    gerar_excel.dowload(df_sugestao_mix, 'Sugestão MIX')
            else:
                st.write('Não foi passado nome da planilha')                
                df_mix_cliente_grupo = df_mix_row.copy()

                # # forma 1 - usando loop (menos elegante)
                # # clientes = list(df_mix['Cliente'].unique())
                # # df_mix[clientes] = pd.get_dummies(df_mix['Cliente']).mul(df_mix['Qtd'], axis=0)

                # forma 2 - usando join (mais elegante)
                df_mix_cliente_grupo = df_mix_cliente_grupo.join(
                    pd.get_dummies(df_mix_cliente_grupo['Cliente']).mul(df_mix_cliente_grupo['Qtd'], axis=0)
                )

                df_mix_cliente_grupo = df_mix_cliente_grupo.join(
                    pd.get_dummies(df_mix_cliente_grupo['grupo']).mul(df_mix_cliente_grupo['Qtd'], axis=0)
                )

                df_mix_cliente_grupo.drop(columns=['Cliente', 'Qtd', 'grupo'], inplace=True)

                # df_mix = df_mix.groupby(['linha', 'modelo'], as_index=False).sum()

                st.subheader('Mix p/ Cliente e Grupo')
                st.dataframe(df_mix_cliente_grupo)


                df_resumo_grupo = df_mix_cliente_grupo[['linha', 'modelo', 'Comprado', 'Frota']].copy()
                df_resumo_grupo['total'] = df_resumo_grupo['Comprado'] + df_resumo_grupo['Frota']
                df_resumo_grupo = df_resumo_grupo.groupby(['linha', 'modelo'], as_index=False).sum()

                familia = create_filter.create_filter(df_resumo_grupo, 'linha', 'Familia')
                if familia:
                    df_resumo_grupo = df_resumo_grupo[df_resumo_grupo['linha'] == familia]


                st.subheader('Pq total por Grupo')
                st.dataframe(df_resumo_grupo)
                total_resumo = df_resumo_grupo['total'].sum()
                st.write(f'Total de máquinas proprias e G.F. {formaters.br_num(total_resumo)}')
                if st.button('Salvar xlsx'):
                    gerar_excel.dowload(df_resumo_grupo, 'Pq total por Grupo')

    # endregion
    # ========================================================
    # compor_mix_adicao_gf(show_session_state=True,)
    # compor_mix_adicao_gf(show_session_state=True, sheet='pq_total_proprio+gf')