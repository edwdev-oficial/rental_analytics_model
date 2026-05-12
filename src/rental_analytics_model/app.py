import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from rental_analytics_model.utils.loaders import logo_hilti_base64
from rental_analytics_model.services.data_recibos import load_data_recibos

def app():     
    # ==========================================
    # region Session State
    # ==========================================
    if "files" not in st.session_state:
        st.session_state.files = []
    if "df_pq_maquinas" not in st.session_state:
        st.session_state.df_pq_maquinas = None     
    if "df_valores_locacao" not in st.session_state:
        st.session_state.df_valores_locacao = None
    if "df_contratos" not in st.session_state:
        st.session_state.df_contratos = None
    if 'df_recibos' not in st.session_state:
        st.session_state.df_recibos = pd.DataFrame()   
    if 'df_ams_dash' not in st.session_state:
        st.session_state.df_ams_dash = pd.DataFrame()             
    # ==========================================
    # endregion

    # ==========================================
    # region Funções de Carregamento das Páginas
    # ==========================================
    def carregar_dados():
        pass
        from rental_analytics_model.pages import carregar_dados
        lista_unicos, df_pq_maquinas, df_valores_locacao, df_contratos, df_ams_dash = carregar_dados.show()
        if lista_unicos is not None:
            st.session_state.files = lista_unicos
            st.session_state.df_pq_maquinas = df_pq_maquinas
            st.session_state.df_valores_locacao = df_valores_locacao
            st.session_state.df_contratos = df_contratos
            st.session_state.df_recibos = load_data_recibos(lista_unicos, df_valores_locacao)
            # st.session_state.df_ams_dash = df_ams_dash
            
    def configuracoes():
        from rental_analytics_model.pages import configuracoes
        configuracoes.show()

    def taxa_ocupacao():
        from rental_analytics_model.pages import taxa_ocupacao
        taxa_ocupacao.show(
            st.session_state.df_pq_maquinas,
            st.session_state.df_valores_locacao,
            st.session_state.df_contratos
        )
    def indicadores_chaves():
        from rental_analytics_model.pages import indicadores_chaves
        indicadores_chaves.show()

    def dashboard_executivo():
        from rental_analytics_model.pages import dashboard_executivo
        dashboard_executivo.show(
            st.session_state.files,
            st.session_state.df_pq_maquinas,
            st.session_state.df_valores_locacao,
            st.session_state.df_contratos
        )
    def test_dev():
        from rental_analytics_model.pages import teste_dev
        teste_dev.test(st.session_state)
    # ==========================================
    # endregion

    # ==========================================
    # region Menu lateral
    # ==========================================
    with st.sidebar:
        selected = option_menu(
            "Menu",
            [
                "Carregar Dados",
                "Configurações",
                # "Taxa de Ocupação",
                "Indicadores Chaves",
                "Dashboard Executivo",
                # "---",
                # "Teste Dev"
            ],
            icons=[
                "database-fill-down",
                "gear-fill",
                # "bar-chart-fill",
                "file-earmark-bar-graph-fill",
                "speedometer",
                # None,
                # "tools"
                ""
            ],
            default_index=0
        )
    # ==========================================
    # endregion

    # ==========================================
    # region Header
    # ==========================================
    logo_base64 = logo_hilti_base64()   
    st.markdown(
        f"""
        <div class="header-container">
            <img src="data:image/png;base64,{logo_base64}">
            <div class="header-title">
                Rental Analytics Model
                <p>{selected}<p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # ==========================================
    # endregion

    # ==========================================
    # region Roteador de páginas
    # ==========================================
    pages = {
        "Carregar Dados": carregar_dados,
        "Configurações": configuracoes,
        "Taxa de Ocupação": taxa_ocupacao,
        "Indicadores Chaves": indicadores_chaves,
        "Dashboard Executivo": dashboard_executivo,
        "Teste Dev": test_dev
    }
    # ==========================================
    # endregion

    # ==========================================
    # region Execução da página selecionada
    # ==========================================
    pages[selected]()
    # ==========================================
    # endregion
