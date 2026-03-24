import pandas as pd
from pathlib import Path

def get_project_root():
    return Path(__file__).resolve().parents[3]

def load_normal_itens()-> pd.DataFrame:
    file_path = get_project_root() / 'data' / 'normal_itens.json'
    return pd.read_json(file_path)