def get_index(lista, string):
  for index, item in enumerate(lista):
    if string in item:
      return index
    
def converter_moeda_br(df, colunas):

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