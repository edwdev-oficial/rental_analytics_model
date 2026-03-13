import streamlit as st
from rental_analytics_model.app import app

st.set_page_config(
    page_title="Rental Analytics Model",
    page_icon="🟢",
    layout='wide'
)

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