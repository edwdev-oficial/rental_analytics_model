import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures


def prever_curva_modelo(
    df_metricas: pd.DataFrame,
    modelo: str,
    alvo: str = "prob_falha_suavizada",
    grau_polinomio: int = 2,
    idade_max_previsao: int | None = None,
    clip_lower: float | None = 0,
):
    """
    Gera previsão polinomial para um modelo específico.

    Parâmetros
    ----------
    df_metricas : pd.DataFrame
        Saída de gerar_curva_coorte()['df_metricas'].

    modelo : str
        Ex.: 'TE-500'

    alvo : str
        Coluna a prever. Exemplos:
        - 'prob_falha_suavizada'
        - 'reparacoes_suavizada'
        - 'custo_suavizado'

    grau_polinomio : int
        Grau do polinômio. Recomendo 2 ou 3.

    idade_max_previsao : int | None
        Idade máxima da previsão.
        Se None, usa idade máxima observada + 3.

    clip_lower : float | None
        Limite inferior para cortar previsões negativas.
        Use 0 para probabilidade, reparações e custo.

    Retorna
    -------
    dict com:
        df_modelo
        df_pred
        model
    """

    df_modelo = df_metricas[df_metricas["modelo"] == modelo].copy()

    if df_modelo.empty:
        raise ValueError(f"Nenhum dado encontrado para o modelo {modelo}")

    if alvo not in df_modelo.columns:
        raise ValueError(f"Coluna alvo '{alvo}' não existe em df_metricas")

    df_modelo = df_modelo.dropna(subset=["idade_int", alvo]).copy()

    if df_modelo.empty:
        raise ValueError(f"Sem dados válidos para prever '{alvo}' no modelo {modelo}")

    X = df_modelo[["idade_int"]]
    y = df_modelo[alvo]

    model = make_pipeline(
        PolynomialFeatures(degree=grau_polinomio, include_bias=False),
        LinearRegression()
    )

    model.fit(X, y)

    idade_max_obs = int(df_modelo["idade_int"].max())
    if idade_max_previsao is None:
        idade_max_previsao = idade_max_obs + 3

    idades = np.arange(int(df_modelo["idade_int"].min()), idade_max_previsao + 1)
    X_pred = pd.DataFrame({"idade_int": idades})

    pred = model.predict(X_pred)

    df_pred = pd.DataFrame({
        "modelo": modelo,
        "idade_int": idades,
        "valor_previsto": pred
    })

    if clip_lower is not None:
        df_pred["valor_previsto"] = df_pred["valor_previsto"].clip(lower=clip_lower)

    return {
        "df_modelo": df_modelo.reset_index(drop=True),
        "df_pred": df_pred.reset_index(drop=True),
        "model": model,
    }
