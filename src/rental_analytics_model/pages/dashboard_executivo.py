import streamlit as st
from rental_analytics_model.services.valores_locacao import load_xlsx
from rental_analytics_model.services.data_recibos import load_data_recibos
from rental_analytics_model.services.normal_itens import load_normal_itens
from rental_analytics_model.components.dashboard_executifo import show_dash
from rental_analytics_model.utils import formaters

def show (lista_unicos, df_valores_locacao, df_contratos):

    if not len(lista_unicos):
        st.error('Carregue os arquivos...')
        st.stop()


    # st.dataframe(df_contratos)
    # total_receita = df_contratos['valor'].sum()
    # st.write(f'Receita total: {formaters.format_brl(total_receita, True)}')


    df_recibos = load_data_recibos(lista_unicos, df_valores_locacao, df_contratos)

    familias = ['']
    familias.extend(sorted(
        list(
            df_recibos[df_recibos['Tipo'] == 'Ferramenta']
            ['Linha']
            .unique()
        )
    ))
    familia = st.sidebar.selectbox(
        'Familia',
        familias,
        index=5
    )

    modelos = ['']
    modelos.extend(sorted(
        list(
            df_recibos[df_recibos['Linha'] == familia]
            ['Modelo']
            .unique()
        )
    ))

    modelo = st.sidebar.selectbox(
        'Modelo',
        modelos,
        index=0
    )

    show_dash(df_recibos, familia, modelo)

