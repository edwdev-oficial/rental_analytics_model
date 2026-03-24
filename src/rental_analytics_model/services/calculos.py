import pandas as pd
import numpy as np

# =========================================================
# CÁLCULO PRINCIPAL
# =========================================================
def calcular_faturamento_frota(
    df: pd.DataFrame,
    tx_disp_use,
    tx_ocup_use,
    dias_semana
) -> pd.DataFrame:
    """
    Calcula o faturamento da frota.

    Parâmetros:
    - df: DataFrame com os dados da frota
    - DISPONIBILIDADE: se informada, sobrescreve a DISPONIBILIDADE de todas as linhas
    - OCUPACAO: se informada, sobrescreve a ocupação de todas as linhas

    Retorna:
    - DataFrame com colunas calculadas
    """
    # df_calc = preparar_dataframe(df)

    # st.write(st.session_state)

    DISPONIBILIDADE = tx_disp_use / 100
    OCUPACAO = tx_ocup_use / 100
    DIAS_UTEIS = np.round((52 /12) * float(dias_semana)).astype(int)

    SEMANAS_POSSIVEIS = 4 if dias_semana else 0
    QUINZENAS_POSSIVEIS = 2 if dias_semana else 0
    MENSAL_POSSIVEL = 1 if dias_semana else 0


    df_calc = df

    if DISPONIBILIDADE is not None:
        df_calc["DISPONIBILIDADE"] = DISPONIBILIDADE

    if OCUPACAO is not None:
        df_calc["OCUPACAO"] = OCUPACAO

    df_calc['mix_dia'] = 0.812
    df_calc['mix_semana'] = 0.115        
    df_calc['mix_quinzena'] = 0.0403        
    df_calc['mix_mes'] = 0.0327

    # Potencial mensal por modalidade
    df_calc["potencial_dia"] = df_calc["dia"] * DIAS_UTEIS * df_calc["mix_dia"]
    df_calc["potencial_semana"] = df_calc["semana"] * SEMANAS_POSSIVEIS * df_calc["mix_semana"]
    df_calc["potencial_quinzena"] = df_calc["quinzena"] * QUINZENAS_POSSIVEIS * df_calc["mix_quinzena"]
    df_calc["potencial_mes"] = df_calc["mes"] * MENSAL_POSSIVEL * df_calc["mix_mes"]

    # Potencial mensal por máquina
    df_calc["potencial_mensal_por_maquina"] = (
        df_calc["potencial_dia"] +
        df_calc["potencial_semana"] +
        df_calc["potencial_quinzena"] +
        df_calc["potencial_mes"]
    )

    # Potencial total sem perdas
    df_calc["faturamento_potencial_total"] = (
        df_calc["Qt."] * df_calc["potencial_mensal_por_maquina"]
    )

    # Após DISPONIBILIDADE
    df_calc["faturamento_apos_disponibilidade"] = (
        df_calc["faturamento_potencial_total"] * df_calc["DISPONIBILIDADE"]
    )

    # Faturamento real
    df_calc["faturamento_real"] = (
        df_calc["faturamento_potencial_total"] *
        df_calc["DISPONIBILIDADE"] *
        df_calc["OCUPACAO"]
    )

    # Utilização econômica
    df_calc["Utilizacao_Economica"] = (
        df_calc["DISPONIBILIDADE"] * df_calc["OCUPACAO"]
    )

    df_calc['gap_operacional'] = df_calc['faturamento_potencial_total'] - df_calc['faturamento_apos_disponibilidade']
    df_calc['gap_faturamento'] = df_calc['faturamento_apos_disponibilidade'] - df_calc['faturamento_real']
    df_calc['receita_por_maquina'] = df_calc['faturamento_real'] / df_calc['Qt.']
    df_calc['potencial_por_maquina'] = df_calc['faturamento_potencial_total'] / df_calc['Qt.']
    df_calc['gap_por_maquina'] = df_calc['gap_faturamento'] / df_calc['Qt.']
    df_calc['share_faturamento'] = df_calc['faturamento_real'] / df_calc['faturamento_real'].sum()
    df_calc['share_qt'] = df_calc['Qt.'] / df_calc['Qt.'].sum()
    df_calc['indice_monetizacao'] = df_calc['faturamento_real'] / df_calc['faturamento_potencial_total']
    df_calc['perda_por_indisponibilidade'] = df_calc['faturamento_potencial_total'] - df_calc['faturamento_apos_disponibilidade']
    df_calc['perda_por_baixa_ocupacao'] = df_calc['faturamento_apos_disponibilidade'] - df_calc['faturamento_real']
    df_calc['eficiencia_operacional'] = df_calc['faturamento_real'] / df_calc['faturamento_apos_disponibilidade']
    df_calc["share_qt"] = df_calc["Qt."] / df_calc["Qt."].sum()
    df_calc["indice_relevancia"] = df_calc["share_faturamento"] / df_calc["share_qt"]
    return df_calc