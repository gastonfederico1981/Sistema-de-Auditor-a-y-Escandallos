import streamlit as st
import pandas as pd
import urllib.parse

# 1. Configuración de página y caché
st.set_page_config(page_title="Carranza Auditoría", layout="wide")

@st.cache_data(ttl=3600)
def get_data(url):
    df = pd.read_csv(url, engine='c', low_memory=False)
    df.columns = df.columns.str.strip().str.lower()
    return df

# 2. Gestión de Sesión (Login de Alumno)
if 'alumno' not in st.session_state:
    st.session_state.alumno = None

if st.session_state.alumno is None:
    st.title("💎 Carranza Control | Acceso")
    nombre = st.text_input("Ingrese su Nombre y Apellido para comenzar:")
    if st.button("Iniciar Auditoría") and nombre:
        st.session_state.alumno = nombre
        st.rerun() # Limpia la interfaz para el nuevo usuario
    st.stop() # Detiene la ejecución hasta que se identifique

# 3. Sidebar Personalizado
st.sidebar.title(f"👤 {st.session_state.alumno}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.alumno = None
    st.rerun()

menu = st.sidebar.radio("Navegación", ["Dashboard", "Inventario", "Escandallos"])

# 4. Módulo de Inventario con Claves Únicas por Alumno
if menu == "Inventario":
    st.title("📦 Carga de Insumos")
    
    # El uso de 'key' basado en el nombre del alumno evita el error de removeChild
    id_unico = f"uploader_{st.session_state.alumno.replace(' ', '_')}"
    archivo = st.file_uploader("📁 Subir remito", type=["jpg", "png", "jpeg"], key=id_unico)

    if archivo:
        st.image(archivo, width=250)
        try:
            # Los secretos se mantienen centralizados
            SHEET_URL = st.secrets["general"]["sheet_url"]
            LINK_BASE = st.secrets["general"]["form_url"]
            
            df = get_data(SHEET_URL)
            
            with st.form(f"form_{st.session_state.alumno}"):
                st.subheader("Confirmación de Datos")
                c1, c2, c3 = st.columns(3)
                insumo = c1.selectbox("Insumo", df['nombre'].tolist())
                cantidad = c2.number_input("Cantidad", value=1.0)
                precio = c3.number_input("Precio Unitario", value=0.0)
                
                confirmar = st.form_submit_button("Generar Enlace")
                
            if confirmar:
                # Inyectamos el nombre del alumno en el link para trazabilidad
                link = LINK_BASE.replace("NOMBRE", urllib.parse.quote(str(insumo)))
                link = link.replace("111", str(cantidad)).replace("222", str(precio))
                # Nota: Deberías tener un campo en tu Form para el Alumno
                
                st.markdown(f'''
                    <a href="{link}" target="_blank">
                        <button style="background-color:#D4AF37;color:black;padding:15px;width:100%;border-radius:10px;font-weight:bold;cursor:pointer;border:none;">
                            🚀 VALIDAR CARGA (ALUMNO: {st.session_state.alumno})
                        </button>
                    </a>
                ''', unsafe_allow_html=True)
        except Exception as e:
            st.error("Error al conectar con la base de datos.")

# ... (Dashboard y otros módulos)
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
        