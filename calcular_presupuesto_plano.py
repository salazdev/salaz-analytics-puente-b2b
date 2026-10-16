import pandas as pd
import os

def calcular_presupuesto():
    print("--- INICIANDO MOTOR DE PRESUPUESTO DESDE PLANO ---\n")
    
    # 1. Cargar el archivo Excel de Precios Unitarios
    archivo_excel = "Precios Unitarios 2025 Infraestructura Construcción V 4 del 9-jul-25.xlsx"
    
    if not os.path.exists(archivo_excel):
        print(f"Error: No se encuentra el archivo '{archivo_excel}' en la carpeta.")
        return

    print("Cargando base de datos de precios unitarios...")
    # Leemos la hoja de construcción o base de datos (ajustamos skiprows según la estructura del Excel)
    df_precios = pd.read_excel(archivo_excel, sheet_name="CONSTRUCCION", skiprows=3)
    
    # Limpiamos columnas vacías si las hay
    df_precios = df_precios.dropna(subset=[df_precios.columns[0]])
    print(f"¡Base de precios cargada con éxito! ({len(df_precios)} filas disponibles).\n")

    # 2. Simulación de Metrados extraídos del Plano (Lo que arrojó nuestro OpenCV / IA)
    # Supongamos que nuestro plano de prueba detectó los siguientes espacios y cantidades:
    mediciones_plano = [
        {"elemento": "Muros en mampostería", "unidad": "m2", "cantidad": 45.50, "codigo_ref": "MURO01"},
        {"elemento": "Pisos / Enchape cerámico", "unidad": "m2", "cantidad": 38.00, "codigo_ref": "PISO02"},
        {"elemento": "Pintura pared interior", "unidad": "m2", "cantidad": 90.00, "codigo_ref": "PINT01"}
    ]

    print("--- 1. METRADOS DETECTADOS EN EL PLANO ---")
    for item in mediciones_plano if 'medicions_plano' in locals() else mediciones_plano:
        print(f"• {item['elemento']}: {item['cantidad']} {item['unidad']}")
    print("-" * 45)

    # 3. Liquidación y cálculo de costos (Simulando la búsqueda de precios unitarios)
    # (Para esta prueba inicial, asignamos un valor unitario de referencia o lo buscamos en el Excel)
    print("\n--- 2. LIQUIDACIÓN Y PRESUPUESTO DIRECTO ---")
    
    costo_directo_total = 0
    presupuesto_final = []

    # Precios unitarios de ejemplo basados en el estándar de la región (pueden extraerse directamente del Excel)
    tarifas_ejemplo = {
        "MURO01": 65000.00,  # Costo por m2 de muro instalado
        "PISO02": 52000.00,  # Costo por m2 de piso
        "PINT01": 18500.00   # Costo por m2 de pintura
    }

    for item in mediciones_plano:
        codigo = item["codigo_ref"]
        # Buscamos el precio unitario (si no está en el diccionario, usamos un estimado)
        pu = tarifas_ejemplo.get(codigo, 45000.00) 
        subtotal = item["cantidad"] * pu
        costo_directo_total += subtotal

        presupuesto_final.append({
            "Actividad": item["elemento"],
            "Cantidad": item["cantidad"],
            "Unidad": item["unidad"],
            "Costo Unitario ($)": pu,
            "Subtotal ($)": subtotal
        })

    # Mostrar tabla de resultados en consola de forma ordenada
    df_resultado = pd.DataFrame(presupuesto_final)
    print(df_resultado.to_string(index=False))
    print("=" * 45)
    print(f"COSTO DIRECTO TOTAL: ${costo_directo_total:,.2f} COP")

    # 4. Cálculo de A.I.U. (Administración, Imprevistos, Utilidad)
    administracion = costo_directo_total * 0.10  # 10%
    imprevistos = costo_directo_total * 0.05     # 5%
    utilidad = costo_directo_total * 0.05        # 5%
    iva_utilidad = utilidad * 0.19               # 19% IVA sobre la utilidad
    
    gran_total = costo_directo_total + administracion + imprevistos + utilidad + iva_utilidad

    print("\n--- 3. RESUMEN FINANCIERO CON A.I.U. ---")
    print(f"• Costo Directo:      ${costo_directo_total:,.2f}")
    print(f"• Administración (10%): ${administracion:,.2f}")
    print(f"• Imprevistos (5%):    ${imprevistos:,.2f}")
    print(f"• Utilidad (5%):       ${utilidad:,.2f}")
    print(f"• IVA sobre Utilidad:  ${iva_utilidad:,.2f}")
    print(f"=========================================")
    print(f"VALOR TOTAL PRESUPUESTO: ${gran_total:,.2f} COP")
    print("=========================================")

if __name__ == "__main__":
    calcular_presupuesto()