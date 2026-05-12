import re
import numpy as np
import pandas as pd
import streamlit as st

from rental_analytics_model.constants.rental_analytics_constantes import (
    MODELOS_ROMPEDOR_VALIDOS,
    COL_RENAME_REPAROS,
    COLS_REPAROS_FINAL
)

def modelo_para_regex(modelo: str) -> str:
    partes = re.findall(r'[a-z]+|\d+', modelo.lower())
    return r'[\s-]*'.join(map(re.escape, partes)) + r'\b'


@st.cache_data
def identificar_familia_modelo(
    df: pd.DataFrame,
    coluna_texto: str,
    familias_modelos: dict[str, list[str]],
    coluna_familia: str = 'familia',
    coluna_modelo: str = 'modelo_identificado',
    enviar_nulos: bool = False
) -> pd.DataFrame:

    df = df.copy()

    col_norm = (
        df[coluna_texto]
        .fillna('')
        .astype(str)
        .str.lower()
        .str.replace(r'[^a-z0-9]+', ' ', regex=True)
        .str.strip()
    )

    df[coluna_familia] = None
    df[coluna_modelo] = None

    pares = []
    for familia, modelos in familias_modelos.items():
        for modelo in modelos:
            pares.append((familia, modelo.lower(), modelo_para_regex(modelo)))

    # modelos mais específicos primeiro
    pares.sort(key=lambda x: len(x[1].replace(' ', '').replace('-', '')), reverse=True)

    for familia, modelo_original, pattern in pares:
        mask = (
            col_norm.str.contains(pattern, regex=True, na=False)
            & df[coluna_modelo].isna()
        )

        df.loc[mask, coluna_familia] = familia
        df.loc[mask, coluna_modelo] = modelo_original

    if enviar_nulos: return df[df.isna().any(axis=1)]

    return df[df[coluna_modelo].notna()].copy()
    # return df


