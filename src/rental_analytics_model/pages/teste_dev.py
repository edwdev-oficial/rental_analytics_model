# ========================================================
# region IMPORTS
# ========================================================
import math
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

from rental_analytics_model.utils import formaters
from rental_analytics_model.services.data_recibos import load_data_recibos

# endregion
# ========================================================

def test(session_state):

    from rental_analytics_model.services.data_recibos import load_data_recibos
    from rental_analytics_model.services.calcular_periodos import calcular_periodos_df
    from rental_analytics_model.services.calculos import calcular_faturamento_frota
    from rental_analytics_model.services.calcular_valor import calcular_valor
    from rental_analytics_model.utils import loaders
    from rental_analytics_model.utils import formaters

    # ========================================================
    # region TITLE
    # ========================================================
    st.title('Teste')

    with st.expander('Sesseion State'):
        st.write(st.session_state)

    st.divider()
    # endregion
    # ========================================================

    # ========================================================
    # region GAUGE_GRAPH
    # ========================================================
    def gauge_graph():
        lista_unicos = session_state.files

        df_valores_locacao = session_state.df_valores_locacao.copy()
        
        df_contratos = session_state.df_contratos.copy()
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

        valor_gf = st.session_state.valor_gf
        # valor_gf = 300000
        potencial_tot_faturamento = st.session_state.potencial_total_faturamento
        tx_disp = st.session_state.tx_disponibilidade / 100
        st.write(f'Valor G.F.: {formaters.format_brl(valor_gf)}')
        st.write(f'Potencial total de faturamento: {formaters.format_brl(potencial_tot_faturamento)}')
        st.write(f'Taxa de disponibilidade: {tx_disp * 100}%')

        tx_ocup_mark_up = (valor_gf / potencial_tot_faturamento / tx_disp) * 100
        st.write(f'Taxa ocupação mínima para mark up: {round(tx_ocup_mark_up, 1)}%')

        col1, col2, col3, col4 = st.columns(4)


        with col1:
            tx_ocupacao = tx_ocup_mark_up

            fig = go.Figure(
                go.Indicator(
                    mode='gauge+number',
                    value=tx_ocupacao,
                    title={'text': 'Taxa de ocupação % Break Even'},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"thickness": 0.22},
                        "steps": [
                            {"range": [0, tx_ocupacao], "color": "#d2051e"},
                            {"range": [tx_ocupacao, 55], "color": "rgba(82, 79, 83, 0.2)"},
                            {"range": [55, 100], "color": "rgba(82, 79, 83, 0.6)"},
                        ],
                        "threshold": {
                            "line": {"color": "yellow", "width": 1},
                            "thickness": 0.5,
                            "value": tx_ocupacao
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
                        "bar": {"thickness": 0.22},
                        "steps": [
                            {"range": [0, 12], "color": "#d2051e"},
                            {"range": [12, 55], "color": "rgba(82, 79, 83, 0.2)"},
                            {"range": [55, 100], "color": "rgba(82, 79, 83, 0.6)"},
                        ],
                        "threshold": {
                            "line": {"color": "yellow", "width": 1},
                            "thickness": 0.5,
                            "value": 12
                        }
                    }
                )
            )

            # with st.container(border=True):
            st.plotly_chart(fig, key='gauge2')
    
    # endregion
    # ========================================================
    # gauge_graph()

    # ========================================================
    # region TAXA_OCUPACAO
    # ========================================================
    def taxa_ocupacao(session_state):

        st.subheader('Teste Taxa Ocupação', divider='red')
        
        # ========================================================
        # region RECIBOS
        # ========================================================
        df_recibos = session_state.df_recibos.copy()
        df_recibos.rename(columns={'Linha': 'familia', 'Modelo': 'modelo'}, inplace=True)
        # df_recibos = df_recibos[df_recibos['familia'] == 'Rompedor']
        df_recibos['periodo'] = pd.to_datetime(df_recibos['Período']).dt.to_period('M')
        df_recibos_group = (
            df_recibos
            .groupby(['periodo','familia', 'modelo'], as_index=False)
            .agg({
                'Qt.': 'sum',
                'Subtotal c/imp': 'sum'
            })
        )
        st.write('Recibos agrupados')
        st.dataframe(df_recibos_group)
        st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region VALORES LOCACAO
        # ========================================================
        
        df_valores_locacao = st.session_state.df_valores_locacao.copy()
        df_valores_locacao.rename(columns={
                'Modelo': 'modelo',
                'dia': 'p_dia',
                'semana': 'p_semana',
                'quinzena': 'p_quinzena',
                'mes': 'p_mes'
            }, inplace=True)
        # st.write('Valores Locação')
        # st.dataframe(df_valores_locacao)
        # st.divider()
        # endregion
        # ========================================================

        # ========================================================
        # region CONTRATOS
        # ========================================================
        df_contratos = session_state.df_contratos.copy()
        df_contratos = calcular_periodos_df(df_contratos)
        df_contratos['periodo'] = pd.to_datetime(df_contratos['locacao']).dt.to_period('M')


        # st.write('Contratos')
        # st.dataframe(df_contratos)

        df_contratos_group = (df_contratos
            .groupby(['periodo', 'familia', 'modelo'], as_index=False)
            .agg({
                'dias': 'sum',
                'dia': 'sum',
                'quinzena': 'sum',
                'semana': 'sum',
                'mes':'sum',
            })
        )

        # ========================================================
        # region FILTER
        # ========================================================
        periodos = df_contratos_group['periodo'].unique().tolist()
        familias = sorted(df_contratos_group['familia'].unique().tolist())
        modelos = sorted(df_contratos_group['modelo'].unique().tolist())
        col1, col2, col3 = st.columns(3)
        with col1:
            periodos_selected = st.multiselect(
                'Periodos',
                options=periodos
            )
        with col2:
            familias_selected = st.multiselect(
                'Familias',
                options=familias
            )
        with col3:
            modelos_selected = st.multiselect(
                'Modelos',
                options=modelos
            )
        df_contratos_group = df_contratos_group[
                (df_contratos_group['periodo'].isin(periodos_selected))
                &
                (df_contratos_group['familia'].isin(familias_selected))
                &
                (df_contratos_group['modelo'].isin(modelos_selected))
            ]        
        # endregion
        # ========================================================        


        df_contratos_group = pd.merge(
            df_contratos_group, 
            df_recibos_group,
            on=['periodo', 'familia', 'modelo'],
            how='left',

        )

        df_contratos_group['dias_no_periodo'] = df_contratos_group['periodo'].dt.days_in_month
        df_contratos_group['dias_possiveis'] =  df_contratos_group['dias_no_periodo'] * df_contratos_group['Qt.']
        df_contratos_group['tx_disp'] = session_state.tx_disponibilidade / 100
        df_contratos_group['tx_ocupacao'] = df_contratos_group['dias'] / df_contratos_group['dias_possiveis']
        df_contratos_group['total_contratos'] = df_contratos_group[['dia', 'semana', 'quinzena', 'mes']].sum(axis=1)
        df_contratos_group['mix_dia'] = df_contratos_group['dia'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_semana'] = df_contratos_group['semana'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_quinzena'] = df_contratos_group['quinzena'] / df_contratos_group['total_contratos']
        df_contratos_group['mix_mes'] = df_contratos_group['mes'] / df_contratos_group['total_contratos']
        df_contratos_group['sum_mix'] = (
            df_contratos_group['mix_dia']
            +
            df_contratos_group['mix_semana'] * 7
            +
            df_contratos_group['mix_quinzena'] * 15
            +
            df_contratos_group['mix_mes'] * 30
        )
        df_contratos_group['dias_possiveis/sum_mix'] = df_contratos_group['dias_possiveis'] / df_contratos_group['sum_mix']
        df_contratos_group['dias_real/sum_mix'] = df_contratos_group['dias'] / df_contratos_group['sum_mix']
          
        df_contratos_group['fator_dias_pot'] = df_contratos_group['mix_dia'] * df_contratos_group['dias_possiveis/sum_mix']
        df_contratos_group['fator_semanas_pot'] = df_contratos_group['mix_semana'] * df_contratos_group['dias_possiveis/sum_mix']
        df_contratos_group['fator_quinzenas_pot'] = df_contratos_group['mix_quinzena'] * df_contratos_group['dias_possiveis/sum_mix']
        df_contratos_group['fator_meses_pot'] = df_contratos_group['mix_mes'] * df_contratos_group['dias_possiveis/sum_mix']
        
        df_contratos_group['fator_dias_real'] = df_contratos_group['mix_dia'] * df_contratos_group['dias_real/sum_mix']
        df_contratos_group['fator_semanas_real'] = df_contratos_group['mix_semana'] * df_contratos_group['dias_real/sum_mix']
        df_contratos_group['fator_quinzenas_real'] = df_contratos_group['mix_quinzena'] * df_contratos_group['dias_real/sum_mix']
        df_contratos_group['fator_meses_real'] = df_contratos_group['mix_mes'] * df_contratos_group['dias_real/sum_mix']
        # df_contratos_group['fator_meses_real'] = df_contratos_group['mix_mes'] * df_contratos_group['sum_mix / dias']



        df_contratos_group = pd.merge(
            df_contratos_group,
            df_valores_locacao,
            on=['modelo'],
            how='left'
        )

        # df_contratos_group['pot_dia'] = df_contratos_group['p_dia'] * df_contratos_group['fator_dias_pot']
        # df_contratos_group['pot_semana'] = df_contratos_group['p_semana'] * df_contratos_group['fator_semanas_pot']
        # df_contratos_group['pot_quinzena'] = df_contratos_group['p_quinzena'] * df_contratos_group['fator_quinzenas_pot']
        # df_contratos_group['pot_mes'] = df_contratos_group['p_mes'] * df_contratos_group['fator_meses_pot']
        # df_contratos_group['potencial_total'] = df_contratos_group[['pot_dia', 'pot_semana', 'pot_quinzena', 'pot_mes']].sum(axis=1)

        # df_contratos_group['real_dia'] = df_contratos_group['p_dia'] * df_contratos_group['fator_dias_real']
        # df_contratos_group['real_semana'] = df_contratos_group['p_semana'] * df_contratos_group['fator_semanas_real']
        # df_contratos_group['real_quinzena'] = df_contratos_group['p_quinzena'] * df_contratos_group['fator_quinzenas_real']
        # df_contratos_group['real_mes'] = df_contratos_group['p_mes'] * df_contratos_group['fator_meses_real']
        # df_contratos_group['real_total'] = df_contratos_group[['real_dia', 'real_semana', 'real_quinzena', 'real_mes']].sum(axis=1)

        df_contratos_group['mix_fat_dia'] = df_contratos_group['dia'] / df_contratos_group['dias']
        df_contratos_group['mix_fat_semana'] = df_contratos_group['semana'] * 7 / df_contratos_group['dias']
        df_contratos_group['mix_fat_quinzena'] = df_contratos_group['quinzena'] * 15 / df_contratos_group['dias']
        df_contratos_group['mix_fat_mes'] = df_contratos_group['mes'] * 30 / df_contratos_group['dias']

        df_contratos_group['pot_dia'] = df_contratos_group['p_dia'] * df_contratos_group['dias_possiveis'] * df_contratos_group['mix_fat_dia']
        df_contratos_group['pot_semana'] = df_contratos_group['p_semana'] * df_contratos_group['dias_possiveis'] / 7 * df_contratos_group['mix_fat_semana']
        df_contratos_group['pot_quinzena'] = df_contratos_group['p_quinzena'] * df_contratos_group['dias_possiveis'] / 15 * df_contratos_group['mix_fat_quinzena']
        df_contratos_group['pot_mes'] = df_contratos_group['p_mes'] * df_contratos_group['dias_possiveis'] / 30 * df_contratos_group['mix_fat_mes']
        df_contratos_group['pot_total'] = df_contratos_group[['pot_dia', 'pot_semana', 'pot_quinzena', 'pot_mes']].sum(axis=1)

        df_contratos_group['real_dia'] = df_contratos_group['dia'] * df_contratos_group['p_dia']
        df_contratos_group['real_semana'] = df_contratos_group['semana'] * df_contratos_group['p_semana']
        df_contratos_group['real_quinzena'] = df_contratos_group['quinzena'] * df_contratos_group['p_quinzena']
        df_contratos_group['real_mes'] = df_contratos_group['mes'] * df_contratos_group['p_mes']
        df_contratos_group['real_total'] = df_contratos_group[['real_dia', 'real_semana', 'real_quinzena', 'real_mes']].sum(axis=1)
        
        df_contratos_group.rename(columns={'Subtotal c/imp': 'Custo G.F.'}, inplace=True)

        st.write('Contratos Agrupados')
        st.dataframe(
            df_contratos_group[[
                'familia',
                'modelo',
                'periodo',
                'Custo G.F.',
                'dias_no_periodo',
                'Qt.',
                'dias_possiveis',
                'dias',
                'dia',
                'semana',
                'quinzena',
                'mes',
                'tx_disp',
                'tx_ocupacao',
                'p_dia',
                'p_semana',
                'p_quinzena',
                'p_mes',
                'mix_fat_dia',
                'mix_fat_semana',
                'mix_fat_quinzena',
                'mix_fat_mes',
                'pot_dia',
                'pot_semana',   
                'pot_quinzena',
                'pot_mes',
                'pot_total',
                'real_dia',
                'real_semana',
                'real_quinzena',
                'real_mes',
                'real_total'
            ]]
        )



        df_pot_total = df_contratos_group[[
            'Custo G.F.',
            'dias_possiveis',
            'dias',
            'dia',
            'semana',
            'quinzena',
            'mes'
        ]].sum(skipna=True).to_frame().T

        # st.dataframe(df_pot_total)

        df_pot_total['tx_ocupacao'] = df_pot_total['dias'] / df_pot_total['dias_possiveis']
        df_pot_total['preco_dia'] = df_contratos_group['p_dia'].mean()
        df_pot_total['preco_semana'] = df_contratos_group['p_semana'].mean()
        df_pot_total['preco_quinzena'] = df_contratos_group['p_quinzena'].mean()
        df_pot_total['preco_mes'] = df_contratos_group['p_mes'].mean()
        df_pot_total['mix_fat_dia'] = df_pot_total['dia'] / df_pot_total['dias']
        df_pot_total['mix_fat_semana'] = df_pot_total['semana'] * 7 / df_pot_total['dias']
        df_pot_total['mix_fat_quinzena'] = df_pot_total['quinzena'] * 15 / df_pot_total['dias']
        df_pot_total['mix_fat_mes'] = df_pot_total['mes'] * 30 / df_pot_total['dias']
        df_pot_total['pot_dia'] = df_pot_total['preco_dia'] * df_pot_total['dias_possiveis'] * df_pot_total['mix_fat_dia'] 
        df_pot_total['pot_semana'] = df_pot_total['preco_semana'] * df_pot_total['dias_possiveis'] / 7 * df_pot_total['mix_fat_semana'] 
        df_pot_total['pot_quinzena'] = df_pot_total['preco_quinzena'] * df_pot_total['dias_possiveis'] / 15 * df_pot_total['mix_fat_quinzena'] 
        df_pot_total['pot_mes'] = df_pot_total['preco_mes'] * df_pot_total['dias_possiveis'] / 30 * df_pot_total['mix_fat_mes'] 
        df_pot_total['pot_total'] = df_pot_total[['pot_dia', 'pot_semana', 'pot_quinzena', 'pot_mes']].sum(axis=1)
        df_pot_total['real_total'] = df_pot_total['pot_total'] * df_pot_total['tx_ocupacao']

        st.dataframe(df_pot_total)


        st.divider()

        df_resumo = df_pot_total[['Custo G.F.', 'pot_total', 'tx_ocupacao', 'real_total']].sum(skipna=True).to_frame().T
        # df_resumo['ocup x pot'] = df_resumo['tx_ocupacao'] * df_resumo['pot_total']
        df_resumo['Markup'] = df_resumo['real_total'] / df_resumo['Custo G.F.']
        df_resumo['Margem'] = (df_resumo['real_total'] - df_resumo['Custo G.F.']) / df_resumo['real_total'] * 100

        def br_num(x, casas=2):
            s = f"{x:,.{casas}f}"
            return s.replace(",", "X").replace(".", ",").replace("X", ".")

        df_exibir = df_resumo.copy()
        df_exibir["tx_ocupacao"] = df_exibir["tx_ocupacao"] * 100
        df_exibir['Break Even'] = df_exibir['Custo G.F.'] / df_exibir['pot_total'] * 100
        df_exibir["Break Even"] = df_exibir["Break Even"].map(lambda x: f'{formaters.br_num(x, 2)}%')
        df_exibir["Margem"] = df_exibir["Margem"].map(lambda x: f'{formaters.br_num(x, 2)}%')
        df_exibir["tx_ocupacao"] = df_exibir["tx_ocupacao"].map(lambda x: f'{formaters.br_num(x, 2)}%')
        df_exibir['Custo G.F.'] = df_exibir['Custo G.F.'].map(lambda x: formaters.br_num(x, 2))
        df_exibir['Markup'] = df_exibir['Markup'].map(lambda x: formaters.br_num(x, 2))
        df_exibir['pot_total'] = df_exibir['pot_total'].map(lambda x: formaters.br_num(x, 2))
        df_exibir['real_total'] = df_exibir['real_total'].map(lambda x: formaters.br_num(x, 2))

        df_exibir.rename(columns={
                'real_total': 'Faturamento',
                'pot_total': 'Potencial',
                'tx_ocupacao': 'Tx Ocupação'
            },
            inplace=True
        )

        df_exibir = df_exibir[['Custo G.F.', 'Potencial', 'Break Even', 'Tx Ocupação', 'Faturamento', 'Markup', 'Margem' ]]

        st.write('Resumo dos resultados')
        st.dataframe(
            df_exibir,
            hide_index=True,
            use_container_width=True
        )

        # # # endregion
        # # # ========================================================

        # # # st.write(df_contratos_group.dtypes)


        # # # # calculos
        # # # qtd_maquinas = df_qtd_by_linha_modelo['Qt.'].sum()
        # # # date_start = df_contratos['locacao'].min()
        # # # date_end = df_contratos['locacao'].max()
        # # # qtd_meses = (date_end.year - date_start.year) * 12 + (date_end.month - date_start.month) + 1
        # # # dias_uteis = qtd_meses * 26
        # # # capacidade_total = qtd_maquinas * dias_uteis
        # # # disponibilidade = .8
        # # # capacidade_disponivel = capacidade_total * disponibilidade
        # # # dias_locados = df_contratos['dias'].sum()
        # # # tx_ocupacao = dias_locados / capacidade_disponivel

        # # # st.subheader('Resumo')
        # # # st.write(f'Qtd máquinas: {qtd_maquinas}')
        # # # st.write(f'Dias úteis: {dias_uteis}')
        # # # st.write(f'Capacidade total: {capacidade_total}')
        # # # st.write(f'Disponibilidade: {disponibilidade * 100}%')
        # # # st.write(f'Capacidade disponível: {capacidade_disponivel}')
        # # # st.write(f'Taxa de ocupação: {tx_ocupacao * 100}%')

        # # # st.write(f'Total de período em dias: {total_periodo_dias}')

    # endregion
    # ========================================================
    taxa_ocupacao(session_state)

    # ========================================================
    # region FILTER_TEST
    # ========================================================
    def filter_test():
        
        itens = [
            {'name': 'abc'},
            {'name': 'abcd'},
            {'name': 'abcde'},
        ]

        itens_filter = [i for i in itens if 'abcd' in i['name']]
        if itens_filter:
            st.write(itens_filter)

    # endregion
    # ========================================================
    # filter_test()

    # ========================================================
    # region PREPARAR_CONTRATOS
    # ========================================================

    @st.cache_data
    def gerar_excel(df):
        import io
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return buffer

  

    def converter_coluna_datetime(col):
        col = col.astype("string").str.strip()

        # remove vazios
        amostra = col[col.notna() & (col != "")]
        
        if amostra.empty:
            return pd.to_datetime(col, errors="coerce")

        primeiro_valor = amostra.iloc[0]

        formatos_possiveis = [
            "%d-%m-%Y",
            "%d-%m-%Y %H:%M",
            "%d-%m-%Y %H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
        ]

        formato_detectado = None

        for fmt in formatos_possiveis:
            try:
                pd.to_datetime(primeiro_valor, format=fmt)
                formato_detectado = fmt
                break
            except (ValueError, TypeError):
                continue

        if formato_detectado is None:
            raise ValueError(f"Formato de data não reconhecido: {primeiro_valor}")

        return pd.to_datetime(col, format=formato_detectado, errors="coerce")

    def preparar_contratos():
        df_contratos = st.session_state.df_contratos
        df_contratos = df_contratos.fillna('')
        df_contratos['familia'] = 'Rompedor'
        df_contratos.rename(columns={
            'Contrato': 'numero_contrato',
            'NumPat': 'patrimonio',
            'DescPat': 'modelo',
            'VlTotalFaturado': 'valor',
            'VlTotalSemDesc': 'valor',
            'QTDE_DIAS': 'dias_no_periodo_original'
        }, inplace=True)
        
        # # para os contratos da mil máquinas
        # df_contratos['marca'] = 'Hilti'

        # para os contratos da lorenzon
        df_contratos['marca'] = np.where(
            df_contratos['modelo'].str.contains('HILTI', case=False, na=False),
            'Hilti',
            'Outros'
        )
        df_contratos[['locacao', 'devolucao']] = df_contratos['PeriodoItem'].str.split(' a ', expand=True)

        df_contratos['modelo'] = df_contratos['modelo'].str.replace('hilti', '', case=False)
        df_contratos['modelo'] = df_contratos['modelo'].str.replace('rompedor', '', case=False)
        df_contratos['modelo'] = df_contratos['modelo'].str.replace(' ', '', case=False)
        df_contratos['locacao'] = df_contratos['locacao'].astype(str)
        df_contratos['devolucao'] = df_contratos['devolucao'].astype(str)
        df_contratos['locacao'] = df_contratos['locacao'].str.replace('/', '-')
        df_contratos['devolucao'] = df_contratos['devolucao'].str.replace('/', '-')
        df_contratos['locacao'] = converter_coluna_datetime(df_contratos['locacao'])
        df_contratos['devolucao'] = converter_coluna_datetime(df_contratos['devolucao'])
        df_contratos['numero_contrato'] = df_contratos['numero_contrato'].astype(str)
        # df_contratos['locacao'] = df_contratos['locacao'].replace('/', '-')
        # df_contratos = df_contratos[['numero_contrato', 'patrimonio', 'familia', 'marca', 'modelo', 'locacao', 'devolucao', 'dias_no_periodo_original', 'valor']].fillna('')

        # df_contratos = df_contratos[
        #     pd.to_datetime(df_contratos['locacao'], format='%d/%m/%Y %H:%M') < pd.to_datetime(df_contratos['devolucao'], format='%d/%m/%Y %H:%M')
        # ]

        df_contratos = df_contratos[['numero_contrato', 'patrimonio', 'familia', 'marca', 'modelo', 'locacao', 'devolucao', 'valor']]

        st.dataframe(df_contratos)
        buffer = gerar_excel(df_contratos)
        st.download_button(
            label="Baixar Excel",
            data=buffer,
            file_name="contratos.xlsx"
        )
    # endregion
    # ========================================================
    # preparar_contratos()

    # ========================================================
    # region INCLUIR PERÍODOS
    # ========================================================
    @st.cache_data
    def calcular_periodos_df(df):
        
        if df.empty:
            st.warning('Carregue o arquivo contratos')
            return
            
        # garante datetime
        df['locacao'] = pd.to_datetime(df['locacao'], format='%d/%m/%Y %H:%M')
        df['devolucao'] = pd.to_datetime(df['devolucao'], format='%d/%m/%Y %H:%M')
        # df['locacao'] = pd.to_datetime(df['locacao'], errors='coerce')
        # df['devolucao'] = pd.to_datetime(df['devolucao'], errors='coerce')

        # 🔥 cálculo vetorizado (igual sua regra de calendário)
        dias_total = (
            df['devolucao'].dt.normalize() - df['locacao'].dt.normalize()
        ).dt.days

        # mínimo 1 dia
        dias_total = dias_total.clip(lower=1)

        df['dias'] = dias_total

        df['mes'] = dias_total // 30
        dias_restantes = dias_total % 30

        df['quinzena'] = dias_restantes // 15
        dias_restantes = dias_restantes % 15

        df['semana'] = dias_restantes // 7
        df['dia'] = dias_restantes % 7

        return df 

    def incluir_periodos():
        df_contratos = st.session_state.df_contratos

        df = df_contratos.copy() 
        df_periodo = calcular_periodos_df(df)
        # df_periodo = df_periodo[['numero_contrato', 'patrimonio', 'familia', 'marca', 'modelo', 'locacao', 'devolucao', 'dias', 'mes', 'quinzena', 'semana', 'dia', 'valor']]
        df_periodo = df_periodo[['numero_contrato', 'patrimonio', 'familia', 'marca', 'modelo', 'locacao', 'devolucao', 'dias', 'mes', 'quinzena', 'semana', 'dia']]
        df_periodo = df_periodo.fillna('')
        st.dataframe(df_periodo)
        st.write(f'Dias: {df_periodo['dias'].sum()}')
    # endregion
    # ========================================================
    # incluir_periodos()

    # ========================================================
    # region ST.TABLE
    # ========================================================
    def st_table():
        product_data = pd.DataFrame({
            "Product": [
                ":material/devices: Widget Pro",
                ":material/smart_toy: Smart Device",
                ":material/inventory: Premium Kit",
            ],
            "Category": [":blue[Electronics]", ":green[IoT]", ":violet[Bundle]"],
            "Stock": ["🟢 Full", "🟡 Low", "🔴 Empty"],
            "Units sold": [1247, 892, 654],
            "Revenue": [125000, 89000, 98000],
        })
        st.table(product_data, border="horizontal")
        from rental_analytics_model.utils import gerar_excel
        gerar_excel.dowload(product_data, 'product_data')        
    # endregion
    # ========================================================
    # st_table()

    # ========================================================
    # region CALC_MEDIA_POTENCIAL
    # ========================================================
    def calc_media_potencial():
        
        df = pd.DataFrame({
            'dias_possiveis': [2108, 1904],
            'dias_loc': [1275, 879],
            'locacoes_diarias': [214,134],
            'p_dia': [160, 160],
        })

        df['mix_dia'] = df['locacoes_diarias'] / df['dias_loc']
        df['pot_dia'] = df['mix_dia'] * df['p_dia'] * df['dias_possiveis']
        df['peso'] = df['p_dia'] * df['dias_possiveis']


        st.dataframe(df)
        total_1 = df['pot_dia'].sum()
        st.write(f'total_1: {total_1:,.2f}')


        peso_total = df['peso'].sum()
        taxa_pond = (df['mix_dia'] * df['peso']).sum() / peso_total

        total_2 = taxa_pond * peso_total
        st.write(f'total_2: {total_2:,.2f}')

        st.write(f'total_1 == total_2', f'✅{total_1 == total_2}' )  # ✅ True        

        # mix_dia_ponderado = (df['mix_dia'] * df['peso']).sum() / df['peso'].sum()
        # pot_total = df['pot_dia'].sum()

        # st.write('Taxa ponderada:', mix_dia_ponderado)
        # st.write(f'{pot_total:,.2f}')


    # endregion
    # ========================================================
    # calc_media_potencial()

    # ========================================================
    # region RECIBOS GF
    # ========================================================
    def recibos_gf():
        df = st.session_state.df_recibos.copy()
        # st.dataframe(df)
        valor_total = df['Subtotal c/imp'].sum()
        st.write(f'Total dos contratos: {valor_total:,.2f}')

        # df_group_periodo = df.groupby('Período')['Subtotal c/imp'].sum()
        df_group_periodo = (
            df
            .groupby('Período', as_index=False)['Subtotal c/imp']
            .sum()
        )

        df_group_periodo = df_group_periodo.sort_values('Período')

        fig = px.bar(
            df_group_periodo,
            x='Período',
            y='Subtotal c/imp',
            text='Subtotal c/imp',
            title='Valor G.F. por Período'
        )

        fig.update_layout(
            xaxis=dict(tickformat="%m/%Y"),
            yaxis_tickprefix='R$ '
        )

        fig.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='outside'
        )


        # st.plotly_chart(fig)

    # endregion
    # ========================================================
    recibos_gf()

    # ========================================================
    # region CRIAR NORMAL ITENS
    # ========================================================
    def criar_normal_itens():
        st.subheader('Normal Itens')
        df = st.session_state.df_recibos.copy()
        df = df[df['Tipo'].isna() ]
        if df.empty:
            st.warning('Nenhuma descrição sem Tipo, Linha e Modelo')
            return
        st.dataframe(df)
        descricoes = df['Descrição'].dropna().astype(str).sort_values().unique().tolist()
        # st.write(descricoes)
        df = loaders.load_normal_itens()

        descricao_selected = st.selectbox('Descrição', descricoes)
        tipo = st.selectbox('Tipo', ['Ferramenta', 'Acessório'])
        linha = st.text_input('Linha')
        modelo = st.text_input('Modelo')

        df_new = pd.DataFrame([{
            'Descrição': descricao_selected,
            'Tipo': tipo,
            'Linha': linha,
            'Modelo': modelo
        }])

        # st.dataframe(df_new)
        if modelo != '':
            df = pd.concat([df, df_new], axis=0, ignore_index=True)

        st.dataframe(df)
        if st.button('Salvar'):
            BASE_DIR = Path(__file__).parents[3]
            df.to_json(BASE_DIR/'data'/'normal_itens.json', orient='records', force_ascii=False, indent=4)
            st.success('Arquivo salvo com sucesso!')
    # endregion
    # ========================================================
    # criar_normal_itens()

    # ========================================================
    # region TABLE STYLE
    # ========================================================
    def table_estyle():

        from rental_analytics_model.utils import formaters
        from rental_analytics_model.components import table

        df = pd.DataFrame({
            "Custo G.F.": [551782.6777],
            "Potencial": [3124556.9794],
            "Break Even": [0.1766],
            "Ocupação": ["🟢 0.35%"],
            "Faturamento": [1104977.1572],
            "Markup": [2.0026],
            "Margem": [0.5006],
        })

        df['Margem'] = df['Margem'] * 100

        df_exibir = df.copy()
        df_exibir["Custo G.F."] = df_exibir["Custo G.F."].map(lambda x: formaters.br_num(x, 2))
        df_exibir["Potencial"] = df_exibir["Potencial"].map(lambda x: formaters.br_num(x, 2))
        df_exibir["Break Even"] = df_exibir["Break Even"].map(lambda x: formaters.br_num(x, 4))
        df_exibir["Faturamento"] = df_exibir["Faturamento"].map(lambda x: formaters.br_num(x, 2))
        df_exibir["Markup"] = df_exibir["Markup"].map(lambda x: formaters.br_num(x, 1))
        df_exibir["Margem"] = df_exibir["Margem"].map(lambda x: f'{formaters.br_num(x, 2)} %')


        table.personal_table(df_exibir)


    # endregion
    # ========================================================
    # table_estyle()
