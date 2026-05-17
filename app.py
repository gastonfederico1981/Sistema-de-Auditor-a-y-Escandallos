import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import os
import urllib.parse


# =================================================================
# CONFIGURACIÓN DE PÁGINA (Debe ser SIEMPRE la primera línea)
# =================================================================
st.set_page_config(page_title="Carranza Control v1.1", layout="wide", page_icon="💎")

# =================================================================
# 1. CREDENCIALES Y PARÁMETROS DE CONEXIÓN (Inyección Directa)
# =================================================================
RAW_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDZ65TOBcYnHX7m\\nE63xCYr1a6CLuQ7nIlPdd1tafpZrQXgxBcE3n/9qid4PhbgFeR2zjA6rcoQpDggM\\nkcUlI/Jr71v6BV85BJCI2G633Kac/VQw4nyVmQf9kUpYm4yZLqNd6mV9Hg+As/+H\\nbAZE9wnU7YdvKzVgmnQehg+BYWt0MoZkmQPSYwgPCF5LFoLRkV1bLZ7dD0yXkAvq\\nlgwcxozcJVwpfSZqnXbjDOlOgFnJPwl05xDkiPfBEUC4+ASwmOT3VQ2trzX1iG/3\\nwqDQD8YgUpZkkkotDlU2+risHwz0WSmkAyYsh1TPl4huvu4d/fQxVRCmukMtg+d+\\nsVI3fimpAgMBAAECggEAJgGmVEBBjPTh+vKXtaA6cg8xUu0Vok4kXk3Aywmk5lPm\\nyHX+etsWytf8uKxTqfCzs2rL7C7uydI+qSKLRaz9TMHUQsjJEMKxCozk0oBTNrIg\\nCt6VZ+nmsNy0ILwQS28M4wZMaQPjJElAWbgHZ+PF/TLoGgVpK84EToaHEcOR4BPV\\nUYsHUc1vL+HqB6awCxiR9U2q2XeU5ft6VT43q0MPCCDVa+5FXfWUHRbS+nPFDbul\\nq97ly3OGCCmehV5zrDFqR4Pi8Ehz25i5cbO6Es4Mft3qI9qKekgHcGxDw2vETT7e\\nCC6MdzDAm/p4R8MbwlvfoH8BOq011V07rGaXuSLlYQKBgQD2npenwF2z7Hm+hUvU\\n42klBU1IT3lFb1MHl4K9MlmPOsPHcrxNLlB9SeHvqlQK4DBtQVvQ8Zpytsk+f1se\\n9VGuo9z6u3Rn5ZI7beDVlRGn6tPXPOmttdhrl3Wt7bfY0n7lIm3l/ONYuHYlvYQj\\nLTQgvC/FVx8oiX/9jnlmCCqwzQKBgQDiNYkctmY917nO0QTfypOdCT3SEhQGw4g4\\nOZ6wIZidKVXPYJ7dh9kAKwrPr2ZT+7h73t6qGpcMPJfcntORaf8sF5NBCS2WYb5H\\nTENzYHAiqvtMIMozFz/ocsbXPLvfC4TQ6cMEH2XQiKj47XJwJ32WFLvmLB5uCPU+\\nKPeM3lLsTQKBgE9jpDxLL57g7BwJuuyQPGO/fi5d7xMMEDVsb5jKIYx7BVUqOTW7\\nSAvdAc9uDFnn647wMEdlzytIbiYhR0sC+8V1WIiaWZGslFNvPqZis2lTrdgm8q6J\\n0F5qRma0FK/GqzTFzYzwyJrh3p6tkGDmh1ZWXiZvskcRZFNSTwAqdtutAoGAEvzF\\nZoiU6mn6Kbb3vsUlQNAuxTxJPAwbmgSUIlqfkcmPb1m/2/50I4R5YtdpMnF1mcgq\\nToLu3NMVOCqIvbL0/UF5VcMsdWv86cUoAD4/C1nowAocjs9LyPohYJ2zc1RnMJX+\\njZEJHcjqzgI4UduuufNBll9rqnbMBwyvQr7CnR0CgYB2RY+UKICd8gWQqp5VH7Fl\\n6rdPIBzGFUR3AUq8PMcwLdIw2TZJTqJEVZMQZv0E/pjKZVdQhZgAC8WXy7XGQC+q\\nUeUXwyUUcWuIEWwUlWif85G8rU1h/+lyFptZIzHFEpoSeVnOkfHQoz1PCj141P0J\\nGvk6wLGfN3UqZzlczKNWBg==\\n-----END PRIVATE KEY-----\\n"""

CREDENTIALS = {
    "type": "service_account",
    "project_id": "carranza-control",
    "private_key_id": "6b9bd2ca99c04651f14cd031cca6b755f4dc19ac",
    "private_key": RAW_PRIVATE_KEY.replace("\\n", "\n"),
    "client_email": "streamlit-sheets@carranza-control.iam.gserviceaccount.com",
    "client_id": "105455300514550592854",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-sheets%40carranza-control.iam.gserviceaccount.com"
}

ID_PLANILLA_RECETAS = "1RUXNBYG8mrnJdsCPN6UWDqNWVTwx-R47OJC15y3IZGg"
ID_PLANILLA_ALUMNOS = "1BikXKXQzYyhnmJsjz23-98v8MWg_u-G69_O0_xpeQoM"

def despachar_datos_a_sheet(nueva_fila, destino):
    """
    Función centralizada de escritura.
    destino puede ser: "recetas" o "alumnos"
    """
    try:
        gc = gspread.service_account_from_dict(CREDENTIALS)
        
        if destino == "recetas":
            spreadsheet_id = ID_PLANILLA_RECETAS
        elif destino == "alumnos":
            spreadsheet_id = ID_PLANILLA_ALUMNOS
        else:
            raise ValueError("Destino no válido.")
            
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.get_worksheet(0) 
        worksheet.append_row(nueva_fila)
        return True
    except Exception as e:
        st.error(f"Error crítico en módulo {destino}: {e}")
        return False
    
def leer_historico_filtrado(alumno_actual):
    """
    Trae los datos de la hoja de recetas y devuelve solo 
    los registros que coinciden con el alumno actual.
    """
    try:
        gc = gspread.service_account_from_dict(CREDENTIALS)
        sh = gc.open_by_key(ID_PLANILLA_RECETAS)
        worksheet = sh.get_worksheet(0)
        
        # Traer todos los registros como una lista de diccionarios
        todos_los_datos = worksheet.get_all_records()
        
        if not todos_los_datos:
            return pd.DataFrame()
            
        df = pd.DataFrame(todos_los_datos)
        
        # Convertimos los nombres de las columnas a mayúsculas/minúsculas estándar si es necesario
        # Asumiendo que la segunda columna en tu 'nueva_fila' guarda el nombre del alumno
        # Filtramos para que solo vea sus propios datos
        df_filtrado = df[df['Usuario'].astype(str).str.lower() == str(alumno_actual).lower()]
        
        return df_filtrado
    except Exception as e:
        st.error(f"Error al leer el histórico: {e}")
        return pd.DataFrame()
st.markdown("""
    <style>
    /* Fondo y colores principales */
    .stApp {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: #D4AF37 !important; /* Dorado */
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* Estilo para los botones de la barra lateral */
    .stSidebar {
        background-color: #1A1C23 !important;
    }
    /* Botón dorado personalizado */
    .stButton>button {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100%;
    }
    /* Estilo de métricas */
    [data-testid="stMetricValue"] {
        color: #D4AF37 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Función de datos optimizada
@st.cache_data(ttl=3600)
def get_data(url):
    try:
        # Cambiamos a read_excel para manejar archivos .xlsx de Google
        df = pd.read_excel(url) 
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        # Si falla el Excel, intentamos CSV por las dudas
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
 # 2. FUNCIONES DE APOYO (Corregidas)

# 2. FUNCIONES DE APOYO CORREGIDAS

def cargar_alumnos():
    try:
        # Usamos la conexión específica definida arriba
        return conn_alumnos.read(worksheet="Hoja 1", ttl=0)
    except Exception as e:
        st.error(f"Error al leer base de alumnos: {e}")
        return pd.DataFrame()

def guardar_receta_nube(nueva_fila):
    try:
        columnas_audit = ["Fecha", "Alumno", "Producto", "Costo_Neto", "Merma", "Costo_Real", "Precio_Sugerido"]
        
        try:
            # Traemos el histórico con la conexión explícita
            df_historico = conn_recetas.read(worksheet="recetas_archivo", ttl=0)
        except Exception:
            df_historico = pd.DataFrame(columns=columnas_audit)

        # Normalizamos la fila entrante para que no contenga tipos nativos complejos
        nuevo_registro = pd.DataFrame([nueva_fila], columns=columnas_audit)
        
        # Pasamos todo a string limpio para que impacte plano en las celdas
        nuevo_registro = nuevo_registro.astype(str)
        df_historico = df_historico.astype(str)

        df_final = pd.concat([df_historico, nuevo_registro], ignore_index=True)

        # Impactamos usando la conexión blindada
        conn_recetas.update(worksheet="recetas_archivo", data=df_final)
        return True

    except Exception as e:
        st.error(f"Error fatal en capa CRUD: {e}")
        return False
    
# Función para enviar datos a la nube
def registrar_receta_final(datos):
    try:
        # Aquí es donde conectarías con tu lógica de escritura (gspread o st.connection)
        # Por ahora, simulamos el éxito para que veas la interfaz funcionando
        # En una implementación real, aquí harías df.to_excel o sheet.append_row
        return True
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return False    
    
# 3. Definición de Variables y Secretos
try:
    SHEET_URL = st.secrets["general"]["sheet_url"]
    # 3. Definición de Variables
# Ya no necesitamos SHEET_URL para escribir, usamos las conexiones conn_alumnos y conn_recetas
    LINK_BASE = st.secrets.get("general", {}).get("form_url", "https://docs.google.com/forms/...")
except:
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTtRbAmRk1QRuV5yF0aQn-V31F553pSGK5RDhQcYywYY6CN2wfuBZvg3g2hGeO9rMtG745FVavNnZZW/pub?output=csv"
    LINK_BASE = "https://docs.google.com/forms/d/e/..."

# 4. Gestión de Sesión
if 'alumno' not in st.session_state:
    st.session_state.alumno = None

if st.session_state.alumno is None:
    st.title("💎 Carranza Control | Acceso")
    nombre = st.text_input("Ingrese su Nombre y Apellido:")
    if st.button("Iniciar Auditoría") and nombre:
        st.session_state.alumno = nombre
        st.rerun()
    st.stop()

# 5. Navegación
st.sidebar.title(f"👤 {st.session_state.alumno}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.alumno = None
    st.rerun()

menu = st.sidebar.radio("Navegación", ["Dashboard", "Inventario", "Escandallos", "Punto de Equilibrio"])
df_principal = get_data(SHEET_URL)

if st.session_state.alumno == "Gaston Carranza": # Acceso exclusivo para vos
    st.sidebar.divider()
    # Este link abre el Excel completo en una pestaña nueva
    link_excel = SHEET_URL.replace("output=csv", "output=xlsx")
    st.sidebar.link_button("📂 Abrir Excel Maestro", link_excel)

if menu == "Dashboard":
    st.title("📊 Dashboard de Gestión")
    
    # 1. Recuperamos la sesión del alumno activo de forma segura
    alumno_actual = st.session_state.get('alumno', None)
    
    # Inicialización limpia de variables de control
    df_principal = pd.DataFrame()
    error_conexion = None

    # =================================================================
    # CONEXIÓN ENCAPSULADA (Sin elementos visuales que rompan el DOM)
    # =================================================================
# =================================================================
# CARGA DE DATOS (Apertura y Cierre rápido del bloque Try)
# =================================================================
# =================================================================
# CARGA DE DATOS CON DIAGNÓSTICO DE RUTA ACTIVO
# =================================================================
df_principal = pd.DataFrame()
error_conexion = None

try:
    # Nivel 1 (4 espacios): Dentro del try principal
    ruta_local_creds = r"C:\Users\gaston carranza\OneDrive\Desktop\Carranza Control v1.0\credenciales_oficiales.json"
        
    # 1. FORZAMOS DETECCIÓN EN TU MÁQUINA LOCAL
    if os.name == 'nt':  # Si estás en Windows
        
        # Si la ruta exacta falla, investigamos qué está pasando en esa carpeta
        if not os.path.exists(ruta_local_creds):
            carpeta_padre = r"C:\Users\gaston carranza\OneDrive\Desktop\Carranza Control v1.0"
            if os.path.exists(carpeta_padre):
                archivos_encontrados = os.listdir(carpeta_padre)
                raise FileNotFoundError(
                    f"⚠️ El archivo 'credenciales.json' NO está en la ruta especificada.\n"
                    f"Archivos reales que detecto dentro de esa carpeta: {archivos_encontrados}\n"
                    f"Asegurate de que el nombre sea exactamente 'credenciales.json' y no 'credenciales.json.json'."
                )
            else:
                escritorio_base = r"C:\Users\gaston carranza\OneDrive"
                carpetas_onedrive = os.listdir(escritorio_base) if os.path.exists(escritorio_base) else "No encontré raíz de OneDrive"
                raise FileNotFoundError(
                    f"⚠️ No detecto la carpeta del proyecto en el Escritorio.\n"
                    f"Estructura de tu OneDrive: {carpetas_onedrive}\n"
                    f"Verificá si tu ruta del escritorio no se llama 'OneDrive - Personal' o algo similar."
                )
        
        # Conexión local limpia mediante archivo binario
        gc = gspread.service_account(filename=ruta_local_creds)
        
        try:
            url_alumnos = st.secrets["connections"]["gsheets_alumnos"]["spreadsheet"]
            sh = gc.open_by_url(url_alumnos)
        except:
            sh = gc.open("DB_CarranzaControl_Alumnos")
                
    # 2. ENTORNO NUBE (Solo corre si el servidor no es Windows / Streamlit Cloud)
    else:
        if "connections" in st.secrets and "gsheets_alumnos" in st.secrets["connections"]:
            creds_base = dict(st.secrets["connections"]["gsheets_alumnos"])
            url_planilla_alumnos = st.secrets["connections"]["gsheets_alumnos"]["spreadsheet"]
        else:
            raise KeyError("Faltan las credenciales relacionales en la nube.")

        # Armamos el diccionario asegurando que CADA campo requerido por Google exista sí o sí
        credentials_dict = {
            "type": "service_account",
            "project_id": creds_base.get("project_id"),
            "private_key_id": creds_base.get("private_key_id"),
            "private_key": creds_base.get("private_key").replace("\\n", "\n") if creds_base.get("private_key") else None,
            "client_email": creds_base.get("client_email"),
            "client_id": creds_base.get("client_id"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",  # 🛡️ ESCUDO: Forzado explícitamente para evitar el error
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{creds_base.get('client_email', '').replace('@', '%40')}"
        }
        
        gc = gspread.service_account_from_dict(credentials_dict)
        sh = gc.open_by_url(url_planilla_alumnos)

    # =================================================================
    # LECTURA UNIFICADA (Alineada a 4 espacios: Corre para ambos entornos)
    # =================================================================
    worksheet = sh.get_worksheet(0) 
    todos_los_datos = worksheet.get_all_records()
    if todos_los_datos:
        df_principal = pd.DataFrame(todos_los_datos)
    else:
        df_principal = pd.DataFrame()

    error_conexion = None

except Exception as e:
    # Regresa al ras del borde izquierdo para cerrar el try principal
    error_conexion = str(e)
    df_principal = pd.DataFrame()

# =================================================================
# INTERFAZ DE USUARIO (Alineado al ras del borde izquierdo)
# =================================================================

if error_conexion:
    st.error(f"❌ Error de Conexión: {error_conexion}")

elif menu == "Dashboard":
    # Acá abajo sigue tu código visual tal cual lo tenías...
    if not df_principal.empty:
        col_usuario = [c for c in df_principal.columns if 'usuario' in c.lower() or 'alumno' in c.lower()]
        alumno_safe = str(alumno_actual).lower().replace(' ', '_') if alumno_actual else "admin"

        if alumno_actual and col_usuario:
            df_dashboard = df_principal[df_principal[col_usuario[0]].astype(str).str.lower() == str(alumno_actual).lower()].copy()
            texto_contexto = f" (Filtro activo: {alumno_actual})"
        else:
            df_dashboard = df_principal.copy()
            texto_contexto = " (Consolidado General)"

        st.caption(f"📌 Vista actual: {texto_contexto}")
        
        if not df_dashboard.empty:
            col_p = [c for c in df_dashboard.columns if 'precio' in c or 'costo' in c][0]
            col_q = [c for c in df_dashboard.columns if 'cantidad' in c or 'stock' in c][0]
            col_fecha = [c for c in df_dashboard.columns if 'fecha' in c]

            df_dashboard['valor_total'] = df_dashboard[col_p] * df_dashboard[col_q]
            
            if col_fecha:
                df_dashboard[col_fecha[0]] = pd.to_datetime(df_dashboard[col_fecha[0]], errors='coerce')
                df_dashboard = df_dashboard.sort_values(by=col_fecha[0], ascending=False)
            
            total_inventario = df_dashboard['valor_total'].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Insumos Activos", len(df_dashboard), key=f"met_ins_act_{alumno_safe}")
            c2.metric("VALOR TOTAL STOCK", f"$ {total_inventario:,.2f}", key=f"met_val_tot_{alumno_safe}")
            c3.metric("Estado", "Auditoría Ok" if alumno_actual else "Modo Admin", key=f"met_est_{alumno_safe}")
            
            st.divider()
            st.write("📂 **Acciones del Sistema:**")
            
            link_drive = st.secrets["connections"]["gsheets_alumnos"]["spreadsheet"] if "connections" in st.secrets else "https://drive.google.com"
            st.link_button("🚀 VALIDAR EN GOOGLE DRIVE", url=link_drive, use_container_width=True)
            
            st.divider()

            with st.expander("👁️ Ver detalle de existencias (Ordenado por Fecha)"):
                st.dataframe(
                    df_dashboard, 
                    use_container_width=True, 
                    hide_index=True,
                    key=f"df_dash_view_{alumno_safe}"
                )
        else:
            st.info(f"💡 Hola {alumno_actual}, actualmente no tenés insumos registrados en tu inventario.")
    else:
        st.warning("⚠️ No se encontraron registros para procesar el Dashboard.")

elif menu == "Inventario":
    st.title("📦 Carga de Insumos")
    
    # 🌟 Estabilizamos la Key y nos aseguramos de que acepte formatos correctos.
    # Si vas a cargar imágenes de remitos físicos, dejamos estos types pero bien declarados.
    id_u = f"uploader_inv_{st.session_state.alumno.replace(' ', '_')}"
    archivo = st.file_uploader("📁 Subir remito físico", type=["jpg", "png", "jpeg"], key=id_u)

    if archivo:
        st.image(archivo, width=300)
        
        # Estabilizamos el ID del formulario para que React no rompa el frontend
        with st.form(key=f"form_carga_{st.session_state.alumno.replace(' ', '_')}"):
            st.subheader("Confirmar Datos")
            
            # Evitamos que rompa si 'nombre' no existe en las columnas de tu DF maestro
            opciones_insumos = []
            if not df_principal.empty:
                col_nombre = [c for c in df_principal.columns if 'nombre' in c.lower()]
                if col_nombre:
                    opciones_insumos = df_principal[col_nombre[0]].dropna().unique().tolist()
            
            if not opciones_insumos:
                opciones_insumos = ["Ejemplo Insumo Base"] # Callback por seguridad
                
            insumo = st.selectbox("Insumo", opciones_insumos)
            cantidad = st.number_input("Cantidad", min_value=0.1, value=1.0, step=1.0)
            precio = st.number_input("Precio Unitario", min_value=0.0, value=0.0, step=10.0)
            
            if st.form_submit_button("Generar Enlace"):
                # Formateamos el link de forma segura
                link_armado = LINK_BASE.replace("NOMBRE", urllib.parse.quote(str(insumo)))
                link_armado = link_armado.replace("111", str(cantidad)).replace("222", str(precio))
                
                st.divider()
                st.write("👉 **Presioná el botón dorado para registrar los datos:**")
                
                # 🌟 BOTÓN HTML LIMPIO Y CORREGIDO (Quitamos el código Streamlit mezclado dentro del string)
                st.markdown(f'''
                    <a href="{link_armado}" target="_blank" style="text-decoration: none;">
                        <button style="background-color:#D4AF37; color:black; padding:18px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer; border:none; font-size:16px; transition: 0.3s;">
                            🚀 VALIDAR EN GOOGLE DRIVE
                        </button>
                    </a>
                ''', unsafe_allow_html=True)

elif menu == "Escandallos":
    st.title("🍳 Calculadora de Fichas Técnicas")
    st.write("Definí el nombre de tu producto y seleccioná los insumos de la base de datos.")

    if not df_principal.empty:
        col_form, col_res = st.columns([2, 1])

        with col_form:
            st.subheader("🛠️ Composición de la Receta")
            nombre_p = st.text_input("📦 Nombre del Producto:", "Ej: Baguette", key="nombre_prod_esc")
            insumos_sel = st.multiselect("Seleccioná ingredientes:", df_principal['nombre'].tolist())

            receta_data = []
            # --- INICIO DEL BUCLE: Esto solo pide cantidades ---
            for insumo in insumos_sel:
                st.write(f"--- **{insumo}** ---")
                c1, c2 = st.columns(2)
                
                datos_insumo = df_principal[df_principal['nombre'] == insumo]
                cols_precio = [c for c in df_principal.columns if 'precio' in c or 'costo' in c or 'valor' in c]
                
                costo_u = float(datos_insumo[cols_precio[0]].values[0]) if cols_precio else 0.0
                
                with c1:
                    cantidad = st.number_input(f"Cantidad para {insumo}", min_value=0.001, value=1.0, key=f"cant_{insumo}")
                with c2:
                    st.caption(f"Costo unitario: ${costo_u:,.2f}")
                    st.caption(f"Subtotal: ${cantidad * costo_u:,.2f}")
                
                receta_data.append({"insumo": insumo, "cantidad": cantidad, "costo_u": costo_u})
            # --- FIN DEL BUCLE ---

        with col_res:
            st.subheader("💰 Análisis de Rentabilidad")
            st.info(f"Análisis para: **{nombre_p}**")
            
            if receta_data:
                # 1. CÁLCULOS BASE REALES
                costo_neto = sum(item['cantidad'] * item['costo_u'] for item in receta_data)
                
                # Slider único por sesión de alumno
                merma_esc = st.slider("% Merma Operativa", 0, 50, 10, key=f"fixed_merma_v2_{st.session_state.alumno}")
                
                costo_real = costo_neto / (1 - (merma_esc / 100))
                st.metric("Costo Neto Total", f"$ {costo_neto:,.2f}")
                st.metric("Costo Real (con Merma)", f"$ {costo_real:,.2f}", delta=f"{merma_esc}%")
                
                st.divider()
                margen = st.number_input("% Margen deseado", 50, 500, 200, key=f"margen_esc_{st.session_state.alumno}")
                precio_sugerido = costo_real * (1 + (margen/100))
                
                # Cuadro de resultado final dorado
                st.markdown(f"""
                    <div style="background-color:#1A1C23; padding:20px; border-radius:10px; border: 2px solid #D4AF37; text-align:center;">
                        <p style="color:white; margin-bottom:5px;">Sugerido para <b>{nombre_p}</b></p>
                        <h1 style="color:#D4AF37; margin:0;">$ {precio_sugerido:,.2f}</h1>
                    </div>
                """, unsafe_allow_html=True)

                # Definición segura de la variable de entorno para las llaves
                alumno_actual = st.session_state.alumno if hasattr(st.session_state, 'alumno') and st.session_state.alumno else "No_especificado"

                # =================================================================
                # 2. GENERACIÓN DEL CONTENIDO DE TEXTO (PASADO ARRIBA DE LOS BOTONES)
                # =================================================================
                contenido_imprimir = f"""==================================================
RECETA DE: {nombre_p.upper()}
==================================================
Fecha de Análisis: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
Usuario: {alumno_actual}

--------------------------------------------------
METRICAS DE COSTOS:
--------------------------------------------------
> Costo Neto Base:   $ {costo_neto:,.2f}
> Porcentaje Merma:  {merma_esc}%
> Costo Real Total:  $ {costo_real:,.2f}
--------------------------------------------------
> PRECIO SUGERIDO:   $ {precio_sugerido:,.2f}
==================================================
Generado automáticamente por Carranza Control v1.1
"""                                     

                st.divider()

                # =================================================================
                # 3. ACCIONES Y BOTONES (Ahora que existe la variable, no va a fallar)
                # =================================================================
                
                # Botón de descarga de receta individual
                st.download_button(
                    label="📥 Descargar Receta",
                    data=contenido_imprimir,
                    file_name=f"receta_{nombre_p.replace(' ', '_')}.txt",
                    mime="text/plain",
                    key=f"dl_btn_{alumno_actual}"
                )

                # Botón de grabado en Google Sheets
                if st.button("💾 Grabar Receta en el Histórico", key=f"save_btn_{alumno_actual}"):
                    nueva_fila = [
                        pd.Timestamp.now().strftime('%d/%m/%Y %H:%M'),
                        str(alumno_actual),
                        str(nombre_p),
                        round(costo_neto, 2),
                        f"{merma_esc}%",
                        round(costo_real, 2),
                        round(precio_sugerido, 2)
                    ]
                    with st.spinner("Guardando en el histórico..."):
                        exito = despachar_datos_a_sheet(nueva_fila, destino="recetas")
                    if exito:
                        st.success(f"✅ ¡Receta de '{nombre_p}' grabada con éxito!")
                        st.balloons()
                    else:
                        st.error("❌ Error de guardado. Revisá credenciales.")

                # --- SECCIÓN HISTÓRICO PERSONAL ---
                st.markdown("---")
                st.subheader(f"📋 Tu Histórico de Auditorías ({alumno_actual})")
                
                placeholder_historial = st.empty()

                with placeholder_historial.container():
                    with st.spinner("Cargando tus registros personales..."):
                        df_alumno = leer_historico_filtrado(alumno_actual)

                # Ahora renderizamos la tabla por fuera del bloque del spinner
                if not df_alumno.empty:
                    st.dataframe(
                        df_alumno, 
                        use_container_width=True,
                        hide_index=True,
                        key=f"df_recetas_hist_{alumno_actual}" # 👈 Clave única para evitar el cruce
                    )
                    csv = df_alumno.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📊 Exportar mi histórico a CSV",
                        data=csv,
                        file_name=f"historico_{alumno_actual.replace(' ', '_')}.csv",
                        mime="text/csv",
                        key=f"dl_csv_hist_{alumno_actual}"
                    )
                else:
                    st.info(f"Aún no tenés recetas grabadas en el histórico, {alumno_actual}.")     
        
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
        