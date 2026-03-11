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
    # Usuarios: tel, nom, pw, eme, rol, v_tipo, v_desc, pla, foto
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (tel TEXT PRIMARY KEY, nom TEXT, pw TEXT, eme TEXT, rol TEXT, 
                  veh_tipo TEXT, veh_desc TEXT, pla TEXT, foto BLOB)''')
    # Rutas: id, tel_p, cond, v_tipo, v_desc, pla, ori, des, hora, cupos, precio, estado
    c.execute('''CREATE TABLE IF NOT EXISTS rutas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tel_p TEXT, cond TEXT, 
                  veh_tipo TEXT, veh_desc TEXT, pla TEXT, ori TEXT, des TEXT, 
                  hora TEXT, cupos INTEGER, precio TEXT, estado TEXT DEFAULT 'Activa')''')
    # Pagos: id, ruta_id, tel_cliente, monto, metodo, estado
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

# --- NAVEGACIÓN ---
if 'user' not in st.session_state: st.session_state.user = None
if 'pagina' not in st.session_state: st.session_state.pagina = "Bienvenida"

# --- 1. BIENVENIDA ---
if st.session_state.pagina == "Bienvenida":
    st.title("🛡️ Caribe Seguro Network")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 INICIAR SESIÓN", use_container_width=True): st.session_state.pagina = "Login"; st.rerun()
    with col2:
        if st.button("📝 REGISTRARME", use_container_width=True): st.session_state.pagina = "Registro"; st.rerun()
    st.divider()
    with st.expander("📄 Términos y Manual de Seguridad"):
        st.write("Pagos seguros vía Nequi/Daviplata. Perfiles verificados con foto.")

# --- 2. LOGIN / REGISTRO ---
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

elif st.session_state.pagina == "Registro":
    st.title("📝 Registro")
    c1, c2 = st.columns(2)
    with c1:
        r_tel = st.text_input("Teléfono")
        r_nom = st.text_input("Nombre")
        r_pw = st.text_input("Contraseña", type="password")
        r_eme = st.text_input("Emergencia S.O.S")
    with c2:
        r_rol = st.selectbox("Rol", ["Cliente", "Prestador"])
        r_tipo_v = st.selectbox("Vehículo", ["Automóvil", "Van", "SUV", "Moto"])
        r_pla = st.text_input("Placa")
        r_foto = st.camera_input("Foto")
    if st.button("✅ Finalizar"):
        if r_foto and r_tel:
            conn = conectar_db(); c = conn.cursor()
            c.execute("INSERT INTO usuarios VALUES (?,?,?,?,?,?,?,?,?)", 
                      (r_tel, r_nom, r_pw, r_eme, r_rol, r_tipo_v, "N/A", r_pla, r_foto.getvalue()))
            conn.commit(); conn.close()
            st.success("¡Registrado!"); st.session_state.pagina = "Login"; st.rerun()
    if st.button("⬅️ Volver"): st.session_state.pagina = "Bienvenida"; st.rerun()

# --- 3. PANEL PRINCIPAL ---
elif st.session_state.pagina == "Panel":
    u = st.session_state.user
    with st.sidebar:
        if len(u) > 8: st.image(u[8], width=100)
        st.markdown(f"### {u[1]}")
        st.info(f"🎭 {u[4]}")
        if st.button("🚨 S.O.S", type="primary", use_container_width=True):
            st.error(f"Alerta enviada a: {u[3]}")
        st.divider()
        menu = st.radio("Menú", ["📍 Viajes", "💳 Pagos", "📜 Historial"])
        if st.button("Cerrar Sesión"):
            st.session_state.user = None; st.session_state.pagina = "Bienvenida"; st.rerun()

    if menu == "📍 Viajes":
        if u[4] == "Prestador":
            st.header("📤 Mis Rutas")
            with st.expander("➕ Publicar Nueva Ruta"):
                with st.form("f_ruta"):
                    d_o = st.selectbox("Dpto Origen", list(DEPARTAMENTOS_COSTA.keys()))
                    m_o = st.selectbox("Ciudad Origen", DEPARTAMENTOS_COSTA[d_o])
                    d_d = st.selectbox("Dpto Destino", list(DEPARTAMENTOS_COSTA.keys()))
                    m_d = st.selectbox("Ciudad Destino", DEPARTAMENTOS_COSTA[d_d])
                    cupos = st.number_input("Cupos", 1, 20, 4)
                    precio = st.text_input("Precio por persona", "25.000")
                    if st.form_submit_button("🚀 PUBLICAR"):
                        conn = conectar_db(); c = conn.cursor()
                        c.execute("INSERT INTO rutas (tel_p, cond, veh_tipo, veh_desc, pla, ori, des, hora, cupos, precio) VALUES (?,?,?,?,?,?,?,?,?,?)",
                                  (u[0], u[1], u[5], "N/A", u[7], m_o, m_d, "Ahora", cupos, precio))
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
                        conn.commit(); conn.close(); st.rerun()

        else: # CLIENTE
            st.header("🔍 Buscar Transporte")
            conn = conectar_db()
            df = pd.read_sql("SELECT * FROM rutas WHERE cupos > 0 AND estado='Activa'", conn)
            conn.close()
            for idx, r in df.iterrows():
                urg = "🔥 ¡ÚLTIMO CUPO!" if r['cupos'] == 1 else f"👥 {r['cupos']} Cupos"
                with st.expander(f"🚗 {r['cond']} | {r['ori']} ➔ {r['des']} | {urg}"):
                    st.write(f"**Vehículo:** {r['veh_tipo']} | **Placa:** {r['pla']}")
                    st.write(f"**Precio:** ${r['precio']}")
                    
                    # PASARELA DE PAGO INTEGRADA
                    metodo = st.radio("Método de Pago", ["Nequi", "Daviplata", "Efectivo"], key=f"met_{r['id']}")
                    if st.button(f"Pagar y Reservar con {metodo}", key=f"res_{r['id']}"):
                        conn = conectar_db(); c = conn.cursor()
                        c.execute("UPDATE rutas SET cupos = cupos - 1 WHERE id=?", (r['id'],))
                        c.execute("INSERT INTO pagos (ruta_id, tel_c, monto, metodo, fecha) VALUES (?,?,?,?,?)",
                                  (r['id'], u[0], r['precio'], metodo, str(datetime.now())))
                        conn.commit(); conn.close()
                        st.success(f"¡Reserva y Pago por {metodo} exitoso!"); st.rerun()

    elif menu == "💳 Pagos":
        st.header("💸 Resumen de Pagos")
        conn = conectar_db()
        if u[4] == "Prestador":
            st.write("Ingresos recibidos por tus rutas:")
            df_p = pd.read_sql(f"SELECT p.*, r.ori, r.des FROM pagos p JOIN rutas r ON p.ruta_id = r.id WHERE r.tel_p='{u[0]}'", conn)
        else:
            st.write("Tus pagos realizados:")
            df_p = pd.read_sql(f"SELECT p.*, r.cond, r.ori, r.des FROM pagos p JOIN rutas r ON p.ruta_id = r.id WHERE p.tel_c='{u[0]}'", conn)
        conn.close()
        st.dataframe(df_p)

    elif menu == "📜 Historial":
        st.header("Viajes Finalizados")
        conn = conectar_db()
        filtro = f"tel_p='{u[0]}'" if u[4] == "Prestador" else "estado='Finalizado'"
        df_h = pd.read_sql(f"SELECT * FROM rutas WHERE {filtro} AND estado='Finalizado'", conn)
        conn.close()
        st.table(df_h[['ori', 'des', 'cond', 'precio']])
