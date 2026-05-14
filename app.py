import streamlit as st
import pandas as pd
import urllib.parse

# 1. Configuración de página
st.set_page_config(page_title="Carranza Control v1.0", layout="wide")

# 2. Conexión con Caché (Crucial para evitar lentitud y errores de red)
@st.cache_data(ttl=300) # Guarda los datos por 5 minutos
def get_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower()
    return df

# Manejo de Secrets
try:
    SHEET_URL = st.secrets["general"]["sheet_url"]
    LINK_PRE_RELLENADO = st.secrets["general"]["form_url"]
except:
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtRbAmRk1QRuV5yF0aQn-V31F553pSGK5RDhQcYywYY6CN2wfuBZvg3g2hGeO9rMtG745FVavNnZZW/pub?output=csv"
    LINK_PRE_RELLENADO = "https://docs.google.com/forms/d/e/1FAIpQLSeBmsQmnlf5BzEUKDHtatfb9d7QjB2A2Cohvn4-oUPHMUk4Wg/viewform?usp=pp_url&entry.445714982=NOMBRE&entry.992341123=111&entry.1041327483=222"

# 3. Estilo Visual
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    [data-testid="stMetric"] {
        background-color: #1E2130; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #D4AF37;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. Sidebar
st.sidebar.title("💎 Carranza Control")
menu = st.sidebar.radio("Navegación", ["Dashboard", "Inventario", "Escandallos", "Punto de Equilibrio"])

# --- LÓGICA DE MÓDULOS ---

if menu == "Dashboard":
    st.title("📊 Tablero de Control Real")
    try:
        df = get_data(SHEET_URL)
        df['stock_actual'] = pd.to_numeric(df['stock_actual'], errors='coerce').fillna(0)
        df['costo_unitario'] = pd.to_numeric(df['costo_unitario'], errors='coerce').fillna(0)
        df['stock_minimo'] = pd.to_numeric(df['stock_minimo'], errors='coerce').fillna(0)

        valor_total = (df['stock_actual'] * df['costo_unitario']).sum()
        alertas = len(df[df['stock_actual'] <= df['stock_minimo']])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Capital Inmovilizado", f"$ {valor_total:,.2f}")
        col2.metric("Insumos en Riesgo", alertas)
        col3.metric("Estatus", "CONTROLADO" if alertas == 0 else "REVISAR STOCK")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error técnico: {e}")

elif menu == "Inventario":
    st.title("📦 Carga de Insumos")
    
    # La cámara se mantiene estática para evitar el error de removeChild
    foto = st.camera_input("📷 Sacale una foto al remito")

    if foto:
        try:
            # Usamos el caché para que el selector sea instantáneo
            df_datos = get_data(SHEET_URL)
            lista_insumos = df_datos['nombre'].tolist()
            
            # El Formulario encapsula los cambios y evita que la página parpadee
            with st.form("confirmacion_datos"):
                st.subheader("Confirmación de Datos")
                c1, c2, c3 = st.columns(3)
                insumo_sel = c1.selectbox("Insumo", lista_insumos)
                cantidad_sel = c2.number_input("Cantidad", min_value=0.0, value=1.0)
                precio_sel = c3.number_input("Precio Unitario", min_value=0.0, value=0.0)
                confirmar = st.form_submit_button("Generar Enlace de Carga")
                
            if confirmar:
                link = LINK_PRE_RELLENADO.replace("NOMBRE", urllib.parse.quote(str(insumo_sel)))
                link = link.replace("111", str(cantidad_sel)).replace("222", str(precio_sel))
                st.markdown(f'<a href="{link}" target="_blank"><button style="background-color: #D4AF37; color: black; padding: 15px; border-radius: 10px; width: 100%; font-weight: bold; cursor: pointer;">🚀 VALIDAR E INYECTAR A DRIVE</button></a>', unsafe_allow_html=True)
        except Exception as e:
            st.error("Error al cargar la lista de insumos.")

# ... (Módulos de Escandallos y Punto de Equilibrio sin cambios mayores) ...

elif menu == "Escandallos":
    st.title("🍳 Calculadora de Fichas Técnicas")
    st.write("Calculá el costo real de tus productos.")

    try:
        df = get_data()
        col_form, col_res = st.columns([2, 1])

        with col_form:
            st.subheader("Configuración de la Receta")
            nombre_producto = st.text_input("Nombre del Producto", "Nuevo Producto")
            insumos_seleccionados = st.multiselect("Seleccioná ingredientes:", df['nombre'].tolist())

            receta_data = []
            for insumo in insumos_seleccionados:
                st.write(f"--- **{insumo}** ---")
                c1, c2 = st.columns(2)
                with c1:
                    cantidad = st.number_input(f"Cantidad necesaria", min_value=0.001, key=f"cant_{insumo}", format="%.3f")
                with c2:
                    datos_insumo = df[df['nombre'] == insumo]
                    costo_u = float(datos_insumo['costo_unitario'].values[0])
                    unidad_u = datos_insumo['unidad'].values[0]
                    st.caption(f"Costo: ${costo_u} por {unidad_u}")
                
                receta_data.append({"insumo": insumo, "cantidad": cantidad, "costo_u": costo_u})

        with col_res:
            st.subheader("💰 Análisis de Costos")
            if receta_data:
                costo_neto = sum(item['cantidad'] * item['costo_u'] for item in receta_data)
                st.metric("Costo Neto Total", f"$ {costo_neto:,.2f}")
                
                merma = st.slider("% Merma Operativa", 0, 50, 10)
                costo_real = costo_neto / (1 - (merma/100))
                st.metric("Costo Real (con Merma)", f"$ {costo_real:,.2f}", delta=f"{merma}%")
                
                st.divider()
                margen = st.number_input("% Margen deseado", 50, 500, 200)
                precio_sugerido = costo_real * (1 + (margen/100))
                st.header(f"Sugerido: ${precio_sugerido:,.2f}")
            else:
                st.info("Seleccioná ingredientes para empezar.")

    except Exception as e:
        st.error(f"Error al cargar escandallos: {e}")

elif menu == "Punto de Equilibrio":
    st.title("📈 Punto de Equilibrio")
    col_fijos, col_prod = st.columns(2)

    with col_fijos:
        alquiler = st.number_input("Alquiler", value=0)
        sueldos = st.number_input("Sueldos", value=0)
        servicios = st.number_input("Servicios", value=0)
        otros = st.number_input("Otros", value=0)
        total_fijos = alquiler + sueldos + servicios + otros
        st.metric("Costos Fijos", f"$ {total_fijos:,.2f}")

    with col_prod:
        precio_vta = st.number_input("Precio Venta Promedio", min_value=1.0, value=1000.0)
        costo_vta = st.number_input("Costo Producción Promedio", min_value=1.0, value=400.0)
        margen_unitario = precio_vta - costo_vta
        st.metric("Margen Unitario", f"$ {margen_unitario:,.2f}")

    if margen_unitario > 0:
        unidades_eq = total_fijos / margen_unitario
        st.success(f"### Objetivo: {int(unidades_eq)} unidades/mes")      
        