@st.cache_data(show_spinner=False)
def normalizar_material(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["material_norm"] = (
        df["Nome do Material"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.replace(r"[^a-z0-9]", "", regex=True)
    )
    return df


@st.cache_data(show_spinner=False)
def preparar_base_filtro(
    df_resultado: pd.DataFrame,
    df_vips_excel: pd.DataFrame,
) -> pd.DataFrame:
    df = df_resultado.copy()

    col_index = df.columns.get_loc("Cliente")

    df.insert(
        loc=col_index,
        column="id",
        value=df["Cliente"].astype(str).str.partition(" - ")[0],
    )

    df["Cliente"] = df["Cliente"].astype(str).str.partition("-")[2].str.strip()

    df_vips_excel = df_vips_excel.copy()
    df_vips_excel["id conta"] = df_vips_excel["id conta"].astype(str)

    df = df.merge(
        df_vips_excel,
        how="left",
        left_on="id",
        right_on="id conta",
    )

    df['idade_int'] = np.floor(df['Idade em Anos']).astype(int)

    cols_drop = [col for col in ["id conta", "nome"] if col in df.columns]
    if cols_drop:
        df.drop(columns=cols_drop, inplace=True)

    cols_ordem = ["nome hierarquia", "nó hierarquia"]
    cols_existentes = [col for col in cols_ordem if col in df.columns]
    demais_cols = [col for col in df.columns if col not in cols_existentes]
    df = df[cols_existentes + demais_cols]

    return df


def aplicar_filtros(
    df: pd.DataFrame,
    hierarquia: str = "",
    ano_reparo: int = 0,
    ano_reparo_max: int = 0,
    familia: str = "",
    modelo: str = "",
    idade_minima="",
    idade_maxima="",
) -> pd.DataFrame:
    df = df.copy()

    if hierarquia and "nome hierarquia" in df.columns:
        df = df[
            df["nome hierarquia"].fillna("").str.contains(hierarquia, case=False, na=False)
        ]

    if familia and "familia" in df.columns:
        df = df[
            df["familia"].fillna("").str.contains(familia, case=False, na=False)
        ]

    if ano_reparo and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"] >= ano_reparo
        ]

    if ano_reparo_max and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"] <= ano_reparo_max
        ]

    df = df.rename(columns={"modelo_identificado": "modelo"})

    if modelo and "modelo" in df.columns:
        df = df[
            df["modelo"].fillna("").str.contains(modelo, case=False, na=False)
        ]

    if idade_minima != "" and "idade_int" in df.columns:
        df = df[df["idade_int"] >= idade_minima]

    if idade_maxima != "" and "idade_int" in df.columns:
        df = df[df["idade_int"] <= idade_maxima]

    return df.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def preparar_df_filter(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # df['idade_int'] = np.floor(df['Idade em Anos']).astype(int)
    df.rename(columns=COL_RENAME_REPAROS, inplace=True)

    df = (
        df
        .groupby(['modelo', 'Número de Série', 'Idade em Anos', 'idade_int'], as_index=False)
        .agg({
            'falhas': 'sum',
            '# Reparos': 'sum',
            'custo_total': 'sum',
            'custo_cliente': 'sum',
            'economia': 'sum'
        })
    )

    df.sort_values(['idade_int', 'falhas'], inplace=True)

    return df[COLS_REPAROS_FINAL]


@st.cache_data(show_spinner=False)
def agrupar_por_idade(df_filter: pd.DataFrame) -> pd.DataFrame:
    df = df_filter.copy()
    df = df.rename(columns={"Idade em Anos": "idade_anos_frac"})
    df["idade_int"] = np.floor(df["idade_anos_frac"]).astype(int)

    # df = pd.DataFrame({
    #     "idade_int": [1, 1, 2, 2, 3, 3],
    #     "falhas":    [0, 1, 1, 2, 2, 4],
    #     "qtd":       [50, 50, 40, 60, 30, 70]
    # })    

    df = (
        df.groupby(["idade_int", "falhas"])
        .size()
        .reset_index(name="qtd")
    )

    df_media = (
        df.groupby("idade_int")
        .apply(lambda g: (g["falhas"] * g["qtd"]).sum() / g["qtd"].sum())
        .reset_index(name="falhas_acumuladas_media")
        .sort_values("idade_int")
    )

    df_media["falhas_no_ano"] = df_media["falhas_acumuladas_media"].diff()

    df_media.loc[df_media["idade_int"] == 1, "falhas_no_ano"] = df_media["falhas_acumuladas_media"]

    df_media["falhas_no_ano_suavizada"] = (
        df_media["falhas_no_ano"]
        .rolling(3, min_periods=1)
        .mean()
    )    

    # df_aux = df_agg.copy()
    # df_aux["falhas_totais_grupo"] = df_aux["falhas"] * df_aux["qtd"]

    # df_media = (
    #     df_aux.groupby("idade_int")
    #     .agg(
    #         falhas_totais=("falhas_totais_grupo", "sum"),
    #         maquinas_totais=("qtd", "sum")
    #     )
    #     .reset_index()
    # )

    # df_media["media_falhas_por_maquina"] = (
    #     df_media["falhas_totais"] / df_media["maquinas_totais"]
    # )    

    # df = (
    #     df.groupby("idade_int", as_index=False)
    #     .agg(
    #         qtd=("Número de Série", "count"),
    #         falhas=("falhas", "sum"),
    #         reparos=("# Reparos", "sum"),
    #         custo_total=("custo_total", "sum"),
    #         custo_cliente=("custo_cliente", "sum"),
    #         economia=("economia", "sum"),
    #     )
    #     .sort_values("idade_int")
    #     .reset_index(drop=True)
    # )

    # df_media = (
    #     df.groupby("idade_int")
    #     .apply(lambda g: (g["falhas"] * g["qtd"]).sum() / g["qtd"].sum())
    #     .reset_index(name="falhas_acumuladas_media")
    #     .sort_values("idade_int")
    # )

    # df_media["falhas_no_ano"] = df_media["falhas_acumuladas_media"].diff()

    # df_media["falhas_no_ano_suavizada"] = (
    #     df_media["falhas_no_ano"]
    #     .rolling(3, min_periods=1)
    #     .mean()
    # )    

    return df_media


def validar_df_group_idade(df_group_idade: pd.DataFrame) -> tuple[bool, str]:
    if df_group_idade.empty:
        return False, "Sem dados após os filtros aplicados."

    obrigatorias = {"idade_int", "falhas", "qtd", "reparos", "custo_total"}
    faltantes = obrigatorias - set(df_group_idade.columns)

    if faltantes:
        return False, f"Colunas obrigatórias ausentes: {', '.join(sorted(faltantes))}"

    return True, ""


def calcular_taxa_falha(df_group_idade: pd.DataFrame) -> pd.DataFrame:
    df = df_group_idade.copy()
    df["taxa_falha"] = np.where(df["qtd"] > 0, df["falhas"] / df["qtd"], np.nan)
    return df


def _garantir_coluna_modelo(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "modelo" not in df.columns and "modelo_identificado" in df.columns:
        df = df.rename(columns={"modelo_identificado": "modelo"})
    return df


def listar_hierarquias(df_base: pd.DataFrame) -> list:
    df = df_base.copy()

    opcoes = [""]
    if "nome hierarquia" in df.columns:
        valores = df["nome hierarquia"].dropna().astype(str).sort_values().unique().tolist()
        opcoes.extend(valores)

    return opcoes


def listar_anos_reparo_por_hierarquia(
    df_base: pd.DataFrame,
    hierarquia: str = "",
    familia: str = "",        
) -> list:
    df = df_base.copy()

    # return [hierarquia]

    if hierarquia and "nome hierarquia" in df.columns:
        df = df[
            df["nome hierarquia"].fillna("").str.contains(hierarquia, case=False, na=False)
        ].copy()

    opcoes = [""]
    if "ano_reparo" in df.columns:
        valores = df["ano_reparo"].dropna().astype(int).sort_values().unique().tolist()
        opcoes.extend(valores)

    return opcoes


def listar_anos_reparo_max_por_filtro(
    df_base: pd.DataFrame,
    hierarquia: str = "",
    ano_reparo: int = 0
) -> list:
    df = df_base.copy()

    if hierarquia and "nome hierarquia" in df.columns:
        df = df[
            df["nome hierarquia"].fillna("").str.contains(hierarquia, case=False, na=False)
        ].copy()

    if ano_reparo and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"] >= ano_reparo
        ].copy()

    opcoes = [""]
    if "ano_reparo" in df.columns:
        valores = df["ano_reparo"].dropna().astype(int).sort_values().unique().tolist()
        opcoes.extend(valores)

    return opcoes        


def listar_familias_por_filtros(
    df_base: pd.DataFrame,
    hierarquia: str = "",
    ano_reparo: int = 0,
    ano_reparo_max: int = 0,
) -> list:
    df = df_base.copy()

    if hierarquia and "nome hierarquia" in df.columns:
        df = df[
            df["nome hierarquia"].fillna("").str.contains(hierarquia, case=False, na=False)
        ].copy()

    if ano_reparo and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"].fillna("") >= ano_reparo
        ].copy()

    if ano_reparo_max and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"].fillna("") <= ano_reparo_max
        ].copy()

    opcoes = [""]
    if "familia" in df.columns:
        valores = df["familia"].dropna().astype(str).sort_values().unique().tolist()
        opcoes.extend(valores)

    return opcoes


