import pandas as pd
import numpy as np


def processar_reparos_json(df_raw: pd.DataFrame) -> dict:
    """
    Processa base de reparos no formato:
    serie, modelo, data_venda, ano_relatorio, falhas, reparos, custo_reparos

    Retorna:
    - df_base (limpa)
    - df_exposicao
    - df_lifecycle
    - df_metricas
    """

    # =============================
    # 1. LIMPEZA INICIAL
    # =============================
    df = df_raw.copy()

    df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")

    df = df.dropna(subset=["serie", "modelo", "data_venda", "ano_relatorio"]).copy()

    df["serie"] = df["serie"].astype(str).str.strip()
    df["modelo"] = df["modelo"].astype(str).str.strip().str.lower()

    df["falhas"] = pd.to_numeric(df["falhas"], errors="coerce").fillna(0)
    df["reparos"] = pd.to_numeric(df["reparos"], errors="coerce").fillna(0)
    df["custo_reparos"] = pd.to_numeric(df["custo_reparos"], errors="coerce").fillna(0)

    # =============================
    # 2. CONSOLIDAR DUPLICIDADE
    # =============================
    df = df.groupby(
        ["serie", "modelo", "data_venda", "ano_relatorio"],
        as_index=False
    ).agg({
        "falhas": "sum",
        "reparos": "sum",
        "custo_reparos": "sum"
    })

    # =============================
    # 3. CALCULAR IDADE
    # =============================
    df["idade_int"] = df["ano_relatorio"] - df["data_venda"].dt.year

    # remover possíveis inconsistências
    df = df[df["idade_int"] >= 0].copy()

    # =============================
    # 4. BASE DE OBSERVAÇÃO
    # =============================
    df_obs = df.groupby(
        ["serie", "modelo", "data_venda"],
        as_index=False
    ).agg(
        ano_final=("ano_relatorio", "max")
    )

    df_obs["idade_final"] = df_obs["ano_final"] - df_obs["data_venda"].dt.year

    # =============================
    # 5. EXPOSIÇÃO (CRÍTICO)
    # =============================
    registros = []

    for _, row in df_obs.iterrows():
        for idade in range(int(row["idade_final"]) + 1):
            registros.append({
                "serie": row["serie"],
                "modelo": row["modelo"],
                "idade_int": idade
            })

    df_exposicao = pd.DataFrame(registros)

    # =============================
    # 6. JUNTAR FALHAS
    # =============================
    df_lifecycle = df_exposicao.merge(
        # df[](%22serie%22,%20%22modelo%22,%20%22idade_int%22,%20%22falhas%22,%20%22custo_reparos%22),
        df[["serie", "modelo", "idade_int", "falhas", "custo_reparos"]],
        on=["serie", "modelo", "idade_int"],
        how="left"
    )

    df_lifecycle["falhas"] = df_lifecycle["falhas"].fillna(0)
    df_lifecycle["custo_reparos"] = df_lifecycle["custo_reparos"].fillna(0)

    df_lifecycle["teve_falha"] = df_lifecycle["falhas"] > 0

    # =============================
    # 7. MÉTRICAS
    # =============================
    df_metricas = df_lifecycle.groupby(
        ["modelo", "idade_int"],
        as_index=False
    ).agg(
        maquinas=("serie", "nunique"),
        falhas_totais=("falhas", "sum"),
        custo_total=("custo_reparos", "sum"),
        maquinas_com_falha=("teve_falha", "sum"),
        falhas_por_maquina=("falhas", "mean"),
        custo_por_maquina=("custo_reparos", "mean"),
    )

    df_metricas["perc_maquinas_com_falha"] = np.where(
        df_metricas["maquinas"] > 0,
        df_metricas["maquinas_com_falha"] / df_metricas["maquinas"],
        np.nan
    )

    df_metricas["custo_por_falha"] = np.where(
        df_metricas["falhas_totais"] > 0,
        df_metricas["custo_total"] / df_metricas["falhas_totais"],
        np.nan
    )

    # =============================
    # 8. ORDENAÇÃO FINAL
    # =============================
    df_metricas = df_metricas.sort_values(["modelo", "idade_int"]).reset_index(drop=True)

    return {
        "df_base": df,
        "df_exposicao": df_exposicao,
        "df_lifecycle": df_lifecycle,
        "df_metricas": df_metricas,
    }

