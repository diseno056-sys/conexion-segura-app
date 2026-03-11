import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Caribe Seguro PRO", layout="wide", page_icon="🛡️")

# --- BASE DE DATOS ---
def conectar_db():
    return sqlite3.connect('caribe_data.db', check_same_thread=False)

def init_db():
    conn = conectar_db()
    c = conn.cursor()
    # Tabla Usuarios: 9 columnas (tel, nom, pw, eme, rol, veh_tipo, veh_desc, pla, foto)
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (tel TEXT PRIMARY KEY, nom TEXT, pw TEXT, eme TEXT, rol TEXT, 
                  veh_tipo TEXT, veh_desc TEXT, pla TEXT, foto BLOB)''')
    # Tabla Rutas: 10 columnas (id, tel_p, cond, veh_tipo, veh_desc, pla, ori, des, hora, cupos, precio)
    c.execute('''CREATE TABLE IF NOT EXISTS rutas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tel_p TEXT, cond TEXT, 
                  veh_tipo TEXT, veh_desc TEXT, pla TEXT, ori TEXT, des TEXT, 
                  hora TEXT, cupos INTEGER, precio TEXT, estado TEXT DEFAULT 'Activa')''')
    conn.commit()
    conn.close()

init_db()

# --- CIUDADES COSTA ---
DEPARTAMENTOS_COSTA = {
    "Atlántico": ["Barranquilla", "Sabanalarga", "Soledad", "Baranoa", "Luruaco"],
    "Bolívar": ["Cartagena", "Magangué", "Turbaco", "Arjona", "El Carmen"],
    "Magdalena": ["Santa Marta", "Ciénaga", "Fundación", "Plato"],
    "Cesar": ["Valledupar", "Aguachica", "Codazzi", "Bosconia"],
    "Córdoba": ["Montería", "Cereté", "Sahagún", "Lorica"],
    "Sucre": ["Sincelejo", "Corozal", "San Marcos", "Tolú"],
    "La Guajira": ["Riohacha", "Maicao", "Uribia", "San Juan"]
}

# --- NAVEGACIÓN ---
if 'user' not in st.session_state: st.session_state.user = None
if 'pagina' not in st.session_state: st.session_state.pagina = "Bienvenida"

if st.session_state.pagina == "Bienvenida":
    st.title("🛡️ Caribe Seguro Network")
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
    st.title("📝 Registro de Usuario")
    c1, c2 = st.columns(2)
    with c1:
        r_tel = st.text_input("Número Telefónico")
        r_nom = st.text_input("Nombre Completo")
        r_pw = st.text_input("Contraseña", type="password")
        r_eme = st.text_input("Contacto Emergencia")
    with c2:
        r_rol = st.selectbox("Rol", ["Cliente", "Prestador"])
        r_tipo_v = st.selectbox("Clase de Vehículo", ["Automóvil", "Van", "SUV (4x4)", "Buseta"])
        r_desc_v = st.text_input("Modelo y Color")
        r_pla = st.text_input("Placa")
        r_foto = st.camera_input("Foto de Rostro")
    
    if st.button("✅ Finalizar Registro"):
        if r_foto and r_tel and r_nom:
            conn = conectar_db()
            c = conn.cursor()
            try:
                c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?,?,?)", 
                          (r_tel, r_nom, r_pw, r_eme, r_rol, r_tipo_v, r_desc_v, r_pla, r_foto.getvalue()))
                conn.commit()
                st.success("¡Registrado!"); st.session_state.pagina = "Login"; st.rerun()
            except: st.error("Error al registrar.")
            finally: conn.close()

# --- PANEL DE CONTROL (AJUSTADO) ---
elif st.session_state.pagina == "Panel":
    u = st.session_state.user # 0:tel, 1:nom, 4:rol, 5:tipo_v, 6:desc, 7:placa, 8:foto
    
    # PERFIL PRIVADO (Oculta teléfono y dirección)
    st.sidebar.image(u[8], width=100)
    st.sidebar.markdown(f"### {u[1]}")
    st.sidebar.info(f"🎭 Rol: {u[4]}")
    
    menu = st.sidebar.radio("Menú", ["📍 Gestión de Rutas", "💬 Chat", "🚨 S.O.S"])

    if menu == "📍 Gestión de Rutas":
        if u[4] == "Prestador":
            st.header("📤 Publicar Nueva Ruta")
            with st.form("ruta_form"):
                col1, col2 = st.columns(2)
                with col1:
                    d_o = st.selectbox("Dpto. Origen", list(DEPARTAMENTOS_COSTA.keys()))
                    m_o = st.selectbox("Ciudad Origen", DEPARTAMENTOS_COSTA[d_o])
                with col2:
                    d_d = st.selectbox("Dpto. Destino", list(DEPARTAMENTOS_COSTA.keys()))
                    m_d = st.selectbox("Ciudad Destino", DEPARTAMENTOS_COSTA[d_d])
                
                h = st.time_input("Hora de Salida")
                cupos = st.number_input("Cupos Disponibles", 1, 20, 4)
                precio = st.text_input("Precio Sugerido", "25.000")
                
                if st.form_submit_button("🚀 PUBLICAR RUTA"):
                    conn = conectar_db()
                    c = conn.cursor()
                    # CORRECCIÓN: 10 parámetros coincidiendo con la tabla
                    c.execute("""INSERT INTO rutas 
                                (tel_p, cond, veh_tipo, veh_desc, pla, ori, des, hora, cupos, precio) 
                                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                              (u[0], u[1], u[5], u[6], u[7], m_o, m_d, str(h), cupos, precio))
                    conn.commit(); conn.close()
                    st.success("¡Ruta Guardada!")

        else: # CLIENTE
            st.header("🔍 Rutas Disponibles")
            conn = conectar_db()
            df = pd.read_sql("SELECT * FROM rutas WHERE cupos > 0 AND estado='Activa'", conn)
            conn.close()
            
            if not df.empty:
                for idx, r in df.iterrows():
                    urgencia = "🔥 ¡ÚLTIMO CUPO!" if r['cupos'] == 1 else f"👥 {r['cupos']} Cupos"
                    with st.expander(f"🚗 {r['cond']} | {r['ori']} ➔ {r['des']} | {urgencia}"):
                        st.write(f"**Vehículo:** {r['veh_tipo']} ({r['veh_desc']}) | **Placa:** {r['pla']}")
                        st.write(f"**Precio:** ${r['precio']} | **Hora:** {r['hora']}")
                        if st.button(f"Reservar Cupo", key=r['id']):
                            conn = conectar_db(); c = conn.cursor()
                            c.execute("UPDATE rutas SET cupos = cupos - 1 WHERE id=?", (r['id'],))
                            conn.commit(); conn.close()
                            st.success("Cupo reservado automáticamente."); st.rerun()
            else: st.warning("No hay rutas activas.")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None; st.session_state.pagina = "Bienvenida"; st.rerun()
