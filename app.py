import streamlit as st
import sqlite3
from datetime import datetime

# --- CONFIGURACIÓN DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('caribe_elite.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios 
                 (telefono TEXT PRIMARY KEY, nombre TEXT, password TEXT, emergencia TEXT, 
                  rol TEXT, vehiculo TEXT, placa TEXT, foto BLOB, estrellas REAL DEFAULT 5.0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rutas 
                 (id INTEGER PRIMARY KEY AUTO_INCREMENT, tel_p TEXT, conductor TEXT,
                  origen TEXT, destino TEXT, hora TEXT, cupos INTEGER, estado TEXT DEFAULT 'Activo')''')
    conn.commit()
    conn.close()

init_db()

# --- LÓGICA DE NAVEGACIÓN ---
if 'user' not in st.session_state: st.session_state.user = None
if 'pagina' not in st.session_state: st.session_state.pagina = "Bienvenida"

# --- 1. BIENVENIDA CON MENÚ LEGAL ---
if st.session_state.pagina == "Bienvenida" and st.session_state.user is None:
    st.title("🛡️ Caribe Seguro PRO")
    st.subheader("Transporte Confiable y Verificado")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔑 Iniciar Sesión", use_container_width=True): st.session_state.pagina = "Login"; st.rerun()
    with col_b:
        if st.button("📝 Registrarse", use_container_width=True): st.session_state.pagina = "Registro"; st.rerun()

    st.divider()
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        with st.expander("📄 Términos y Condiciones"):
            st.write("**1. Naturaleza:** Esta plataforma es un intermediario tecnológico.")
            st.write("**2. Seguridad:** Es obligatorio el registro con foto real y cédula.")
            st.write("**3. Pagos:** Los pagos digitales se procesan vía Nequi/Daviplata.")
            st.write("**4. Jurisdicción:** Sujeto a las leyes comerciales de Colombia.")
    with col_l2:
        with st.expander("📖 Manual de Usuario"):
            st.write("**Para Conductores:** Sube foto de placa y rostro. Finaliza el viaje para recibir el pago.")
            st.write("**Para Pasajeros:** Verifica la placa antes de subir. Usa el botón S.O.S si es necesario.")

# --- 2. FINALIZACIÓN Y CALIFICACIÓN (LOGUEADO) ---
elif st.session_state.user:
    u = st.session_state.user
    menu = st.sidebar.radio("Navegación", ["📍 Rutas", "📜 Historial de Viajes", "⭐ Calificaciones"])

    if u[4] == "Prestador" and menu == "📍 Rutas":
        st.header("Gestionar mis Viajes en Curso")
        # Simulación de un viaje activo
        with st.container():
            st.info("🚗 Viaje en curso: Sabanalarga ➔ Barranquilla (3 pasajeros)")
            if st.button("🏁 FINALIZAR VIAJE Y COBRAR"):
                st.success("Viaje finalizado. ¡Por favor califica a tus pasajeros!")
                st.session_state.calificar = True

        if st.session_state.get('calificar'):
            st.subheader("Califica a tus Pasajeros")
            puntos = st.select_slider("¿Cómo fue el comportamiento?", options=[1,2,3,4,5], value=5)
            if st.button("Enviar Calificación"):
                st.write("¡Gracias! Tu reputación como conductor ha subido.")
                st.session_state.calificar = False

    elif u[4] == "Cliente" and menu == "📜 Historial de Viajes":
        st.header("Tus Viajes Recientes")
        with st.expander("✅ Viaje Finalizado: Barranquilla ➔ Cartagena"):
            st.write("Conductor: Juan Pérez (Placa: KLO-987)")
            st.write("¿Cómo estuvo el servicio?")
            estrellas = st.feedback("stars")
            if estrellas is not None:
                st.success(f"Has calificado con {estrellas + 1} estrellas. ¡Gracias por mejorar la comunidad!")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.session_state.pagina = "Bienvenida"
        st.rerun()
