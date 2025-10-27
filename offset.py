import streamlit as st
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import hashlib

# ---------------- CONFIGURACIÓN DE PÁGINA ----------------
st.set_page_config(page_title="Offset CAD", layout="centered")
st.title("Offset y Ángulo Interno Visual (Estilo AutoCAD)")

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

@st.cache_data
def calcular_offset(x1, y1, x2, y2, dist_offset, lado):
    """Calcula un offset perpendicular exacto (90°) respecto a la línea base"""
    dx = x2 - x1
    dy = y2 - y1
    L = math.sqrt(dx**2 + dy**2)
    if L < 1e-6:
        return None, None, None

    # Vector unitario de la línea base
    ux_dir = dx / L
    uy_dir = dy / L

    # Vector perpendicular exacto (rotado 90°), INVERSIÓN DE LADO
    if "Izquierda" in lado:
        ux_perp = uy_dir  # Offset en lado horario
        uy_perp = -ux_dir
    else:
        ux_perp = -uy_dir  # Offset en lado antihorario
        uy_perp = ux_dir

    # Coordenadas del offset perpendicular exacto
    P1_offset = (x1 + ux_perp * dist_offset, y1 + uy_perp * dist_offset)
    P2_offset = (x2 + ux_perp * dist_offset, y2 + uy_perp * dist_offset)
    return P1_offset, P2_offset, L

@st.cache_data(show_spinner=False)
def generar_grafico_cached(_hash, x1, y1, x2, y2, P1o, P2o, lado_str, L, desviacion_mm, color_desv):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Línea base (de P1 a P2)
    ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1.5, label='Línea base (P1 → P2)', zorder=5)

    # Línea offset
    color_offset = 'blue' if "Izquierda" in lado_str else 'red'
    ax.plot([P1o[0], P2o[0]], [P1o[1], P2o[1]], color=color_offset, linestyle='--', linewidth=1.5,
            label=f'Offset ({lado_str}, P1′ → P2′)', zorder=5)

    # Flechas direccionales para enfatizar P1 → P2
    dx, dy = x2 - x1, y2 - y1
    scale = 0.3
    ax.annotate('', xy=(x1 + dx*scale, y1 + dy*scale), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    ax.annotate('', xy=(P1o[0] + dx*scale, P1o[1] + dy*scale), xytext=(P1o[0], P1o[1]),
                arrowprops=dict(arrowstyle='->', color=color_offset, lw=1.5))

    # Puntos y etiquetas
    ax.text(x1, y1, "  P1 (inicio)", fontsize=9, verticalalignment='bottom')
    ax.text(x2, y2, "  P2 (fin)", fontsize=9, verticalalignment='bottom')
    ax.text(P1o[0], P1o[1], "  P1′ (inicio)", fontsize=9, color=color_offset, verticalalignment='bottom')
    ax.text(P2o[0], P2o[1], "  P2′ (fin)", fontsize=9, color=color_offset, verticalalignment='bottom')

    # Arco de 90°, orientado según dirección P1 → P2
    radio = L * 0.2
    ang_base = math.degrees(math.atan2(dy, dx))  # Dirección de P1 a P2
    theta2 = ang_base - 90 if "Izquierda" in lado_str else ang_base + 90  # Invertido por cambio de lado

    arc = Arc((x1, y1), radio*2, radio*2, angle=0, theta1=ang_base, theta2=theta2,
              color='orange', linewidth=1.5)
    ax.add_patch(arc)

    # Texto del ángulo y desviación
    mid_angle = math.radians((ang_base + theta2) / 2)
    x_text = x1 + (radio * 0.8) * math.cos(mid_angle)
    y_text = y1 + (radio * 0.8) * math.sin(mid_angle)
    ax.text(x_text, y_text,
            f"90°00′00″\nDesv: {desviacion_mm:.2f} mm",
            fontsize=9, color=color_desv, ha='center', va='center')

    # Ajustes del gráfico
    ax.set_aspect('equal', adjustable='datalim')
    ax.grid(True, alpha=0.2)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.legend(loc='upper left')
    ax.set_title("Offset perpendicular (90° exacto, medición P1 → P2)", pad=10)
    return fig

# ---------------- INTERFAZ ----------------
st.sidebar.header("Línea base")
x1 = st.sidebar.number_input("X1 (P1, inicio)", value=984.765, step=0.001, format="%.3f")
y1 = st.sidebar.number_input("Y1 (P1, inicio)", value=964.723, step=0.001, format="%.3f")
x2 = st.sidebar.number_input("X2 (P2, fin)", value=997.622, step=0.001, format="%.3f")
y2 = st.sidebar.number_input("Y2 (P2, fin)", value=980.027, step=0.001, format="%.3f")

st.sidebar.header("Offset")
dist_offset = st.sidebar.number_input("Distancia (m)", value=10.0, step=0.001, format="%.3f")
lado = st.sidebar.radio("Lado", ("Izquierda (Antihorario)", "Derecha (Horario)"))

st.sidebar.header("Error angular del equipo (segundos)")
error_seg = st.sidebar.number_input("Ingrese error angular", value=2.0, min_value=1.0, max_value=5.0, step=0.1, format="%.1f")

# ---------------- CÁLCULOS ----------------
# Calcular offset
P1_offset, P2_offset, L = calcular_offset(x1, y1, x2, y2, dist_offset, lado)

# Calcular desviación lineal según error angular
desviacion_mm = desviacion_lineal_mm(L, error_seg)

# Color según tolerancia
color_desv = 'green' if error_seg <= 2 else 'red'

# ---------------- RESULTADOS ----------------
st.subheader("Resultados")
st.write("**Base (P1 → P2):**")
st.write(f"P1 (inicio) → X = {x1:.3f}, Y = {y1:.3f}")
st.write(f"P2 (fin) → X = {x2:.3f}, Y = {y2:.3f}")
st.write("**Offset (P1′ → P2′):**")
st.write(f"P1′ (inicio) → X = {P1_offset[0]:.3f}, Y = {P1_offset[1]:.3f}")
st.write(f"P2′ (fin) → X = {P2_offset[0]:.3f}, Y = {P2_offset[1]:.3f}")
st.write("**Ángulo interno:** 90°00′00″")
st.write(f"**Desviación angular:** {error_seg:.2f}″ → **{desviacion_mm:.2f} mm** en {L:.2f} m")

# ---------------- GRÁFICO ----------------
hash_datos = hashlib.md5(str((x1, y1, x2, y2, dist_offset, lado, error_seg)).encode()).hexdigest()
with st.spinner("Generando gráfico..."):
    fig = generar_grafico_cached(hash_datos, x1, y1, x2, y2, P1_offset, P2_offset, lado, L, desviacion_mm, color_desv)
    st.pyplot(fig, use_container_width=True)

st.caption("Offset calculado y mostrado con ángulo perpendicular exacto considerando el error angular del equipo. Medición desde P1 hacia P2.")
