import streamlit as st
import pandas as pd
import pdfplumber
import hashlib

from rental_analytics_model import utils

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

def app():
    st.title("Faturas Gestão de Frotas")
    st.divider()

    st.markdown("""
    <style>
    [data-testid="stFileUploader"] ul {display:none;}
    [data-testid="stFileUploader"] li {display:none;}
    </style>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Selecione os recibos de G.F.",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:

        arquivos_unicos = {}
        
        # filtra duplicados
        for file in uploaded_files:
            pdf_bytes = file.getvalue()
            file_hash = hashlib.md5(pdf_bytes).hexdigest()

            if file_hash not in arquivos_unicos:
                arquivos_unicos[file_hash] = file

        lista_unicos = list(arquivos_unicos.values())

        with st.expander("PDFs"):

            abas = st.tabs([f"Recibo {lista_unicos[i].name}" for i in range(len(lista_unicos))])

            for aba, file in zip(abas, lista_unicos):

                with aba:
                    st.write(f"**{file.name}**")
                    st.pdf(file.getvalue(), height=900)    