def processar_base_reparacoes(df_raw: pd.DataFrame):
    """
    Pipeline completo para tratar base de reparações AMS.

    Retorna:
        df_limpo
        df_metricas_idade
        df_intervalos
        df_modelo_resumo
    """

    # ================================
    # 1. LIMPEZA
    # ================================

    df = df_raw.copy()

    # Datas
    df["data_reparacao"] = pd.to_datetime(df["data_reparacao"], errors="coerce")

    # Idade
    df["idade_meses"] = pd.to_numeric(df["idade_meses"], errors="coerce")

    # Série / modelo
    df["serie"] = df["serie"].astype(str).str.strip()
    df["modelo"] = df["modelo"].astype(str).str.strip().str.upper()

    # Remover inválidos
    df = df.dropna(subset=["serie", "modelo", "data_reparacao", "idade_meses"]).copy()
    df = df[df["idade_meses"] >= 0]
    df = df[df["idade_meses"] < 1000]

    # ================================
    # 2. COLUNAS DERIVADAS
    # ================================

    df["idade_anos"] = df["idade_meses"] / 12
    df["idade_int"] = (df["idade_meses"] // 12).astype(int)

    df["ano_reparacao"] = df["data_reparacao"].dt.year
    df["mes_reparacao"] = df["data_reparacao"].dt.to_period("M").astype(str)

    # ================================
    # 3. MÉTRICAS POR IDADE
    # ================================

    df_metricas_idade = (
        df.groupby(["modelo", "idade_int"])
        .agg(
            reparacoes=("serie", "size"),
            maquinas=("serie", "nunique"),
            custo_total=("custo_reparacao", "sum")
        )
        .reset_index()
    )

    df_metricas_idade["reparacoes_por_maquina"] = (
        df_metricas_idade["reparacoes"] / df_metricas_idade["maquinas"]
    )

    df_metricas_idade["custo_por_maquina"] = (
        df_metricas_idade["custo_total"] / df_metricas_idade["maquinas"]
    )

    # ================================
    # 4. INTERVALO ENTRE REPARAÇÕES
    # ================================

    df_intervalos = df.sort_values(["serie", "data_reparacao"]).copy()

    df_intervalos["dias_entre_reparacoes"] = (
        df_intervalos.groupby("serie")["data_reparacao"]
        .diff()
        .dt.days
    )

    # ================================
    # 5. RESUMO POR MODELO
    # ================================

    df_modelo_resumo = (
        df.groupby("modelo")
        .agg(
            total_reparacoes=("serie", "size"),
            maquinas=("serie", "nunique"),
            custo_total=("custo_reparacao", "sum"),
            idade_media=("idade_anos", "mean")
        )
        .reset_index()
    )

    df_modelo_resumo["reparacoes_por_maquina"] = (
        df_modelo_resumo["total_reparacoes"] / df_modelo_resumo["maquinas"]
    )

    df_modelo_resumo["custo_por_maquina"] = (
        df_modelo_resumo["custo_total"] / df_modelo_resumo["maquinas"]
    )

    return df, df_metricas_idade, df_intervalos, df_modelo_resumo

def gerar_curva_coorte(
    df_limpo: pd.DataFrame,
    idade_coorte_min: int = 10,
    min_maquinas_por_idade: int = 20,
    janela_suavizacao: int = 3,
):
    """
    Gera curva por idade reduzindo viés de sobrevivência.

    Parâmetros
    ----------
    df_limpo : pd.DataFrame
        Base já limpa contendo ao menos:
        - serie
        - modelo
        - idade_int
        - custo_reparacao
        - data_reparacao

    idade_coorte_min : int
        Só entram máquinas que chegaram pelo menos até essa idade.

    min_maquinas_por_idade : int
        Remove idades com poucas máquinas expostas.

    janela_suavizacao : int
        Janela da média móvel.

    Retorna
    -------
    dict com:
        df_obs
        df_coorte
        df_exposicao
        df_falhas
        df_lifecycle
        df_metricas
    """
    
    df = df_limpo.copy()

    # -------------------------------------------------
    # 1. Descobrir até que idade cada máquina chegou
    # -------------------------------------------------
    df_obs = (
        df.groupby(["serie", "modelo"], as_index=False)
        .agg(idade_max=("idade_int", "max"))
    )

    # -------------------------------------------------
    # 2. Filtrar coorte
    # -------------------------------------------------
    series_validas = df_obs.loc[
        df_obs["idade_max"] >= idade_coorte_min, "serie"
    ].unique()

    df_coorte = df[df["serie"].isin(series_validas)].copy()
    df_obs_coorte = df_obs[df_obs["serie"].isin(series_validas)].copy()

    # -------------------------------------------------
    # 3. Criar exposição por idade
    # -------------------------------------------------
    registros = []

    for _, row in df_obs_coorte.iterrows():
        for idade in range(int(row["idade_max"]) + 1):
            registros.append({
                "serie": row["serie"],
                "modelo": row["modelo"],
                "idade_int": idade
            })

    df_exposicao = pd.DataFrame(registros)

    # -------------------------------------------------
    # 4. Marcar falhas por máquina por idade
    # -------------------------------------------------
    df_falhas = (
        df_coorte.groupby(["serie", "modelo", "idade_int"], as_index=False)
        .agg(
            reparacoes=("data_reparacao", "size"),
            custo_total=("custo_reparacao", "sum"),
        )
    )

    df_falhas["teve_falha"] = 1


    # -------------------------------------------------
    # 5. Lifecycle = exposição + falhas
    # -------------------------------------------------
    df_lifecycle = df_exposicao.merge(
        df_falhas,
        on=["serie", "modelo", "idade_int"],
        how="left"
    )

    df_lifecycle["reparacoes"] = df_lifecycle["reparacoes"].fillna(0)
    df_lifecycle["custo_total"] = df_lifecycle["custo_total"].fillna(0)
    df_lifecycle["teve_falha"] = df_lifecycle["teve_falha"].fillna(0)

    # return df_lifecycle

    # -------------------------------------------------
    # 6. Métricas por modelo e idade
    # -------------------------------------------------
    df_metricas = (
        df_lifecycle.groupby(["modelo", "idade_int"], as_index=False)
        .agg(
            maquinas=("serie", "nunique"),
            maquinas_com_falha=("teve_falha", "sum"),
            reparacoes_totais=("reparacoes", "sum"),
            custo_total=("custo_total", "sum"),
        )
    )


    # Probabilidade de falha
    df_metricas["prob_falha"] = np.where(
        df_metricas["maquinas"] > 0,
        df_metricas["maquinas_com_falha"] / df_metricas["maquinas"],
        np.nan
    )

    # Reparações por máquina exposta
    df_metricas["reparacoes_por_maquina"] = np.where(
        df_metricas["maquinas"] > 0,
        df_metricas["reparacoes_totais"] / df_metricas["maquinas"],
        np.nan
    )

    # Custo por máquina exposta
    df_metricas["custo_por_maquina"] = np.where(
        df_metricas["maquinas"] > 0,
        df_metricas["custo_total"] / df_metricas["maquinas"],
        np.nan
    )

    # -------------------------------------------------
    # 7. Cortar idades com pouca amostra
    # -------------------------------------------------
    df_metricas = df_metricas[
        df_metricas["maquinas"] >= min_maquinas_por_idade
    ].copy()

    # -------------------------------------------------
    # 8. Suavização
    # -------------------------------------------------
    df_metricas = df_metricas.sort_values(["modelo", "idade_int"]).reset_index(drop=True)

    df_metricas["prob_falha_suavizada"] = (
        df_metricas.groupby("modelo")["prob_falha"]
        .transform(lambda s: s.rolling(janela_suavizacao, center=True, min_periods=1).mean())
    )

    df_metricas["reparacoes_suavizada"] = (
        df_metricas.groupby("modelo")["reparacoes_por_maquina"]
        .transform(lambda s: s.rolling(janela_suavizacao, center=True, min_periods=1).mean())
    )

    df_metricas["custo_suavizado"] = (
        df_metricas.groupby("modelo")["custo_por_maquina"]
        .transform(lambda s: s.rolling(janela_suavizacao, center=True, min_periods=1).mean())
    )

    return {
        "df_obs": df_obs,
        "df_coorte": df_coorte,
        "df_exposicao": df_exposicao,
        "df_falhas": df_falhas,
        "df_lifecycle": df_lifecycle,
        "df_metricas": df_metricas,
    }
