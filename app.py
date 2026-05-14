import streamlit as st
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Carranza Control v1.0", layout="wide")

# 2. Tu link de Google Sheets (Publicado como CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtRbAmRk1QRuV5yF0aQn-V31F553pSGK5RDhQcYywYY6CN2wfuBZvg3g2hGeO9rMtG745FVavNnZZW/pub?output=csv"

# Función optimizada para leer los datos
def get_data():
    # Leemos el CSV directamente desde tu link
    df = pd.read_csv(SHEET_URL)
    # Limpiamos nombres de columnas (quita espacios y pone en minúscula)
    df.columns = df.columns.str.strip().str.lower()
    return df

# 3. Estilo Visual "Carranza Gold"
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    [data-testid="stMetric"] {
        background-color: #1E2130; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #D4AF37;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #333;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Sidebar
st.sidebar.title("💎 Carranza Control")
st.sidebar.info("Software de Auditoría Forense")
menu = st.sidebar.radio("Navegación", ["Dashboard", "Inventario", "Escandallos", "Punto de Equilibrio"])

# 5. Lógica de Módulos
if menu == "Dashboard":
    st.title("📊 Tablero de Control Real")
    
    try:
        df = get_data()
        
        # Cálculos de Auditoría
        # Aseguramos que los números sean números
        df['stock_actual'] = pd.to_numeric(df['stock_actual'], errors='coerce').fillna(0)
        df['costo_unitario'] = pd.to_numeric(df['costo_unitario'], errors='coerce').fillna(0)
        df['stock_minimo'] = pd.to_numeric(df['stock_minimo'], errors='coerce').fillna(0)

        valor_total = (df['stock_actual'] * df['costo_unitario']).sum()
        alertas = len(df[df['stock_actual'] <= df['stock_minimo']])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Capital Inmovilizado", f"$ {valor_total:,.2f}")
        col2.metric("Insumos en Riesgo", alertas)
        col3.metric("Estatus del Negocio", "CONTROLADO" if alertas == 0 else "REVISAR STOCK")

        st.subheader("📋 Auditoría de Insumos")
        # Mostramos la tabla completa
        st.dataframe(df, use_container_width=True)

        if alertas > 0:
            st.warning(f"⚠️ Tenés {alertas} insumos por debajo del stock mínimo configurado.")

    except Exception as e:
        st.error("No se pudo leer la planilla.")
        st.info("Verificá que la planilla de Drive tenga los encabezados: nombre, unidad, stock_actual, stock_minimo, costo_unitario")
        st.write(f"Error técnico: {e}")

elif menu == "Inventario":
    st.title("📦 Carga de Insumos por Escaneo")
    st.write("Capturá el remito para actualizar el stock en Drive.")

    # ACÁ DEBÉS PEGAR EL ENLACE QUE COPIES DEL PASO "OBTENER ENLACE PREVIAMENTE RELLENADO"
    LINK_PRE_RELLENADO = "PEGÁ_TU_ENLACE_AQUÍ"

    foto = st.camera_input("📷 Sacale una foto al remito o factura")

    if foto:
        st.success("Imagen capturada. Procesando datos para auditoría...")
        
        # Traemos la lista de insumos de tu Excel actual
        try:
            df_datos = get_data()
            lista_insumos = df_datos['nombre'].tolist()
        except:
            lista_insumos = ["Cargá datos en tu Excel primero"]

        with st.container():
            st.subheader("Confirmación de Datos")
            col1, col2, col3 = st.columns(3)
            
            insumo_sel = col1.selectbox("Insumo", lista_insumos)
            cantidad_sel = col2.number_input("Cantidad", min_value=0.0, value=1.0)
            precio_sel = col3.number_input("Precio Unitario", min_value=0.0, value=0.0)

            if LINK_PRE_RELLENADO != "https://docs.google.com/forms/d/e/1FAIpQLSeBmsQmnlf5BzEUKDHtatfb9d7QjB2A2Cohvn4-oUPHMUk4Wg/viewform?usp=pp_url&entry.445714982=NOMBRE&entry.992341123=111&entry.1041327483=222":
                import urllib.parse
                
                # Esta lógica inyecta los datos en el link de Google
                link_dinamico = LINK_PRE_RELLENADO
                link_dinamico = link_dinamico.replace("NOMBRE", urllib.parse.quote(str(insumo_sel)))
                link_dinamico = link_dinamico.replace("111", str(cantidad_sel))
                link_dinamico = link_dinamico.replace("222", str(precio_sel))

                st.markdown(f"""
                    <div style="text-align: center; padding: 20px;">
                        <a href="{link_dinamico}" target="_blank" style="text-decoration: none;">
                            <button style="
                                background-color: #D4AF37;
                                color: black;
                                padding: 15px 30px;
                                border: none;
                                border-radius: 10px;
                                font-weight: bold;
                                font-size: 18px;
                                cursor: pointer;
                                width: 100%;
                                box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
                            ">
                                🚀 VALIDAR E INYECTAR A DRIVE
                            </button>
                        </a>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Falta configurar el link del formulario en el código para habilitar la carga.")

    st.divider()
    st.info("💡 **Tip de Auditor:** Al usar el formulario, los datos quedan registrados con fecha y hora exacta (Timestamp) en una nueva solapa de tu Excel.")

elif menu == "Escandallos":
    st.title("🍳 Calculadora de Fichas Técnicas")
    st.write("Calculá el costo real de tus productos basado en los precios de tu inventario.")

    try:
        df = get_data()
        # Aseguramos limpieza de datos
        df.columns = df.columns.str.strip().str.lower()
        
        col_form, col_res = st.columns([2, 1])

        with col_form:
            st.subheader("Configuración de la Receta")
            nombre_producto = st.text_input("Nombre del Producto (Ej: Baguette, Croissant)", "Nuevo Producto")
            
            # Selector de múltiples insumos
            insumos_seleccionados = st.multiselect(
                "Seleccioná los ingredientes de la receta:",
                df['nombre'].tolist()
            )

            receta_data = []
            for insumo in insumos_seleccionados:
                st.write(f"--- **{insumo}** ---")
                c1, c2 = st.columns(2)
                with c1:
                    cantidad = st.number_input(f"Cantidad necesaria", min_value=0.001, key=f"cant_{insumo}", format="%.3f")
                with c2:
                    # Buscamos el costo unitario en el DataFrame
                    costo_u = df[df['nombre'] == insumo]['costo_unitario'].values[0]
                    unidad_u = df[df['nombre'] == insumo]['unidad'].values[0]
                    st.caption(f"Costo base: ${costo_u} por {unidad_u}")
                
                receta_data.append({"insumo": insumo, "cantidad": cantidad, "costo_u": costo_u})

        with col_res:
            st.subheader("💰 Análisis de Costos")
            if receta_data:
                costo_neto = sum(item['cantidad'] * item['costo_u'] for item in receta_data)
                
                st.metric("Costo Neto Total", f"$ {costo_neto:,.2f}")
                
                merma = st.slider("% Merma Operativa (Falla/Desperdicio)", 0, 50, 10)
                costo_real = costo_neto / (1 - (merma/100))
                
                st.metric("Costo Real (con Merma)", f"$ {costo_real:,.2f}", delta=f"{merma}% merma")
                
                st.divider()
                margen = st.number_input("% Margen de Utilidad deseado", 50, 500, 200)
                precio_sugerido = costo_real * (1 + (margen/100))
                
                st.header(f"Sugerido: ${precio_sugerido:,.2f}")
                st.caption("Este es el precio mínimo para mantener tu estructura.")
            else:
                st.info("Seleccioná ingredientes a la izquierda para empezar el cálculo.")

    except Exception as e:
        st.error("Error al cargar el módulo de escandallos.")
        st.write(e)
elif menu == "Punto de Equilibrio":
    st.title("📈 Análisis de Viabilidad Financiera")
    st.write("Determiná el volumen de ventas necesario para cubrir tus costos fijos.")

    col_fijos, col_prod = st.columns(2)

    with col_fijos:
        st.subheader("1. Costos Fijos Mensuales")
        alquiler = st.number_input("Alquiler y Expensas", value=0)
        sueldos = st.number_input("Sueldos y Cargas Sociales", value=0)
        servicios = st.number_input("Servicios (Luz, Gas, Agua)", value=0)
        otros = st.number_input("Otros Gastos Fijos", value=0)
        
        total_fijos = alquiler + sueldos + servicios + otros
        st.metric("Total Costos Fijos", f"$ {total_fijos:,.2f}")

    with col_prod:
        st.subheader("2. Margen de Contribución")
        st.caption("Usá un producto promedio o el más vendido de la panadería.")
        precio_vta = st.number_input("Precio de Venta Promedio (Unitario)", min_value=1.0, value=1000.0)
        costo_vta = st.number_input("Costo de Producción Promedio (Unitario)", min_value=1.0, value=400.0)
        
        margen_unitario = precio_vta - costo_vta
        porcentaje_margen = (margen_unitario / precio_vta) * 100 if precio_vta > 0 else 0
        
        st.metric("Margen por Venta", f"$ {margen_unitario:,.2f}", f"{porcentaje_margen:.1f}%")

    st.divider()

    # Cálculo Final
    if margen_unitario > 0:
        unidades_eq = total_fijos / margen_unitario
        facturacion_eq = unidades_eq * precio_vta
        
        c1, c2 = st.columns(2)
        with c1:
            st.success(f"### Punto de Equilibrio: {int(unidades_eq)} unidades")
            st.write(f"Debés vender **{int(unidades_eq)}** unidades al mes solo para no perder dinero.")
        with c2:
            st.success(f"### Facturación de Equilibrio: $ {facturacion_eq:,.2f}")
            st.write(f"Esta es la facturación mínima mensual requerida.")
    else:
        st.error("El precio de venta debe ser mayor al costo de producción para calcular el equilibrio.")

    st.info("💡 **Consejo de Auditoría:** Si el punto de equilibrio es muy alto, revisá los costos de producción (Escandallos) o bajá los costos fijos.")        
        