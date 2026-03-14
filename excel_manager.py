import pandas as pd

def cargar_excel(ruta):
    df = pd.read_excel(ruta)
    return df


def guardar_excel(df, ruta):
    df.to_excel(ruta, index=False)