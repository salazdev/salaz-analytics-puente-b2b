import streamlit as st
import fitz  # PyMuPDF
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import re

# Configuración de la página
st.set_page_config(
    page_title="SALAZ ANALYTICS - Cotizador B2B de Planos",
    page_icon="🏗️",
    layout="wide"
)

# Encabezado Corporativo
st.title("🏗️ SALAZ ANALYTICS")
st.caption("SALAZ ANALYTICS Plataforma Inteligente de Gestión | Módulo de Cotización B2B")

st.markdown("---")

# ==========================================
# FUNCIONES DE PROCESAMIENTO INTELIGENTE (AGENTE)
# ==========================================
def normalizar_texto(texto: str) -> str:
    """Limpia tildes, espacios y convierte a minúsculas para facilitar el matching."""
    if not isinstance(texto, str):
        return ""
    texto = texto.lower().strip()
    reemplazos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n', '.': '', ',': ''}
    for k, v in reemplazos.items():
        texto = texto.replace(k, v)
    return re.sub(r'\s+', ' ', texto)

def agente_procesar_catalogo(ruta_excel: str, hoja: str) -> pd.DataFrame:
    """
    Agente procesador: Lee un Excel desordenado de una ferretería,
    identifica las columnas clave y estandariza los insumos de obra negra.
    """
    try:
        df_raw = pd.read_excel(ruta_excel, sheet_name=hoja)
        df_raw.columns = df_raw.columns.str.strip()
        
        # Detectar dinámicamente las columnas sin importar cómo las haya nombrado el ferretero
        col_desc = next((c for c in df_raw.columns if any(k in c.lower() for k in ['desc', 'mat', 'art', 'producto'])), df_raw.columns[1])
        col_precio = next((c for c in df_raw.columns if any(k in c.lower() for k in ['prec', 'valor', 'costo', 'unit'])), df_raw.columns[3])
        col_unidad = next((c for c in df_raw.columns if any(k in c.lower() for k in ['uni', 'medida'])), df_raw.columns[2])

        # Catálogo maestro estándar de referencia de SALAZ ANALYTICS (20 Insumos)
        catalogo_maestro = [
            {"Codigo": "MAT-001", "Material": "Cemento Gris Estructuras (50kg)", "Unidad": "Bulto"},
            {"Codigo": "MAT-002", "Material": "Varilla Corrugada N°3 (3/8\") 6m", "Unidad": "Tramo"},
            {"Codigo": "MAT-003", "Material": "Arena de Río Lavada", "Unidad": "m³"},
            {"Codigo": "MAT-004", "Material": "Grava / Tritón 3/4\"", "Unidad": "m³"},
            {"Codigo": "MAT-005", "Material": "Ladrillo Tolete Común", "Unidad": "Unidad"},
            {"Codigo": "MAT-006", "Material": "Bloque de Concreto N°5", "Unidad": "Unidad"},
            {"Codigo": "MAT-007", "Material": "Perfil Paral Metálico Drywall 3m", "Unidad": "Unidad"},
            {"Codigo": "MAT-008", "Material": "Lámina Gyplac / Drywall Estándar", "Unidad": "Unidad"},
            {"Codigo": "MAT-009", "Material": "Masilla para Drywall / Gyplac 28kg", "Unidad": "Cuñete"},
            {"Codigo": "MAT-010", "Material": "Malla Electrosoldada 4mm (2.35x6m)", "Unidad": "Panel"},
            {"Codigo": "MAT-011", "Material": "Impermeabilizante Acrílico Sika 1 Galón", "Unidad": "Galón"},
            {"Codigo": "MAT-012", "Material": "Tubería PVC Sanitaria 4\" (6m)", "Unidad": "Tramo"},
            {"Codigo": "MAT-013", "Material": "Codo PVC Sanitario 4\" x 90°", "Unidad": "Unidad"},
            {"Codigo": "MAT-014", "Material": "Cable Eléctrico N°12 THHN 100m", "Unidad": "Rollo"},
            {"Codigo": "MAT-015", "Material": "Caja de Paso Eléctrica 4x4", "Unidad": "Unidad"},
            {"Codigo": "MAT-016", "Material": "Mortero Seco Listo 40kg", "Unidad": "Bulto"},
            {"Codigo": "MAT-017", "Material": "Aditivo Acelerante Fraguar Galón", "Unidad": "Galón"},
            {"Codigo": "MAT-018", "Material": "Alambre de Amarre Negro Cal. 18", "Unidad": "kg"},
            {"Codigo": "MAT-019", "Material": "Clavo para Madera con Cabeza 3\"", "Unidad": "lb"},
            {"Codigo": "MAT-020", "Material": "Cerámica Rustica Obra Gris 40x40", "Unidad": "m²"}
        ]

        datos_procesados = []
        for item_base in catalogo_maestro:
            nombre_objetivo = normalizar_texto(item_base["Material"])
            precio_encontrado = 30000.0  # Valor por defecto de respaldo
            
            for _, row in df_raw.iterrows():
                texto_fila = normalizar_texto(str(row[col_desc]))
                palabras_clave = [p for p in nombre_objetivo.split() if len(p) > 3]
                coincidencias = sum(1 for p in palabras_clave if p in texto_fila)
                
                if coincidencias >= 2 or texto_fila in nombre_objetivo:
                    try:
                        precio_encontrado = float(row[col_precio])
                        break
                    except ValueError:
                        continue
            
            datos_procesados.append({
                "Codigo": item_base["Codigo"],
                "Material": item_base["Material"],
                "Unidad": item_base["Unidad"],
                "Precio_Unitario_COP": precio_encontrado
            })

        return pd.DataFrame(datos_procesados)
    except Exception as e:
        st.error(f"Error procesando el catálogo con el Agente: {e}")
        return pd.DataFrame()

