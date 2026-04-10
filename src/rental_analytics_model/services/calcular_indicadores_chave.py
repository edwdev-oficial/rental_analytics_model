import pandas as pd

def calc(df):

    from rental_analytics_model.utils.formaters import br_num

    # ========================================================
    # region STATUS OCUPAÇÃO
    # ========================================================
    def status_ocupacao(row):
        ocup_break_even = row['Break Even']
        ocup = row['Taxa de Ocupação']

        if ocup >= ocup_break_even * 2:
            return f'🟢 {ocup:.2f}%'
        elif ocup > ocup_break_even:
            return f'🟡 {ocup:.2f}%'
        else:
            return f'🔴 {ocup:.2f}%'
    # endregion
    # ========================================================

    df['dias_possiveis'] = df['Qt.'] * df['dias_mes']
    df['dias_loc'] = df['dias_possiveis'] * df['tx_ocupacao']
    df['sum_mix'] = df['mix_dia'] + df['mix_semana'] * 7 + df['mix_quinzena'] * 15 + df['mix_mes'] * 30
    df['contratos'] = df['dias_loc'] / df['sum_mix']
    df['diarias'] = df['mix_dia'] * df['contratos']
    df['semanas'] = df['mix_semana'] * df['contratos']
    df['quinzenas'] = df['mix_quinzena'] * df['contratos']
    df['meses'] = df['mix_mes'] * df['contratos']
    df['pot_dia'] = df['dias_possiveis'] / df['sum_mix'] * df['mix_dia'] * df['p_dia']
    df['pot_semana'] = df['dias_possiveis'] / df['sum_mix'] * df['mix_semana'] * df['p_semana']
    df['pot_quinzena'] = df['dias_possiveis'] / df['sum_mix'] * df['mix_quinzena'] * df['p_quinzena']
    df['pot_mes'] = df['dias_possiveis'] / df['sum_mix'] * df['mix_mes'] * df['p_mes']
    df['pot_total'] = df[['pot_dia', 'pot_semana', 'pot_quinzena', 'pot_mes']].sum(axis=1)
    df['fat_dia'] = df['diarias'] * df['p_dia']
    df['fat_semana'] = df['semanas'] * df['p_semana']
    df['fat_quinzena'] = df['quinzenas'] * df['p_quinzena']
    df['fat_mes'] = df['meses'] * df['p_mes']
    df['fat_total'] = df[['fat_dia', 'fat_semana', 'fat_quinzena', 'fat_mes']].sum(axis=1)

    df = (
        df
        .groupby('modelo')
        .agg({
            'Subtotal c/imp': 'sum',
            'pot_total': 'sum',
            'fat_total': 'sum'
        }).reset_index()
    )

    df.rename(columns={
        'modelo': 'Modelo',
        'Subtotal c/imp': 'Custo G.F.',
        'pot_total': 'Potencial',
        'fat_total': 'Faturamento'
    }, inplace=True)

    df.insert(df.columns.get_loc('Faturamento'), 'Taxa de Ocupação', df['Faturamento'] / df['Potencial'] * 100)
    df.insert(df.columns.get_loc('Taxa de Ocupação'), 'Break Even', df['Custo G.F.'] / df['Potencial'] * 100)
    df['Markup'] = df['Faturamento'] / df['Custo G.F.']
    df['Margem'] = (df['Faturamento'] - df['Custo G.F.']) / df['Faturamento'] * 100
    df['Taxa de Ocupação'] = df.apply(status_ocupacao, axis=1)
    df['Lucro Bruto'] = df['Faturamento'] - df['Custo G.F.']

    custo_total = df['Custo G.F.'].sum()
    potencial_total = df['Potencial'].sum()
    faturamento_total = df['Faturamento'].sum()

    df_total = pd.DataFrame({
        'Modelo': ['Todos'],
        'Custo G.F.': [custo_total],
        'Potencial': [potencial_total],
        'Faturamento': [faturamento_total]
    })

    df_total.insert(df_total.columns.get_loc('Faturamento'), 'Break Even', df_total['Custo G.F.'] / df_total['Potencial'] * 100)
    df_total.insert(df_total.columns.get_loc('Faturamento'), 'Taxa de Ocupação', df_total['Faturamento'] / df_total['Potencial'] * 100)
    df_total['Markup'] = df['Faturamento'] / df['Custo G.F.']
    df_total['Margem'] = (df['Faturamento'] - df['Custo G.F.']) / df['Faturamento'] * 100
    df_total['Lucro Bruto'] = df_total['Faturamento'] - df_total['Custo G.F.']

    df['Custo G.F.'] = df['Custo G.F.'].map(lambda x: br_num(x, 2) )
    df['Potencial'] = df['Potencial'].map(lambda x: br_num(x, 2) )
    df['Break Even'] = df['Break Even'].map(lambda x: f'{br_num(x, 2)}%' )
    df['Faturamento'] = df['Faturamento'].map(lambda x: br_num(x, 2) )
    df['Markup'] = df['Markup'].map(lambda x: br_num(x, 2) )
    df['Margem'] = df['Margem'].map(lambda x: f'{br_num(x, 2)}%' )
    df['Lucro Bruto'] = df['Lucro Bruto'].map(lambda x: br_num(x, 2))

    df_total['Custo G.F.'] = df_total['Custo G.F.'].map(lambda x: br_num(x, 2) )
    df_total['Potencial'] = df_total['Potencial'].map(lambda x: br_num(x, 2) )
    df_total['Faturamento'] = df_total['Faturamento'].map(lambda x: br_num(x, 2) )
    df_total['Markup'] = df_total['Markup'].map(lambda x: br_num(x, 2) )
    df_total['Margem'] = df_total['Margem'].map(lambda x: f'{br_num(x, 2)}%' )
    df_total['Taxa de Ocupação'] = df_total.apply(status_ocupacao, axis=1)
    df_total['Break Even'] = df_total['Break Even'].map(lambda x: f'{br_num(x, 2)}%' )
    df_total['Lucro Bruto'] = df_total['Lucro Bruto'].map(lambda x: br_num(x, 2) )

    return df, df_total