import streamlit as st
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Conexión Segura", page_icon="🚐", layout="centered")

# Variables de sesión para que la web "recuerde" si hay un chat activo
if "chat_activo" not in st.session_state:
    st.session_state.chat_activo = False
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

st.title("🚐 Conexión Segura: Sabanalarga - Barranquilla")
st.write("Tu plataforma de confianza con perfiles verificados.")

# --- NAVEGACIÓN POR PESTAÑAS ---
tab_inicio, tab_buscar, tab_chat, tab_ayuda = st.tabs(["🏠 Inicio", "🔍 Buscar", "💬 Chat Activo", "❓ Ayuda"])

# --- 1. PESTAÑA DE INICIO ---
with tab_inicio:
    st.header("Bienvenido a la red de transporte seguro")
    st.info("💡 **Regla de oro:** Todos los usuarios en esta plataforma deben subir una foto real en el momento de registrarse. Si no hay foto, no hay viaje.")
    
    st.subheader("📸 Tu Perfil")
    nombre = st.text_input("Ingresa tu nombre para empezar:")
    foto = st.camera_input("Tómate una foto para identificarte")
    if foto and nombre:
        st.success(f"Perfil verificado, {nombre}. ¡Ya puedes buscar tu conexión!")

# --- 2. PESTAÑA DE BÚSQUEDA ---
with tab_buscar:
    st.header("🔍 Encuentra tu viaje")
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha del viaje", datetime.now())
    with col2:
        hora = st.time_input("Hora aproximada", datetime.now())
    
    st.divider()
    st.write("### Prestadores disponibles:")
    
    # Simulamos un prestador verificado
    c1, c2 = st.columns([1, 3])
    with c1:
        st.write("👤 (Foto Verificada)")
    with c2:
        st.write("**Carlos M.** - Conductor habitual")
        st.write(f"Disponible hoy cerca de las {hora}")
        if st.button("Reservar y Contactar a Carlos"):
            st.session_state.chat_activo = True
            st.session_state.mensajes = [{"rol": "Carlos (Prestador)", "texto": "¡Hola! Vi tu reserva. ¿En qué parte exacta de Sabanalarga te recojo?"}]
            st.success("¡Reserva confirmada! Ve a la pestaña de 'Chat Activo' para coordinar.")

# --- 3. PESTAÑA DE CHAT INTERACTIVO ---
with tab_chat:
    st.header("💬 Coordinación del Servicio")
    
    if st.session_state.chat_activo:
        st.write("Estás chateando en un entorno seguro. **No compartas contraseñas ni datos bancarios.**")
        st.divider()
        
        # Mostrar el historial de mensajes
        for msg in st.session_state.mensajes:
            with st.chat_message("user" if msg["rol"] == "Tú" else "assistant"):
                st.write(f"**{msg['rol']}:** {msg['texto']}")
        
        # Caja para escribir un nuevo mensaje
        nuevo_mensaje = st.chat_input("Escribe tu mensaje aquí...")
        if nuevo_mensaje:
            # Guardar y mostrar el mensaje del usuario
            st.session_state.mensajes.append({"rol": "Tú", "texto": nuevo_mensaje})
            st.rerun() # Recarga la pantalla para mostrar el mensaje
            
    else:
        st.warning("Aún no tienes ninguna reserva activa. Ve a la pestaña 'Buscar' para conectar con un prestador y abrir un chat.")

# --- 4. PESTAÑA DE AYUDA / SOPORTE ---
with tab_ayuda:
    st.header("❓ Centro de Ayuda")
    
    with st.expander("¿Cómo funciona la verificación por foto?"):
        st.write("Para garantizar la seguridad en la ruta Sabanalarga-Barranquilla, nuestra plataforma exige que tanto el cliente como el prestador se tomen una foto en tiempo real. Esta foto será visible para ambas partes al confirmar el viaje.")
        
    with st.expander("¿Qué pasa si el prestador cancela?"):
        st.write("Si el prestador cancela, el sistema te notificará inmediatamente y te mostrará opciones alternativas disponibles en tu mismo rango de hora.")
        
    with st.expander("Tengo un problema urgente"):
        st.write("Si necesitas asistencia inmediata, escríbenos a **soporte@conexionsabanalarga.com** o presiona el botón de pánico en la app (Próximamente).")
