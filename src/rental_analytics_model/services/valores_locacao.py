import pandas as pd
import hashlib

def load_xlsx(xls_files):
    return pd.read_excel(xls_files[0])