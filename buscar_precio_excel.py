import pandas as pd
import os

def encontrar_fila_exacta():
    archivo_excel = "Base de datos pereira Agosto 15 de 2026.xlsx"
    excel_file = pd.ExcelFile(archivo_excel)
    nombre_hoja = excel_file.sheet_names[0]
    
    # Leemos sin omitir nada para ver las filas del 4 al 12
    df_bruto = pd.read_excel(archivo_excel, sheet_name=nombre_hoja, header=None)
    
    print("--- VISTA PREVIA DE LAS FILAS 4 A 10 ---")
    for i in range(4, 11):
        if i < len(df_bruto):
            print(f"Fila {i}: {df_bruto.iloc[i].values[:6]}...")

if __name__ == "__main__":
    encontrar_fila_exacta()