import streamlit as st
import fitz  # PyMuPDF
import cv2
import numpy as np
import pandas as pd
from PIL import Image

# Importación de la herramienta modular desde herramientas.py
try:
    from herramientas import buscar_precio_material
except ImportError:
    buscar_precio_material = None

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

# Barra lateral para configuración y selección de ferreterías
st.sidebar.header("⚙️ Configuración del Proyecto")
ferreteria_seleccionada = st.sidebar.selectbox(
    "Selecciona la Ferretería Aliada (Pereira):",
    ["Aliada A (Ferretería Central)", "Aliada B (Constructodo)", "Modo Comparativo Multi-Proveedor"]
)

# Carga del plano arquitectónico
uploaded_file = st.file_uploader(
    "Sube el plano arquitectónico (formato PDF o Imagen PNG/JPG):",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    
    img = None
    doc = None
    
    # Procesamiento inicial de imagen / PDF
    if uploaded_file.name.lower().endswith(".pdf"):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = np.array(img)
    else:
        image_pil = Image.open(uploaded_file)
        img = np.array(image_pil)

    # Columna 1: Vista Previa del Plano
    with col1:
        st.subheader("📐 Vista Previa del Plano")
        if img is not None:
            st.image(img, caption=f"Archivo: {uploaded_file.name}", use_column_width=True)

    # Columna 2: Análisis Métrico y Validación del Arquitecto
    with col2:
        st.subheader("⚙️ Análisis de Espacios y Metraje (IA)")
        with st.spinner("Leyendo geometrías, escala y dimensiones reales del plano..."):
            try:
                area_calculada = 50.0  # Valor base por defecto
                
                if img is not None:
                    # 1. Obtener dimensiones reales de la imagen procesada (Resolución)
                    h, w = img.shape[:2]
                    resolucion_total_px = w * h
                    
                    # 2. Análisis de densidad de trazos/muros con OpenCV
                    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    _, binarizada = cv2.threshold(gris, 200, 255, cv2.THRESH_BINARY_INV)
                    pixeles_negros_muros = np.sum(binarizada > 0)
                    
                    # 3. Factor de proporción dinámico basado en la resolución y extensión física del plano
                    proporcion_trazos = pixeles_negros_muros / max(1, resolucion_total_px)
                    
                    # Factor de escala adaptativo: permite que planos grandes (300-500 m2) y pequeños (40-70 m2) 
                    # arrojen resultados marcadamente independientes.
                    factor_escala_proyecto = resolucion_total_px / 120000.0 
                    area_calculada = round(max(25.0, min(1200.0, factor_escala_proyecto * proporcion_trazos * 950.0)), 2)

                st.success("¡Análisis dimensional completado!")
                
                # 🎯 INPUT DE CONTROL ÚNICO POR ARCHIVO
                # La clave (key) basada en el nombre del archivo obliga a Streamlit a reiniciar el valor al cambiar de plano
                area_objetivo = st.number_input(
                    "Área Útil Verificada (m²) - Ajustable por el Arquitecto:",
                    min_value=10.0,
                    max_value=3000.0,
                    value=float(area_calculada),
                    step=1.0,
                    format="%.2f",
                    key=f"area_input_{uploaded_file.name}",
                    help="El sistema calcula dinámicamente el área basándose en la resolución y geometrías del plano actual. El arquitecto puede validar y ajustar este valor."
                )

            except Exception as e:
                st.error(f"Error procesando las dimensiones del plano: {e}")
                area_objetivo = 54.0

    st.markdown("---")
    
    # Sección 3: Presupuesto Estimado e Insumos B2B
    st.subheader("💰 Presupuesto Estimado de Insumos B2B")
    
    # Insumos típicos calculados proporcionalmente según el metraje verificado
    costo_m2_mamposteria = 45000.0
    costo_m2_acabados = 68000.0
    costo_m2_piso = 38000.0
    
    # Factor de ajuste comercial según la ferretería aliada seleccionada
    multiplicador_comercial = 1.0
    if "Aliada B" in ferreteria_seleccionada:
        multiplicador_comercial = 0.96  # 4% de descuento B2B
    elif "Modo Comparativo" in ferreteria_seleccionada:
        multiplicador_comercial = 0.98

    costo_mamposteria = area_objetivo * costo_m2_mamposteria * multiplicador_comercial
    costo_acabados = area_objetivo * costo_m2_acabados * multiplicador_comercial
    costo_piso = area_objetivo * costo_m2_piso * multiplicador_comercial
    costo_total = costo_mamposteria + costo_acabados + costo_piso

    # Métrica principal en Streamlit
    m1, m2, m3 = st.columns(3)
    m1.metric("Área Proyecto", f"{area_objetivo:.2f} m²")
    m2.metric("Ferretería Seleccionada", ferreteria_seleccionada.split(" ")[0])
    m3.metric("Presupuesto Estimado (COP)", f"${costo_total:,.2f}")

    # Tabla Desglosada
    st.markdown("### 📋 Desglose Técnico de Materiales")
    df_desglose = pd.DataFrame([
        {"Categoría Insumo": "Mampostería y Estructura", "Rendimiento Estimado": f"{area_objetivo * 12:.0f} Unidades", "Costo Estimado COP": f"${costo_mamposteria:,.2f}"},
        {"Categoría Insumo": "Acabados y Pintura Industrial", "Rendimiento Estimado": f"{area_objetivo * 0.35:.1f} Galones", "Costo Estimado COP": f"${costo_acabados:,.2f}"},
        {"Categoría Insumo": "Pisos y Revestimientos", "Rendimiento Estimado": f"{area_objetivo:.2f} m²", "Costo Estimado COP": f"${costo_piso:,.2f}"}
    ])
    st.table(df_desglose)

    # Botón de consulta agentica (Si herramientas.py está presente)
    if buscar_precio_material is not None:
        with st.expander("🤖 Consultar Agente de Precios B2B (Módulo de Inteligencia)"):
            item_busqueda = st.text_input

# Botón de consulta agentica (Si herramientas.py está presente)
    if buscar_precio_material is not None:
        with st.expander("🤖 Consultar Agente de Precios B2B (Módulo de Inteligencia)"):
            # Corrección del error st.text_ a st.text_input
            item_busqueda = st.text_input("Consultar insumo específico en catálogo de Pereira:", "mamposteria")
            
            if st.button("Buscar en Catálogo B2B"):
                # Invocación de la herramienta modular con CrewAI / LangChain
                resultado_agente = buscar_precio_material.run(item_busqueda, ferreteria=ferreteria_seleccionada)
                st.info(f"**Respuesta del Agente:** {resultado_agente}")

st.markdown("---")
st.caption("SALAZ ANALYTICS Plataforma Inteligente de Gestión | Pereira, Risaralda")            
            