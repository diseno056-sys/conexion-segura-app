import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Caribe Seguro PRO", layout="wide", page_icon="🛡️")

# --- BASE DE DATOS REGIONAL ---
DEPARTAMENTOS_COSTA = {
    "Atlántico": ["Barranquilla", "Sabanalarga", "Soledad", "Baranoa", "Luruaco"],
    "Bolívar": ["Cartagena", "Magangué", "Turbaco", "Arjona", "El Carmen"],
    "Magdalena": ["Santa Marta", "Ciénaga", "Fundación", "Plato"],
    "Cesar": ["Valledupar", "Aguachica", "Codazzi", "Bosconia"],
    "Córdoba": ["Montería", "Cereté", "Sahagún", "Lorica"],
    "Sucre": ["Sincelejo", "Corozal", "San Marcos", "Tolú"],
    "La Guajira": ["Riohacha", "Maicao", "Uribia", "San Juan"]
}

def conectar_db():
    return sqlite3.connect('caribe_data.db', check_same_thread=False)

def init_db():
    conn = conectar_db()
    c = conn.cursor()
    # Tabla Usuarios (Incluye Clase de Vehículo)
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

# --- 1. BIENVENIDA / LOGIN / REGISTRO ---
if st.session_state.pagina == "Bienvenida":
    st.title("🌴 Caribe Seguro")
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
    if st.button("Volver"): st.session_state.pagina = "Bienvenida"; st.rerun()

elif st.session_state.pagina == "Registro":
    st.title("📝 Registro Nuevo")
    c1, c2 = st.columns(2)
    with c1:
        r_tel = st.text_input("Teléfono (ID)")
        r_nom = st.text_input("Nombre Completo")
        r_pw = st.text_input("Contraseña", type="password")
        r_eme = st.text_input("Contacto Emergencia")
    with c2:
        r_rol = st.selectbox("Rol", ["Cliente", "Prestador"])
        r_tipo_v = st.selectbox("Clase de Vehículo", ["Automóvil", "Van", "SUV (4x4)", "Moto", "Buseta"])
        r_desc_v = st.text_input("Marca/Color (Ej: Kia Gris)")
        r_pla = st.text_input("Placa")
        r_foto = st.camera_input("Foto de Rostro")
    
    if st.button("Finalizar Registro"):
        if r_foto and r_tel:
            conn = conectar_db()
            c = conn.cursor()
            c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?,?,?)", 
                      (r_tel, r_nom, r_pw, r_eme, r_rol, r_tipo_v, r_desc_v, r_pla, r_foto.getvalue()))
            conn.commit()
            conn.close()
            st.success("¡Registro exitoso! Ya puedes entrar."); st.session_state.pagina = "Login"; st.rerun()
    if st.button("Volver"): st.session_state.pagina = "Bienvenida"; st.rerun()

# --- 2. PANEL DE CONTROL (RUTAS AUTOMATIZADAS) ---
elif st.session_state.pagina == "Panel":
    u = st.session_state.user # 0:tel, 1:nom, 3:eme, 4:rol, 5:tipo_v, 6:desc_v, 7:pla, 8:foto
    st.sidebar.image(u[8], width=100)
    st.sidebar.title(f"Hola, {u[1]}")
    
    menu = st.sidebar.radio("Menú Principal", ["📍 Gestión de Rutas", "💬 Chat", "📜 Historial", "🚨 S.O.S"])

    if menu == "📍 Gestión de Rutas":
        if u[4] == "Prestador":
            st.header("📤 Publicar Nueva Ruta")
            with st.form("form_ruta"):
                col1, col2 = st.columns(2)
                with col1:
                    dep_o = st.selectbox("Dpto. Origen", list(DEPARTAMENTOS_COSTA.keys()))
                    mun_o = st.selectbox("Ciudad Origen", DEPARTAMENTOS_COSTA[dep_o])
                with col2:
                    dep_d = st.selectbox("Dpto. Destino", list(DEPARTAMENTOS_COSTA.keys()))
                    mun_d = st.selectbox("Ciudad Destino", DEPARTAMENTOS_COSTA[dep_d])
                
                c_hora = st.time_input("Hora de Salida")
                c_cupos = st.number_input("Cupos Totales", 1, 20, 4)
                c_precio = st.text_input("Precio por Cupo", "25.000")
                
                if st.form_submit_button("🚀 PUBLICAR RUTA"):
                    conn = conectar_db()
                    c = conn.cursor()
                    c.execute("INSERT INTO rutas (tel_p, cond, veh_tipo, veh_desc, pla, ori, des, hora, cupos, precio) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                              (u[0], u[1], u[5], u[6], u[7], mun_o, mun_d, str(c_hora), c_cupos, c_precio))
                    conn.commit(); conn.close()
                    st.success("Ruta publicada con éxito.")

        else: # ROL CLIENTE
            st.header("🔍 Buscar Transporte")
            col_a, col_b = st.columns(2)
            with col_a: b_ori = st.selectbox("Origen", ["Todos"] + [m for d in DEPARTAMENTOS_COSTA.values() for m in d])
            with col_b: b_des = st.selectbox("Destino", ["Todos"] + [m for d in DEPARTAMENTOS_COSTA.values() for m in d])
            
            conn = conectar_db()
            query = "SELECT * FROM rutas WHERE estado='Activa' AND cupos > 0"
            if b_ori != "Todos": query += f" AND ori='{b_ori}'"
            if b_des != "Todos": query += f" AND des='{b_des}'"
            df_rutas = pd.read_sql(query, conn)

            if not df_rutas.empty:
                for index, row in df_rutas.iterrows():
                    with st.expander(f"🚗 {row['cond']} | {row['ori']} ➔ {row['des']} | 👥 {row['cupos']} Cupos"):
                        st.write(f"**Vehículo:** {row['veh_tipo']} ({row['veh_desc']}) - Placa: {row['pla']}")
                        st.write(f"**Hora:** {row['hora']} | **Precio:** ${row['precio']}")
                        if st.button(f"Confirmar Reserva", key=row['id']):
                            # LÓGICA DE DESCUENTO AUTOMÁTICO
                            c = conn.cursor()
                            c.execute("UPDATE rutas SET cupos = cupos - 1 WHERE id=?", (row['id'],))
                            conn.commit()
                            st.success("¡Reserva exitosa! Cupo descontado automáticamente.")
                            st.rerun()
            else:
                st.warning("No hay rutas disponibles para este trayecto.")
            conn.close()

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.session_state.pagina = "Bienvenida"; st.rerun()
