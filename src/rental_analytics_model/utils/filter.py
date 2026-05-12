import pandas as pd

def filter_df(df: pd.DataFrame, columa: str, lista: list):
    return df[df[columa].isin(lista)]