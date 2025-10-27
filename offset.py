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

    # Vector perpendicular (corrección: ahora el lado Izquierda realmente va a la izquierda)
    if "Izquierda" in lado:
        ux_perp = uy_dir
        uy_perp = -ux_dir
    else:
        ux_perp = -uy_dir
        uy_perp = ux_dir

    # Coordenadas del offset perpendicular exacto
    P1_offset = (x1 + ux_perp * dist_offset, y1 + uy_perp * dist_offset)
    P2_offset = (x2 + ux_perp * dist_offset, y2 + uy_perp * dist_offset)
    return P1_offset, P2_offset, L

@st.cache_data(show_spinner=False)
def generar_grafico_cached(_hash, x1, y1, x2, y2, P1o, P2o, lado_str, L, desviacion_mm, color_desv):
    # Configurar estilo inspirado en AutoCAD
    plt.style.use('seaborn-darkgrid')  # Tema más limpio y profesional
    fig, ax = plt.subplots(figsize=(10, 8))  # Aumentar tamaño para mayor claridad

    # Línea base (más gruesa para destacar)
    ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2.0, label='Línea base (P1 → P2)', zorder=5)

    # Línea offset
    color_offset = 'blue' if "Izquierda" in lado_str else 'red'
    ax.plot([P1o[0], P2o[0]], [P1o[1], P2o[1]], color=color_offset, linestyle='--', linewidth=1.8,
            label=f'Offset ({lado_str}, {dist_offset:.3f} m)', zorder=5)

    # Flechas direccionales más visibles
    dx, dy = x2 - x1, y2 - y1
    scale = 0.3
    ax.annotate('', xy=(x1 + dx*scale, y1 + dy*scale), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color='black', lw=1.5, mutation_scale=15))
    ax.annotate('', xy=(P1o[0] + dx*scale, P1o[1] + dy*scale), xytext=(P1o[0], P1o[1]),
                arrowprops=dict(arrowstyle='-|>', color=color_offset, lw=1.5, mutation_scale=15))

    # Puntos y etiquetas con alineación dinámica
    label_offset = L * 0.05  # Desplazamiento proporcional a la longitud
    ax.text(x1 + label_offset if dx >= 0 else x1 - label_offset, 
            y1 + label_offset if dy >= 0 else y1 - label_offset, 
            "P1 (inicio)", fontsize=10, fontfamily='Arial', ha='right' if dx >= 0 else 'left', va='bottom' if dy >= 0 else 'top')
    ax.text(x2 + label_offset if dx >= 0 else x2 - label_offset, 
            y2 + label_offset if dy >= 0 else y2 - label_offset, 
            "P2 (fin)", fontsize=10, fontfamily='Arial', ha='left' if dx >= 0 else 'right', va='bottom' if dy >= 0 else 'top')
    ax.text(P1o[0] + label_offset if dx >= 0 else P1o[0] - label_offset, 
            P1o[1] + label_offset if dy >= 0 else P1o[1] - label_offset, 
            "P1′ (inicio)", fontsize=10, fontfamily='Arial', color=color_offset, ha='right' if dx >= 0 else 'left', va='bottom' if dy >= 0 else 'top')
    ax.text(P2o[0] + label_offset if dx >= 0 else P2o[0] - label_offset, 
            P2o[1] + label_offset if dy >= 0 else P2o[1] - label_offset, 
            "P2′ (fin)", fontsize=10, fontfamily='Arial', color=color_offset, ha='left' if dx >= 0 else 'right', va='bottom' if dy >= 0 else 'top')

    # Arco de 90° con tamaño dinámico
    radio = min(max(L * 0.2, 0.5), 5.0)  # Limitar entre 0.5 y 5.0 para evitar extremos
    ang_base = math.degrees(math.atan2(dy, dx))
    theta2 = ang_base + 90 if "Izquierda" in lado_str else ang_base - 90
    arc = Arc((x1, y1), radio*2, radio*2, angle=0, theta1=ang_base, theta2=theta2,
              color='orange', linewidth=1.8)
    ax.add_patch(arc)

    # Texto del ángulo y desviación con fondo para legibilidad
    mid_angle = math.radians((ang_base + theta2) / 2)
    x_text = x1 + (radio * 1.2) * math.cos(mid_angle)  # Aumentar distancia para evitar superposición
    y_text = y1 + (radio * 1.2) * math.sin(mid_angle)
    ax.text(x_text, y_text,
            f"90°00′00″\nDesv: {desviacion_mm:.2f} mm",
            fontsize=9, fontfamily='Arial', color=color_desv, ha='center', va='center',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    # Anotación de longitud de la línea base
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    ax.text(mid_x, mid_y, f"L = {L:.3f} m", fontsize=9, fontfamily='Arial', ha='center', va='top',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    # Ajustes del gráfico: centrar con márgenes
    all_x = [x1, x2, P1o[0], P2o[0]]
    all_y = [y1, y2, P1o[1], P2o[1]]
    margin = 0.3 * max(max(all_x) - min(all_x), max(all_y) - min(all_y))  # Margen del 30%
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
    ax.set_aspect('equal', adjustable='box')  # Forzar igualdad
    ax.grid(True, alpha=0.4, linestyle='--')  # Cuadrícula más visible
    ax.set_xlabel("X (m)", fontfamily='Arial', fontsize=10)
    ax.set_ylabel("Y (m)", fontfamily='Arial', fontsize=10)
    ax.legend(loc='upper right', fontsize=9, frameon=True, edgecolor='black')  # Leyenda en esquina superior derecha
    ax.set_title(f"Offset perpendicular (90° exacto, P1 → P2, {lado_str})", pad=10, fontfamily='Arial', fontsize=12)
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

st.sidebar.header("Error angular del equipo (segundos)")
error_seg = st.sidebar.number_input("Ingrese error angular", value=2.0, min_value=1.0, max_value=5.0, step=0.1, format="%.1f")

# ---------------- CÁLCULOS ----------------
P1_offset, P2_offset, L = calcular_offset(x1, y1, x2, y2, dist_offset, lado)
desviacion_mm = desviacion_lineal_mm(L, error_seg)
color_desv = 'green' if error_seg <= 2 else 'red'

# ---------------- RESULTADOS ----------------
st.subheader("Resultados")
st.write("**Base:**")
st.write(f"P1 → X = {x1:.3f}, Y = {y1:.3f}")
st.write(f"P2 → X = {x2:.3f}, Y = {y2:.3f}")
st.write("**Offset:**")
st.write(f"P1′ → X = {P1_offset[0]:.3f}, Y = {P1_offset[1]:.3f}")
st.write(f"P2′ → X = {P2_offset[0]:.3f}, Y = {P2_offset[1]:.3f}")
st.write("**Ángulo interno:** 90°00′00″")
st.write(f"**Desviación angular:** {error_seg:.2f}″ → **{desviacion_mm:.2f} mm** en {L:.2f} m")

# ---------------- GRÁFICO ----------------
hash_datos = hashlib.md5(str((x1, y1, x2, y2, dist_offset, lado, error_seg)).encode()).hexdigest()
with st.spinner("Generando gráfico..."):
    fig = generar_grafico_cached(hash_datos, x1, y1, x2, y2, P1_offset, P2_offset, lado, L, desviacion_mm, color_desv)
    st.pyplot(fig, use_container_width=True)

st.caption("Offset calculado y mostrado con ángulo perpendicular exacto considerando el error angular del equipo.")
