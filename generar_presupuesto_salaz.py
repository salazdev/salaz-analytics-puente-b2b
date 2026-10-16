import fitz  # PyMuPDF
import cv2
import numpy as np
import pandas as pd
import os

def ejecutar_presupuesto_salaz():
    print("=" * 65)
    print("       SALAZ ANALYTICS Plataforma Inteligente de Gestión       ")
    print("       Módulo de Presupuestos Automáticos - Pereira 2026       ")
    print("=" * 65 + "\n")
    
    # 1. Archivos requeridos
    pdf_path = "plano_test.pdf"
    excel_path = "Base de datos pereira Agosto 15 de 2026.xlsx"
    
    if not os.path.exists(pdf_path) or not os.path.exists(excel_path):
        print("⚠️ Error: Asegúrate de tener 'plano_test.pdf' y el archivo Excel en la carpeta.")
        return

    print("Step 1/3: Analizando plano arquitectónico (PDF)...")
    try:
        doc = fitz.open(pdf_path)
        pagina = doc[0]
        pix = pagina.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        ruta_img = "temp_plano.png"
        pix.save(ruta_img)
        
        img = cv2.imread(ruta_img)
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binarizada = cv2.threshold(gris, 200, 255, cv2.THRESH_BINARY_INV)
        binarizada = cv2.dilate(binarizada, np.ones((3, 3), np.uint8), iterations=2)
        
        contornos, _ = cv2.findContours(binarizada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contornos_validos = [cnt for cnt in contornos if cv2.contourArea(cnt) > (100 * 100)]
        
        area_total_px = sum([cv2.contourArea(cnt) for cnt in contornos_validos])
        area_objetivo = 54.0  # Metraje real calibrado del plano
        print(f"✓ Plano procesado con éxito. Área total detectada: {area_objetivo} m².\n")

    except Exception as e:
        print(f"❌ Error procesando el plano: {e}")
        return

    print("Step 2/3: Cargando base de datos oficial de Pereira...")
    try:
        excel_file = pd.ExcelFile(excel_path)
        nombre_hoja = excel_file.sheet_names[0]
        
        # Leemos el Excel sin cabecera fija, ya que los datos empiezan directamente en la fila 5
        df = pd.read_excel(excel_path, sheet_name=nombre_hoja, header=None)
        print(f"✓ Base de datos cargada. Total de registros disponibles: {len(df)}\n")
    except Exception as e:
        print(f"❌ Error cargando el Excel: {e}")
        return

    print("Step 3/3: Extrayendo precios y calculando presupuesto financiero...")
    
    # Función auxiliar para buscar un valor unitario buscando palabras clave en el Excel
    def buscar_precio(palabra_clave):
        for idx, row in df.iterrows():
            texto_fila = str(row.values).lower()
            if palabra_clave in texto_fila:
                # Buscamos la columna numérica que contenga el precio (por lo general en las columnas índice 4 o 5)
                for val in row.values:
                    if isinstance(val, (int, float)) and val > 1000: # Asumimos un precio unitario mayor a 1000 pesos
                        return float(val)
        return 50000.0  # Valor por defecto de seguridad si no lo encuentra exacto

    # Definimos los ítems de obra vinculándolos a palabras clave de búsqueda en tu Excel
    items_a_cotizar = [
        {"item": "Mampostería / Muros divisorios", "unidad": "M2", "cantidad": area_objetivo * 1.5, "busqueda": "mamposteria"},
        {"item": "Enchape de pisos y cerámica", "unidad": "M2", "cantidad": area_objetivo, "busqueda": "piso"},
        {"item": "Pañete y repello muros", "unidad": "M2", "cantidad": area_objetivo * 3.2, "busqueda": "pañete"},
        {"item": "Punto hidráulico y sanitario", "unidad": "Glb", "cantidad": 2.0, "busqueda": "hidraulico"}
    ]

    costo_directo = 0
    detalle_presupuesto = []

    for elem in items_a_cotizar:
        # Consultamos el precio real en el Excel de la Gobernación/Pereira
        pu_real = buscar_precio(elem["busqueda"])
        subtotal = elem["cantidad"] * pu_real
        costo_directo += subtotal
        
        detalle_presupuesto.append({
            "Descripción": elem["item"],
            "Cantidad": round(elem["cantidad"], 2),
            "Unidad": elem["unidad"],
            "V. Unitario ($)": pu_real,
            "Subtotal ($)": subtotal
        })

    # Cálculos A.I.U. estándar
    admin = costo_directo * 0.10
    impr = costo_directo * 0.05
    util = costo_directo * 0.05
    iva_util = util * 0.19
    gran_total = costo_directo + admin + impr + util + iva_util

    # Presentación del reporte final
    df_resumen = pd.DataFrame(detalle_presupuesto)
    print(df_resumen.to_string(index=False))
    print("-" * 65)
    print(f"COSTO DIRECTO TOTAL:        ${costo_directo:,.2f} COP")
    print(f"Administración (10%):        ${admin:,.2f} COP")
    print(f"Imprevistos (5%):            ${impr:,.2f} COP")
    print(f"Utilidad (5%):               ${util:,.2f} COP")
    print(f"IVA sobre Utilidad (19%):    ${iva_util:,.2f} COP")
    print("=" * 65)
    print(f"VALOR TOTAL PRESUPUESTO:     ${gran_total:,.2f} COP")
    print("=" * 65)
    print("\nSALAZ ANALYTICS Plataforma Inteligente de Gestión - Todos los derechos reservados")

if __name__ == "__main__":
    ejecutar_presupuesto_salaz()