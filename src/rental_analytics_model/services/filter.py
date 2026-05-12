def filter(df, column, lista):
    return df[df[column].isin(lista)].copy()   