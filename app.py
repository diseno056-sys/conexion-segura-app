import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Caribe Seguro PRO", layout="wide", page_icon="🛡️")

def conectar_db():
    return sqlite3.connect('caribe_data.db', check_same_thread=False)

def init_db():
    conn = conectar_db()
    c = conn.cursor()
    # Tabla Usuarios: Aseguramos el orden exacto
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (tel TEXT PRIMARY KEY, nom TEXT, pw TEXT, eme TEXT, rol TEXT, 
                  veh_tipo TEXT, veh_desc TEXT, pla TEXT, foto BLOB)''')
    # Tabla Rutas
    c.execute('''CREATE TABLE IF NOT EXISTS rutas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tel_p TEXT, cond TEXT, 
                  veh_tipo TEXT, veh_desc TEXT, pla TEXT, ori TEXT, des TEXT, 
                  hora TEXT, cupos INTEGER, precio TEXT, estado TEXT DEFAULT 'Activa')''')
    conn.commit()
    conn.close()

init_db()

# --- NAVEGACIÓN ---
if 'user' not in st.session_state: st.session_state.user = None
if 'pagina' not in st.session_state: st.session_state.pagina = "Bienvenida"

# --- BLOQUE DE SEGURIDAD PARA INDEX ERROR ---
def obtener_foto(usuario):
    try:
        # En el registro actual, la foto es el último elemento (índice 8)
        return usuario[8]
    except IndexError:
        return None

# --- VISTAS ---
if st.session_state.pagina == "Bienvenida":
    st.title("🛡️ Caribe Seguro")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 INICIAR SESIÓN", use_container_width=True): st.session_state.pagina = "Login"; st.rerun()
    with col2:
        if st.button("📝 REGISTRARME", use_container_width=True): st.session_state.pagina = "Registro"; st.rerun()

elif st.session_state.pagina == "Login":
    st.title("🔓 Ingreso")
    t_log = st.text_input("Teléfono")
    p_log = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        conn = conectar_db()
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE tel=? AND pw=?", (t_log, p_log))
        res = c.fetchone()
        conn.close()
        if res:
            st.session_state.user = res
            st.session_state.pagina = "Panel"; st.rerun()
        else: st.error("Datos incorrectos.")
    if st.button("⬅️ Volver"): st.session_state.pagina = "Bienvenida"; st.rerun()

elif st.session_state.pagina == "Registro":
    st.title("📝 Registro Nuevo")
    c1, c2 = st.columns(2)
    with c1:
        r_tel = st.text_input("Teléfono")
        r_nom = st.text_input("Nombre")
        r_pw = st.text_input("Contraseña", type="password")
    with c2:
        r_rol = st.selectbox("Rol", ["Cliente", "Prestador"])
        r_tipo_v = st.selectbox("Vehículo", ["Automóvil", "Van", "SUV", "Buseta"])
        r_pla = st.text_input("Placa")
        r_foto = st.camera_input("Foto")
    
    if st.button("Finalizar"):
        if r_foto and r_tel:
            conn = conectar_db(); c = conn.cursor()
            try:
                # Insertamos las 9 columnas exactas
                c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?,?,?)", 
                          (r_tel, r_nom, r_pw, "N/A", r_rol, r_tipo_v, "N/A", r_pla, r_foto.getvalue()))
                conn.commit()
                st.success("¡Registrado!"); st.session_state.pagina = "Login"; st.rerun()
            except: st.error("Error al guardar.")
            finally: conn.close()

elif st.session_state.pagina == "Panel":
    u = st.session_state.user
    
    # --- PERFIL PRIVADO SEGURO ---
    with st.sidebar:
        foto = obtener_foto(u)
        if foto: st.image(foto, width=100)
        st.markdown(f"### {u[1]}") # Nombre
        st.write(f"🏷️ **Rol:** {u[4]}")
        if u[4] == "Prestador":
            st.write(f"🚗 **Vehículo:** {u[5]}")
            st.write(f"🔢 **Placa:** {u[7]}")
        
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state.user = None
            st.session_state.pagina = "Bienvenida"; st.rerun()

    st.success(f"Bienvenido al panel de {u[4]}")
    # Aquí iría el resto de la lógica de rutas...
