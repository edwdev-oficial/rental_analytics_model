import streamlit as st
from streamlit_option_menu import option_menu
from rental_analytics_model.utils.loaders import logo_hilti_base64

def app():     
    # ==========================================
    # region Session State
    # ==========================================
    if "files" not in st.session_state:
        st.session_state.files = []
    if "df_valores_locacao" not in st.session_state:
        st.session_state.df_valores_locacao = None
    if "df_contratos" not in st.session_state:
        st.session_state.df_contratos = None
    # ==========================================
    # endregion

    # ==========================================
    # region Funções de Carregamento das Páginas
    # ==========================================
    def carregar_dados():
        from rental_analytics_model.pages import carregar_dados
        files, df_valores_locacao, df_contratos = carregar_dados.show(st.session_state.files)
        if files is not None:
            st.session_state.files = files
            st.session_state.df_valores_locacao = df_valores_locacao
            st.session_state.df_contratos = df_contratos

    def configuracoes():
        from rental_analytics_model.pages import configuracoes
        configuracoes.show()

    def dashboard_executivo():
        from rental_analytics_model.pages import dashboard_executivo
        dashboard_executivo.show(
            st.session_state.files,
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
                "Dashboard Executivo",
                "---",
                "Teste Dev"
            ],
            icons=[
                "database-fill-down",
                "gear-fill",
                "speedometer",
                None,
                "tools"
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
