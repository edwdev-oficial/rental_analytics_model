import streamlit as st
from rental_analytics_model.utils.gerar_excel import dowload

def render_bloco_filtro_reparos(df_filter, filtros: dict):
    with st.expander("filter e reparos"):
        if any(filtros.values()):
            st.subheader(
                f"Filtro por {filtros['hierarquia']} {filtros['familia']} {filtros['modelo']}".strip()
            )

        st.write(f"Qtd linhas: {df_filter.shape[0]} | Qtd colunas: {df_filter.shape[1]}")
        st.dataframe(df_filter)
        st.write(f"{df_filter['falhas'].sum():,.0f} falhas {df_filter['# Reparos'].sum():,.0f} reparos")
        dowload(df_filter, 'reparacoes')
