import streamlit as st
import pandas as pd

from rental_analytics_model.components.multi_select_persist import multiselect_persist
from rental_analytics_model.utils import formaters


def save_config():
    st.session_state["dias_semana"] = st.session_state["_dias_semana"]
    st.session_state["tx_disponibilidade"] = st.session_state["_tx_disponibilidade"]
    st.session_state["tx_ocupacao"] = st.session_state["_tx_ocupacao"]

def show():

    st.divider()

    # ============================================================
    # region BASE
    # ============================================================
    if 'df_recibos' in st.session_state and not st.session_state.df_recibos.empty:
        if 'df_recibos_originais' not in st.session_state or st.session_state.df_recibos_originais.empty:
            st.session_state.df_recibos_originais = st.session_state.df_recibos.copy()

    if 'df_recibos_originais' not in st.session_state or st.session_state.df_recibos_originais.empty:
        st.warning("df_recibos_originais não disponível.")
        return

    if 'df_contratos' in st.session_state and not st.session_state.df_contratos.empty:
        if 'df_contratos_originais' not in st.session_state or st.session_state.df_contratos_originais.empty:
            st.session_state.df_contratos_originais = st.session_state.df_contratos.copy()

    if 'df_contratos_originais' not in st.session_state or st.session_state.df_contratos_originais.empty:
        st.warning("df_contratos_originais não disponível.")
        return

    df_recibos_originais = st.session_state.df_recibos_originais.copy()
    df_contratos_originais = st.session_state.df_contratos_originais.copy()

    # endregion
    # ============================================================

    # ============================================================
    # region UNIDADE
    # ============================================================
    # unidades = df_recibos_originais['Razão Social'].dropna().astype(str).sort_values().unique().tolist()   

    # if 'unidades_selected_persist' not in st.session_state:
    #     st.session_state.unidades_selected_persist = unidades.copy()

    # st.session_state.unidades_selected_persist = [
    #     unidade for unidade in st.session_state.unidades_selected_persist
    #     if unidade in unidades
    # ]

    # if '_unidades_selected_widget' not in st.session_state:
    #     st.session_state['_unidades_selected_widget'] = st.session_state.unidades_selected_persist.copy()

    # st.session_state['_unidades_selected_widget'] = [
    #     unidade for unidade in st.session_state['_unidades_selected_widget']
    #     if unidade in unidades
    # ]

    # def sync_unidades():
    #     st.session_state.unidades_selected_persist = st.session_state['_unidades_selected_widget'].copy()

    # st.multiselect(
    #     'Unidades',
    #     options=unidades,
    #     key='_unidades_selected_widget',
    #     on_change=sync_unidades
    # )
    # endregion
    # ============================================================

    # ============================================================
    # region PERIODOS
    # ============================================================
    # periodos = df_recibos_originais['periodo'].dropna().sort_values().unique().tolist()

    # if 'periodos_selected_persist' not in st.session_state:
    #     st.session_state.periodos_selected_persist = periodos.copy()

    # st.session_state.periodos_selected_persist = [
    #     periodo for periodo in st.session_state.periodos_selected_persist
    #     if periodo in periodos
    # ]

    # if '_periodos_selected_widget' not in st.session_state:
    #     st.session_state['_periodos_selected_widget'] = st.session_state.periodos_selected_persist.copy()

    # st.session_state['_periodos_selected_widget'] = [
    #     periodo for periodo in st.session_state['_periodos_selected_widget']
    #     if periodo in periodos
    # ]

    # def sync_periodos():
    #     st.session_state.periodos_selected_persist = st.session_state['_periodos_selected_widget'].copy()

    # st.multiselect(
    #     'Periodos',
    #     options=periodos,
    #     key='_periodos_selected_widget',
    #     on_change=sync_periodos
    # )
    # endregion
    # ============================================================

    # ============================================================
    # region PERIODO
    # ============================================================
    # garante datetime
    # df_recibos_originais["Período"] = pd.to_datetime(df_recibos_originais["Período"], errors="coerce")
    # df_recibos_originais = df_recibos_originais.dropna(subset=["Período"]).copy()    
    # periodo_min_df = df_recibos_originais["Período"].min().date()
    # periodo_max_df = df_recibos_originais["Período"].max().date()

    # if "periodo_inicial_persist" not in st.session_state:
    #     st.session_state["periodo_inicial_persist"] = periodo_min_df

    # if "periodo_final_persist" not in st.session_state:
    #     st.session_state["periodo_final_persist"] = periodo_max_df        

    # # garante faixa válida caso o df mude
    # if st.session_state["periodo_inicial_persist"] < periodo_min_df:
    #     st.session_state["periodo_inicial_persist"] = periodo_min_df

    # if st.session_state["periodo_inicial_persist"] > periodo_max_df:
    #     st.session_state["periodo_inicial_persist"] = periodo_max_df

    # if st.session_state["periodo_final_persist"] < periodo_min_df:
    #     st.session_state["periodo_final_persist"] = periodo_min_df

    # if st.session_state["periodo_final_persist"] > periodo_max_df:
    #     st.session_state["periodo_final_persist"] = periodo_max_df

    # if "_periodo_inicial_widget" not in st.session_state:
    #     st.session_state["_periodo_inicial_widget"] = st.session_state["periodo_inicial_persist"]

    # if "_periodo_final_widget" not in st.session_state:
    #     st.session_state["_periodo_final_widget"] = st.session_state["periodo_final_persist"]

    # def sync_periodo_inicial():
    #     data_inicial = st.session_state["_periodo_inicial_widget"]
    #     data_final = st.session_state["periodo_final_persist"]

    #     if data_inicial > data_final:
    #         st.session_state["_periodo_final_widget"] = data_inicial
    #         st.session_state["periodo_final_persist"] = data_inicial

    #     st.session_state["periodo_inicial_persist"] = data_inicial

    # def sync_periodo_final():
    #     data_inicial = st.session_state["periodo_inicial_persist"]
    #     data_final = st.session_state["_periodo_final_widget"]

    #     if data_final < data_inicial:
    #         st.session_state["_periodo_inicial_widget"] = data_final
    #         st.session_state["periodo_inicial_persist"] = data_final

    #     st.session_state["periodo_final_persist"] = data_final

    # col1, col2 = st.columns(2)

    # with col1:
    #     st.date_input(
    #         "Período inicial",
    #         min_value=periodo_min_df,
    #         max_value=periodo_max_df,
    #         key="_periodo_inicial_widget",
    #         format="DD/MM/YYYY",
    #         on_change=sync_periodo_inicial
    #     )

    # with col2:
    #     st.date_input(
    #         "Período final",
    #         min_value=periodo_min_df,
    #         max_value=periodo_max_df,
    #         key="_periodo_final_widget",
    #         format="DD/MM/YYYY",
    #         on_change=sync_periodo_final
    #     )
    # data_inicial = pd.to_datetime(st.session_state["periodo_inicial_persist"])
    # data_final = pd.to_datetime(st.session_state["periodo_final_persist"])

    # df_filtrado = df_recibos_originais[
    #     (df_recibos_originais['Razão Social'].isin(st.session_state.unidades_selected_persist))  &
    #     (df_recibos_originais['Período'] >= data_inicial) &
    #     (df_recibos_originais['Período'] <= data_final)
    # ].copy()
    # endregion
    # ============================================================    

    # ============================================================
    # region MULTI SELECT UNIDADES, PERIODOS, FAMILIAS e MODELOS
    # ============================================================

    def filter(df, column, lista):
        return df[df[column].isin(lista)].copy()        

    # ========================================================
    # region FILTRO UNIDADES
    # ========================================================
    unidades = (
        df_recibos_originais['Razão Social']
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
        .tolist()
    )

    unidades_selected = multiselect_persist(
        label='Unidades',
        options=unidades,
        key_base='unidades'
    )

    df_recibos_originais = filter(df_recibos_originais, 'Razão Social', unidades_selected)
    # endregion
    # ========================================================

    # ========================================================
    # region FILTRO PERIODOS
    # ========================================================
    periodos = (
        df_recibos_originais['periodo']
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    )

    periodos_selected = multiselect_persist(
        label='Períodos',
        options=periodos,
        key_base='periodos'
    )

    df_recibos_originais = filter(df_recibos_originais, 'periodo', periodos_selected)
    # endregion
    # ========================================================

    # ========================================================
    # region FILTRO FAMILIAS
    # ========================================================
    familias = (
        df_recibos_originais['familia']
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    )

    familias_selected = multiselect_persist(
        label='Familias',
        options=familias,
        key_base='familias'
    )

    df_recibos_originais = filter(df_recibos_originais, 'familia', familias_selected)
    # endregion
    # ========================================================

    # ========================================================
    # region FILTRO MODELOS
    # ========================================================
    modelos = (
        df_recibos_originais['modelo']
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    )

    modelos_selected = multiselect_persist(
        label='Modelos',
        options=modelos,
        key_base='modelos'
    )
    df_recibos_originais = filter(df_recibos_originais, 'modelo', modelos_selected)
    # endregion
    # ========================================================

    # df_contratos_originais = df_contratos_originais[
    #     (df_contratos_originais['familia'].isin(familias_selected))
    #     &
    #     (df_contratos_originais['modelo'].isin(modelos_selected))
    #     &
    #     (df_contratos_originais['periodo'].isin(periodos_selected))
    # ]

    # # endregion
    # # ============================================================

    # # ============================================================
    # # region FILTRO FINAL
    # # ============================================================

    # # df_filtrado = df_recibos_originais[
    # #     (df_recibos_originais['Razão Social'].isin(unidades_selected)) 
    # #     &
    # #     (df_recibos_originais['periodo'].isin(periodos_selected))
    # #     &
    # #     (df_recibos_originais['familia'].isin(familias_selected))
    # #     &
    # #     (df_recibos_originais['modelo'].isin(modelos_selected))
    # # ].copy()

    # # endregion
    # # ============================================================
    # # st.write(df_recibos_originais.columns)

    df_recibos_originais = (
        df_recibos_originais
        .groupby(['periodo', 'familia', 'modelo'])
        .agg({
            'Qt.': 'sum',
            'Subtotal c/imp': 'sum'
        })
        .reset_index()
    )


    df_filtrado = df_recibos_originais.copy()
    # df_filtrado.reset_index(drop=True, inplace=True)
    # # # df_filtrado.drop(columns=['Razão Social'], inplace=True)
    # st.session_state.df_recibos = df_filtrado
    # st.session_state.df_contratos = df_contratos_originais
    # st.dataframe(df_filtrado)
    # st.dataframe(st.session_state.df_contratos)

    # ========================================================
    # region EXPANDER
    # ========================================================
    # with st.expander('Recigos G.F. - Test Dev'):
    #     st.write('st.session_state.df_recibos')
    #     st.dataframe(st.session_state.df_recibos)
    #     st.write('st.session_state.df_contratos')
    #     st.write(st.session_state.df_contratos)
    #     st.write(f'Valor total G.F. com impostos: {formaters.br_num(df_filtrado['Subtotal c/imp'].sum())}')
    # endregion
    # ========================================================

    # ============================================================
    # region CONFIGS NUMERICAS
    # ============================================================
    if "dias_semana" not in st.session_state:
        st.session_state["dias_semana"] = int(0)

    if "tx_disponibilidade" not in st.session_state:
        st.session_state["tx_disponibilidade"] = int(0)

    if "tx_ocupacao" not in st.session_state:
        st.session_state["tx_ocupacao"] = int(0)

    st.session_state["_dias_semana"] = st.session_state["dias_semana"]
    st.session_state["_tx_disponibilidade"] = st.session_state["tx_disponibilidade"]
    st.session_state["_tx_ocupacao"] = st.session_state["tx_ocupacao"]

    st.number_input(
        "Dias na semana",
        min_value=0,
        max_value=7,
        step=1,
        key="_dias_semana",
        on_change=save_config,
        value=6
    )

    st.number_input(
        "Taxa de disponibilidade %",
        min_value=0,
        max_value=100,
        step=1,
        key="_tx_disponibilidade",
        on_change=save_config,
        value=65
    )

    st.number_input(
        "Taxa de ocupação %",
        min_value=0,
        max_value=100,
        step=1,
        key="_tx_ocupacao",
        on_change=save_config,
        value=75
    )
    # endregion
    # ============================================================