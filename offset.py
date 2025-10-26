import streamlit as st
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import hashlib

# ---------------- CONFIGURACIÓN DE PÁGINA ----------------
st.set_page_config(page_title="Offset CAD - Ángulo Real", layout="centered")
st.title("Offset y Ángulo Interno Real (Estilo AutoCAD)")

# ---------------- FUNCIONES AUXILIARES ----------------
def grados_a_dms(grados):
    """Convierte grados decimales a formato grados, minutos, segundos"""
    grados_abs = abs(grados)
    g = int(grados_abs)
    m = int((grados_abs - g) * 60)
    s = (grados_abs - g - m/60) * 3600
    signo = "-" if grados < 0 else ""
    return f"{signo}{g}° {m:02d}' {s:05.2f}\""

def desviacion_lineal_mm(distancia_m, segundos):
    """Convierte desviación angular (en segundos) a desviación lineal (en mm)"""
    rad = segundos * (math.pi / (180 * 3600))
    return distancia_m * math.tan(rad) * 1000

def calcular_offset_teorico(x1, y1, x2, y2, dist_offset, lado):
    """Calcula coordenadas del offset perpendicular exacto (90°)"""
    dx = x2 - x1
    dy = y2 - y1
    L = math.sqrt(dx**2 + dy**2)
    if L < 1e-6:
        return None, None, None
    ux = dx / L
    uy = dy / L
    if "Izquierda" in lado:
        ux_perp = -uy
        uy_perp = ux
    else:
        ux_perp = uy
        uy_perp = -ux
    P1o = (x1 + ux_perp * dist_offset, y1 + uy_perp * dist_offset)
    P2o = (x2 + ux_perp * dist_offset, y2 + uy_perp * dist_offset)
    return P1o, P2o, L

def calcular_angulo_real(x1, y1, x2, y2, x3, y3):
    """Calcula ángulo entre P1→P2 y P1→P1′"""
    v1x, v1y = x2 - x1, y2 - y1
    v2x, v2y = x3 - x1, y3 - y1
    dot = v1x*v2x + v1y*v2y
    mag1 = math.sqrt(v1x**2 + v1y**2)
    mag2 = math.sqrt(v2x**2 + v2y**2)
    if mag1 * mag2 == 0:
        return 0
    cos_theta = max(min(dot/(mag1*mag2), 1), -1)
    return math.degrees(math.acos(cos_theta))

@st.cache_data(show_spinner=False)
def generar_grafico(x1, y1, x2, y2, P1o, P2o, P1m, lado, L, ang_real, desv_mm):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Línea base
    ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1.5, label='Línea base')
    
    # Offset teórico
    color = 'blue' if "Izquierda" in lado else 'red'
    ax.plot([P1o[0], P2o[0]], [P1o[1], P2o[1]], '--', color=color, label=f'Offset ({lado})')
    
    # Puntos
    ax.scatter([x1, x2, P1o[0], P2o[0], P1m[0]], [y1, y2, P1o[1], P2o[1], P1m[1]],
               color='black', s=25)
    ax.text(x1, y1, " P1", fontsize=9)
    ax.text(x2, y2, " P2", fontsize=9)
    ax.text(P1o[0], P1o[1], " P1′ (Teórico)", fontsize=9, color=color)
    ax.text(P2o[0], P2o[1], " P2′ (Teórico)", fontsize=9, color=color)
    ax.text(P1m[0], P1m[1], " P1′ (Medido)", fontsize=9, color='green')
    
    # Arco del ángulo real
    dx, dy = x2 - x1, y2 - y1
    ang_base = math.degrees(math.atan2(dy, dx))
    ang_offset = math.degrees(math.atan2(P1m[1]-y1, P1m[0]-x1))
    arc = Arc((x1, y1), L*0.4, L*0.4, angle=0, theta1=ang_base, theta2=ang_offset,
              color='orange', linewidth=1.5)
    ax.add_patch(arc)
    
    # Texto del ángulo y desviación
    mid_angle = math.radians((ang_base + ang_offset)/2)
    x_text = x1 + (L*0.25) * math.cos(mid_angle)
    y_text = y1 + (L*0.25) * math.sin(mid_angle)
    ax.text(x_text, y_text,
            f"{grados_a_dms(ang_real)}\nDesv: {desv_mm:.2f} mm",
            fontsize=9, color='orange', ha='center', va='center')
    
    # Ajustes
    ax.set_aspect('equal', adjustable='datalim')
    ax.grid(True, alpha=0.2)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.legend()
    ax.set_title("Ángulo interno real y desviación lineal")
    return fig

# ---------------- INTERFAZ ----------------
st.sidebar.header("Línea base")
x1 = st.sidebar.number_input("X1 (P1)", value=984.765, step=0.001, format="%.3f")
y1 = st.sidebar.number_input("Y1 (P1)", value=964.723, step=0.001, format="%.3f")
x2 = st.sidebar.number_input("X2 (P2)", value=997.622, step=0.001, format="%.3f")
y2 = st.sidebar.number_input("Y2 (P2)", value=980.027, step=0.001, format="%.3f")

st.sidebar.header("Offset")
dist_offset = st.sidebar.number_input("Distancia (m)", value=10.0, step=0.001, format="%.3f")
lado = st.sidebar.radio("Lado", ("Izquierda (Antihorario)", "Derecha (Horario)"))

st.sidebar.header("P1′ medido")
x1m = st.sidebar.number_input("X1′ (medido)", value=0.0, step=0.001, format="%.3f")
y1m = st.sidebar.number_input("Y1′ (medido)", value=0.0, step=0.001, format="%.3f")

# Calcular offset teórico
P1o, P2o, L = calcular_offset_teorico(x1, y1, x2, y2, dist_offset, lado)
P1m = (x1m, y1m)

# Calcular ángulo real y desviación
ang_real = calcular_angulo_real(x1, y1, x2, y2, x1m, y1m)
desv_seg = abs((ang_real - 90)*3600)
desv_mm = desviacion_lineal_mm(L, desv_seg)

# ---------------- RESULTADOS ----------------
st.subheader("Resultados")
st.write("**Base:**")
st.write(f"P1 → X = {x1:.3f}, Y = {y1:.3f}")
st.write(f"P2 → X = {x2:.3f}, Y = {y2:.3f}")
st.write("**Offset teórico:**")
st.write(f"P1′ → X = {P1o[0]:.3f}, Y = {P1o[1]:.3f}")
st.write(f"P2′ → X = {P2o[0]:.3f}, Y = {P2o[1]:.3f}")
st.write("**P1′ medido:**")
st.write(f"P1′ → X = {P1m[0]:.3f}, Y = {P1m[1]:.3f}")
st.write(f"**Ángulo real:** {grados_a_dms(ang_real)}")
st.write(f"**Desviación angular:** {desv_seg:.2f}″")
st.write(f"**Desviación lineal:** {desv_mm:.2f} mm (en {L:.2f} m)")

# ---------------- GRÁFICO ----------------
hash_datos = hashlib.md5(str((x1, y1, x2, y2, dist_offset, lado, P1m))).hexdigest()
fig = generar_grafico(x1, y1, x2, y2, P1o, P2o, P1m, lado, L, ang_real, desv_mm)
st.pyplot(fig, use_container_width=True)

st.caption("Cálculo automático del ángulo real y desviación según P1′ medido.")
