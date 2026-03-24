import streamlit as st

def save_config():
    st.session_state["dias_semana"] = st.session_state["_dias_semana"]
    st.session_state["tx_disponibilidade"] = st.session_state["_tx_disponibilidade"]
    st.session_state["tx_ocupacao"] = st.session_state["_tx_ocupacao"]

def show():

    st.divider()

    # valor persistente
    if "dias_semana" not in st.session_state:
        st.session_state["dias_semana"] = int(0)

    if "tx_disponibilidade" not in st.session_state:
        st.session_state["tx_disponibilidade"] = int(0)

    if "tx_ocupacao" not in st.session_state:
        st.session_state["tx_ocupacao"] = int(0)

    # carrega no widget ao entrar na página
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

    st.write(f"Dias na semana: {st.session_state["dias_semana"]}")
    st.write(f"Taxa de disponibilidade: {st.session_state["tx_disponibilidade"]} %")
    st.write(f"tx_ocupacao: {st.session_state["tx_ocupacao"]} %")