import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import os
import urllib.parse
import numpy as np

# =================================================================
# CONFIGURACIÓN DE PÁGINA (Debe ser SIEMPRE la primera línea)
# =================================================================
st.set_page_config(page_title="Carranza Control v1.1", layout="wide", page_icon="💎")

# =================================================================
# 1. CREDENCIALES Y PARÁMETROS DE CONEXIÓN (Inyección Directa)
# =================================================================
RAW_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDZ65TOBcYnHX7m\nE63xCYr1a6CLuQ7nIlPdd1tafpZrQXgxBcE3n/9qid4PhbgFeR2zjA6rcoQpDggM\nkcUlI/Jr71v6BV85BJCI2G633Kac/VQw4nyVmQf9kUpYm4yZLqNd6mV9Hg+As/+H\nbAZE9wnU7YdvKzVgmnQehg+BYWt0MoZkmQPSYwgPCF5LFoLRkV1bLZ7dD0yXkAvq\nlgwcxozcJVwpfSZqnXbjDOlOgFnJPwl05xDkiPfBEUC4+ASwmOT3VQ2trzX1iG/3\nwqDQD8YgUpZkkkotDlU2+risHwz0WSmkAyYsh1TPl4huvu4d/fQxVRCmukMtg+d+\nsVI3fimpAgMBAAECggEAJgGmVEBBjPTh+vKXtaA6cg8xUu0Vok4kXk3Aywmk5lPm\nyHX+etsWytf8uKxTqfCzs2rL7C7uydI+qSKLRaz9TMHUQsjJEMKxCozk0oBTNrIg\nCt6VZ+nmsNy0ILwQS28M4wZMaQPjJElAWbgHZ+PF/TLoGgVpK84EToaHEcOR4BPV\nUYsHUc1vL+HqB6awCxiR9U2q2XeU5ft6VT43q0MPCCDVa+5FXfWUHRbS+nPFDbul\nq97ly3OGCCmehV5zrDFqR4Pi8Ehz25i5cbO6Es4Mft3qI9qKekgHcGxDw2vETT7e\nCC6MdzDAm/p4R8MbwlvfoH8BOq011V07rGaXuSLlYQKBgQD2npenwF2z7Hm+hUvU\n42klBU1IT3lFb1MHl4K9MlmPOsPHcrxNLlB9SeHvqlQK4DBtQVvQ8Zpytsk+f1se\n9VGuo9z6u3Rn5ZI7beDVlRGn6tPXPOmttdhrl3Wt7bfY0n7lIm3l/ONYuHYlvYQj\nLTQgvC/FVx8oiX/9jnlmCCqwzQKBgQDiNYkctmY917nO0QTfypOdCT3SEhQGw4g4\nOZ6wIZidKVXPYJ7dh9kAKwrPr2ZT+7h73t6qGpcMPJfcntORaf8sF5NBCS2WYb5H\nTENzYHAiqvtMIMozFz/ocsbXPLvfC4TQ6cMEH2XQiKj47XJwJ32WFLvmLB5uCPU+\nKPeM3lLsTQKBgE9jpDxLL57g7BwJuuyQPGO/fi5d7xMMEDVsb5jKIYx7BVUqOTW7\nSAvdAc9uDFnn647wMEdlzytIbiYhR0sC+8V1WIiaWZGslFNvPqZis2lTrdgm8q6J\n0F5qRma0FK/GqzTFzYzwyJrh3p6tkGDmh1ZWXiZvskcRZFNSTwAqdtutAoGAEvzF\nZoiU6mn6Kbb3vsUlQNAuxTxJPAwbmgSUIlqfkcmPb1m/2/50I4R5YtdpMnF1mcgq\nToLu3NMVOCqIvbL0/UF5VcMsdWv86cUoAD4/C1nowAocjs9LyPohYJ2zc1RnMJX+\njZEJHcjqzgI4UduuufNBll9rqnbMBwyvQr7CnR0CgYB2RY+UKICd8gWQqp5VH7Fl\n6rdPIBzGFUR3AUq8PMcwLdIw2TZJTqJEVZMQZv0E/pjKZVdQhZgAC8WXy7XGQC+q\nUeUXwyUUcWuIEWwUlWif85G8rU1h/+lyFptZIzHFEpoSeVnOkfHQoz1PCj141P0J\nGvk6wLGfN3UqZzlczKNWBg==\n-----END PRIVATE KEY-----\n"""

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

# URL de respaldo para administradores
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{ID_PLANILLA_RECETAS}/edit?usp=sharing"

# =================================================================
# 2. FUNCIONES DE LECTURA SEGURA ANTI-DUPLICADOS
# =================================================================
def leer_hoja_segura(worksheet_obj):
    """
    Lee cualquier pestaña de Google Sheets usando get_all_values()
    y resuelve dinámicamente duplicados o vacíos en los encabezados.
    """
    try:
        filas_puras = worksheet_obj.get_all_values() 
        
        if not filas_puras:
            return pd.DataFrame()
            
        encabezados_originales = filas_puras[0]
        encabezados_seguros = []
        
        for i, col in enumerate(encabezados_originales):
            nombre = col.strip()
            if nombre == "" or nombre in encabezados_seguros:
                encabezados_seguros.append(f"Columna_{i}_{nombre if nombre else 'vacia'}")
            else:
                encabezados_seguros.append(nombre)
        
        return pd.DataFrame(filas_puras[1:], columns=encabezados_seguros)
        
    except Exception as e_proc:
        st.error(f"⚠️ Error en lectura segura de pestaña: {str(e_proc)}")
        return pd.DataFrame()

@st.cache_data(ttl=60)  
def cargar_hoja_segura(_ws):
    """
    Versión con caché de lectura segura para optimizar llamadas.
    """
    return leer_hoja_segura(_ws)

# =================================================================
# 3. MÓDULOS CRUD Y LOGÍSTICA DE DATOS (Centralizados con gspread)
# =================================================================
def despachar_datos_a_sheet(nueva_fila, destino):
    """
    Función centralizada de escritura masiva/individual.
    """
    try:
        gc = gspread.service_account_from_dict(CREDENTIALS)
        spreadsheet_id = ID_PLANILLA_RECETAS if destino == "recetas" else ID_PLANILLA_ALUMNOS
            
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.get_worksheet(0) 
        worksheet.append_row(nueva_fila)
        return True
    except Exception as e:
        st.error(f"Error crítico en módulo de escritura {destino}: {e}")
        return False
    
def leer_historico_filtrado(alumno_actual):
    """
    Trae los datos históricos mapeando la variable 'todos_los_datos' 
    y 'df_principal' para blindar el Dashboard global.
    """
    try:
        gc = gspread.service_account_from_dict(CREDENTIALS)
        sh = gc.open_by_key(ID_PLANILLA_RECETAS)
        worksheet = sh.get_worksheet(0)
        
        df_principal = leer_hoja_segura(worksheet)
        
        if df_principal.empty:
            return pd.DataFrame()
            
        # 🛡️ EL PUENTE DEFINITIVO: Resolvemos la variable huérfana para todo el script
        st.session_state["todos_los_datos"] = df_principal.copy()
        
        if 'Alumno' in df_principal.columns:
            df_filtrado = df_principal[df_principal['Alumno'] == alumno_actual]
        else:
            df_filtrado = df_principal.copy()
        
        return df_filtrado
    except Exception as e:
        st.error(f"⚠️ Error al leer el histórico: {e}")
        return pd.DataFrame()

def cargar_alumnos():
    """
    Carga la lista de alumnos registrados usando la API segura.
    """
    try:
        gc = gspread.service_account_from_dict(CREDENTIALS)
        sh = gc.open_by_key(ID_PLANILLA_ALUMNOS)
        worksheet = sh.get_worksheet(0)
        return leer_hoja_segura(worksheet)
    except Exception as e:
        st.error(f"Error al leer base de alumnos: {e}")
        return pd.DataFrame()

def guardar_receta_nube(nueva_fila):
    """
    Inserta recetas en el archivo histórico asegurando consistencia.
    """
    try:
        gc = gspread.service_account_from_dict(CREDENTIALS)
        sh = gc.open_by_key(ID_PLANILLA_RECETAS)
        worksheet = sh.get_worksheet(0)
        
        # Mapeamos plano directo usando append_row
        worksheet.append_row([str(x) for x in nueva_fila])
        return True
    except Exception as e:
        st.error(f"Error fatal en capa CRUD de recetas: {e}")
        return False

# =================================================================
# 4. DISEÑO DE INTERFAZ (CSS INYECTADO)
# =================================================================
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Helvetica Neue', sans-serif; }
    .stSidebar { background-color: #1A1C23 !important; }
    .stButton>button {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100%;
    }
    [data-testid="stMetricValue"] { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 5. CONFIGURACIÓN DE ACCESOS Y SESIÓN
# =================================================================
LINK_BASE = st.secrets.get("general", {}).get("form_url", "https://docs.google.com/forms/...")

if 'alumno' not in st.session_state:
    st.session_state.alumno = None

if st.session_state.alumno is None:
    st.title("💎 Carranza Control | Acceso")
    nombre = st.text_input("Ingrese su Nombre y Apellido:")
    if st.button("Iniciar Auditoría") and nombre:
        st.session_state.alumno = nombre.strip()
        st.rerun()
    st.stop()

# Si el flujo pasa de acá, cargamos los datos históricos obligatorios
df_historico_alumno = leer_historico_filtrado(st.session_state.alumno)

# 5. Navegación
st.sidebar.title(f"👤 {st.session_state.alumno}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.alumno = None
    st.rerun()

menu = st.sidebar.radio("Navegación", ["Dashboard", "Inventario", "Escandallos", "Punto de Equilibrio"])

# Inicializamos gspread para la lectura global del script
try:
    gc = gspread.service_account_from_dict(CREDENTIALS)
    sh = gc.open_by_key(ID_PLANILLA_RECETAS)
    worksheet_maestra = sh.get_worksheet(0)

    # Leemos de forma segura resolviendo duplicados en el acto
    df_principal = leer_hoja_segura(worksheet_maestra)

    # 🛡️ CONVERSIÓN SEGURA A NÚMEROS
    columnas_numericas = ['Cantidad', 'Precio Unitario', 'Subtotal', 'Precio', 'Costo_Neto', 'Costo_Real', 'Precio_Sugerido', 'nombre']
    for col in columnas_numericas:
        if col in df_principal.columns:
            df_principal[col] = pd.to_numeric(df_principal[col].astype(str).str.replace(',', '.').str.extract(r'([\d\.]+)')[0], errors='coerce').fillna(0.0)

    # Aseguramos que la columna 'nombre' exista o esté normalizada si se usa en Escandallos
    if 'nombre' not in df_principal.columns and 'Insumo / Producto' in df_principal.columns:
        df_principal['nombre'] = df_principal['Insumo / Producto']

    # 🛡️ VALIDACIÓN CORRECTA ANTI-AMBIGÜEDAD
    if df_principal.empty:
        df_principal = pd.DataFrame()
        todos_los_datos = pd.DataFrame()
        st.session_state["todos_los_datos"] = pd.DataFrame()
    else:
        # Alimentamos el puente de datos seguro para el resto de los módulos
        todos_los_datos = df_principal.copy()
        st.session_state["todos_los_datos"] = df_principal.copy()
    
except Exception as e_global:
    st.error(f"⚠️ Error al inicializar los datos globales: {e_global}")
    df_principal = pd.DataFrame()
    todos_los_datos = pd.DataFrame()
    st.session_state["todos_los_datos"] = pd.DataFrame()

if st.session_state.alumno == "Gaston Carranza": # Acceso exclusivo para vos
    st.sidebar.divider()
    link_excel = SHEET_URL.replace("edit?usp=sharing", "export?format=xlsx")
    st.sidebar.link_button("📂 Abrir Excel Maestro", link_excel)

if menu == "Dashboard":
    st.title("📊 Dashboard de Gestión")
    
    # 1. Recuperamos la sesión del alumno activo de forma segura
    alumno_actual = st.session_state.get('alumno', None)
    
    df_principal = pd.DataFrame()
    error_conexion = None

    try:
        ruta_local_creds = r"C:\Users\gaston carranza\OneDrive\Desktop\Carranza Control v1.0\credenciales_oficiales.json"
            
        # 1. FORZAMOS DETECCIÓN EN TU MÁQUINA LOCAL (Windows)
        if os.name == 'nt':  
            if not os.path.exists(ruta_local_creds):
                carpeta_padre = r"C:\Users\gaston carranza\OneDrive\Desktop\Carranza Control v1.0"
                if os.path.exists(carpeta_padre):
                    archivos_encontrados = os.listdir(carpeta_padre)
                    raise FileNotFoundError(
                        f"⚠️ El archivo 'credenciales_oficiales.json' NO está en la ruta.\n"
                        f"Archivos en carpeta: {archivos_encontrados}"
                    )
                else:
                    raise FileNotFoundError("⚠️ No detecto la carpeta del proyecto en el Escritorio Windows.")
            
            gc = gspread.service_account(filename=ruta_local_creds)
            try:
                # Intentamos abrir la de recetas para consolidar el inventario real del alumno
                sh = gc.open_by_key(ID_PLANILLA_RECETAS)
            except:
                sh = gc.open("DB_CarranzaControl_Alumnos")
                    
        # 2. ENTORNO NUBE (Streamlit Cloud)
        else:
            if "connections" in st.secrets and "gsheets_alumnos" in st.secrets["connections"]:
                creds_base = dict(st.secrets["connections"]["gsheets_alumnos"])
            else:
                raise KeyError("Faltan las credenciales relacionales en la nube.")

            credentials_dict = {
                "type": "service_account",
                "project_id": creds_base.get("project_id"),
                "private_key_id": creds_base.get("private_key_id"),
                "private_key": creds_base.get("private_key").replace("\\n", "\n") if creds_base.get("private_key") else None,
                "client_email": creds_base.get("client_email"),
                "client_id": creds_base.get("client_id"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/raw/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{creds_base.get('client_email', '').replace('@', '%40')}"
            }
            
            gc = gspread.service_account_from_dict(credentials_dict)
            sh = gc.open_by_key(ID_PLANILLA_RECETAS)

        # =================================================================
        # LECTURA DE DATOS PARA EL DASHBOARD (CON CAÍDA SEGURA)
        # =================================================================
        # =================================================================
        # LECTURA DE DATOS PARA EL DASHBOARD (CON INTENTO INTELIGENTE Y CAÍDA SEGURA)
        # =================================================================
        try:
            # 1. Intento primario: Buscar la pestaña específica de Inventario
            worksheet = sh.worksheet("Inventario")
            df_principal = leer_hoja_segura(worksheet)
        except Exception:
            try:
                # 2. Intento secundario: Si no existe "Inventario", leemos la primera pestaña disponible de la planilla abierta
                worksheet = sh.get_worksheet(0)
                df_principal = leer_hoja_segura(worksheet)
            except Exception:
                # Si ambas fallan, inicializamos vacío para forzar el uso del backup en memoria
                df_principal = pd.DataFrame()
        
        # 🔄 BACKUP SEGURO: Si la lectura directa de Drive falló o quedó vacía, recuperamos la persistencia en memoria
        if df_principal.empty and "todos_los_datos" in st.session_state:
            if isinstance(st.session_state["todos_los_datos"], pd.DataFrame) and not st.session_state["todos_los_datos"].empty:
                df_principal = st.session_state["todos_los_datos"].copy()
            elif isinstance(st.session_state["todos_los_datos"], list) and st.session_state["todos_los_datos"]:
                df_principal = pd.DataFrame(st.session_state["todos_los_datos"])

        # Si después de agotar Drive y Memoria sigue vacío, lanzamos el aviso controlado sin romper la app
        if df_principal.empty:
            raise ValueError("No se encontraron datos válidos en Drive (pestaña 'Inventario' o Principal) ni registros activos en la sesión actual.")

        error_conexion = None

    except Exception as e:
        # Captura cualquier falla crítica de credenciales o el ValueError de arriba
        error_conexion = str(e)
        df_principal = pd.DataFrame()

    else:
        if not df_principal.empty:
            # Normalizamos nombres de columnas a minúsculas para mapear sin fallas
            columnas_lowercase = [c.lower() for c in df_principal.columns]
            
            col_usuario = [df_principal.columns[i] for i, c in enumerate(columnas_lowercase) if 'usuario' in c or 'alumno' in c or 'sucursal' in c]
            alumno_safe = str(alumno_actual).lower().replace(' ', '_') if alumno_actual else "admin"

            if alumno_actual and col_usuario:
                df_dashboard = df_principal[df_principal[col_usuario[0]].astype(str).str.lower() == str(alumno_actual).lower()].copy()
                texto_contexto = f" (Filtro activo: {alumno_actual})"
            else:
                df_dashboard = df_principal.copy()
                texto_contexto = " (Consolidado General)"

            st.caption(f"📌 Vista actual: {texto_contexto}")
            
            if not df_dashboard.empty:
                # 🛡️ ESCUDO ANTI INDEX-ERROR: Buscamos posiciones dinámicamente con tus columnas reales
                columnas_dash_lower = [c.lower() for c in df_dashboard.columns]
                
                # Mapeo de Precio/Costo: Busca costo_real, costo_neto, precio_sugerido, etc.
                indices_p = [i for i, c in enumerate(columnas_dash_lower) if 'precio' in c or 'costo' in c or 'valor' in c or 'subtotal' in c]
                
                # Mapeo de Cantidad/Stock: Busca cantidad, stock, cerrado, merma, etc.
                indices_q = [i for i, c in enumerate(columnas_dash_lower) if 'cantidad' in c or 'stock' in c or 'cerrado' in c or 'merma' in c]
                
                # 📅 DETECCIÓN DE FECHA (Esto evita el NameError)
                col_fecha = [df_dashboard.columns[i] for i, c in enumerate(columnas_dash_lower) if 'fecha' in c]

                # Asignación segura de columnas
                col_p = df_dashboard.columns[indices_p[0]] if indices_p else None
                col_q = df_dashboard.columns[indices_q[0]] if indices_q else None

                # 🚀 AJUSTE TÁCTICO: Si falta la columna de cantidad (Stock), forzamos un fallback inteligente
                if col_p and not col_q:
                    st.info("💡 Se detectaron costos pero no columna de Stock. Calculando valor unitario base (Cantidad = 1).")
                    df_dashboard['Cantidad_Ficticia'] = 1.0
                    col_q = 'Cantidad_Ficticia'

                if not col_p:
                    st.warning("⚠️ No se detectó ninguna columna de costo o precio. Mostrando vista cruda.")
                    st.dataframe(df_dashboard, use_container_width=True, hide_index=True)
                else:
                    # Forzamos la conversión limpia a números
                    df_dashboard[col_p] = pd.to_numeric(df_dashboard[col_p].astype(str).str.replace(',', '.').str.extract(r'([\d\.]+)')[0], errors='coerce').fillna(0.0)
                    df_dashboard[col_q] = pd.to_numeric(df_dashboard[col_q].astype(str).str.replace(',', '.').str.extract(r'([\d\.]+)')[0], errors='coerce').fillna(0.0)
                    
                    # 🚀 LÍNEA CLAVE: Calculamos el valor total multiplicando Costo/Precio por Cantidad
                    df_dashboard['valor_total'] = df_dashboard[col_p] * df_dashboard[col_q]
                    
                    # Formateo y ordenamiento por fecha si existe la columna
                    if col_fecha:
                        df_dashboard[col_fecha[0]] = pd.to_datetime(df_dashboard[col_fecha[0]], errors='coerce')
                        df_dashboard = df_dashboard.sort_values(by=col_fecha[0], ascending=False)
                    
                    # 📊 Ahora sí, ejecutamos la sumatoria para las métricas del Dashboard
                    total_inventario = df_dashboard['valor_total'].sum()
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Insumos Activos", len(df_dashboard))
                    c2.metric("VALOR TOTAL STOCK", f"$ {total_inventario:,.2f}")
                    c3.metric("Estado", "Auditoría Ok" if alumno_actual else "Modo Admin")
                    
                    st.divider()
                    st.write("📂 **Acciones del Sistema:**")
                    
                    st.link_button("🚀 VALIDAR EN GOOGLE DRIVE", url=SHEET_URL, use_container_width=True)
                    
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

# Aquí continúa con "elif menu == "Inventario":"...

elif menu == "Inventario":
    st.title("📦 Centro de Carga y Gestión de Stock")
    st.caption(f"👤 Operando como: **{st.session_state.alumno}**")

    tipo_movimiento = st.selectbox(
        "📝 Seleccionar Tipo de Registro",
        ["Remito de Entrada (Stock)", "Factura de Compra (Proveedor)", "Control de Movimiento Manual"]
    )

    id_u = f"uploader_inv_{st.session_state.alumno.replace(' ', '_')}"
    archivo = st.file_uploader("📁 Arrastrá tu planilla de Excel / CSV o Factura aquí", type=["xlsx", "xls", "csv"], key=id_u)

    if archivo:
        try:
            if archivo.name.endswith('.csv'):
                df_remito = pd.read_csv(archivo, encoding='latin1')
            else:
                df_remito = pd.read_excel(archivo)
            
            df_remito = df_remito.where(pd.notnull(df_remito), None)
            
            st.write("👀 **Verificación previa de las filas detectadas en tu planilla:**")
            st.dataframe(df_remito.head(5), use_container_width=True, hide_index=True)
            
            with st.form(key=f"form_grabado_directo_{st.session_state.alumno.replace(' ', '_')}"):
                st.subheader("📋 Parámetros de Carga")
                observaciones = st.text_input("Observaciones o N° Comprobante", value=f"Carga via {archivo.name}")
                
                if st.form_submit_button("💾 GRABAR DIRECTO EN GOOGLE DRIVE"):
                    with st.spinner("💾 Procesando columnas e impactando en Google Drive..."):
                        
                        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        filas_a_insertar = []
                        
                        for _, fila in df_remito.iterrows():
                            producto = fila.get('Producto', fila.get('producto', None))
                            
                            if not producto or str(producto).strip() == "":
                                continue
                                
                            proveedor_origen = fila.get('Proveedor', fila.get('proveedor', 'Desconocido'))
                            if not proveedor_origen:
                                proveedor_origen = 'Desconocido'
                            
                            raw_cantidad = fila.get('Subtotal', fila.get('cerrado', 1.0))
                            try:
                                cantidad = float(raw_cantidad) if raw_cantidad is not None else 1.0
                            except:
                                cantidad = 1.0
                                
                            raw_precio = fila.get('Precio', fila.get('precio', 0.0))
                            try:
                                precio_unitario = float(raw_precio) if raw_precio is not None else 0.0
                            except:
                                precio_unitario = 0.0

                            registro = [
                                fecha_actual,                            # 1. Fecha
                                st.session_state.alumno,                  # 2. Alumno / Sucursal
                                tipo_movimiento,                         # 3. Tipo de Registro
                                str(producto).strip(),                   # 4. Insumo / Producto
                                cantidad,                                # 5. Cantidad
                                precio_unitario,                         # 6. Precio Unitario
                                str(proveedor_origen).strip(),           # 7. Proveedor
                                str(observaciones).strip()               # 8. Observaciones
                            ]
                            filas_a_insertar.append(registro)
                        
                        if filas_a_insertar:
                            try:
                                gc = gspread.service_account_from_dict(CREDENTIALS)
                                sh = gc.open_by_key(ID_PLANILLA_RECETAS)
                                worksheet_historico = sh.get_worksheet(0)
                                
                                worksheet_historico.append_rows(
                                    filas_a_insertar, 
                                    value_input_option='USER_ENTERED',
                                    insert_data_option='INSERT_ROWS'
                                )
                                
                                st.success(f"🔥 ¡Éxito! Se grabaron {len(filas_a_insertar)} registros de stock en Google Drive.")
                                st.balloons()
                            except Exception as err_api:
                                st.error(f"⚠️ Error de escritura en la API de Google Sheets: {str(err_api)}")
                        else:
                            st.warning("⚠️ No se detectaron productos válidos para procesar en el archivo.")
                            
        except Exception as e_archivo:
            st.error(f"⚠️ Error al procesar el archivo subido: {str(e_archivo)}")

elif menu == "Escandallos":
    st.title("🍳 Calculadora de Fichas Técnicas")
    st.write("Definí el nombre de tu producto y seleccioná los insumos de la base de datos.")

    if not df_principal.empty:
        col_form, col_res = st.columns([2, 1])

        with col_form:
            st.subheader("🛠️ Composición de la Receta")
            nombre_p = st.text_input("📦 Nombre del Producto:", "Ej: Baguette", key="nombre_prod_esc")
            
            opciones_insumos = []
            if 'nombre' in df_principal.columns:
                opciones_insumos = df_principal['nombre'].dropna().unique().tolist()
            
            insumos_sel = st.multiselect("Seleccioná ingredientes:", opciones_insumos)

            receta_data = []
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

        with col_res:
            st.subheader("💰 Análisis de Rentabilidad")
            st.info(f"Análisis para: **{nombre_p}**")
            
            if receta_data:
                costo_neto = sum(item['cantidad'] * item['costo_u'] for item in receta_data)
                merma_esc = st.slider("% Merma Operativa", 0, 50, 10, key=f"fixed_merma_v2_{st.session_state.alumno}")
                
                costo_real = costo_neto / (1 - (merma_esc / 100)) if merma_esc < 100 else costo_neto
                st.metric("Costo Neto Total", f"$ {costo_neto:,.2f}")
                st.metric("Costo Real (con Merma)", f"$ {costo_real:,.2f}", delta=f"{merma_esc}%")
                
                st.divider()
                margen = st.number_input("% Margen deseado", 50, 500, 200, key=f"margen_esc_{st.session_state.alumno}")
                precio_sugerido = costo_real * (1 + (margen/100))
                
                st.markdown(f"""
                    <div style="background-color:#1A1C23; padding:20px; border-radius:10px; border: 2px solid #D4AF37; text-align:center;">
                        <p style="color:white; margin-bottom:5px;">Sugerido para <b>{nombre_p}</b></p>
                        <h1 style="color:#D4AF37; margin:0;">$ {precio_sugerido:,.2f}</h1>
                    </div>
                """, unsafe_allow_html=True)

                alumno_actual = st.session_state.alumno if (hasattr(st.session_state, 'alumno') and st.session_state.alumno) else "No_especificado"

                contenido_imprimir = f"""==================================================
