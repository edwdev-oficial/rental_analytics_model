import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from rental_analytics_model.utils import formaters

def test(sesseion_state):

    from rental_analytics_model.services.data_recibos import load_data_recibos

    st.title('Teste')
    st.divider()

    with st.expander('Sesseion State'):
        st.write(sesseion_state)

    lista_unicos = sesseion_state.files

    df_valores_locacao = sesseion_state.df_valores_locacao.copy()
    
    df_contratos = sesseion_state.df_contratos.copy()
    df_contratos['locacao'] = df_contratos['locacao'] + pd.DateOffset(years=1)
    df_contratos['devolucao'] = df_contratos['devolucao'] + pd.DateOffset(years=1)

    df_recibos = load_data_recibos(lista_unicos, df_valores_locacao, df_contratos)
    df_recibos['periodo_dt'] = pd.to_datetime(df_recibos['Período'], format='%m/%Y')

    min_date_recibos = df_recibos['periodo_dt'].min()
    max_date_recibos = (df_recibos['periodo_dt'].max() + pd.DateOffset(months=1)) - pd.DateOffset(days=1)

    #%% FILTROS
    df_contratos = df_contratos[
        (df_contratos['locacao'] >= min_date_recibos)
        &
        (df_contratos['locacao'] <= max_date_recibos)
    ].reset_index(drop=True)

    # st.write(f'min_date_recibos: {min_date_recibos} | max_date_recibos {max_date_recibos}')

    #%% SHOW DATAFRAMES
    st.write('Recibos G.F.')
    st.dataframe(df_recibos)
    st.divider()
    
    st.write('Valores Locação')
    st.dataframe(df_valores_locacao)
    st.divider()
    
    st.write('Contratos')
    st.dataframe(df_contratos)
    st.divider()

    #%% CÁLCULOS
    valor_total_recibos = df_recibos['Subtotal c/imp'].sum()
    valor_total_contratos = df_contratos['valor'].sum()
    margem_de_contribuicao = (valor_total_contratos - valor_total_recibos) / valor_total_contratos
    markup = (valor_total_contratos - valor_total_recibos ) / valor_total_recibos * 100
    lucro_bruto = valor_total_contratos - valor_total_recibos

    #%% RESUMO
    st.subheader('Resumo')
    st.write(f'Valor total dos recibos {formaters.format_brl(valor_total_recibos, True)}')
    st.write(f'Valor total de contratos: {formaters.format_brl(valor_total_contratos, True)}')
    st.write(f'Margem de contribuição: {round(margem_de_contribuicao * 100, 1)}%')
    st.write(f'Markup: {round(markup, 1)}')
    st.write(f'Lucro bruto: {formaters.format_brl(lucro_bruto, True)}')
    st.divider()

    #%% INSITE
    st.subheader('💡 Insites')
    st.html(f"""
        <div>
            <p>🔴 Ponto de equilíbrio total</p>
            <p>🔴 Ponto de equilíbrio por máquina</p>
        </div>
    """)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tx_ocupacao = 12

        fig = go.Figure(
            go.Indicator(
                mode='gauge+number',
                value=tx_ocupacao,
                title={'text': 'Taxa de ocupação % Break Even'},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"thickness": 0.3},
                    "steps": [
                        {"range": [0, 12], "color": "red"},
                        {"range": [12, 55], "color": "#a6a6a6"},
                        {"range": [55, 100], "color": "#595959"},
                    ],
                    "threshold": {
                        "line": {"color": "yellow", "width": 4},
                        "thickness": 0.8,
                        "value": 12
                    }
                }
            )
        )

        # with st.container(border=True):
        st.plotly_chart(fig, key='gauge')
    
    
    with col2:
        tx_ocupacao = 60

        fig = go.Figure(
            go.Indicator(
                mode='gauge+number',
                value=tx_ocupacao,
                title={'text': 'Taxa de ocupação % Efetiva'},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"thickness": 0.3},
                    "steps": [
                        {"range": [0, 12], "color": "#d9d9d9"},
                        {"range": [12, 55], "color": "#a6a6a6"},
                        {"range": [55, 100], "color": "#595959"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.8,
                        "value": 12
                    }
                }
            )
        )

        # with st.container(border=True):
        st.plotly_chart(fig, key='gauge2')