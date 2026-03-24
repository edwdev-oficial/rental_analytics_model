import hashlib
import streamlit as st
from src.rental_analytics_model.services.valores_locacao import load_xlsx
import io

def arquivos_recebidos(arquivos):

        if 'arquivos_unicos' not in st.session_state:
            st.session_state.arquivos_unicos = {}

        for file in arquivos:
            pdf_bytes = file.getvalue()
            file_hash = hashlib.md5(pdf_bytes).hexdigest()

            if file_hash not in st.session_state.arquivos_unicos:
                st.session_state.arquivos_unicos[file_hash] = file


        lista_unicos = list(st.session_state.arquivos_unicos.values())
        # st.write(lista_unicos)

        with st.expander("Faturas Gestão de Frotas"):
            pdf_files = [f for f in lista_unicos if f.type == "application/pdf"]
            if len(pdf_files) > 0:
                abas = st.tabs([f"Recibo {lista_unicos[i].name}" for i in range(len(pdf_files))])
                for aba, file in zip(abas, pdf_files):
                    with aba:
                        st.pdf(file.getvalue(), height=900)

        with st.expander('Contratos'):
            pass
            contratos = [f for f in lista_unicos if 'contratos' in f.name]
            df_contratos = load_xlsx(contratos)
            st.dataframe(df_contratos)

        with st.expander('Valores Locação'):
    
            valores_locacao = [f for f in lista_unicos if f.name == "valores_locacao.xlsx"]
    
            df_valores_locacao = load_xlsx(valores_locacao)
            # 👇 CAPTURA O RETORNO
            df_editado = st.data_editor(
                df_valores_locacao,
                key="editor_valores_locacao"
            )

            # 👇 BOTÃO DE SALVAR
            if not df_editado.equals(df_valores_locacao):
                df_valores_locacao = df_editado
                buffer = io.BytesIO()
                df_valores_locacao.to_excel(buffer, index=False)
                buffer.seek(0)

                st.download_button(
                    label="Baixar Excel",
                    data=buffer,
                    file_name=f"valores_locacao.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        return lista_unicos, df_valores_locacao, df_contratos