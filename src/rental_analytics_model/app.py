import streamlit as st
import pandas as pd
import pdfplumber
import hashlib
import re

from rental_analytics_model.utils.loaders import load_normal_itens
from rental_analytics_model.utils.formaters import format_brl
from rental_analytics_model.utils.formaters import convert_moeda_br_str_to_number
from rental_analytics_model.utils.get_index import get_index
from rental_analytics_model.utils.formaters import convert_col_df_moeda_br_str_to_number
from rental_analytics_model.utils.loaders import logo_hilti_base64
from rental_analytics_model.utils.loaders import logo_hilti

def app():

    # region header
    logo_base64 = logo_hilti_base64()   
    st.markdown(
        f"""
        <style>
        .header-container {{
            display: flex;
            aling-itens: center;
            justify-content: space-between;
            margin-bottom: 0;
            padding: 0;
        }}

        .header-container img {{
            height: 60px;
            object-fit: cover; /* Cobre todo o espaço, mantendo proporção (pode cortar) */
            /* object-fit: contain; /* A imagem fica toda visível, sem cortar */#           
        }}

        .header-title {{
            font-size: 2rem;
            font-weight: 700;
            color: #3c3f4a;
            text-align: right;
        }}
        </style>

        <div class="header-container">
            <img src="data:image/png;base64,{logo_base64}">
            <div class="header-title">Rental Analytics Model</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # endregion

    # region normal_itens
    df_normal_itens = load_normal_itens()
    # endregion

    # region uploaded_files
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
    # endregion

    if uploaded_files:

        valor_total_recibos = 0
        arquivos_unicos = {}
        
        # filtra duplicados
        for file in uploaded_files:
            pdf_bytes = file.getvalue()
            file_hash = hashlib.md5(pdf_bytes).hexdigest()

            if file_hash not in arquivos_unicos:
                arquivos_unicos[file_hash] = file

        lista_unicos = list(arquivos_unicos.values())

        with st.expander("PDFs recibos"):

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
            id = linhas[get_index(linhas, 'Número cliente')].split(' ')[2]
            razao_social = linhas[get_index(linhas, 'Local Descarga')].split(',')
            remover = ['Local Descarga: Empresa', 'Local Descarga: ']
            razao_social = [x for x in razao_social if x not in remover][0].replace('Local Descarga: ', '').strip()
            recibo = linhas[get_index(linhas, 'Recibo de Aluguel')].replace('Recibo de Aluguel ', '')
            periodo = linhas[get_index(linhas, 'Período :')].replace('Período : ', '').split(' ')[0]
            valor_sem_impostos = linhas[get_index(linhas, 'Valor total com impostos BRL ') - 1]
            valor_com_impostos = linhas[get_index(linhas, 'Valor total com impostos BRL')].replace('Valor total com impostos BRL ', '')
            valor_com_impostos_float = convert_moeda_br_str_to_number(valor_com_impostos)
            valor_total_recibos += valor_com_impostos_float
            # endregion

            # region detalhe dos recibos
            index_in = get_index(linhas, 'Hilti Fleet Premium - Gestão de Frota') + 1
            index_out = get_index(linhas, 'Valor total com impostos') - 1
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
                    
        df_recibos = pd.DataFrame(recibos)

        df_recibos = df_recibos.merge(
            df_normal_itens[['Descrição', 'Tipo', 'Linha', 'Modelo']],
            on='Descrição',
            how='left'
        )


        df_recibos = convert_col_df_moeda_br_str_to_number(df_recibos, ['Valor s/imp', 'Valor c/imp', 'Subtotal s/imp', 'Mensal s/imp'])
        pos = df_recibos.columns.get_loc("Mensal s/imp") + 1
        df_recibos.insert(pos, "Mensal c/imp", round(df_recibos["Mensal s/imp"] / (1 - 0.0925), 2))
        df_recibos['Subtotal c/imp'] = df_recibos['Subtotal s/imp'] / (1 - 0.0925)
        df_recibos['Data Início'] = pd.to_datetime(df_recibos['Data Início'], format='%m/%Y')
        df_recibos['Qt.'] = df_recibos['Qt.'].astype(int)
        
        # st.dataframe(df_recibos)

        df_tipo_group = (
            df_recibos.groupby('Tipo', as_index=False)
                .agg({
                    'Qt.': 'sum',
                    'Subtotal c/imp': 'sum'
                })
        )

        familias = ['']
        familias.extend(sorted(
            list(
                df_recibos[df_recibos['Tipo'] == 'Ferramenta']
                ['Linha']
                .unique()
            )
        ))

        familia = st.selectbox('Familia', familias)
            
        df_group_filter_by_linha = (
        df_recibos[df_recibos['Linha'].str.contains(familia, na=False)]
            .groupby('Modelo', as_index=False)
            .agg({
                'Qt.': 'sum',
                'Subtotal c/imp': 'sum'
            })
        ).sort_values('Subtotal c/imp', ascending=False)

        df_group_filter_by_linha_show = df_group_filter_by_linha.copy()

        df_group_filter_by_linha_show["Subtotal c/imp"] = (
            df_group_filter_by_linha_show["Subtotal c/imp"].apply(format_brl)
        )

        st.dataframe(
            df_group_filter_by_linha_show,
            column_config={
                'Subtotal c/imp': {'alignment':"right"}
            }
        )

        df_group_filter_by_linha = df_group_filter_by_linha['Subtotal c/imp'].sum()
        st.write(df_group_filter_by_linha)

     