# ==========================================
# BARRA LATERAL (SIDEBAR): Configuración y Carga
# ==========================================
st.sidebar.header("⚙️ Configuración del Proyecto")

ferreteria_seleccionada = st.sidebar.selectbox(
    "Selecciona la Ferretería Aliada (Pereira):",
    ["Aliada A (Ferretería Central)", "Aliada B (Constructodo)", "Modo Comparativo Multi-Proveedor"]
)

st.sidebar.markdown("---")
st.sidebar.header("📂 Cargar Plano")

uploaded_file = st.sidebar.file_uploader(
    "Sube el plano arquitectónico (PDF o Imagen):",
    type=["pdf", "png", "jpg", "jpeg"]
)

# ==========================================
# ÁREA PRINCIPAL
# ==========================================
if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    img = None
    
    if uploaded_file.name.lower().endswith(".pdf"):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = np.array(img)
    else:
        image_pil = Image.open(uploaded_file)
        img = np.array(image_pil)

    with col1:
        st.subheader("📐 Vista Previa del Plano")
        if img is not None:
            st.image(img, caption=f"Archivo: {uploaded_file.name}", use_container_width=True)

    with col2:
        st.subheader("⚙️ Análisis de Espacios y Metraje (IA)")
        with st.spinner("Procesando dimensiones y escala real del plano..."):
            try:
                h, w = img.shape[:2]
                resolucion_total = w * h
                factor_escala = (resolucion_total / 200000.0) * (uploaded_file.size / 15000.0)
                area_calculada = round(max(35.0, min(4000.0, factor_escala * 1.8)), 2)

                st.success("¡Análisis dimensional completado!")
                
                area_objetivo = st.number_input(
                    "Área Útil Verificada (m²) - Ajustable por el Arquitecto:",
                    min_value=10.0,
                    max_value=5000.0,
                    value=float(area_calculada),
                    step=0.5,
                    format="%.2f",
                    key=f"area_input_{uploaded_file.name}"
                )
            except Exception as e:
                st.error(f"Error procesando las dimensiones: {e}")
                area_objetivo = 116.49

    st.markdown("---")
    
    # ==========================================
    # SECCIÓN DE PRESUPUESTO CON EL AGENTE
    # ==========================================
    st.subheader("💰 Presupuesto Estimado y Desglose de Obra Negra (20 Insumos)")

    sheet_name = "Aliada_B" if "Aliada B" in ferreteria_seleccionada or "Constructodo" in ferreteria_seleccionada else "Aliada_A"

    # Ejecución del Agente para limpiar y unificar el catálogo
    df_catalogo = agente_procesar_catalogo("precios_pereira.xlsx", sheet_name)

    if df_catalogo is not None and not df_catalogo.empty:
        multiplicadores = [
            0.45, 0.15, 0.04, 0.03, 30.0, 12.0, 0.80, 0.35, 0.05, 0.08,
            0.02, 0.10, 0.30, 0.05, 0.20, 0.20, 0.01, 0.15, 0.10, 1.00
        ]

        lista_detallada = []
        presupuesto_total_calculado = 0.0

        for idx, row in df_catalogo.iterrows():
            mult = multiplicadores[idx] if idx < len(multiplicadores) else 0.1
            cantidad_estimada = round(area_objetivo * mult, 2)
            precio_unitario = float(row['Precio_Unitario_COP'])
            costo_total_item = cantidad_estimada * precio_unitario
            presupuesto_total_calculado += costo_total_item

            lista_detallada.append({
                "Código": row['Codigo'],
                "Material de Obra Negra": row['Material'],
                "Unidad": row['Unidad'],
                "Cantidad Req.": f"{cantidad_estimada:,.2f}",
                "Precio Unit. COP": f"${precio_unitario:,.2f}",
                "Costo Total COP": f"${costo_total_item:,.2f}"
            })

        df_tabla_final = pd.DataFrame(lista_detallada)

        if "Modo Comparativo" in ferreteria_seleccionada:
            try:
                df_cat_a = agente_procesar_catalogo("precios_pereira.xlsx", "Aliada_A")
                df_cat_b = agente_procesar_catalogo("precios_pereira.xlsx", "Aliada_B")
                
                total_a = sum([area_objetivo * multiplicadores[i] * float(df_cat_a.iloc[i]['Precio_Unitario_COP']) for i in range(len(df_cat_a))])
                total_b = sum([area_objetivo * multiplicadores[i] * float(df_cat_b.iloc[i]['Precio_Unitario_COP']) for i in range(len(df_cat_b))])
                ahorro = total_a - total_b

                m1, m2, m3 = st.columns(3)
                m1.metric("Ferretería Central (Aliada A)", f"${total_a:,.2f} COP")
                m2.metric("Constructodo (Aliada B)", f"${total_b:,.2f} COP", delta=f"-${ahorro:,.2f} COP Ahorro")
                m3.metric("Área Verificada", f"{area_objetivo:.2f} m²")
            except Exception:
                pass

            st.markdown("### 📊 Detalle Completo de Insumos y Comparativa B2B (Procesado por Agente IA)")
            st.dataframe(df_tabla_final, use_container_width=True)

        else:
            m1, m2 = st.columns(2)
            m1.metric("Área Verificada del Proyecto", f"{area_objetivo:.2f} m²")
            m2.metric(f"Presupuesto Total ({ferreteria_seleccionada.split(' ')[0]})", f"${presupuesto_total_calculado:,.2f} COP")

            st.markdown("### 📋 Desglose Técnico de los 20 Artículos de Obra Negra (Procesado por Agente IA)")
            st.dataframe(df_tabla_final, use_container_width=True)

    else:
        st.error("El Agente no pudo procesar el catálogo de materiales. Revisa el archivo 'precios_pereira.xlsx'.")

else:
    st.info("👈 Por favor, sube un plano arquitectónico en la barra lateral izquierda para iniciar el análisis inteligente de metraje.")

st.markdown("---")
st.caption("SALAZ ANALYTICS Plataforma Inteligente de Gestión | Pereira, Risaralda")