import pandas as pd
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

def format_brl(valor):
    return locale.format_string("%.2f", valor, grouping=True)

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