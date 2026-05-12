from pathlib import Path
import streamlit as st
import streamlit as st
import pandas as pd
import base64
import json

def get_project_root(index):
    return Path(__file__).resolve().parents[index]

def load_files():
    st.markdown("""
    <style>
    [data-testid="stFileUploader"] ul {display:none;}
    [data-testid="stFileUploader"] li {display:none;}
    [data-testid="stFileUploaderPagination"] {display:none;}                
    </style>
    """, unsafe_allow_html=True)

    return st.file_uploader(
        "Enviar arquivos",
        accept_multiple_files=True
    )

def load_normal_itens() -> pd.DataFrame:
    file_path = get_project_root(3) / 'data' / 'normal_itens.json'
    return pd.read_json(file_path)

def logo_hilti_base64():

    def get_base64(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    BASE_DIR = Path(__file__).parents[1]
    logo_path = BASE_DIR / 'assets' / 'logoHilti.png'
    logo_base64 = get_base64(logo_path)
    return logo_base64

def logo_hilti():

    BASE_DIR = Path(__file__).parents[1]
    return BASE_DIR / 'assets' / 'logoHilti.png'
    
def load_css():
    # css_path = Path().resolve() / 'assets' / 'style.css'
    BASE_DIR = Path(__file__).parents[1]
    css_path = BASE_DIR / 'assets' / 'style.css'
    # return css_path
    # return 'Foo'
    with open (css_path) as f:
        st.html(f'<style>{f.read()}</style>')    

def load_normal_itens_excel():

    BASE_DIR = Path(__file__).parents[1]
    return pd.read_excel(BASE_DIR/'assets'/'normal_itens.xlsx')

def loaders(file, type) -> pd.DataFrame:
    if type == 'xlsx':
        file_path = get_project_root(1) / "assets" / f"{file}.{type}"
        return pd.read_excel(file_path)
    
    if type == 'json':
        file_path = get_project_root(1) / "assets" / f"{file}.{type}"
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)