# ========================================================
# region IMPORTS
# ========================================================
import streamlit as st
import pandas as pd
import unicodedata

from rental_analytics_model.components import table, multi_select_persist
from rental_analytics_model.utils.gerar_excel import dowload
from rental_analytics_model.services import calcular_indicadores_chave, calcular_indicadores_chave_m2, filter
from rental_analytics_model.services.calcular_periodos import calcular_periodos_df
from rental_analytics_model.utils import formaters
# endregion
# ========================================================

# ========================================================
# region MAIN
# ========================================================
def show():

    # ========================================================
    # region Forma Antiga
    # ========================================================
    # # ========================================================
    # # region FUNCTIONS
    # # ========================================================
    # def sync_periodos():
    #         st.session_state.periodos_persist = st.session_state['_periodos_selected_widget'].copy()

    # def sync_familias():
    #         st.session_state.familias_persist = st.session_state['_familias_selected_widget'].copy()

    # def sync_modelos():
    #     st.session_state.modelos_persist = st.session_state['_modelos_selected_widget'].copy()

    # def normalizar_texto(s):
    #     if pd.isna(s):
    #         return s

    #     s = str(s).strip().lower()

    #     s = ''.join(
    #         c for c in unicodedata.normalize('NFKD', s)
    #         if not unicodedata.combining(c)
    #     )

    #     return s
    
    # def get_price(df, cols, col):
    #       df = df.copy()
    #       col_price = [item for item in cols if item == col]
    #       cols_not_price = [item for item in cols if item not in col_price]
    #     #   st.write(col_price[0])
    #     #   st.write(col)
    #     #   st.write(cols_not_price)
    #       df = df[
    #             (df[col_price].gt(0).all(axis=1))
    #             &
    #             (df[cols_not_price].lt(1).all(axis=1))
    #       ]
    #       df = (
    #             df
    #             .groupby(['familia', 'modelo'], as_index=False)
    #             .agg({
    #                 'valor': 'sum',
    #                 col: 'sum'  
    #             })
    #       )
    #       df_valores_locacao[f'p_{col}'] = df['valor'] / df[col]
    #       df_valores_locacao[f'p_{col}'] = df_valores_locacao[f'p_{col}'].fillna(0)    

    # # endregion
    # # ========================================================
        
    # # ========================================================
    # # region SUBHEADER E SESSION STATE
    # # ========================================================
    # st.subheader('Indicadores Chaves', divider='red')

    # session_state = st.session_state
    # # endregion
    # # ========================================================

    # # ========================================================
    # # region RECIBOS
    # # ========================================================
    # df_recibos = session_state.df_recibos.copy()
    # if df_recibos.empty:
    #     st.warning('Não há dados de recibos para exibir os indicadores chaves.')
    #     return
    # df_recibos.rename(columns={'Linha': 'familia', 'Modelo': 'modelo'}, inplace=True)
    # df_recibos_group = (
    #     df_recibos
    #     .groupby(['periodo','familia', 'modelo'], as_index=False)
    #     .agg({
    #         'Qt.': 'sum',
    #         'Subtotal c/imp': 'sum'
    #     })
    # )
    # df_recibos_group['acc'] = df_recibos_group['Subtotal c/imp'].cumsum()
    # # endregion
    # # ========================================================
    
    # # ========================================================
    # # region CONTRATOS
    # # ========================================================
    # df_contratos = st.session_state.df_contratos.copy()
    # if df_contratos.empty:
    #     st.warning('Não há dados de contratos para exibir os indicadores chaves.')
    #     return
    # df_contratos['periodo'] = pd.to_datetime(df_contratos['locacao']).dt.to_period('M')
    # df_contratos['dias_mes'] = df_contratos['periodo'].dt.days_in_month
    # df_contratos = calcular_periodos_df(df_contratos)
    # # endregion
    # # ========================================================
    
    # # ========================================================
    # # region VALORES LOCACAO
    # # ========================================================
    # df_valores_locacao = st.session_state.df_valores_locacao.copy()
    # if df_valores_locacao.empty and 'valor' not in df_contratos.columns:
    #     st.warning('Não há dados de valores locação para exibir os indicadores chaves.')
    #     return
    
    # df_valores_locacao.rename(columns={
    #         'Modelo': 'modelo',
    #         'dia': 'p_dia',
    #         'semana': 'p_semana',
    #         'quinzena': 'p_quinzena',
    #         'mes': 'p_mes'
    #     }, inplace=True)
    # # endregion
    # # ========================================================

    # # ========================================================
    # # region FILTER
    # # ========================================================
    # periodos = df_contratos['periodo'].unique().tolist()
    # familias = sorted(df_contratos['familia'].unique().tolist())
    # modelos = sorted(df_contratos['modelo'].unique().tolist())

    # if 'periodos_persist' not in st.session_state:
    #         st.session_state.periodos_persist = periodos.copy()

    # st.session_state.periodos_persist = [
    #         periodo for periodo in st.session_state.periodos_persist
    #         if periodo in periodos
    # ]

    # if '_periodos_selected_widget' not in st.session_state:
    #         st.session_state['_periodos_selected_widget'] = st.session_state.periodos_persist.copy()

    # st.session_state['_periodos_selected_widget'] = [
    #     periodo for periodo in st.session_state['_periodos_selected_widget']
    #     if periodo in periodos
    # ]

    # st.sidebar.multiselect(
    #     'Periodos',
    #     options=periodos,
    #     key='_periodos_selected_widget',
    #     on_change=sync_periodos
    # )
    
    # if 'familias_persist' not in st.session_state:
    #         st.session_state.familias_persist = familias.copy()

    # st.session_state.familias_persist = [
    #         familia for familia in st.session_state.familias_persist
    #         if familia in familias
    # ]

    # if '_familias_selected_widget' not in st.session_state:
    #         st.session_state['_familias_selected_widget'] = st.session_state.familias_persist.copy()

    # st.session_state['_familias_selected_widget'] = [
    #     familia for familia in st.session_state['_familias_selected_widget']
    #     if familia in familias
    # ]

    # st.sidebar.multiselect(
    #     'familias',
    #     options=familias,
    #     key='_familias_selected_widget',
    #     on_change=sync_familias
    # )

    # if 'modelos_persist' not in st.session_state:
    #         st.session_state.modelos_persist = modelos.copy()

    # st.session_state.modelos_persist = [
    #         modelos for modelos in st.session_state.modelos_persist
    #         if modelos in modelos
    # ]

    # if '_modelos_selected_widget' not in st.session_state:
    #         st.session_state['_modelos_selected_widget'] = st.session_state.modelos_persist.copy()

    # st.session_state['_modelos_selected_widget'] = [
    #     modelos for modelos in st.session_state['_modelos_selected_widget']
    #     if modelos in modelos
    # ]
    # st.sidebar.multiselect(
    #     'modelos',
    #     options=modelos,
    #     key='_modelos_selected_widget',
    #     on_change=sync_modelos
    # )

    # df_contratos = df_contratos[
    #         (df_contratos['periodo'].isin(st.session_state.periodos_persist))
    #         &
    #         (df_contratos['familia'].isin(st.session_state.familias_persist))
    #         &
    #         (df_contratos['modelo'].isin(st.session_state.modelos_persist))
    #     ].reset_index(drop=True)
    # # endregion
    # # ========================================================

    # # ========================================================
    # # region CONTRATOS VALORES
    # # ========================================================
    # if not df_valores_locacao.empty:
    #     if 'familia' in df_valores_locacao.columns:
    #         st.dataframe(df_valores_locacao)
        
    #         df_contratos = pd.merge(
    #                 df_contratos,
    #                 df_valores_locacao,
    #                 on=['familia', 'modelo'],
    #                 how='left'
    #         )
    #     else:
    #         df_contratos = pd.merge(
    #                 df_contratos,
    #                 df_valores_locacao,
    #                 on=['modelo'],
    #                 how='left'
    #         )
              

    #     df_contratos['fat_dia'] = df_contratos['dia'] * df_contratos['p_dia']
    #     df_contratos['fat_semana'] = df_contratos['semana'] * df_contratos['p_semana']
    #     df_contratos['fat_quinzena'] = df_contratos['quinzena'] * df_contratos['p_quinzena']
    #     df_contratos['fat_mes'] = df_contratos['mes'] * df_contratos['p_mes']
    #     df_contratos['valor'] = df_contratos[['fat_dia', 'fat_semana', 'fat_quinzena', 'fat_mes']].sum(axis=1)
    # else:
    #     df_valores_locacao = df_contratos[['familia', 'modelo']].drop_duplicates().reset_index(drop=True)
    #     get_price(df_contratos, ['dia', 'semana', 'quinzena', 'mes'], 'dia')
    #     get_price(df_contratos, ['dia', 'semana', 'quinzena', 'mes'], 'semana')
    #     get_price(df_contratos, ['dia', 'semana', 'quinzena', 'mes'], 'quinzena')
    #     get_price(df_contratos, ['dia', 'semana', 'quinzena', 'mes'], 'mes')
    #     df_contratos = pd.merge(
    #             df_contratos,
    #             df_valores_locacao,
    #             on=['familia', 'modelo'],
    #             how='left'
    #     )
    # # endregion
    # # ========================================================

    # # ========================================================
    # # region CONTRATOS VALORES SHOW
    # # ========================================================
    # df_contratos_valores_show = df_contratos.copy()
    # df_contratos_valores_show = df_contratos_valores_show[[
    #     'numero_contrato',
    #     'patrimonio',
    #     'familia',
    #     'marca',
    #     'modelo',
    #     'locacao',
    #     'devolucao',
    #     'valor'
    # ]]
    # df_contratos_valores_show['valor_acumulado'] = df_contratos_valores_show['valor'].cumsum()
    # # endregion
    # # ========================================================    

    # # ========================================================
    # # region EXPANDER
    # # ========================================================
    # with st.expander('Contratos'):
    #     st.dataframe(df_contratos_valores_show)
    #     st.html(
    #         f"""
    #             <div>
    #                 <p class='detalhe_dataframe'>
    #                 {len(df_contratos_valores_show)} Contratos
    #                 no período de {formaters.date_br(df_contratos_valores_show['locacao'].min())}
    #                 a {formaters.date_br(df_contratos_valores_show['locacao'].max())}
    #                 valor total: {formaters.br_num(df_contratos_valores_show['valor'].sum())}
    #                 </p>
    #             <div>
    #         """
    #     )
    # # endregion
    # # ========================================================        

    # # ========================================================
    # # region DF CONTRATOS GROUP AND MERGE WITH DF RECIBOS
    # # ========================================================
    # df_contratos_group = df_contratos.copy()    

    # df_contratos_group = (df_contratos
    #     .groupby(['periodo', 'dias_mes', 'familia', 'modelo'], as_index=False)
    #     .agg({
    #         'dias': 'sum',
    #         'dia': 'sum',
    #         'quinzena': 'sum',
    #         'semana': 'sum',
    #         'mes':'sum',
    #         'valor': 'sum',
    #     })
    # )

    # df_contratos_group['chave_merge_familia'] = df_contratos_group['familia'].apply(normalizar_texto)
    # df_contratos_group['chave_merge_modelo'] = df_contratos_group['modelo'].apply(normalizar_texto)
    # df_recibos_group['chave_merge_familia'] = df_recibos_group['familia'].apply(normalizar_texto)
    # df_recibos_group['chave_merge_modelo'] = df_recibos_group['modelo'].apply(normalizar_texto)

    # df_contratos_group = df_contratos_group.drop(columns=['familia', 'modelo'])

    # df_contratos_group = pd.merge(
    #     df_contratos_group, 
    #     df_recibos_group,
    #     on=['periodo', 'chave_merge_familia', 'chave_merge_modelo'],
    #     how='left',
    # )

    # df_contratos_group['dias_no_periodo'] = df_contratos_group['periodo'].dt.days_in_month
    # df_contratos_group['dias_possiveis'] =  df_contratos_group['dias_no_periodo'] * df_contratos_group['Qt.']
    # if 'tx_disponibilidade' not in st.session_state:
    #         st.session_state.tx_disponibilidade = 100
    # df_contratos_group['tx_disp'] = session_state.tx_disponibilidade / 100
    # # endregion
    # # ========================================================

    # # ========================================================
    # # region DF CONTRATOS GROUP
    # # ========================================================
    # if df_valores_locacao.empty and 'valor' not in df_contratos.columns:
    #         st.warning('Não há dados de valores de locações para exibir os indicadores chaves')
    #         return
    # if not df_valores_locacao.empty:

    #     if 'familia' in df_valores_locacao:
    #         st.dataframe(df_valores_locacao)

    #         df_valores_locacao['chave_merge_familia'] = df_valores_locacao['familia'].apply(normalizar_texto)
    #         df_valores_locacao['chave_merge_modelo'] = df_valores_locacao['modelo'].apply(normalizar_texto)
    #         df_valores_locacao = df_valores_locacao.drop(columns=['familia', 'modelo'])

    #         df_contratos_group = pd.merge(
    #             df_contratos_group,
    #             df_valores_locacao,
    #             on=['chave_merge_familia', 'chave_merge_modelo'],
    #             how='left'
    #         )

    #     else:
    #         df_valores_locacao['chave_merge_modelo'] = df_valores_locacao['modelo'].apply(normalizar_texto)
    #         df_valores_locacao = df_valores_locacao.drop(columns=['modelo'])

    #         df_contratos_group = pd.merge(
    #             df_contratos_group,
    #             df_valores_locacao,
    #             on=['chave_merge_modelo'],
    #             how='left'
    #         )
    #         # st.dataframe(df_valores_locacao)
                           

    #     df_contratos_group = (
    #         df_contratos_group
    #         .groupby(['periodo', 'dias_mes', 'familia', 'modelo'], as_index=False)
    #         .agg({
    #             'Qt.': 'sum',
    #             'Subtotal c/imp': 'sum',
    #             'dias_possiveis': 'sum',
    #             'dias': 'sum',
    #             'dia': 'sum',
    #             'semana': 'sum',
    #             'quinzena': 'sum',
    #             'mes': 'sum',
    #             'p_dia': 'mean',
    #             'p_semana': 'mean',
    #             'p_quinzena': 'mean',
    #             'p_mes': 'mean',
    #         })
    #     )

    # df_contratos_group['tx_ocupacao'] = df_contratos_group['dias'] / df_contratos_group['dias_possiveis']
    
    # df_contratos_group['total_contratos'] = df_contratos_group[['dia', 'semana', 'quinzena', 'mes']].sum(axis=1)
    
    # df_contratos_group['mix_dia'] = df_contratos_group['dia'] / df_contratos_group['total_contratos']
    
    # df_contratos_group['mix_semana'] = df_contratos_group['semana'] / df_contratos_group['total_contratos']
    
    # df_contratos_group['mix_quinzena'] = df_contratos_group['quinzena'] / df_contratos_group['total_contratos']

    # df_contratos_group['mix_mes'] = df_contratos_group['mes'] / df_contratos_group['total_contratos']

    # # with st.expander('Detalhes'):
    # #     st.write('dias')
    # #     st.write(df_contratos_group['dias'])
    # #     st.write('total_contratos')
    # #     st.write(df_contratos_group['total_contratos'])
    # #     st.write('mix_dia')
    # #     st.write(df_contratos_group[['dia', 'total_contratos', 'mix_dia']])
    # #     st.write('mix_semana')
    # #     st.write(df_contratos_group[['semana', 'total_contratos', 'mix_semana']])
    # #     st.write('mix_quinzena')
    # #     st.write(df_contratos_group[['quinzena', 'total_contratos', 'mix_quinzena']])
    # #     st.write('mix_mes')
    # #     st.write(df_contratos_group[['mes', 'total_contratos', 'mix_mes']])
    # # endregion
    # # ========================================================

    # # ========================================================
    # # region DF CONTRATOS CALCULAR
    # # ========================================================
    # df_contratos_calcular = df_contratos_group.copy()
    # df_contratos_calcular = df_contratos_calcular[[
    #     'familia',
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

    # # st.write('df_contratos_calcular')
    # # st.dataframe(df_contratos_calcular)
    # # st.subheader('', divider='red')
    # # endregion
    # # ========================================================

    # # ========================================================
    # # region DF CALCULADO
    # # ========================================================
    # # # df_calculado, df_total = calcular_indicadores_chave.calc(df_contratos_calcular)
    # df_check, df_calculado, df_total = calcular_indicadores_chave.calc(df_contratos_calcular)
    # # # with st.expander('df_check'):
    # # #     st.write('df_check')
    # # #     st.dataframe(
    # # #         df_check,
    # # #         column_config={
    # # #             'pot_total': st.column_config.NumberColumn(
    # # #                     'Pot_total',
    # # #                     format='R$ %,.2f'
    # # #             )
    # # #         }
    # # #     )
    # # #     fat_total = df_check['fat_total'].sum()
    # # #     cust_gf = df_check['Subtotal c/imp'].sum()
    # # #     markup = fat_total / cust_gf
    # # #     st.write(f'Faturamento: {formaters.br_num(fat_total)}')
    # # #     st.write(f'Custo G.F.: {formaters.br_num(cust_gf)}')
    # # #     st.write(f'Markup: {formaters.br_num(markup)}')
    # # #     dowload(df_check, 'df_check')
    # # df_calculado['prefixo'] = df_calculado['Modelo'].str.extract(r'([A-Za-z]+(?:-[A-Za-z]+)?)')
    # # df_calculado['numero'] = df_calculado['Modelo'].str.extract(r'(\d+)').astype(int)
    # # df_calculado = df_calculado.sort_values(['prefixo', 'numero']).drop(columns=['prefixo', 'numero'])
    # # st.dataframe(df_calculado)
    # # endregion
    # # ========================================================

    # # ========================================================
    # # region SHOW
    # # ========================================================
    # table.personal_table(df_total)
    # with st.expander('Detalhes'):
    #     table.personal_table(df_calculado)
    #     dowload(df_calculado, 'contratos_calcular')
    # # endregion
    # ========================================================
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
    if st.toggle('Exibir contratos'):
        with st.expander('Contratos'):
            st.dataframe(df_contratos_valores_show)
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
    # region EXPANDER DETAILS
    # ========================================================
    # if st.toggle('Show Details'):
    #     with st.expander('RECIBOS'):
    #         st.dataframe(df_recibos_group)
    #         custo_gf = df_recibos_group['Subtotal c/imp'].sum()
    #         st.write(f'Custo G.F. c/ impostos: {formaters.br_num(custo_gf)}')        
    #     with st.expander('VALORES LOCACAO'):
    #         st.dataframe(df_valores_locacao)
    #     with st.expander('CONTRATOS MERGE VALORES'):
    #         st.dataframe(df_contratos_valores)
    #     with st.expander('CONTRATOS VALORES SHOW'):
    #         st.dataframe(df_contratos_valores_show)
    #     with st.expander('CONTRATOS GROUP AND MERGE WITH DF RECIBOS GROUP'):
    #         st.dataframe(df_contratos_group)
    #     with st.expander('CONTRATOS GROUP MERGE VALORES LOCAÇÃO'):
    #         st.dataframe(df_contratos_group_merge_valores)
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
    # df_check, df_calculado, df_total = calcular_indicadores_chave.calc(df_contratos_calcular)

    # df_check, df_check_group, df, df_total = calcular_indicadores_chave_m2.calc(df_contratos_calcular)



    df_check, df_check_group, df_calculado, df_total = calcular_indicadores_chave_m2.calc(df_contratos_calcular)
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