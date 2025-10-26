import streamlit as st
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import hashlib

# Configuración de página
st.set_page_config(page_title="Offset CAD", layout="centered")
st.title("Offset y Ángulo Interno Visual (Estilo AutoCAD)")

# -------------------- FUNCIONES AUXILIARES --------------------
def distancia_punto_linea(x1, y1, x2, y2, xp, yp):
    num = abs((x2 - x1)*(y1 - yp) - (x1 - xp)*(y2 - y1))
    den = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return num / den if den > 1e-10 else 0

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

    # Vector perpendicular exacto (rotado 90°)
    if "Izquierda" in lado:
        ux_perp = -uy_dir
        uy_perp = ux_dir
    else:
        ux_perp = uy_dir
        uy_perp = -ux_dir

    # Coordenadas del offset perpendicular exacto
    P1_offset = (x1 + ux_perp * dist_offset, y1 + uy_perp * dist_offset)
    P2_offset = (x2 + ux_perp * dist_offset, y2 + uy_perp * dist_offset)
    return P1_offset, P2_offset, L

@st.cache_data(show_spinner=False)
def generar_grafico_cached(_hash, x1, y1, x2, y2, P1o, P2o, lado_str, L, angulo, desviacion_mm):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Línea base
    ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1.5, label='Línea base', zorder=5)

    # Línea offset
    color_offset = 'blue' if "Izquierda" in lado_str else 'red'
    ax.plot([P1o[0], P2o[0]], [P1o[1], P2o[1]], color=color_offset, linestyle='--', linewidth=1.5,
            label=f'Offset ({lado_str})', zorder=5)

    # Flechas direccionales
    dx, dy = x2 - x1, y2 - y1
    scale = 0.3
    ax.annotate('', xy=(x1 + dx*scale, y1 + dy*scale), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='black', lw=1))
    ax.annotate('', xy=(P1o[0] + dx*scale, P1o[1] + dy*scale), xytext=(P1o[0], P1o[1]),
                arrowprops=dict(arrowstyle='->', color=color_offset, lw=1))

    # Puntos y etiquetas
    ax.text(x1, y1, "  P1", fontsize=9)
    ax.text(x2, y2, "  P2", fontsize=9)
    ax.text(P1o[0], P1o[1], "  P1′", fontsize=9, color=color_offset)
    ax.text(P2o[0], P2o[1], "  P2′", fontsize=9, color=color_offset)

    # Arco de 90° ± desviación
    radio = L * 0.2
    ang_base = math.degrees(math.atan2(dy, dx))
    diff = angulo - 90  # Desviación angular real
    theta2 = ang_base + 90 if "Izquierda" in lado_str else ang_base - 90

    arc = Arc((x1, y1), radio*2, radio*2, angle=0, theta1=ang_base, theta2=theta2,
              color='orange', linewidth=1.5)
    ax.add_patch(arc)

    # Texto del ángulo y desviación
    mid_angle = math.radians((ang_base + theta2) / 2)
    x_text = x1 + (radio * 0.8) * math.cos(mid_angle)
    y_text = y1 + (radio * 0.8) * math.sin(mid_angle)
    ax.text(x_text, y_text,
            f"{grados_a_dms(angulo)}\nDesv: {desviacion_mm:.2f} mm",
            fontsize=9, color='orange', ha='center', va='center')

    # Ajustes del gráfico
    ax.set_aspect('equal', adjustable='datalim')
    ax.grid(True, alpha=0.2)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.legend(loc='upper left')
    ax.set_title("Offset perpendicular (con desviación mostrada)", pad=10)
    return fig

# -------------------- INTERFAZ --------------------
st.sidebar.header("Línea base")
x1 = st.sidebar.number_input("X1 (P1)", value=984.765, step=0.001, format="%.3f")
y1 = st.sidebar.number_input("Y1 (P1)", value=964.723, step=0.001, format="%.3f")
x2 = st.sidebar.number_input("X2 (P2)", value=997.622, step=0.001, format="%.3f")
y2 = st.sidebar.number_input("Y2 (P2)", value=980.027, step=0.001, format="%.3f")

st.sidebar.header("Offset")
dist_offset = st.sidebar.number_input("Distancia (m)", value=10.0, step=0.001, format="%.3f")
lado = st.sidebar.radio("Lado", ("Izquierda (Antihorario)", "Derecha (Horario)"))

# Calcular offset
P1_offset, P2_offset, L = calcular_offset(x1, y1, x2, y2, dist_offset, lado)
if P1_offset is None:
    st.warning("Ingresa dos puntos distintos.")
    st.stop()

hash_datos = hashlib.md5(str((x1, y1, x2, y2, dist_offset, lado)).encode()).hexdigest()

# -------------------- CÁLCULOS DE ÁNGULO Y DESVIACIÓN --------------------
angulo_real = 90.0  # Por defecto exacto
desviacion_seg = 0.0
desviacion_mm = 0.0

# (Si quisieras simular una pequeña desviación, puedes descomentar:)
# angulo_real = 89.9966  # ejemplo
# desviacion_seg = abs((angulo_real - 90) * 3600)
# desviacion_mm = desviacion_lineal_mm(L, desviacion_seg)

# Mostrar resultados
st.subheader("Resultados")
st.write("**Base:**")
st.write(f"P1 → X = {x1:.3f}, Y = {y1:.3f}")
st.write(f"P2 → X = {x2:.3f}, Y = {y2:.3f}")
st.write("**Offset:**")
st.write(f"P1′ → X = {P1_offset[0]:.3f}, Y = {P1_offset[1]:.3f}")
st.write(f"P2′ → X = {P2_offset[0]:.3f}, Y = {P2_offset[1]:.3f}")

st.write(f"**Ángulo interno:** {grados_a_dms(angulo_real)}")
st.write(f"**Desviación angular:** {desviacion_seg:.2f}″ → **{desviacion_mm:.2f} mm** en {L:.2f} m")

if desviacion_seg < 0.5:
    st.success("Offset perpendicular exacto: 90°00′00″ (sin desviación significativa)")
else:
    st.warning(f"Desviación detectada: {desviacion_seg:.2f}″ = {desviacion_mm:.2f} mm")

# Mostrar gráfico
with st.spinner("Generando gráfico..."):
    fig = generar_grafico_cached(hash_datos, x1, y1, x2, y2, P1_offset, P2_offset, lado, L, angulo_real, desviacion_mm)
    st.pyplot(fig, use_container_width=True)

st.caption("Offset calculado y mostrado con desviación angular y lineal.")
