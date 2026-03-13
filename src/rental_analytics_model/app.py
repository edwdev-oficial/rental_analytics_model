import streamlit as st
import pandas as pd
import pdfplumber
import hashlib
import re

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


        recibos = []

        for arquivo in arquivos_unicos.values():
            linhas = []
            with pdfplumber.open(arquivo) as pdf:
                for pagina in pdf.pages:
                    text = pagina.extract_text()
                    if text:
                        linhas.extend(text.splitlines())


            # region resumo dos recibos
            id = linhas[utils.get_index(linhas, 'Número cliente')].split(' ')[2]
            razao_social = linhas[utils.get_index(linhas, 'Local Descarga')].split(',')
            remover = ['Local Descarga: Empresa', 'Local Descarga: ']
            razao_social = [x for x in razao_social if x not in remover][0].replace('Local Descarga: ', '').strip()
            recibo = linhas[utils.get_index(linhas, 'Recibo de Aluguel')].replace('Recibo de Aluguel ', '')
            periodo = linhas[utils.get_index(linhas, 'Período :')].replace('Período : ', '').split(' ')[0]
            valor_sem_impostos = linhas[utils.get_index(linhas, 'Valor total com impostos BRL ') - 1]
            valor_com_impostos = linhas[utils.get_index(linhas, 'Valor total com impostos BRL')].replace('Valor total com impostos BRL ', '')            
            # endregion

            # region detalhe dos recibos
            index_in = utils.get_index(linhas, 'Hilti Fleet Premium - Gestão de Frota') + 1
            index_out = utils.get_index(linhas, 'Valor total com impostos') - 1
            itens = linhas[index_in: index_out ]
            itens = [x for x in itens if x not in ['Extensão de Serviços para Novos Equipamentos']]
            
            for item in itens:

                pattern = r'^(\d+)\s+(.*?)\s+(\d{2}/\d{4}),\s+(\d+\s+Meses)\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)$'

                match = re.match(pattern, item)

                if match:
                    parsed_item = {
                        'Cust_id': id,
                        'Razão Social': razao_social,
                        'Recibo nº': recibo,
                        'Período': periodo,
                        'Valor s/imp': valor_sem_impostos,
                        'Valor c/imp': valor_com_impostos,
                        'Artigo': match.group(1),
                        'Descrição': match.group(2).strip(),
                        'Data Início': match.group(3),
                        'Período de Utilização': match.group(4),
                        'Qt.': match.group(5),
                        'Mensal s/imp': match.group(6),
                        'Subtotal s/imp': match.group(7)
                    }
                    recibos.append(parsed_item)        
            
            # endregion
                    
        df = pd.DataFrame(recibos)
        df = utils.converter_moeda_br(df, ['Valor s/imp', 'Valor c/imp', 'Subtotal s/imp', 'Mensal s/imp'])
        pos = df.columns.get_loc("Mensal s/imp") + 1
        df.insert(pos, "Mensal c/imp", df["Mensal s/imp"] / (1 - 0.0925))
        df['Subtotal c/imp'] = df['Subtotal s/imp'] / (1 - 0.0925)
        df['Data Início'] = pd.to_datetime(df['Data Início'], format='%m/%Y')
        df['Qt.'] = df['Qt.'].astype(int)

        st.dataframe(df)                    