import pandas as pd

def br_num(x, casas=2):
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def format_brl(valor, useBRL=False):
    if valor is None:
        return ""
    
    if useBRL:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
def convert_moeda_br_str_to_number(value):
   return float(value.replace('.', '').replace(',', '.'))

def convert_col_df_moeda_br_str_to_number(df, colunas):

    for col in colunas:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
        )

        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def convert_col_df_number_to_moeda_br(df, colunas):

    for col in colunas:
        df[col] = (
            df[col]
            .astype(float)
            .map(lambda x: f"{x:,.2f}")
            .str.replace(",", "X", regex=False)
            .str.replace(".", ",", regex=False)
            .str.replace("X", ".", regex=False)
        )

    return df

def date_br(date):
    return date.strftime('%d/%m/%Y')