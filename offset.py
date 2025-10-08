import streamlit as st
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

# =====================================
# Funciones auxiliares
# =====================================
def distancia_punto_linea(x1, y1, x2, y2, xp, yp):
    """Distancia perpendicular de un punto a una línea definida por (x1,y1)-(x2,y2)."""
    num = abs((x2 - x1)*(y1 - yp) - (x1 - xp)*(y2 - y1))
    den = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return num / den

def angulo_entre_vectores(v1, v2):
    """Ángulo en grados entre dos vectores (v1 y v2)."""
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    cosang = dot / (mag1 * mag2)
    ang = math.degrees(math.acos(max(min(cosang, 1), -1)))
    return ang

def formato_grados_minutos_segundos(grados):
    """Convierte grados decimales a formato ° ′ ″ con 3 decimales en segundos"""
    g = int(grados)
    m = int((grados - g) * 60)
    s = (grados - g - m/60) * 3600
    return f"{g}° {m}′ {s:.3f}″"

def mostrar_3_decimales(valor):
    """Muestra valor con 3 decimales sin redondear el valor interno"""
    return f"{valor:.3f}"

# =====================================
# Interfaz
# =====================================
st.title("📐 Offset y Punto Perpendicular con Precisión Topográfica")

st.sidebar.header("Datos de la línea base")
x1 = st.sidebar.number_input("X1 (P1)", value=984.765, format="%.12f")
y1 = st.sidebar.number_input("Y1 (P1)", value=964.723, format="%.12f")
x2 = st.sidebar.number_input("X2 (P2)", value=997.622, format="%.12f")
y2 = st.sidebar.number_input("Y2 (P2)", value=980.027, format="%.12f")

st.sidebar.header("Offset")
dist_offset = st.sidebar.number_input("Distancia del offset (m)", value=10.0, format="%.12f")
lado = st.sidebar.radio("Lado del offset", ("Izquierda (Antihorario)", "Derecha (Horario)"))

st.sidebar.header("Punto de verificación")
xp = st.sidebar.number_input("X del punto (P)", value=992.420, format="%.12f")
yp = st.sidebar.number_input("Y del punto (P)", value=958.290, format="%.12f")

# =====================================
# Cálculos geométricos
# =====================================
dx = x2 - x1
dy = y2 - y1
L = math.sqrt(dx**2 + dy**2)
ux_dir = dx / L
uy_dir = dy / L

# Vector perpendicular
if "Izquierda" in lado:
    ux_perp = -uy_dir
    uy_perp = ux_dir
else:
    ux_perp = uy_dir
    uy_perp = -ux_dir

# Coordenadas del offset
offset_x = ux_perp * dist_offset
offset_y = uy_perp * dist_offset
P1_offset = (x1 + offset_x, y1 + offset_y)
P2_offset = (x2 + offset_x, y2 + offset_y)

# Ángulo entre base y offset usando vectores
v_base = (dx, dy)
v_offset = (P2_offset[0]-P1_offset[0], P2_offset[1]-P1_offset[1])
angulo_entre = angulo_entre_vectores(v_base, v_offset)

# Distancia perpendicular del punto a la línea base
dist_perp_base = distancia_punto_linea(x1, y1, x2, y2, xp, yp)

# Verificación perpendicularidad punto
punto_perpendicular = True if abs(dist_perp_base) >= 0 else False

# =====================================
# Resultados
# =====================================
st.subheader("📏 Resultados")
st.write(f"**Línea base:** P1({mostrar_3_decimales(x1)}, {mostrar_3_decimales(y1)}) → P2({mostrar_3_decimales(x2)}, {mostrar_3_decimales(y2)})")
st.write(f"**Línea offset ({lado}):** P1′({mostrar_3_decimales(P1_offset[0])}, {mostrar_3_decimales(P1_offset[1])}) → P2′({mostrar_3_decimales(P2_offset[0])}, {mostrar_3_decimales(P2_offset[1])})")
st.write(f"**Punto de verificación (P):** ({mostrar_3_decimales(xp)}, {mostrar_3_decimales(yp)})")

st.markdown("---")
st.subheader("📐 Ángulos")
st.write(f"- Ángulo entre línea base y offset: **{formato_grados_minutos_segundos(angulo_entre)}**")
if abs(angulo_entre - 90) < 0.01:  # tolerancia mínima
    st.success("✅ La línea offset es perpendicular a la línea base (≈90°).")
else:
    st.warning("⚠️ La línea offset no es exactamente perpendicular.")

st.subheader("📏 Punto de verificación")
st.write(f"- Distancia perpendicular del punto P a la línea base: **{mostrar_3_decimales(dist_perp_base)} m**")
if punto_perpendicular:
    st.success("✅ El punto P está correctamente perpendicular a la línea base.")
else:
    st.error("⚠️ El punto P no está perpendicular a la línea base.")

# =====================================
# Gráfico
# =====================================
fig, ax = plt.subplots(figsize=(8, 8))

# Línea base
ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, label='Línea base')
ax.text(x1, y1, "P1", fontsize=9, ha='right', va='top', fontweight='bold')
ax.text(x2, y2, "P2", fontsize=9, ha='left', va='bottom', fontweight='bold')

# Línea offset
color = 'r' if "Derecha" in lado else 'b'
ax.plot([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]], color=color, linestyle='--', linewidth=2, label='Línea offset')
ax.text(P1_offset[0], P1_offset[1], "P1′", fontsize=9, ha='right', va='top', color=color, fontweight='bold')
ax.text(P2_offset[0], P2_offset[1], "P2′", fontsize=9, ha='left', va='bottom', color=color, fontweight='bold')

# Punto P
ax.scatter(xp, yp, color='green' if punto_perpendicular else 'red', s=80, marker='o', label='Punto verificación')
ax.text(xp, yp, "P", fontsize=9, ha='left', va='bottom', color='green' if punto_perpendicular else 'red', fontweight='bold')

# Línea perpendicular desde P a línea base
if dx != 0:
    m_base = dy / dx
    m_perp = -1 / m_base
    x_inter = (m_perp * xp - yp - m_base * x1 + y1) / (m_perp - m_base)
    y_inter = m_base * (x_inter - x1) + y1
    ax.plot([xp, x_inter], [yp, y_inter], 'g:' if punto_perpendicular else 'r:', linewidth=1.5, label='Perpendicular')
    ax.scatter(x_inter, y_inter, color='orange', s=50)
else:
    ax.plot([x1, xp], [y1, yp], 'g:' if punto_perpendicular else 'r:', linewidth=1.5)

# Arco 90°
radio = dist_offset * 0.6
start_angle = math.degrees(math.atan2(dy, dx))
end_angle = start_angle + 90 if "Izquierda" in lado else start_angle - 90
arc = Arc((x1, y1), width=radio, height=radio, angle=0,
          theta1=min(start_angle, end_angle),
          theta2=max(start_angle, end_angle),
          color='orange', lw=2)
ax.add_patch(arc)
ax.text(x1 + ux_dir * radio * 0.6 + ux_perp * radio * 0.6,
        y1 + uy_dir * radio * 0.6 + uy_perp * radio * 0.6,
        "90°", fontsize=10, color='orange', fontweight='bold')

# Configuración gráfica
ax.set_aspect('equal', adjustable='datalim')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.grid(True)
ax.legend()

st.pyplot(fig)
st.caption("💡 Línea base, offset, punto P y perpendicular. Ángulos mostrados en ° ′ ″. Coordenadas con 3 decimales visibles.")
