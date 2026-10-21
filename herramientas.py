import pandas as pd
from crewai.tools import tool
from crewai import Agent, Task, Crew

EXCEL_PATH = "Base de datos pereira Agosto 15 de 2026.xlsx"

def _cargar_catalogo():
    """Lee el catálogo Excel y devuelve un DataFrame limpio."""
    try:
        excel_file = pd.ExcelFile(EXCEL_PATH)
        df = pd.read_excel(EXCEL_PATH, sheet_name=excel_file.sheet_names[0], header=None)
        return df
    except Exception as e:
        print(f"Error cargando catálogo: {e}")
        return None

@tool("Buscar precio de material")
def buscar_precio_material(palabra_clave: str, ferreteria: str = "Aliada A") -> str:
    """
    Busca el precio unitario oficial de un material de construcción en la base de datos de Pereira.
    
    Args:
        palabra_clave: El nombre del material o insumo (ej: 'mamposteria', 'cemento', 'piso').
        ferreteria: La ferretería objetivo ('Aliada A' para Ferretería Central o 'Aliada B' para Constructodo).
    """
    df = _cargar_catalogo()
    if df is None:
        return "Error: No se pudo acceder a la base de datos de precios."

    # Factor de descuento o ajuste según la ferretería aliada
    multiplicador = 1.0 if "Aliada A" in ferreteria else 0.96
    palabra = palabra_clave.lower().strip()
    
    for idx, row in df.iterrows():
        texto_fila = str(row.values).lower()
        if palabra in texto_fila:
            for val in row.values:
                if isinstance(val, (int, float)) and val > 1000:
                    precio_final = float(val) * multiplicador
                    return f"Material: '{palabra_clave}' | Ferretería: {ferreteria} | Precio Unitario: ${precio_final:,.2f} COP"

    precio_base = 50000.0 * multiplicador
    return f"Material: '{palabra_clave}' (Precio estimado base) | Ferretería: {ferreteria} | Precio Unitario: ${precio_base:,.2f} COP"