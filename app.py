import streamlit as st
from rental_analytics_model.app import app

st.set_page_config(
    page_title="Rental Analytics Model",
    page_icon="🟢",
    layout='wide'
)

st.markdown("""
<style>
.block-container {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# region ocultar menu footer e header
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# endregion

app()