import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Caribe Seguro PRO", layout="wide", page_icon="🛡️")

# --- BASE DE DATOS LOCAL ---
def init_db():
    conn = sqlite3.connect('caribe_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (tel TEXT PRIMARY KEY, nom TEXT, pw TEXT, eme TEXT, rol TEXT, veh TEXT, pla TEXT, foto BLOB)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rutas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tel_p TEXT, conductor TEXT, ori TEXT, des TEXT, cupos INTEGER, estado TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- ESTADO DE SESIÓN ---
if 'user' not in st.session_state: st.session_state.user = None
if 'pagina' not in st.session_state: st.session_state.pagina = "Bienvenida"

# --- PANTALLA DE BIENVENIDA ---
if st.session_state.pagina == "Bienvenida":
    st.title("🌴 Bienvenido a Caribe Seguro")
    st.subheader("La red de transporte verificado de la Costa")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 INICIAR SESIÓN", use_container_width=True):
            st.session_state.pagina = "Login"; st.rerun()
    with col2:
        if st.button("📝 REGISTRARME", use_container_width=True):
            st.session_state.pagina = "Registro"; st.rerun()
    
    st.divider()
    with st.expander("📄 Términos, Condiciones y Manual"):
        st.write("**Manual:** Conductores deben subir placa. Clientes deben verificar identidad.")
        st.write("**Legal:** Esta App es un intermediario de confianza.")

# --- PANTALLA DE LOGIN ---
elif st.session_state.pagina == "Login":
    st.title("🔓 Ingreso Seguro")
    t_log = st.text_input("Teléfono")
    p_log = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        conn = sqlite3.connect('caribe_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE tel=? AND pw=?", (t_log, p_log))
        res = c.fetchone()
        conn.close()
        if res:
            st.session_state.user = res
            st.session_state.pagina = "Panel"; st.rerun()
        else: st.error("Datos no coinciden.")
    if st.button("⬅️ Volver"): st.session_state.pagina = "Bienvenida"; st.rerun()

# --- PANTALLA DE REGISTRO ---
elif st.session_state.pagina == "Registro":
    st.title("📝 Registro Nuevo Usuario")
    c1, c2 = st.columns(2)
    with c1:
        r_tel = st.text_input("Teléfono Móvil")
        r_nom = st.text_input("Nombre Completo")
        r_pw = st.text_input("Contraseña", type="password")
        r_eme = st.text_input("Contacto de Emergencia")
    with c2:
        r_rol = st.selectbox("Rol", ["Cliente", "Prestador"])
        r_veh = st.text_input("Vehículo (Marca/Color)")
        r_pla = st.text_input("Placa")
        r_foto = st.camera_input("Foto de Rostro Obligatoria")
    
    if st.button("Finalizar Registro"):
        if r_foto and r_tel:
            conn = sqlite3.connect('caribe_data.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?,?)", 
                          (r_tel, r_nom, r_pw, r_eme, r_rol, r_veh, r_pla, r_foto.getvalue()))
                conn.commit()
                st.success("¡Registro exitoso! Ve a Iniciar Sesión.")
            except: st.error("El teléfono ya existe.")
            conn.close()

# --- PANEL PRINCIPAL ---
elif st.session_state.pagina == "Panel":
    u = st.session_state.user
    st.sidebar.image(u[7], width=100)
    st.sidebar.write(f"**{u[1]}**")
    
    if st.sidebar.button("🚨 S.O.S (ALERTA)", type="primary"):
        st.error(f"Alerta enviada a emergencia: {u[3]}")
    
    opcion = st.sidebar.radio("Menú", ["📍 Viajes", "💬 Chat", "💳 Pagos", "📜 Historial"])
    
    if opcion == "📍 Viajes":
        st.header("Rutas en la Costa")
        if u[4] == "Prestador":
            st.subheader("Publicar Ruta")
            # Aquí va el formulario de origen/destino
        else:
            st.subheader("Buscar Conductor")
            # Aquí va el buscador

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.session_state.pagina = "Bienvenida"
        st.rerun()
