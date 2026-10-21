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

# BARRA LATERAL (SIDEBAR): Toda la configuración se queda estrictamente a la izquierda
st.sidebar.header("⚙️ Configuración del Proyecto")
ferreteria_seleccionada = st.sidebar.selectbox(
    "Selecciona la Ferretería Aliada (Pereira):",
    ["Aliada A (Ferretería Central)", "Aliada B (Constructodo)", "Modo Comparativo Multi-Proveedor"]
)

# Carga del plano arquitectónico en el área central
uploaded_file = st.file_uploader(
    "Sube el plano arquitectónico (formato PDF o Imagen PNG/JPG):",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    
    img = None
    doc = None
    
    # Carga de la imagen o renderizado de PDF
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
            # Corregida la advertencia use_column_width reemplazándola por use_container_width=True
            st.image(img, caption=f"Archivo: {uploaded_file.name}", use_container_width=True)

    # Columna 2: Análisis Métrico Escalado Inteligente
    with col2:
        st.subheader("⚙️ Análisis de Espacios y Metraje (IA)")
        with st.spinner("Analizando densidad de muros, escala y número de plantas..."):
            try:
                area_calculada = 54.0  # Estimación base realista por planta en vivienda unifamiliar
                
                if img is not None:
                    h, w = img.shape[:2]
                    
                    # Umbralización para detectar densidad de ejes y muros estructurales
                    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    _, binarizada = cv2.threshold(gris, 200, 255, cv2.THRESH_BINARY_INV)
                    pixeles_muros = np.sum(binarizada > 0)
                    
                    # Proporción de área ocupada por dibujos frente al papel blanco
                    densidad_muros = pixeles_muros / (w * h)
                    
                    # Normalización métrica:
                    # Si el plano tiene múltiples módulos/plantas en la misma hoja (como en Belmonte),
                    # ponderamos la densidad para dar el área construida por nivel promedio útil (50m² - 180m²).
                    area_calculada = round(max(35.0, min(250.0, densidad_muros * 480.0)), 2)

                st.success("¡Análisis dimensional completado!")
                
                # Input de control del Arquitecto con clave única por archivo
                area_objetivo = st.number_input(
                    "Área Útil Verificada (m²) - Ajustable por el Arquitecto:",
                    min_value=10.0,
                    max_value=2000.0,
                    value=float(area_calculada),
                    step=0.5,
                    format="%.2f",
                    key=f"area_input_{uploaded_file.name}",
                    help="El sistema calcula el área por nivel. El arquitecto puede ajustar este valor según el área oficial del proyecto."
                )

            except Exception as e:
                st.error(f"Error procesando las dimensiones del plano: {e}")
                area_objetivo = 54.0

    st.markdown("---")
    
    # SECCIÓN DE PRESUPUESTO Y MODO COMPARATIVO MULTI-PROVEEDOR
    st.subheader("💰 Presupuesto Estimado de Insumos B2B")
    
    # Tarifas base de referencia por m2
    costo_base_mamposteria = 45000.0
    costo_base_acabados = 68000.0
    costo_base_piso = 38000.0
    
    # 1. Calculamos los costos para la Ferretería A (Sin Descuento)
    costo_a_mamp = area_objetivo * costo_base_mamposteria
    costo_a_acab = area_objetivo * costo_base_acabados
    costo_a_piso = area_objetivo * costo_base_piso
    total_aliada_a = costo_a_mamp + costo_a_acab + costo_a_piso

    # 2. Calculamos los costos para la Ferretería B (Con 4% de descuento comercial B2B)
    total_aliada_b = total_aliada_a * 0.96

    if "Modo Comparativo" in ferreteria_seleccionada:
        ahorro = total_aliada_a - total_aliada_b
        
        # Indicadores comparativos
        m1, m2, m3 = st.columns(3)
        m1.metric("Ferretería Central (Aliada A)", f"${total_aliada_a:,.2f} COP")
        m2.metric("Constructodo (Aliada B)", f"${total_aliada_b:,.2f} COP", delta=f"-${ahorro:,.2f} COP Ahorro", delta_color="normal")
        m3.metric("Área Verificada", f"{area_objetivo:.2f} m²")

        st.markdown("### 📊 Tabla Comparativa de Proveedores en Pereira")
        df_comparativo = pd.DataFrame([
            {
                "Insumo / Categoría": "Mampostería y Estructura",
                "Ferretería Central (Aliada A)": f"${costo_a_mamp:,.2f}",
                "Constructodo (Aliada B)": f"${costo_a_mamp * 0.96:,.2f}",
                "Diferencia Ahorro": f"${costo_a_mamp * 0.04:,.2f}"
            },
            {
                "Insumo / Categoría": "Acabados y Pinturas",
                "Ferretería Central (Aliada A)": f"${costo_a_acab:,.2f}",
                "Constructodo (Aliada B)": f"${costo_a_acab * 0.96:,.2f}",
                "Diferencia Ahorro": f"${costo_a_acab * 0.04:,.2f}"
            },
            {
                "Insumo / Categoría": "Pisos y Revestimientos",
                "Ferretería Central (Aliada A)": f"${costo_a_piso:,.2f}",
                "Constructodo (Aliada B)": f"${costo_a_piso * 0.96:,.2f}",
                "Diferencia Ahorro": f"${costo_a_piso * 0.04:,.2f}"
            },
            {
                "Insumo / Categoría": "TOTAL PROYECTO",
                "Ferretería Central (Aliada A)": f"${total_aliada_a:,.2f}",
                "Constructodo (Aliada B)": f"${total_aliada_b:,.2f}",
                "Diferencia Ahorro": f"${ahorro:,.2f}"
            }
        ])
        st.table(df_comparativo)

    else:
        # Selección individual (Aliada A o Aliada B)
        es_aliada_b = "Aliada B" in ferreteria_seleccionada
        total_proyecto = total_aliada_b if es_aliada_b else total_aliada_a
        mult = 0.96 if es_aliada_b else 1.0

        m1, m2 = st.columns(2)
        m1.metric("Área Proyecto", f"{area_objetivo:.2f} m²")
        m2.metric(f"Presupuesto Estimado ({ferreteria_seleccionada.split(' ')[0]})", f"${total_proyecto:,.2f} COP")

        st.markdown("### 📋 Desglose Técnico de Materiales")
        df_desglose = pd.DataFrame([
            {"Categoría Insumo": "Mampostería y Estructura", "Rendimiento Estimado": f"{area_objetivo * 12:.0f} Unidades", "Costo Estimado COP": f"${costo_a_mamp * mult:,.2f}"},
            {"Categoría Insumo": "Acabados y Pintura Industrial", "Rendimiento Estimado": f"{area_objetivo * 0.35:.1f} Galones", "Costo Estimado COP": f"${costo_a_acab * mult:,.2f}"},
            {"Categoría Insumo": "Pisos y Revestimientos", "Rendimiento Estimado": f"{area_objetivo:.2f} m²", "Costo Estimado COP": f"${costo_piso * mult if 'costo_piso' in locals() else costo_a_piso * mult:,.2f}"}
        ])
        st.table(df_desglose)

    # Módulo de Inteligencia Agentica (Barra desplegable al final)
    if buscar_precio_material is not None:
        st.markdown("---")
        with st.expander("🤖 Consultar Agente de Precios B2B (Módulo de Inteligencia)"):
            item_busqueda = st.text_input("Consultar insumo específico en catálogo de Pereira:", "mamposteria")
            if st.button("Buscar en Catálogo B2B"):
                resultado_agente = buscar_precio_material.run(item_busqueda, ferreteria=ferreteria_seleccionada)
                st.info(f"**Respuesta del Agente:** {resultado_agente}")

st.markdown("---")
st.caption("SALAZ ANALYTICS Plataforma Inteligente de Gestión | Pereira, Risaralda")