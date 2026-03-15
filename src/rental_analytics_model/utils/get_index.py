import pandas as pd

def get_index(lista, string):
  for index, item in enumerate(lista):
    if string in item:
      return index