import streamlit as st
from rental_analytics_model.app import app
from rental_analytics_model.utils.loaders import logo_hilti_base64

from src.rental_analytics_model.utils import loaders

# =========================================================
# region Page Config
# =========================================================
st.set_page_config(
    page_title="Rental Analytics Model",
    page_icon="🟢",
    layout='wide',
    initial_sidebar_state='expanded'
)
# endregion

loaders.load_css()

app()