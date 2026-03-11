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
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (tel TEXT PRIMARY KEY, nom TEXT, pw TEXT, eme TEXT, rol TEXT, 
                  veh_tipo TEXT, veh_desc TEXT, pla TEXT, foto BLOB)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rutas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tel_p TEXT, cond TEXT, 
                  veh_tipo TEXT, veh_desc TEXT, pla TEXT, ori TEXT, des TEXT, 
                  hora TEXT, cupos INTEGER, precio TEXT, estado TEXT DEFAULT 'Activa')''')
    conn.commit()
    conn.close()

init_db()

# --- DICCIONARIO DE CIUDADES COSTA ---
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

# --- 1. PANTALLA DE BIENVENIDA ---
if st.session_state.pagina == "Bienvenida":
    st.title("🛡️ Caribe Seguro Network")
    st.subheader("Transporte Confiable y Verificado por la Costa")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 INICIAR SESIÓN", use_container_width=True): st.session_state.pagina = "Login"; st.rerun()
    with col2:
        if st.button("📝 REGISTRARME", use_container_width=True): st.session_state.pagina = "Registro"; st.rerun()
    
    st.divider()
    c_l1, c_l2 = st.columns(2)
    with c_l1:
        with st.expander("📄 Términos y Condiciones"):
            st.write("Seguridad garantizada mediante validación de identidad.")
    with c_l2:
        with st.expander("📖 Manual"):
            st.write("Publica o busca rutas seguras en minutos.")

# --- 2. LOGIN ---
elif st.session_state.pagina == "Login":
    st.title("🔓 Ingreso Seguro")
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

# --- 3. REGISTRO ---
elif st.session_state.pagina == "Registro":
    st.title("📝 Registro de Usuario")
    c1, c2 = st.columns(2)
    with c1:
        r_tel = st.text_input("Teléfono (ID)")
        r_nom = st.text_input("Nombre Completo")
        r_pw = st.text_input("Contraseña", type="password")
        r_eme = st.text_input("Emergencia S.O.S")
    with c2:
        r_rol = st.selectbox("Rol", ["Cliente", "Prestador"])
        r_tipo_v = st.selectbox("Clase Vehículo", ["Automóvil", "Van", "SUV (4x4)", "Buseta"])
        r_desc_v = st.text_input("Modelo/Color")
        r_pla = st.text_input("Placa")
        r_foto = st.camera_input("Foto de Rostro")
    
    if st.button("✅ Finalizar Registro"):
        if r_foto and r_tel:
            conn = conectar_db()
            c = conn.cursor()
            c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?,?)", 
                      (r_tel, r_nom, r_pw, r_eme, r_rol, r_tipo_v, r_desc_v, r_pla, r_foto.getvalue()))
            conn.commit(); conn.close()
            st.success("¡Registro Exitoso!"); st.session_state.pagina = "Login"; st.rerun()
    if st.button("⬅️ Volver"): st.session_state.pagina = "Bienvenida"; st.rerun()

# --- 4. PANEL DE CONTROL ---
elif st.session_state.pagina == "Panel":
    u = st.session_state.user
    st.sidebar.image(u[8] if len(u)>8 else u[7], width=100)
    st.sidebar.title(f"Hola, {u[1]}")
    
    menu = st.sidebar.radio("Menú Principal", ["📍 Gestión de Rutas", "💬 Chat", "🚨 S.O.S"])

    if menu == "📍 Gestión de Rutas":
        if u[4] == "Prestador":
            st.header("📤 Publicar Nueva Ruta")
            with st.form("ruta_form"):
                col1, col2 = st.columns(2)
                with col1:
                    dep_o = st.selectbox("Dpto. Origen", list(DEPARTAMENTOS_COSTA.keys()))
                    mun_o = st.selectbox("Ciudad Origen", DEPARTAMENTOS_COSTA[dep_o])
                with col2:
                    dep_d = st.selectbox("Dpto. Destino", list(DEPARTAMENTOS_COSTA.keys()))
                    mun_d = st.selectbox("Ciudad Destino", DEPARTAMENTOS_COSTA[dep_d])
                
                c_hora = st.time_input("Hora Salida")
                c_cupos = st.number_input("Cupos Disponibles", 1, 20, 4)
                c_precio = st.text_input("Precio por Cupo", "25.000")
                
                if st.form_submit_button("🚀 PUBLICAR"):
                    conn = conectar_db()
                    c = conn.cursor()
                    c.execute("INSERT INTO rutas (tel_p, cond, veh_tipo, veh_desc, pla, ori, des, hora, cupos, precio) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                              (u[0], u[1], u[5], u[6], u[7], mun_o, mun_d, str(c_hora), c_cupos, c_precio))
                    conn.commit(); conn.close()
                    st.success("Ruta activa.")

        else: # CLIENTE
            st.header("🔍 Buscar Transporte")
            col_a, col_b = st.columns(2)
            with col_a: b_ori = st.selectbox("Desde", ["Todos"] + [m for d in DEPARTAMENTOS_COSTA.values() for m in d])
            with col_b: b_des = st.selectbox("Hacia", ["Todos"] + [m for d in DEPARTAMENTOS_COSTA.values() for m in d])
            
            conn = conectar_db()
            query = "SELECT * FROM rutas WHERE estado='Activa' AND cupos > 0"
            if b_ori != "Todos": query += f" AND ori='{b_ori}'"
            if b_des != "Todos": query += f" AND des='{b_des}'"
            df_rutas = pd.read_sql(query, conn)

            if not df_rutas.empty:
                for index, row in df_rutas.iterrows():
                    # --- NOTIFICACIÓN DE URGENCIA ---
                    urgencia = "🔥 ¡ÚLTIMO CUPO!" if row['cupos'] == 1 else f"👥 {row['cupos']} Cupos"
                    
                    with st.expander(f"🚗 {row['cond']} | {row['ori']} ➔ {row['des']} | {urgencia}"):
                        if row['cupos'] == 1:
                            st.warning("⚠️ Esta ruta está a punto de completarse. ¡Reserva ya!")
                        
                        st.write(f"**Vehículo:** {row['veh_tipo']} ({row['veh_desc']}) | **Placa:** {row['pla']}")
                        st.write(f"**Precio:** ${row['precio']} | **Hora:** {row['hora']}")
                        
                        if st.button(f"Confirmar mi Cupo", key=row['id']):
                            c = conn.cursor()
                            c.execute("UPDATE rutas SET cupos = cupos - 1 WHERE id=?", (row['id'],))
                            conn.commit()
                            st.success("¡Reserva confirmada automáticamente!"); st.rerun()
            else: st.warning("No hay rutas activas para esta búsqueda.")
            conn.close()

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None; st.session_state.pagina = "Bienvenida"; st.rerun()
