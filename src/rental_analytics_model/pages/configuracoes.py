# import streamlit as st

# def save_config():
#     st.session_state["dias_semana"] = st.session_state["_dias_semana"]
#     st.session_state["tx_disponibilidade"] = st.session_state["_tx_disponibilidade"]
#     st.session_state["tx_ocupacao"] = st.session_state["_tx_ocupacao"]

# def show():

#     st.divider()

#     # ========================================================
#     # region UNIDADE
#     # ========================================================
#     if 'df_recibos' in st.session_state and not st.session_state.df_recibos.empty:
#         if 'df_recibos_originais' not in st.session_state or st.session_state.df_recibos_originais.empty:
#             st.session_state.df_recibos_originais = st.session_state.df_recibos.copy()

#     df = st.session_state.df_recibos_originais.copy()

#     unidades = df['Razão Social'].dropna().astype(str).sort_values().unique().tolist()

#     # chave persistente real
#     if 'unidades_selected_persist' not in st.session_state:
#         st.session_state.unidades_selected_persist = unidades.copy()

#     # remove seleções que não existem mais
#     st.session_state.unidades_selected_persist = [
#         unidade for unidade in st.session_state.unidades_selected_persist
#         if unidade in unidades
#     ]

#     # se o widget ainda não existir nesta renderização, alimenta ele com o valor persistido
#     if '_unidades_selected_widget' not in st.session_state:
#         st.session_state['_unidades_selected_widget'] = st.session_state.unidades_selected_persist.copy()

#     # também garante que o widget só tenha opções válidas
#     st.session_state['_unidades_selected_widget'] = [
#         unidade for unidade in st.session_state['_unidades_selected_widget']
#         if unidade in unidades
#     ]

#     def sync_unidades():
#         st.session_state.unidades_selected_persist = st.session_state['_unidades_selected_widget'].copy()
#     # endregion
#     # ========================================================

#     st.multiselect(
#         'Unidades',
#         options=unidades,
#         key='_unidades_selected_widget',
#         on_change=sync_unidades
#     )

#     st.session_state.df_recibos = df[
#         df['Razão Social'].isin(st.session_state.unidades_selected_persist)
#     ]

#     # valor persistente
#     if "dias_semana" not in st.session_state:
#         st.session_state["dias_semana"] = int(0)

#     if "tx_disponibilidade" not in st.session_state:
#         st.session_state["tx_disponibilidade"] = int(0)

#     if "tx_ocupacao" not in st.session_state:
#         st.session_state["tx_ocupacao"] = int(0)

#     # carrega no widget ao entrar na página
#     st.session_state["_dias_semana"] = st.session_state["dias_semana"]
#     st.session_state["_tx_disponibilidade"] = st.session_state["tx_disponibilidade"]
#     st.session_state["_tx_ocupacao"] = st.session_state["tx_ocupacao"]

#     st.number_input(
#         "Dias na semana",
#         min_value=0,
#         max_value=7,
#         step=1,
#         key="_dias_semana",
#         on_change=save_config
#     )

#     st.number_input(
#         "Taxa de disponibilidade %",
#         min_value=0,
#         max_value=100,
#         step=1,
#         key="_tx_disponibilidade",
#         on_change=save_config

#     )

#     st.number_input(
#         "Taxa de ocupação %",
#         min_value=0,
#         max_value=100,
#         step=1,
#         key="_tx_ocupacao",
#         on_change=save_config

#     )

import streamlit as st
import pandas as pd


def save_config():
    st.session_state["dias_semana"] = st.session_state["_dias_semana"]
    st.session_state["tx_disponibilidade"] = st.session_state["_tx_disponibilidade"]
    st.session_state["tx_ocupacao"] = st.session_state["_tx_ocupacao"]
    # if "_dias_semana" not in st.session_state:
    #     st.session_state["_dias_semana"] = st.session_state["dias_semana"]

    # if "_tx_disponibilidade" not in st.session_state:
    #     st.session_state["_tx_disponibilidade"] = st.session_state["tx_disponibilidade"]

    # if "_tx_ocupacao" not in st.session_state:
    #     st.session_state["_tx_ocupacao"] = st.session_state["tx_ocupacao"]    


