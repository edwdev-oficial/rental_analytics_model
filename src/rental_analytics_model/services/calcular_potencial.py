import streamlit as st
import pandas as pd

def calcular():

    df_recibos = st.session_state.df_recibos.copy()
    df_recibos = (
        df_recibos
        .groupby(['periodo','familia', 'modelo'], as_index=False)
        .agg({
            'Qt.': 'sum',
        })
    )    
    
    
    df_valores_locacao = st.session_state.df_valores_locacao.copy()
    df_valores_locacao.rename(columns={
            'Modelo': 'modelo',
            'dia': 'p_dia',
            'semana': 'p_semana',
            'quinzena': 'p_quinzena',
            'mes': 'p_mes'
        }, inplace=True)       

    df_contratos = st.session_state.df_contratos_originais.copy()

    df_contratos['periodo'] = pd.to_datetime(df_contratos['locacao']).dt.to_period('M')
    df_contratos['dias_mes'] = df_contratos['periodo'].dt.days_in_month

    df_contratos = (df_contratos
        .groupby(['periodo', 'dias_mes', 'familia', 'modelo'], as_index=False)
        .agg({
            'dias': 'sum',
            'dia': 'sum',
            'quinzena': 'sum',
            'semana': 'sum',
            'mes':'sum',
        })
    )

    df_contratos = pd.merge(
        df_contratos, 
        df_recibos,
        on=['periodo', 'familia', 'modelo'],
        how='outer',
    )

    df_contratos = pd.merge(
        df_contratos,
        df_valores_locacao,
        on=['modelo'],
        how='left'
    )    

    df_contratos['dias_no_periodo'] = df_contratos['periodo'].dt.days_in_month
    df_contratos['dias_possiveis'] =  df_contratos['dias_no_periodo'] * df_contratos['Qt.']
    if 'tx_disponibilidade' not in st.session_state:
            st.session_state.tx_disponibilidade = 100

    df_contratos['dias'] = df_contratos['dias'].fillna(0)
    df_contratos['dia'] = df_contratos['dia'].fillna(0)
    df_contratos['semana'] = df_contratos['semana'].fillna(0)
    df_contratos['quinzena'] = df_contratos['quinzena'].fillna(0)
    df_contratos['mes'] = df_contratos['mes'].fillna(0)

    df_contratos = (
        df_contratos
        .groupby(['periodo', 'dias_no_periodo', 'familia', 'modelo'], as_index=False)
        .agg({
            'Qt.': 'sum',
            'dias_possiveis': 'sum',
            'dias': 'sum',
            'dia': 'sum',
            'semana': 'sum',
            'quinzena': 'sum',
            'mes': 'sum',
            'p_dia': 'mean',
            'p_semana': 'mean',
            'p_quinzena': 'mean',
            'p_mes': 'mean',
        })
    )    
 
    df_contratos['tx_ocupacao'] = df_contratos['dias'] / df_contratos['dias_possiveis']
    df_contratos.insert(df_contratos.columns.get_loc('tx_ocupacao'), 'tx_disp', st.session_state.tx_disponibilidade)
    
    df_contratos['total_contratos'] = df_contratos[['dia', 'semana', 'quinzena', 'mes']].sum(axis=1)
    
    df_contratos['mix_dia'] = (df_contratos['dia'] / df_contratos['total_contratos']).fillna(0)
    
    df_contratos['mix_semana'] = (df_contratos['semana'] / df_contratos['total_contratos']).fillna(0)
            
    df_contratos['mix_quinzena'] = (df_contratos['quinzena'] / df_contratos['total_contratos']).fillna(0)

    df_contratos['mix_mes'] = (df_contratos['mes'] / df_contratos['total_contratos']).fillna(0)

    df_contratos = df_contratos[[
        'familia',
        'modelo',
        'periodo',
        'Qt.',
        'dias_no_periodo',
        'tx_disp',
        'tx_ocupacao',
        'mix_dia',
        'mix_semana',
        'mix_quinzena',
        'mix_mes',
        'p_dia',
        'p_semana',
        'p_quinzena',
        'p_mes',
        'dias_possiveis',
    ]]

    df_contratos['dias_loc'] = df_contratos['dias_possiveis'] * df_contratos['tx_ocupacao']
    df_contratos['sum_mix'] = df_contratos['mix_dia'] + df_contratos['mix_semana'] * 7 + df_contratos['mix_quinzena'] * 15 + df_contratos['mix_mes'] * 30
    df_contratos['contratos'] = (df_contratos['dias_loc'] / df_contratos['sum_mix']).fillna(0)
    df_contratos['diarias'] = (df_contratos['mix_dia'] * df_contratos['contratos']).fillna(0)
    df_contratos['semanas'] = (df_contratos['mix_semana'] * df_contratos['contratos']).fillna(0)
    df_contratos['quinzenas'] = (df_contratos['mix_quinzena'] * df_contratos['contratos']).fillna(0)
    df_contratos['meses'] = (df_contratos['mix_mes'] * df_contratos['contratos']).fillna(0)

    df_contratos = (
        df_contratos
        .groupby(['familia', 'modelo'])
        .agg(
            {
                'dias_possiveis': 'sum',
                'dias_loc': 'sum',
                'diarias': 'sum',
                'semanas': 'sum',
                'quinzenas': 'sum',
                'meses': 'sum',
                'contratos': 'sum',
                'p_dia': 'first',
                'p_semana': 'first',
                'p_quinzena': 'first',
                'p_mes': 'first',
            },
        ).reset_index()
    )
    df_contratos['mix_dia'] = (df_contratos['diarias'] / df_contratos['contratos']).fillna(0)
    df_contratos['mix_semana'] = (df_contratos['semanas'] / df_contratos['contratos']).fillna(0)
    df_contratos['mix_quinzena'] = (df_contratos['quinzenas'] / df_contratos['contratos']).fillna(0)
    df_contratos['mix_mes'] = (df_contratos['meses'] / df_contratos['contratos']).fillna(0)
    df_contratos['sum_mix'] = df_contratos['mix_dia'] + df_contratos['mix_semana'] * 7 + df_contratos['mix_quinzena'] * 15 + df_contratos['mix_mes'] * 30
    df_contratos['pot_dia'] = df_contratos['dias_possiveis'] / df_contratos['sum_mix'] * df_contratos['mix_dia'] * df_contratos['p_dia']
    df_contratos['pot_semana'] = df_contratos['dias_possiveis'] / df_contratos['sum_mix'] * df_contratos['mix_semana'] * df_contratos['p_semana']
    df_contratos['pot_quinzena'] = df_contratos['dias_possiveis'] / df_contratos['sum_mix'] * df_contratos['mix_quinzena'] * df_contratos['p_quinzena']
    df_contratos['pot_mes'] = df_contratos['dias_possiveis'] / df_contratos['sum_mix'] * df_contratos['mix_mes'] * df_contratos['p_mes']
    df_contratos['pot_total'] = df_contratos[['pot_dia', 'pot_semana', 'pot_quinzena', 'pot_mes']].sum(axis=1)

    return df_contratos['pot_total'] 