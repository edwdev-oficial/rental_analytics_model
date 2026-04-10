import streamlit as st
import pandas as pd

from rental_analytics_model.components import table
from rental_analytics_model.utils.gerar_excel import dowload
from rental_analytics_model.services import calcular_indicadores_chave
from rental_analytics_model.services.calcular_periodos import calcular_periodos_df


def show():
        
        st.subheader('Indicadores Chaves', divider='red')

        session_state = st.session_state

        # ========================================================
        # region DF RECIBOS
        # ========================================================
        df_recibos = session_state.df_recibos.copy()
        if df_recibos.empty:
            st.warning('Não há dados de recibos para exibir os indicadores chaves.')
            return
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
        # region DF CONTRATOS
        # ========================================================
        df_contratos = st.session_state.df_contratos.copy()
        if df_contratos.empty:
            st.warning('Não há dados de contratos para exibir os indicadores chaves.')
            return
        df_contratos['periodo'] = pd.to_datetime(df_contratos['locacao']).dt.to_period('M')
        df_contratos['dias_mes'] = df_contratos['periodo'].dt.days_in_month
        df_contratos = calcular_periodos_df(df_contratos)
        # st.dataframe(df_contratos)
        # st.divider()
        # endregion
        # ========================================================        

        # ========================================================
        # region DF VALORES LOCACAO
        # ========================================================        
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
        st.write('Valores Locação')
        # st.dataframe(df_valores_locacao)
        # st.divider()
        # endregion
        # ========================================================        

        # ========================================================
        # region FILTER CONTRATOS
        # ========================================================
        periodos = df_contratos['periodo'].unique().tolist()
        familias = sorted(df_contratos['familia'].unique().tolist())
        modelos = sorted(df_contratos['modelo'].unique().tolist())

        # ========================================================
        # region PERIODOS PERSIST
        # ========================================================
        if 'periodos_persist' not in st.session_state:
              st.session_state.periodos_persist = periodos.copy()

        st.session_state.periodos_persist = [
              periodo for periodo in st.session_state.periodos_persist
              if periodo in periodos
        ]

        if '_periodos_selected_widget' not in st.session_state:
              st.session_state['_periodos_selected_widget'] = st.session_state.periodos_persist.copy()

        st.session_state['_periodos_selected_widget'] = [
            periodo for periodo in st.session_state['_periodos_selected_widget']
            if periodo in periodos
        ]

        def sync_periodos():
              st.session_state.periodos_persist = st.session_state['_periodos_selected_widget'].copy()

        st.sidebar.multiselect(
            'Periodos',
            options=periodos,
            key='_periodos_selected_widget',
            on_change=sync_periodos
        )
        # endregion
        # ========================================================
        
        # ========================================================
        # region FAMILIAS PERSIST
        # ========================================================
        if 'familias_persist' not in st.session_state:
              st.session_state.familias_persist = familias.copy()

        st.session_state.familias_persist = [
              familia for familia in st.session_state.familias_persist
              if familia in familias
        ]

        if '_familias_selected_widget' not in st.session_state:
              st.session_state['_familias_selected_widget'] = st.session_state.familias_persist.copy()

        st.session_state['_familias_selected_widget'] = [
            familia for familia in st.session_state['_familias_selected_widget']
            if familia in familias
        ]

        def sync_familias():
              st.session_state.familias_persist = st.session_state['_familias_selected_widget'].copy()

        st.sidebar.multiselect(
            'familias',
            options=familias,
            key='_familias_selected_widget',
            on_change=sync_familias
        )
        # endregion
        # ========================================================

        # ========================================================
        # region MODELOS PERSIST
        # ========================================================
        if 'modelos_persist' not in st.session_state:
              st.session_state.modelos_persist = modelos.copy()

        st.session_state.modelos_persist = [
              modelos for modelos in st.session_state.modelos_persist
              if modelos in modelos
        ]

        if '_modelos_selected_widget' not in st.session_state:
              st.session_state['_modelos_selected_widget'] = st.session_state.modelos_persist.copy()

        st.session_state['_modelos_selected_widget'] = [
            modelos for modelos in st.session_state['_modelos_selected_widget']
            if modelos in modelos
        ]

        def sync_modelos():
            st.session_state.modelos_persist = st.session_state['_modelos_selected_widget'].copy()

        st.sidebar.multiselect(
            'modelos',
            options=modelos,
            key='_modelos_selected_widget',
            on_change=sync_modelos
        )
        # endregion
        # ========================================================

        df_contratos = df_contratos[
                (df_contratos['periodo'].isin(st.session_state.periodos_persist))
                &
                (df_contratos['familia'].isin(st.session_state.familias_persist))
                &
                (df_contratos['modelo'].isin(st.session_state.modelos_persist))
            ]
        
        # st.dataframe(df_contratos)
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
                'valor': 'sum'
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

            st.dataframe(df_contratos_group)


        df_contratos_group['tx_ocupacao'] = df_contratos_group['dias'] / df_contratos_group['dias_possiveis']
        df_contratos_group['total_contratos'] = df_contratos_group[['dia', 'semana', 'quinzena', 'mes']].sum(axis=1)
        df_contratos_group['mix_dia'] = df_contratos_group['dia'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_semana'] = df_contratos_group['semana'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_quinzena'] = df_contratos_group['quinzena'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_mes'] = df_contratos_group['mes'] / df_contratos_group['total_contratos']
        st.dataframe(df_contratos_group)
        # endregion
        # ========================================================        

        # # ========================================================
        # # region DF CALCULAR e DF CALCULADO
        # # ========================================================
        # df_contratos_calcular = df_contratos_group.copy()
        # df_contratos_calcular = df_contratos_calcular[[
        #     'modelo',
        #     'Subtotal c/imp',
        #     'periodo',
        #     'Qt.',
        #     'dias_mes',
        #     'tx_ocupacao',
        #     'mix_dia',
        #     'mix_semana',
        #     'mix_quinzena',
        #     'mix_mes',
        #     'p_dia',
        #     'p_semana',
        #     'p_quinzena',
        #     'p_mes',
        #     'dias_possiveis',
        # ]]        
        # df_contratos_calcular.insert(df_contratos_calcular.columns.get_loc('tx_ocupacao'), 'tx_disp', 1)
        # df_calculado, df_total = calcular_indicadores_chave.calc(df_contratos_calcular)
        # # endregion
        # # ========================================================

        # # ========================================================
        # # region SHOW INDICADORES
        # # ========================================================
        # table.personal_table(df_total)
        # with st.expander('Detalhes'):
        #     table.personal_table(df_calculado)
        #     dowload(df_calculado, 'contratos_calcular')
        # # endregion
        # # ========================================================