def show():

    st.divider()

    # ========================================================
    # region BASE
    # ========================================================
    if 'df_recibos' in st.session_state and not st.session_state.df_recibos.empty:
        if 'df_recibos_originais' not in st.session_state or st.session_state.df_recibos_originais.empty:
            st.session_state.df_recibos_originais = st.session_state.df_recibos.copy()

    if 'df_recibos_originais' not in st.session_state or st.session_state.df_recibos_originais.empty:
        st.warning("df_recibos_originais não disponível.")
        return

    df = st.session_state.df_recibos_originais.copy()

    # garante datetime
    df["Período"] = pd.to_datetime(df["Período"], errors="coerce")
    df = df.dropna(subset=["Período"]).copy()
    # endregion
    # ========================================================

    # ========================================================
    # region UNIDADE
    # ========================================================
    unidades = df['Razão Social'].dropna().astype(str).sort_values().unique().tolist()

    if 'unidades_selected_persist' not in st.session_state:
        st.session_state.unidades_selected_persist = unidades.copy()

    st.session_state.unidades_selected_persist = [
        unidade for unidade in st.session_state.unidades_selected_persist
        if unidade in unidades
    ]

    if '_unidades_selected_widget' not in st.session_state:
        st.session_state['_unidades_selected_widget'] = st.session_state.unidades_selected_persist.copy()

    st.session_state['_unidades_selected_widget'] = [
        unidade for unidade in st.session_state['_unidades_selected_widget']
        if unidade in unidades
    ]

    def sync_unidades():
        st.session_state.unidades_selected_persist = st.session_state['_unidades_selected_widget'].copy()
    # endregion
    # ========================================================

    st.multiselect(
        'Unidades',
        options=unidades,
        key='_unidades_selected_widget',
        on_change=sync_unidades
    )

    # ========================================================
    # region PERIODO
    # ========================================================
    periodo_min_df = df["Período"].min().date()
    periodo_max_df = df["Período"].max().date()

    if "periodo_inicial_persist" not in st.session_state:
        st.session_state["periodo_inicial_persist"] = periodo_min_df

    if "periodo_final_persist" not in st.session_state:
        st.session_state["periodo_final_persist"] = periodo_max_df

    # garante faixa válida caso o df mude
    if st.session_state["periodo_inicial_persist"] < periodo_min_df:
        st.session_state["periodo_inicial_persist"] = periodo_min_df

    if st.session_state["periodo_inicial_persist"] > periodo_max_df:
        st.session_state["periodo_inicial_persist"] = periodo_max_df

    if st.session_state["periodo_final_persist"] < periodo_min_df:
        st.session_state["periodo_final_persist"] = periodo_min_df

    if st.session_state["periodo_final_persist"] > periodo_max_df:
        st.session_state["periodo_final_persist"] = periodo_max_df

    if "_periodo_inicial_widget" not in st.session_state:
        st.session_state["_periodo_inicial_widget"] = st.session_state["periodo_inicial_persist"]

    if "_periodo_final_widget" not in st.session_state:
        st.session_state["_periodo_final_widget"] = st.session_state["periodo_final_persist"]

    def sync_periodo_inicial():
        data_inicial = st.session_state["_periodo_inicial_widget"]
        data_final = st.session_state["periodo_final_persist"]

        if data_inicial > data_final:
            st.session_state["_periodo_final_widget"] = data_inicial
            st.session_state["periodo_final_persist"] = data_inicial

        st.session_state["periodo_inicial_persist"] = data_inicial

    def sync_periodo_final():
        data_inicial = st.session_state["periodo_inicial_persist"]
        data_final = st.session_state["_periodo_final_widget"]

        if data_final < data_inicial:
            st.session_state["_periodo_inicial_widget"] = data_final
            st.session_state["periodo_inicial_persist"] = data_final

        st.session_state["periodo_final_persist"] = data_final
    # endregion
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:
        st.date_input(
            "Período inicial",
            min_value=periodo_min_df,
            max_value=periodo_max_df,
            key="_periodo_inicial_widget",
            format="DD/MM/YYYY",
            on_change=sync_periodo_inicial
        )

    with col2:
        st.date_input(
            "Período final",
            min_value=periodo_min_df,
            max_value=periodo_max_df,
            key="_periodo_final_widget",
            format="DD/MM/YYYY",
            on_change=sync_periodo_final
        )

    # ========================================================
    # region FILTRO FINAL
    # ========================================================
    data_inicial = pd.to_datetime(st.session_state["periodo_inicial_persist"])
    data_final = pd.to_datetime(st.session_state["periodo_final_persist"])

    df_filtrado = df[
        (df['Razão Social'].isin(st.session_state.unidades_selected_persist)) &
        (df['Período'] >= data_inicial) &
        (df['Período'] <= data_final)
    ].copy()

    st.session_state.df_recibos = df_filtrado
    # endregion
    # ========================================================

    # ========================================================
    # region CONFIGS NUMERICAS
    # ========================================================
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
        on_change=save_config
    )

    st.number_input(
        "Taxa de disponibilidade %",
        min_value=0,
        max_value=100,
        step=1,
        key="_tx_disponibilidade",
        on_change=save_config
    )

    st.number_input(
        "Taxa de ocupação %",
        min_value=0,
        max_value=100,
        step=1,
        key="_tx_ocupacao",
        on_change=save_config
    )
    # endregion
    # ========================================================