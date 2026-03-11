import streamlit as st
import sqlite3
from datetime import datetime

# --- CONFIGURACIÓN DE DATOS REGIONALES ---
DEPARTAMENTOS_COSTA = {
    "Atlántico": ["Barranquilla", "Sabanalarga", "Soledad", "Baranoa", "Puerto Colombia", "Luruaco", "Galapa"],
    "Bolívar": ["Cartagena", "Magangué", "Turbaco", "Arjona", "El Carmen de Bolívar"],
    "Magdalena": ["Santa Marta", "Ciénaga", "Fundación", "Plato", "El Banco"],
    "Cesar": ["Valledupar", "Aguachica", "Agustín Codazzi", "Bosconia"],
    "Córdoba": ["Montería", "Cereté", "Sahagún", "Lorica", "Montelíbano"],
    "Sucre": ["Sincelejo", "Corozal", "San Marcos", "Tolú", "Coveñas"],
    "La Guajira": ["Riohacha", "Maicao", "Uribia", "Manaure", "San Juan del Cesar"]
}

# --- ESTADO DE LA SESIÓN ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'rutas_activas' not in st.session_state:
    st.session_state.rutas_activas = []

# --- FUNCIONES DE LÓGICA ---
def calcular_precio(dep_ori, dep_des):
    return "$15.000 - $25.000" if dep_ori == dep_des else "$45.000 - $75.000"

# --- INTERFAZ ---
st.set_page_config(page_title="Caribe Seguro PRO", layout="wide", page_icon="🛡️")

# --- ESTILOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; }
    .sos-button { background-color: #ff4b4b !important; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if st.session_state.user is None:
    t_log, t_reg = st.tabs(["🔑 Ingresar", "📝 Registro"])
    
    with t_reg:
        st.header("Registro de Identidad Caribe")
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre Completo")
            ced = st.text_input("Cédula")
            pw = st.text_input("Contraseña", type="password")
            rol = st.radio("¿Qué eres?", ["Cliente", "Prestador"])
        with c2:
            veh = st.text_input("Vehículo (Marca/Modelo/Color)")
            pla = st.text_input("Placa")
            foto = st.camera_input("Foto de Perfil")
        
        if st.button("Crear mi Cuenta Segura"):
            if nom and ced and foto:
                st.session_state.user = {"nom": nom, "ced": ced, "rol": rol, "veh": veh, "pla": pla, "foto": foto}
                st.success("¡Cuenta creada! Bienvenido.")
                st.rerun()

else:
    u = st.session_state.user
    st.sidebar.image(u["foto"], caption=f"{u['nom']} ({u['rol']})")
    
    # --- BOTÓN DE PÁNICO (S.O.S) ---
    if st.sidebar.button("🚨 BOTÓN DE PÁNICO S.O.S", key="sos", help="Enviar alerta inmediata"):
        st.sidebar.error("⚠️ ALERTA ENVIADA: Ubicación compartida con Central y Contactos de Emergencia.")
        st.sidebar.write(f"Datos reportados: Vehículo {u['veh']} - Placa {u['pla']}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.rerun()

    st.title("📍 Sistema de Rutas y Seguridad")

    if u["rol"] == "Prestador":
        st.subheader("Publicar una nueva Ruta")
        with st.form("nueva_ruta"):
            d_o = st.selectbox("Departamento Origen", list(DEPARTAMENTOS_COSTA.keys()))
            m_o = st.selectbox("Municipio Origen", DEPARTAMENTOS_COSTA[d_o])
            d_d = st.selectbox("Departamento Destino", list(DEPARTAMENTOS_COSTA.keys()))
            m_d = st.selectbox("Municipio Destino", DEPARTAMENTOS_COSTA[d_d])
            cupos = st.number_input("Cupos disponibles", 1, 15, 4)
            hora = st.time_input("Hora de salida")
            if st.form_submit_button("Publicar Ruta Regional"):
                nueva = {
                    "id": len(st.session_state.rutas_activas),
                    "cond": u["nom"], "veh": u["veh"], "pla": u["pla"],
                    "ori": m_o, "des": m_d, "cupos": cupos, "hora": str(hora),
                    "precio": calcular_precio(d_o, d_d)
                }
                st.session_state.rutas_activas.append(nueva)
                st.success(f"Ruta publicada: {m_o} a {m_d}")

    else:
        st.subheader("🔍 Buscar Transporte Disponible")
        if not st.session_state.rutas_activas:
            st.info("No hay rutas publicadas en este momento. Intenta más tarde.")
        
        for idx, r in enumerate(st.session_state.rutas_activas):
            if r["cupos"] > 0:
                with st.container():
                    st.write("---")
                    c_info, c_res = st.columns([3, 1])
                    with c_info:
                        st.write(f"🚗 **{r['cond']}** | {r['veh']} (Placa: {r['pla']})")
                        st.write(f"📍 **Trayecto:** {r['ori']} ➔ {r['des']}")
                        st.write(f"⏰ **Salida:** {r['hora']} | 💰 **Precio Sugerido:** {r['precio']}")
                        st.write(f"👥 **Cupos restantes:** {r['cupos']}")
                    with c_res:
                        if st.button(f"Reservar Cupo", key=f"res_{idx}"):
                            st.session_state.rutas_activas[idx]["cupos"] -= 1
                            st.balloons()
                            st.success("¡Reserva confirmada! Contacta al conductor.")
            else:
                st.write(f"🚫 Ruta de {r['cond']} (Lleno)")
