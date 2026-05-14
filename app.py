import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Carranza Control v1.0", layout="wide")

# Caché para velocidad y evitar latencia
@st.cache_data(ttl=300)
def get_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    SHEET_URL = st.secrets["general"]["sheet_url"]
    LINK_PRE_RELLENADO = st.secrets["general"]["form_url"]
except:
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtRbAmRk1QRuV5yF0aQn-V31F553pSGK5RDhQcYywYY6CN2wfuBZvg3g2hGeO9rMtG745FVavNnZZW/pub?output=csv"
    LINK_PRE_RELLENADO = "https://docs.google.com/forms/d/e/1FAIpQLSeBmsQmnlf5BzEUKDHtatfb9d7QjB2A2Cohvn4-oUPHMUk4Wg/viewform?usp=pp_url&entry.445714982=NOMBRE&entry.992341123=111&entry.1041327483=222"

menu = st.sidebar.radio("Navegación", ["Dashboard", "Inventario", "Escandallos", "Punto de Equilibrio"])

if menu == "Inventario":
    st.title("📦 Carga de Insumos")
    
    # Manejo de estado: Separamos la cámara del formulario
    if 'foto_lista' not in st.session_state:
        st.session_state.foto_lista = None

    if st.session_state.foto_lista is None:
        archivo = st.camera_input("📷 Escaneá el remito")
        if archivo:
            st.session_state.foto_lista = archivo
            st.rerun() # Reinicio limpio para evitar el error 'removeChild'
    else:
        st.image(st.session_state.foto_lista, width=400)
        if st.button("🔄 Borrar y repetir"):
            st.session_state.foto_lista = None
            st.rerun()

        try:
            df = get_data(SHEET_URL)
            with st.form("validador"):
                st.subheader("Datos del Remito")
                c1, c2, c3 = st.columns(3)
                sel = c1.selectbox("Insumo", df['nombre'].tolist())
                cant = c2.number_input("Cantidad", value=1.0)
                prec = c3.number_input("Precio Unitario", value=0.0)
                enviar = st.form_submit_button("Confirmar Carga")
            
            if enviar:
                link = LINK_PRE_RELLENADO.replace("NOMBRE", urllib.parse.quote(str(sel)))
                link = link.replace("111", str(cant)).replace("222", str(prec))
                st.markdown(f'<a href="{link}" target="_blank"><button style="background-color:#D4AF37;color:black;padding:15px;width:100%;border-radius:10px;font-weight:bold;cursor:pointer;">🚀 VALIDAR EN DRIVE</button></a>', unsafe_allow_html=True)
        except:
            st.error("Error de conexión.")
            # ... resto del formulario con st.form ...

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
        