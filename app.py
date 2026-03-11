import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Caribe Seguro", layout="wide", page_icon="🛡️")

# --- CONEXIÓN ROBUSTA A BASE DE DATOS ---
def conectar_db():
    conn = sqlite3.connect('caribe_data.db', check_same_thread=False)
    return conn

def init_db():
    conn = conectar_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (tel TEXT PRIMARY KEY, nom TEXT, pw TEXT, eme TEXT, rol TEXT, veh TEXT, pla TEXT, foto BLOB)''')
    conn.commit()
    conn.close()

init_db()

# --- MANEJO DE ESTADOS ---
if 'user' not in st.session_state: st.session_state.user = None
if 'pagina' not in st.session_state: st.session_state.pagina = "Bienvenida"

# --- 1. PANTALLA DE BIENVENIDA ---
if st.session_state.pagina == "Bienvenida":
    st.title("🌴 Bienvenido a Caribe Seguro")
    st.subheader("La red de transporte verificado de la Costa Caribe")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 INICIAR SESIÓN", use_container_width=True):
            st.session_state.pagina = "Login"
            st.rerun()
    with col2:
        if st.button("📝 REGISTRARME", use_container_width=True):
            st.session_state.pagina = "Registro"
            st.rerun()
    
    st.divider()
    c_l1, c_l2 = st.columns(2)
    with c_l1:
        with st.expander("📄 Términos y Condiciones"):
            st.write("Al usar esta app, aceptas el registro verificado para seguridad de la comunidad.")
    with c_l2:
        with st.expander("📖 Manual de Usuario"):
            st.write("1. Regístrate. 2. Inicia Sesión. 3. Publica o Busca tu ruta segura.")

# --- 2. PANTALLA DE LOGIN ---
elif st.session_state.pagina == "Login":
    st.title("🔓 Ingreso Seguro")
    t_log = st.text_input("Número de Teléfono")
    p_log = st.text_input("Contraseña", type="password")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        if st.button("Entrar", use_container_width=True):
            conn = conectar_db()
            c = conn.cursor()
            c.execute("SELECT * FROM usuarios WHERE tel=? AND pw=?", (t_log, p_log))
            res = c.fetchone()
            conn.close()
            if res:
                st.session_state.user = res
                st.session_state.pagina = "Panel"
                st.rerun()
            else:
                st.error("Datos incorrectos. Verifica tu teléfono y contraseña.")
    with col_l2:
        if st.button("⬅️ VOLVER AL INICIO", use_container_width=True):
            st.session_state.pagina = "Bienvenida"
            st.rerun()

# --- 3. PANTALLA DE REGISTRO ---
elif st.session_state.pagina == "Registro":
    st.title("📝 Registro de Usuario Nuevo")
    c1, c2 = st.columns(2)
    with c1:
        r_tel = st.text_input("Número de Teléfono (ID)")
        r_nom = st.text_input("Nombre Completo")
        r_pw = st.text_input("Contraseña", type="password")
        r_eme = st.text_input("Contacto de Emergencia")
    with c2:
        r_rol = st.selectbox("Rol", ["Cliente", "Prestador"])
        r_veh = st.text_input("Vehículo (Marca/Color)")
        r_pla = st.text_input("Placa")
        r_foto = st.camera_input("Foto de Identidad")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("✅ FINALIZAR REGISTRO", use_container_width=True):
            if r_foto and r_tel and r_nom and r_pw:
                conn = conectar_db()
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?,?)", 
                              (r_tel, r_nom, r_pw, r_eme, r_rol, r_veh, r_pla, r_foto.getvalue()))
                    conn.commit()
                    st.success("¡Registro exitoso! Ahora puedes ir a Iniciar Sesión.")
                    st.balloons()
                except sqlite3.IntegrityError:
                    st.error("Error: Este número ya está registrado.")
                finally:
                    conn.close()
            else:
                st.warning("Por favor completa todos los campos y tómate la foto.")
    with col_r2:
        if st.button("⬅️ VOLVER AL INICIO", use_container_width=True):
            st.session_state.pagina = "Bienvenida"
            st.rerun()

# --- 4. PANEL DE CONTROL ---
elif st.session_state.pagina == "Panel":
    u = st.session_state.user
    st.sidebar.image(u[7], width=100)
    st.sidebar.title(f"Hola, {u[1]}")
    st.sidebar.write(f"Rol: **{u[4]}**")
    
    if st.sidebar.button("🚨 BOTÓN DE PÁNICO", type="primary"):
        st.error(f"¡ALERTA! Notificando a emergencia: {u[3]}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.session_state.pagina = "Bienvenida"
        st.rerun()
    
    st.success(f"Bienvenido al panel de {u[4]}.")
    st.info("Plataforma operativa para Sabanalarga, Barranquilla y toda la Costa.")
