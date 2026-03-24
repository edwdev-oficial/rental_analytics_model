# =========================================================
# region Importes
# =========================================================
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import pandas as pd

from rental_analytics_model.services import calculos
from src.rental_analytics_model.utils import formaters
# =========================================================
# endregion

# =========================================================
# region main
# =========================================================
def show_dash(df, familia, modelo):

    if 'categoria_selecionada' not in st.session_state:
        st.session_state.categoria_selecionada = None

    # =========================================================
    # region PALETA DE CORES
    # =========================================================
    COLOR_RED = "#d2051e"
    COLOR_BEIGE = "#d7cebd"
    COLOR_DARK = "#524f53"
    COLOR_TAUPE = "#887f6e"
    COLOR_WINE = "#671c3e"
    COLOR_WHITE = "#ffffff"
    COLOR_BLACK = "#000000"
    COLOR_BG = "#f5f3ef"

    PLOTLY_SEQUENCE = [COLOR_RED, COLOR_WINE, COLOR_TAUPE, COLOR_DARK, COLOR_BEIGE]
    # =========================================================    
    # endregion

    # =========================================================
    # region CSS CUSTOMIZADO
    # =========================================================
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {COLOR_WHITE};
            }}

            .block-container {{
                padding-top: 2.5rem;
                padding-bottom: 1.5rem;
            }}

            h1, h2, h3, h4 {{
                color: {COLOR_DARK};
            }}

            section[data-testid="stSidebar"] {{
                # background-color: {COLOR_RED};
                # border-right: 1px solid #ddd;
            }}

            # .kpi-card {{
            #     background-color: {COLOR_BG};
            #     border-radius: 14px;
            #     padding: 16px 18px;
            #     border-left: 8px solid {COLOR_RED};
            #     box-shadow: 0 2px 10px rgba(0,0,0,0.06);
            #     margin-bottom: 10px;
            # }}

            # .kpi-title {{
            #     font-size: 13px;
            #     color: {COLOR_TAUPE};
            #     margin-bottom: 6px;
            #     font-weight: 600;
            #     text-transform: uppercase;
            #     letter-spacing: 0.3px;
            # }}

            .kpi-value {{
                font-size: 28px;
                color: {COLOR_DARK};
                font-weight: 700;
                line-height: 1.1;
            }}

            .kpi-sub {{
                font-size: 12px;
                color: {COLOR_WINE};
                margin-top: 6px;
            }}

            .section-card {{
                background-color: {COLOR_BG};
                padding: 14px;
                border-radius: 16px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                margin-bottom: 14px;
            }}

            div[data-testid="stDataFrame"] {{
                background-color: {COLOR_BG};
                border-radius: 12px;
                padding: 4px;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    # =========================================================
    # endregion

    # =========================================================
    # region funções
    # =========================================================
    # FUNÇÕES
    # =========================================================
    def pct(valor):
        return f"{valor:.1%}"

    def make_kpi_card(title, value, subtext=""):
        return f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-sub">{subtext}</div>
            </div>
        """

    def apply_theme(fig, title=None):
        fig.update_layout(
            title=title,
            plot_bgcolor=COLOR_WHITE,
            paper_bgcolor=COLOR_WHITE,
            font=dict(color=COLOR_DARK),
            title_font=dict(size=18, color=COLOR_DARK),
            margin=dict(l=20, r=20, t=60, b=20),
            legend=dict(
                bgcolor="rgba(0,0,0,0)"
            )
        )
        return fig
    # =========================================================
    # endregion

    # =========================================================
    # region df_group_filter_by_linha_modelo
    # =========================================================
    df_group_filter_by_linha_modelo = (
    (df[
        (df['Linha'].str.contains(familia, na=False))
        &
        (df['Modelo'].str.contains(modelo, na=False))
    ])
        .groupby('Modelo', as_index=False)
        .agg({
            'Qt.': 'sum',
            'Subtotal c/imp': 'sum',
            'dia': 'first',
            'semana':'first',
            'quinzena':'first',
            'mes':'first',
        })
    ).sort_values('Subtotal c/imp', ascending=False)
    # st.dataframe(df_group_filter_by_linha_modelo)
    # =========================================================
    # endregion

    # =========================================================
    # region SLIDERS
    # =========================================================
    # valor inicial
    VALOR_INICIAL_DISP = (0, st.session_state["tx_disponibilidade"])
    VALOR_INICIAL_OCUP = (0, st.session_state["tx_ocupacao"])
    if "range_slider_disp" not in st.session_state:
        st.session_state.range_slider_disp = VALOR_INICIAL_DISP

    if "range_slider_ocup" not in st.session_state:
        st.session_state.range_slider_ocup = VALOR_INICIAL_OCUP


    with st.sidebar:

        container_sliders_button = st.container (
            border=True
        )

        with container_sliders_button:
            container_sliders = st.container(
                border=False
            )
            if st.button("🔄 Resetar"):
                st.session_state.range_slider_disp = VALOR_INICIAL_DISP
                st.session_state.range_slider_ocup = VALOR_INICIAL_OCUP
            with container_sliders:
                tx_disp_use = st.slider(
                    'Taxa disponibilidade',
                    min_value=0,
                    max_value=100,
                    step=1,
                    value=st.session_state.range_slider_disp,
                    key="range_slider_disp"
                )

                tx_ocup_use = st.slider(
                    'Taxa ocupação',
                    min_value=0,
                    max_value=100,
                    step=1,
                    value=st.session_state.range_slider_ocup,
                    key="range_slider_ocup"
                )

    # st.write(tx_disp_use[1])
    # st.write(tx_ocup_use[1])
    # =========================================================
    # endregion

    st.dataframe(df_group_filter_by_linha_modelo)
    total_equipamentos = df_group_filter_by_linha_modelo['Qt.'].sum()
    valor_total_gf = df_group_filter_by_linha_modelo['Subtotal c/imp'].sum()
    st.write(f'Qtd: {total_equipamentos} - Total G.F. {formaters.format_brl(valor_total_gf, True)} ')

    # =========================================================
    # region INDICADORES DERIVADOS
    # =========================================================
    df_faturamento = calculos.calcular_faturamento_frota(
        df_group_filter_by_linha_modelo,
        tx_disp_use[1],
        tx_ocup_use[1]
    )
    # st.dataframe(df_faturamento)
    # =========================================================
    # endregion

    # =========================================================
    # region TOTAIS
    # =========================================================
    def write_data(title, data):
        st.write(f'{title}: {formaters.format_brl(data)}')

    qt_total = int(df_faturamento["Qt."].sum())
    # st.write(f'Qtd total: {qt_total}')

    valor_gf = df_faturamento['Subtotal c/imp'].sum()
    # write_data('Valor Gestão de Frotas', valor_gf)


    faturamento_potencial_total = df_faturamento["faturamento_potencial_total"].sum()
    # write_data('Faturamento potencial total', faturamento_potencial_total)

    faturamento_apos_disp_total = df_faturamento["faturamento_apos_disponibilidade"].sum()
    # write_data('Faturamento total após disponibilidade', faturamento_apos_disp_total)

    gap_apos_disponibilidade = faturamento_potencial_total - faturamento_apos_disp_total
    # write_data('Gap após disponibilidade', gap_apos_disponibilidade)

    faturamento_real_total = df_faturamento["faturamento_real"].sum()
    # write_data('Faturamento total real', faturamento_real_total)

    gap_total = df_faturamento["gap_faturamento"].sum()
    # write_data('Gap total', gap_total)

    utilizacao_media = faturamento_real_total / faturamento_potencial_total
    # st.write(f'Utilização média {int(utilizacao_media * 100)} %')
    
    perda_indisp_total = df_faturamento["perda_por_indisponibilidade"].sum()
    # write_data('Perda por indisponibilidade', perda_indisp_total)

    perda_ocup_total = df_faturamento["perda_por_baixa_ocupacao"].sum()
    # write_data('Perda por baixa ocupação', perda_ocup_total)
    # =========================================================
    # endregion

    # =========================================================
    # region DASHBOARD EXECUTIVO
    # =========================================================

    # =========================================================
    # region CARDS
    # =========================================================
    k1, k2, k3, k4, k5, k6, k7 = st.columns(7)

    with k1:
        st.markdown(make_kpi_card("Máquinas", f"{qt_total}", "Tamanho da frota filtrada"), unsafe_allow_html=True)

    with k2:
        st.markdown(make_kpi_card("Potencial Total", formaters.format_brl(faturamento_potencial_total), "Capacidade máxima teórica"), unsafe_allow_html=True)

    with k3:
        st.markdown(make_kpi_card("Após Disponibilidade", formaters.format_brl(faturamento_apos_disp_total), "Potencial após perda operacional"), unsafe_allow_html=True)

    with k4:
        st.markdown(make_kpi_card("Gap Operacional", formaters.format_brl(gap_apos_disponibilidade), "Real ÷ potencial"), unsafe_allow_html=True)

    with k5:
        st.markdown(make_kpi_card("Após Ocupação", formaters.format_brl(faturamento_real_total), "Receita efetivamente capturada"), unsafe_allow_html=True)

    with k6:
        st.markdown(make_kpi_card("Gap Comercial", formaters.format_brl(gap_total), "Disponível, mas não monetizado"), unsafe_allow_html=True)

    with k7:
        st.markdown(make_kpi_card("Utilização Econômica", pct(utilizacao_media), "Real ÷ potencial"), unsafe_allow_html=True)


    # =========================================================
    # endregion

    # =========================================================
    # region GRAFICOS
    # =========================================================

    # =========================================================
    # region COL1 COL2
    # =========================================================
    c1, c2 = st.columns(2)

    with c1:
        fig_real = px.bar(
            df_faturamento.sort_values("faturamento_real"),
            x="faturamento_real",
            y="Modelo",
            orientation="h",
            text="faturamento_real",
            color_discrete_sequence=[COLOR_RED]
        )
        fig_real.update_traces(texttemplate="R$ %{text:,.0f}", textposition="inside")
        fig_real = apply_theme(fig_real, "Faturamento Real por Modelo")
        fig_real.update_layout(
           height=420,
            margin=dict(l=130, r=20, t=50, b=50)
        )

        card_1 = st.container(
            border=True,
            key='card1',
        )
        with card_1:
            st.plotly_chart(fig_real, width='stretch')
    #         selected_points = plotly_events(
    #             fig_real,
    #             click_event=True,
    #         )

    # if selected_points:
    #     if selected_points == st.session_state.categoria_selecionada:
    #         st.session_state.categoria_selecionada = None
    #     else:
    #         st.session_state.categoria_selecionada = selected_points        
    #         st.write(st.session_state.categoria_selecionada)

    with c2:
        df_compare = df_faturamento[["Modelo", "faturamento_potencial_total", "faturamento_real"]].melt(
            id_vars="Modelo",
            var_name="Tipo",
            value_name="Valor"
        )

        fig_comp = px.bar(
            df_compare,
            x="Modelo",
            y="Valor",
            color="Tipo",
            barmode="group",
            color_discrete_map={
                "faturamento_potencial_total": COLOR_TAUPE,
                "faturamento_real": COLOR_WINE
            }
        )
        fig_comp = apply_theme(fig_comp, "Potencial x Real por Modelo")
        card_2 = st.container(
            border=True,
            key='card2',
        )        
        with card_2:
            st.plotly_chart(fig_comp, width='stretch')
    # =========================================================
    # endregion

    # =========================================================
    # region COL3 COL4
    # =========================================================
    c3, c4 = st.columns(2)

    with c3:
        fig_gap = px.bar(
            df_faturamento.sort_values("gap_faturamento"),
            x="gap_faturamento",
            y="Modelo",
            orientation="h",
            text="gap_faturamento",
            color_discrete_sequence=[COLOR_TAUPE]
        )
        fig_gap.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
        fig_gap = apply_theme(fig_gap, "Gap comercial por Modelo")
        card_3 = st.container(
            border=True,
            key='card3',
        )        
        with card_3:
            st.plotly_chart(fig_gap, width='stretch')

    with c4:
        fig_rpm = px.bar(
            df_faturamento.sort_values("receita_por_maquina"),
            x="receita_por_maquina",
            y="Modelo",
            orientation="h",
            text="receita_por_maquina",
            color_discrete_sequence=[COLOR_DARK]
        )
        fig_rpm.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
        fig_rpm = apply_theme(fig_rpm, "Receita por Máquina")
        card_4 = st.container(
            border=True,
            key='card4',
        )        
        with card_4:
            st.plotly_chart(fig_rpm, width='stretch')

    # =========================================================
    # endregion

    # =========================================================
    # region COL5 COL6
    # =========================================================
    c5, c6 = st.columns(2)
    
    with c5:
        df_modalidades = pd.DataFrame({
            "modalidade": ['mes', 'quinzena', 'semana', 'dia'],
            "qtd": [160, 132, 472, 3290]
        })

        df_modalidades = df_modalidades[df_modalidades['qtd'] > 0]

        fig = px.pie(
            df_modalidades,
            names='modalidade',
            values='qtd',
            title='Mix Modalidades',
            hole=0.4,  # vira donut 
            color_discrete_sequence=[COLOR_RED, COLOR_WINE, COLOR_TAUPE, COLOR_DARK]
        )

        fig.update_traces(
            textinfo='percent+label',  # mostra % + nome
            pull=[0, 0, 0, 0.05]      # destaca uma fatia (opcional)
        )

        fig.update_layout(
            legend_title='Modalidade',
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        card_5 = st.container(
            border=True,
            key='card5',
        )        
        with card_5:
            st.plotly_chart(fig)

    with c6:
        fig_scatter = px.scatter(
            df_faturamento,
            x="Qt.",
            y="faturamento_real",
            size="gap_faturamento",
            text="Modelo",
            hover_name="Modelo",
            color_discrete_sequence=[COLOR_RED]
        )
        fig_scatter.update_traces(textposition="top center")
        fig_scatter = apply_theme(fig_scatter, "Quantidade x Faturamento Real")
        card_6 = st.container(
            border=True,
            key="card6"
        )
        with card_6:
            st.plotly_chart(fig_scatter, width='stretch')

    # =========================================================
    # endregion

    # =========================================================
    # endregion

    # =========================================================
    # region COMPOSIÇÃO DAS PERDAS    
    # =========================================================
    st.subheader("Composição das perdas")

    waterfall_df = pd.DataFrame({
        "Etapa": ["Potencial Total", "Perda por Indisponibilidade", "Após Disponibilidade", "Perda por Baixa Ocupação", "Faturamento Real"],
        "Valor": [faturamento_potencial_total, -perda_indisp_total, faturamento_apos_disp_total, -perda_ocup_total, faturamento_real_total]
    })

    fig_waterfall = go.Figure(go.Waterfall(
        name="Fluxo de Receita",
        orientation="v",
        measure=["absolute", "relative", "total", "relative", "total"],
        x=waterfall_df["Etapa"],
        y=waterfall_df["Valor"],
        connector={"line": {"color": COLOR_DARK}},
        increasing={"marker": {"color": COLOR_TAUPE}},
        decreasing={"marker": {"color": COLOR_RED}},
        totals={"marker": {"color": COLOR_WINE}}
    ))
    fig_waterfall = apply_theme(fig_waterfall, "Da Capacidade Teórica ao Faturamento Real")
    
    st.plotly_chart(fig_waterfall, width='stretch')

    st.subheader("Tabela Analítica")

    df_show = df_faturamento[[
        "Modelo",
        "Qt.",
        "faturamento_real",
        "faturamento_potencial_total",
        "faturamento_apos_disponibilidade",
        "gap_faturamento",
        "receita_por_maquina",
        "potencial_por_maquina",
        "gap_por_maquina",
        "indice_monetizacao",
        "eficiencia_operacional",
        "indice_relevancia"
    ]].copy()

    df_show = df_show.sort_values("faturamento_real", ascending=False)

    st.dataframe(
        df_show.style.format({
            "faturamento_real": "R$ {:,.2f}",
            "faturamento_potencial_total": "R$ {:,.2f}",
            "faturamento_apos_disponibilidade": "R$ {:,.2f}",
            "gap_faturamento": "R$ {:,.2f}",
            "receita_por_maquina": "R$ {:,.2f}",
            "potencial_por_maquina": "R$ {:,.2f}",
            "gap_por_maquina": "R$ {:,.2f}",
            "indice_monetizacao": "{:.1%}",
            "eficiencia_operacional": "{:.1%}",
            "indice_relevancia": "{:.2f}"
        }),
        width='stretch',
        hide_index=True
    )
    # =========================================================
    # endregion

    # =========================================================
    # endregion

# =========================================================
# endregion


