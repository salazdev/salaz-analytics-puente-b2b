import pandas as pd

# Detalles del archivo Excel de la Gobernación de Risaralda
archivo_excel = "Precios Unitarios 2025 Infraestructura Construcción V 4 del 9-jul-25.xlsx"

try:
    # Ver las hojas disponibles en el archivo Excel
    xls = pd.ExcelFile(archivo_excel)
    print("Hojas disponibles en el Excel:", xls.sheet_names)

    # Leer la hoja 'BASE DE DATOS'
    df = pd.read_excel(archivo_excel, sheet_name="BASE DE DATOS", skiprows=2)
    print("\nPrimeras filas de la Base de Datos:")
    print(df.head(5))

except Exception as e:
    print("Ocurrió un error al leer el Excel:", e)