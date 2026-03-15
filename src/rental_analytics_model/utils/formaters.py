import pandas as pd

def format_brl(valor):
    if valor is None:
        return ""
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