def listar_modelos_por_filtros(
    df_base: pd.DataFrame,
    hierarquia: str = "",
    ano_reparo: int = 0,
    ano_reparo_max: int = 0,
    familia: str = "",
) -> list:
    df = df_base.copy()
    df = _garantir_coluna_modelo(df)

    if hierarquia and "nome hierarquia" in df.columns:
        df = df[
            df["nome hierarquia"].fillna("").str.contains(hierarquia, case=False, na=False)
        ].copy()

    if ano_reparo and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"].fillna("") >= ano_reparo
        ].copy()

    if ano_reparo_max and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"].fillna("") <= ano_reparo_max
        ].copy()

    if familia and "familia" in df.columns:
        df = df[
            df["familia"].fillna("").str.contains(familia, case=False, na=False)
        ].copy()

    # if familia == "rompedor" and "modelo" in df.columns:
    #     df = df[df["modelo"].isin(MODELOS_ROMPEDOR_VALIDOS)].copy()

    opcoes = [""]
    if "modelo" in df.columns:
        valores = df["modelo"].dropna().astype(str).sort_values().unique().tolist()
        opcoes.extend(valores)

    return opcoes


def listar_idades_por_filtros(
    df_base: pd.DataFrame,
    hierarquia: str = "",
    ano_reparo: int = 0,
    ano_reparo_max: int = 0,
    familia: str = "",
    modelo: str = "",
) -> list:
    df = df_base.copy()

    # garantir modelo
    if "modelo" not in df.columns and "modelo_identificado" in df.columns:
        df = df.rename(columns={"modelo_identificado": "modelo"})

    if hierarquia and "nome hierarquia" in df.columns:
        df = df[
            df["nome hierarquia"].fillna("").str.contains(hierarquia, case=False, na=False)
        ]

    if ano_reparo and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"].fillna("") >= ano_reparo
        ].copy()

    if ano_reparo_max and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"].fillna("") <= ano_reparo_max
        ].copy()

    if familia and "familia" in df.columns:
        df = df[
            df["familia"].fillna("").str.contains(familia, case=False, na=False)
        ]

    if modelo and "modelo" in df.columns:
        df = df[
            df["modelo"].fillna("").str.contains(modelo, case=False, na=False)
        ]

    # aqui entra sua nova coluna
    opcoes = [""]
    if "idade_int" in df.columns:
        valores = sorted(df["idade_int"].dropna().unique().tolist())
        opcoes.extend(valores)

    return opcoes


def listar_idades_maximas_por_filtros(
    df_base: pd.DataFrame,
    hierarquia: str = "",
    ano_reparo: int = 0,
    ano_reparo_max: int = 0,
    familia: str = "",
    modelo: str = "",
    idade_minima="",
) -> list:
    df = df_base.copy()

    if "modelo" not in df.columns and "modelo_identificado" in df.columns:
        df = df.rename(columns={"modelo_identificado": "modelo"})

    if hierarquia and "nome hierarquia" in df.columns:
        df = df[
            df["nome hierarquia"].fillna("").str.contains(hierarquia, case=False, na=False)
        ]

    if ano_reparo and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"].fillna("") >= ano_reparo
        ].copy()

    if ano_reparo_max and "ano_reparo" in df.columns:
        df = df[
            df["ano_reparo"].fillna("") <= ano_reparo_max
        ].copy()

    if familia and "familia" in df.columns:
        df = df[
            df["familia"].fillna("").str.contains(familia, case=False, na=False)
        ]

    if modelo and "modelo" in df.columns:
        df = df[
            df["modelo"].fillna("").str.contains(modelo, case=False, na=False)
        ]

    if "idade_int" not in df.columns:
        return [""]

    valores = sorted(df["idade_int"].dropna().unique().tolist())

    if idade_minima != "":
        valores = [idade for idade in valores if idade >= idade_minima]

    opcoes = [""]
    opcoes.extend(valores)
    return opcoes

