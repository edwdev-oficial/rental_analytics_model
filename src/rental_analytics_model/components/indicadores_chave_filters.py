import streamlit as st

def _resetar_ano_reparo_familia_modelo_idades():
    st.session_state["mp_ano_reparo"] = ""
    st.session_state["mp_ano_reparo_max"] = ""
    st.session_state["mp_familia"] = ""
    st.session_state["mp_modelo"] = ""
    st.session_state["mp_idade_minima"] = ""
    st.session_state["mp_idade_maxima"] = ""


def _resetar_ano_reparo_max_familia_modelo_idades():
    st.session_state["mp_ano_reparo_max"] = ""
    st.session_state["mp_familia"] = ""
    st.session_state["mp_modelo"] = ""
    st.session_state["mp_idade_minima"] = ""
    st.session_state["mp_idade_maxima"] = ""

def _resetar_familia_modelo_idades():
    st.session_state["mp_familia"] = ""
    st.session_state["mp_modelo"] = ""
    st.session_state["mp_idade_minima"] = ""
    st.session_state["mp_idade_maxima"] = ""


def _resetar_modelo_idades():
    st.session_state["mp_modelo"] = ""
    st.session_state["mp_idade_minima"] = ""
    st.session_state["mp_idade_maxima"] = ""


def _resetar_idades():
    st.session_state["mp_idade_minima"] = ""
    st.session_state["mp_idade_maxima"] = ""


def _resetar_idade_maxima():
    st.session_state["mp_idade_maxima"] = ""


def render_filtros_sidebar_dependentes(service, df_base) -> dict:
    
    hierarquias = service.listar_hierarquias(df_base)
    hierarquia = st.sidebar.selectbox(
        "Hierarquia",
        hierarquias,
        key="mp_hierarquia",
        # on_change=_resetar_familia_modelo_idades,
        on_change=_resetar_ano_reparo_familia_modelo_idades,
    )



    container = st.sidebar.container(border=True)

    with container:
        st.write("Ano reparo")

        col1, col2 = st.columns(2)

        anos_reparo = service.listar_anos_reparo_por_hierarquia(
            df_base=df_base,
            hierarquia=hierarquia,
        )

        if st.session_state.get("mp_ano_reparo") not in anos_reparo:
            st.session_state["mp_ano_reparo"] = ""

        with col1:
            ano_reparo = st.selectbox(
                "De",
                anos_reparo,
                key="mp_ano_reparo",
                on_change=_resetar_ano_reparo_max_familia_modelo_idades
            )

        anos_raparo_max = service.listar_anos_reparo_max_por_filtro(
            df_base=df_base,
            hierarquia=hierarquia,
            ano_reparo=ano_reparo
        )

        if st.session_state.get("mp_ano_reparo_max") not in anos_raparo_max:
            st.session_state["mp_ano_reparo_max"] = ""

        with col2:
            ano_reparo_max = st.selectbox(
                "Até",
                anos_raparo_max,
                key="mp_ano_reparo_max",
                on_change=_resetar_familia_modelo_idades
            )

    familias = service.listar_familias_por_filtros(
        df_base=df_base,
        hierarquia=hierarquia,
        ano_reparo=ano_reparo,
        ano_reparo_max=ano_reparo_max
    )

    if st.session_state.get("mp_familia", "") not in familias:
        st.session_state["mp_familia"] = ""

    familia = st.sidebar.selectbox(
        "Família",
        familias,
        key="mp_familia",
        on_change=_resetar_modelo_idades,
    )


    modelos = service.listar_modelos_por_filtros(
        df_base=df_base,
        hierarquia=hierarquia,
        ano_reparo=ano_reparo,
        familia=familia,
    )
    if st.session_state.get("mp_modelo", "") not in modelos:
        st.session_state["mp_modelo"] = ""

    modelo = st.sidebar.selectbox(
        "Modelo",
        modelos,
        key="mp_modelo",
        on_change=_resetar_idades,
    )

    container_idade = st.sidebar.container(border=True)

    with container_idade:

        st.write('Idade')

        col1, col2 = st.columns(2)

        idades_minimas = service.listar_idades_por_filtros(
            df_base=df_base,
            hierarquia=hierarquia,
            ano_reparo=ano_reparo,
            ano_reparo_max=ano_reparo_max,
            familia=familia,
            modelo=modelo,
        )
        if st.session_state.get("mp_idade_minima", "") not in idades_minimas:
            st.session_state["mp_idade_minima"] = ""

        with col1:
            idade_minima = st.selectbox(
                "De",
                idades_minimas,
                key="mp_idade_minima",
                on_change=_resetar_idade_maxima,
            )

        idades_maximas = service.listar_idades_maximas_por_filtros(
            df_base=df_base,
            hierarquia=hierarquia,
            ano_reparo=ano_reparo,
            familia=familia,
            modelo=modelo,
            idade_minima=idade_minima,
        )
        if st.session_state.get("mp_idade_maxima", "") not in idades_maximas:
            st.session_state["mp_idade_maxima"] = ""

        with col2:
            idade_maxima = st.selectbox(
                "Até",
                idades_maximas,
                key="mp_idade_maxima",
            )

    return {
        "hierarquia": hierarquia,
        "ano_reparo": ano_reparo,
        "ano_reparo_max": ano_reparo_max,
        "familia": familia,
        "modelo": modelo,
        "idade_minima": idade_minima,
        "idade_maxima": idade_maxima,
    }