import streamlit as st
import pandas as pd

def app():
    st.title("Rental Analytics Model")

    df = pd.DataFrame({
        "Disponibilidade": [0.90, 0.95],
        "Ocupação": [0.60, 0.70],
        "Receita": [500000, 717252]
    })

    st.dataframe(df)

    st.line_chart(df.set_index("Disponibilidade"))

app()