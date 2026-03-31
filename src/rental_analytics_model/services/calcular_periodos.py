import streamlit as st
import pandas as pd

@st.cache_data
def calcular_periodos_df(df):
    # garante datetime
    df['locacao'] = pd.to_datetime(df['locacao'], errors='coerce')
    df['devolucao'] = pd.to_datetime(df['devolucao'], errors='coerce')

    # 🔥 cálculo vetorizado (igual minha regra de calendário)
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