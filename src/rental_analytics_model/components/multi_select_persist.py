import streamlit as st

def multiselect_persist(
    label: str,
    options: list,
    key_base: str,
    is_sidebar: bool = False
):
    persist_key = f"{key_base}_persist"
    widget_key = f"_{key_base}_widget"

    # 1. inicializa persist (default = tudo selecionado)
    if persist_key not in st.session_state:
        st.session_state[persist_key] = options.copy()

    # 2. remove valores que não existem mais
    st.session_state[persist_key] = [
        v for v in st.session_state[persist_key]
        if v in options
    ]

    # 3. inicializa widget
    if widget_key not in st.session_state:
        st.session_state[widget_key] = st.session_state[persist_key].copy()

    # 4. limpa widget também
    st.session_state[widget_key] = [
        v for v in st.session_state[widget_key]
        if v in options
    ]

    # 5. sync função
    def _sync():
        st.session_state[persist_key] = st.session_state[widget_key].copy()

    # 6. widget
    if is_sidebar:
        st.sidebar.multiselect(
            label,
            options=options,
            key=widget_key,
            on_change=_sync
        )
    else:
        st.multiselect(
            label,
            options=options,
            key=widget_key,
            on_change=_sync
        )

    # 7. retorno
    return st.session_state[persist_key]