RECETA DE: {nombre_p.upper()}
==================================================
Fecha de Análisis: {datetime.now().strftime('%d/%m/%Y %H:%M')}
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

                st.download_button(
                    label="📥 Descargar Receta",
                    data=contenido_imprimir,
                    file_name=f"receta_{nombre_p.replace(' ', '_')}.txt",
                    mime="text/plain",
                    key=f"dl_btn_{alumno_actual}"
                )

                if st.button("💾 Grabar Receta en el Histórico", key=f"save_btn_{alumno_actual}"):
                    nueva_fila = [
                        datetime.now().strftime('%d/%m/%Y %H:%M'),
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

                st.markdown("---")
                st.subheader(f"📋 Tu Histórico de Auditorías ({alumno_actual})")
                
                placeholder_historial = st.empty()

                with placeholder_historial.container():
                    with st.spinner("Cargando tus registros personales..."):
                        df_alumno = leer_historico_filtrado(alumno_actual)

                if not df_alumno.empty:
                    st.dataframe(
                        df_alumno, 
                        use_container_width=True,
                        hide_index=True,
                        key=f"df_recetas_hist_{alumno_actual}"
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
    else:
        st.warning("⚠️ La base de datos maestra está vacía. No se pueden calcular escandallos.")  
        
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
        