import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Caribe Seguro PRO", layout="wide", page_icon="🛡️")

def conectar_db():
    return sqlite3.connect('caribe_data.db', check_same_thread=False)

def init_db():
    conn = conectar_db()
    c = conn.cursor()
    # 1. Usuarios (9 columnas)
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (tel TEXT PRIMARY KEY, nom TEXT, pw TEXT, eme TEXT, rol TEXT, 
                  veh_tipo TEXT, veh_desc TEXT, pla TEXT, foto BLOB)''')
    # 2. Rutas (11 columnas: id + 10 datos)
    c.execute('''CREATE TABLE IF NOT EXISTS rutas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tel_p TEXT, cond TEXT, 
                  veh_tipo TEXT, veh_desc TEXT, pla TEXT, ori TEXT, des TEXT, 
                  hora TEXT, cupos INTEGER, precio TEXT, estado TEXT DEFAULT 'Activa')''')
    # 3. Pagos
    c.execute('''CREATE TABLE IF NOT EXISTS pagos 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, ruta_id INTEGER, tel_c TEXT, 
                  monto TEXT, metodo TEXT, fecha TEXT)''')
    conn.commit()
    conn.close()

init_db()

DEPARTAMENTOS_COSTA = {
    "Atlántico": ["Barranquilla", "Sabanalarga", "Soledad", "Baranoa", "Luruaco"],
    "Bolívar": ["Cartagena", "Magangué", "Turbaco", "Arjona"],
    "Magdalena": ["Santa Marta", "Ciénaga", "Fundación", "Plato"]
}

# --- MANEJO DE SESIÓN ---
if 'user' not in st.session_state: st.session_state.user = None
if 'pagina' not in st.session_state: st.session_state.pagina = "Bienvenida"

# --- VISTA: BIENVENIDA ---
if st.session_state.pagina == "Bienvenida":
    st.title("🛡️ Caribe Seguro Network")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 INICIAR SESIÓN", use_container_width=True): st.session_state.pagina = "Login"; st.rerun()
    with col2:
        if st.button("📝 REGISTRARME", use_container_width=True): st.session_state.pagina = "Registro"; st.rerun()
    st.divider()
    with st.expander("📄 Términos, Manual y Pagos"):
        st.write("Aceptamos Nequi/Daviplata. Registro obligatorio con foto para seguridad.")

# --- VISTA: LOGIN ---
elif st.session_state.pagina == "Login":
    st.title("🔓 Ingreso")
    t_log = st.text_input("Teléfono")
    p_log = st.text_input("Contraseña", type="password")
    if st.button("Entrar", use_container_width=True):
        conn = conectar_db(); c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE tel=? AND pw=?", (t_log, p_log))
        res = c.fetchone()
        conn.close()
        if res:
            st.session_state.user = res; st.session_state.pagina = "Panel"; st.rerun()
        else: st.error("Datos incorrectos.")
    if st.button("⬅️ Volver"): st.session_state.pagina = "Bienvenida"; st.rerun()

# --- VISTA: REGISTRO ---
elif st.session_state.pagina == "Registro":
    st.title("📝 Registro")
    c1, c2 = st.columns(2)
    with c1:
        r_tel = st.text_input("Teléfono")
        r_nom = st.text_input("Nombre")
        r_pw = st.text_input("Contraseña", type="password")
        r_eme = st.text_input("Contacto Emergencia")
    with c2:
        r_rol = st.selectbox("Rol", ["Cliente", "Prestador"])
        r_tipo_v = st.selectbox("Vehículo", ["Automóvil", "Van", "SUV", "Buseta"])
        r_pla = st.text_input("Placa")
        r_foto = st.camera_input("Foto de Identidad")
    if st.button("✅ Finalizar Registro", use_container_width=True):
        if r_foto and r_tel:
            conn = conectar_db(); c = conn.cursor()
            c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?,?,?)", 
                      (r_tel, r_nom, r_pw, r_eme, r_rol, r_tipo_v, "N/A", r_pla, r_foto.getvalue()))
            conn.commit(); conn.close()
            st.success("¡Registrado!"); st.session_state.pagina = "Login"; st.rerun()

# --- VISTA: PANEL PRINCIPAL ---
elif st.session_state.pagina == "Panel":
    u = st.session_state.user
    with st.sidebar:
        if len(u) > 8: st.image(u[8], width=100)
        st.markdown(f"### {u[1]}")
        st.info(f"🎭 Rol: {u[4]}")
        if st.button("🚨 S.O.S", type="primary", use_container_width=True):
            st.error(f"Alerta enviada a: {u[3]}")
        st.divider()
        menu = st.sidebar.radio("Menú", ["📍 Viajes", "💳 Pagos", "📜 Historial"])
        if st.button("Cerrar Sesión"):
            st.session_state.user = None; st.session_state.pagina = "Bienvenida"; st.rerun()

    if menu == "📍 Viajes":
        if u[4] == "Prestador":
            st.header("📤 Mis Rutas")
            with st.expander("➕ Publicar Nueva Ruta"):
                with st.form("f_ruta"):
                    col_o1, col_o2 = st.columns(2)
                    with col_o1: d_o = st.selectbox("Dpto Origen", list(DEPARTAMENTOS_COSTA.keys()))
                    with col_o2: m_o = st.selectbox("Ciudad Origen", DEPARTAMENTOS_COSTA[d_o])
                    col_d1, col_d2 = st.columns(2)
                    with col_d1: d_d = st.selectbox("Dpto Destino", list(DEPARTAMENTOS_COSTA.keys()))
                    with col_d2: m_d = st.selectbox("Ciudad Destino", DEPARTAMENTOS_COSTA[d_d])
                    cupos = st.number_input("Cupos", 1, 20, 4)
                    precio = st.text_input("Precio por persona", "25.000")
                    if st.form_submit_button("🚀 PUBLICAR"):
                        conn = conectar_db(); c = conn.cursor()
                        # CORRECCIÓN DE 10 VALORES PARA INSERTAR
                        c.execute("INSERT INTO rutas (tel_p, cond, veh_tipo, veh_desc, pla, ori, des, hora, cupos, precio) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                  (u[0], u[1], u[5], "Particular", u[7], m_o, m_d, datetime.now().strftime("%H:%M"), cupos, precio))
                        conn.commit(); conn.close(); st.success("Ruta activa."); st.rerun()

            st.subheader("Rutas en Curso")
            conn = conectar_db()
            df_misi = pd.read_sql(f"SELECT * FROM rutas WHERE tel_p='{u[0]}' AND estado='Activa'", conn)
            conn.close()
            for idx, r in df_misi.iterrows():
                with st.container(border=True):
                    st.write(f"🚩 {r['ori']} ➔ {r['des']} | 👥 Cupos: {r['cupos']}")
                    if st.button(f"🏁 FINALIZAR VIAJE #{r['id']}", key=f"fin_{r['id']}"):
                        conn = conectar_db(); c = conn.cursor()
                        c.execute("UPDATE rutas SET estado='Finalizado' WHERE id=?", (r['id'],))
                        conn.commit(); conn.close(); st.success("Viaje cerrado."); st.rerun()

        else: # CLIENTE
            st.header("🔍 Buscar Transporte")
            conn = conectar_db()
            df = pd.read_sql("SELECT * FROM rutas WHERE cupos > 0 AND estado='Activa'", conn)
            conn.close()
            if df.empty:
                st.warning("No hay rutas disponibles en este momento.")
            else:
                for idx, r in df.iterrows():
                    urg = "🔥 ¡ÚLTIMO CUPO!" if r['cupos'] == 1 else f"👥 {r['cupos']} Cupos"
                    with st.expander(f"🚗 {r['cond']} | {r['ori']} ➔ {r['des']} | {urg}"):
                        st.write(f"**Vehículo:** {r['veh_tipo']} | **Placa:** {r['pla']}")
                        st.write(f"**Precio:** ${r['precio']}")
                        metodo = st.radio("Método de Pago", ["Nequi", "Daviplata", "Efectivo"], key=f"met_{r['id']}")
                        if st.button(f"Reservar con {metodo}", key=f"res_{r['id']}"):
                            conn = conectar_db(); c = conn.cursor()
                            c.execute("UPDATE rutas SET cupos = cupos - 1 WHERE id=?", (r['id'],))
                            c.execute("INSERT INTO pagos (ruta_id, tel_c, monto, metodo, fecha) VALUES (?,?,?,?,?)",
                                      (r['id'], u[0], r['precio'], metodo, str(datetime.now())))
                            conn.commit(); conn.close()
                            st.success(f"¡Pago con {metodo} registrado!"); st.rerun()

    elif menu == "💳 Pagos":
        st.header("💸 Resumen de Pagos")
        conn = conectar_db()
        if u[4] == "Prestador":
            df_p = pd.read_sql(f"SELECT p.monto, p.metodo, p.fecha, r.ori, r.des FROM pagos p JOIN rutas r ON p.ruta_id = r.id WHERE r.tel_p='{u[0]}'", conn)
        else:
            df_p = pd.read_sql(f"SELECT p.monto, p.metodo, p.fecha, r.cond, r.ori, r.des FROM pagos p JOIN rutas r ON p.ruta_id = r.id WHERE p.tel_c='{u[0]}'", conn)
        conn.close()
        st.dataframe(df_p, use_container_width=True)

    elif menu == "📜 Historial":
        st.header("Viajes Realizados")
        conn = conectar_db()
        filtro = f"tel_p='{u[0]}'" if u[4] == "Prestador" else "estado='Finalizado'"
        df_h = pd.read_sql(f"SELECT ori, des, cond, precio, hora FROM rutas WHERE {filtro} AND estado='Finalizado'", conn)
        conn.close()
        st.table(df_h)
