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

# =====================================
# Interfaz
# =====================================
st.title("📐 Verificación de Offset con Ángulo y Punto a 90°")

st.sidebar.header("Datos de la línea base")
x1 = st.sidebar.number_input("X1 (P1)", value=984.765, step=0.001)
y1 = st.sidebar.number_input("Y1 (P1)", value=964.723, step=0.001)
x2 = st.sidebar.number_input("X2 (P2)", value=997.622, step=0.001)
y2 = st.sidebar.number_input("Y2 (P2)", value=980.027, step=0.001)

st.sidebar.header("Offset")
dist_offset = st.sidebar.number_input("Distancia del offset (m)", value=10.0, step=0.5)
lado = st.sidebar.radio("Lado del offset", ("Izquierda (Antihorario)", "Derecha (Horario)"))

st.sidebar.header("Punto de verificación")
xp = st.sidebar.number_input("X del punto (P)", value=992.420, step=0.001)
yp = st.sidebar.number_input("Y del punto (P)", value=958.290, step=0.001)

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

offset_x = ux_perp * dist_offset
offset_y = uy_perp * dist_offset

P1_offset = (x1 + offset_x, y1 + offset_y)
P2_offset = (x2 + offset_x, y2 + offset_y)

# =====================================
# Cálculo de ángulos
# =====================================
angulo_base = math.degrees(math.atan2(dy, dx)) % 360
angulo_offset = math.degrees(math.atan2(uy_perp, ux_perp)) % 360
angulo_entre = abs(90 - abs(angulo_offset - angulo_base) % 180)

# =====================================
# Verificación del punto
# =====================================
dist_perp = distancia_punto_linea(x1, y1, x2, y2, xp, yp)

# Vector base y vector hacia el punto desde P1
v_base = (dx, dy)
v_punto = (xp - x1, yp - y1)
angulo_punto = angulo_entre_vectores(v_base, v_punto)

# =====================================
# Resultados
# =====================================
st.subheader("📏 Resultados")
st.write(f"**Línea base:** P1({x1:.3f}, {y1:.3f}) → P2({x2:.3f}, {y2:.3f})")
st.write(f"**Línea offset ({lado}):** P1′({P1_offset[0]:.3f}, {P1_offset[1]:.3f}) → P2′({P2_offset[0]:.3f}, {P2_offset[1]:.3f})")
st.write(f"**Punto de verificación (P):** ({xp:.3f}, {yp:.3f})")

st.markdown("---")

st.subheader("📐 Ángulos")
st.write(f"- Ángulo entre línea base y offset: **{angulo_entre:.2f}°**")
if abs(angulo_entre - 90) < 0.05:
    st.success("✅ La línea offset es perpendicular a la línea base (90° exactos).")
else:
    st.warning("⚠️ La línea offset no es exactamente perpendicular (verifique coordenadas).")

st.write(f"- Ángulo entre la línea base y el punto P: **{angulo_punto:.2f}°**")
if abs(angulo_punto - 90) < 0.05:
    st.success("✅ El punto P está a 90° respecto a la línea base.")
else:
    st.warning("⚠️ El punto P no está a 90° exactos respecto a la línea base.")

st.markdown("---")

st.subheader("📍 Distancia perpendicular del punto P a la línea base")
st.write(f"Distancia: **{dist_perp:.3f} m**")

# =====================================
# Gráfico
# =====================================
fig, ax = plt.subplots(figsize=(8, 8))

# Línea base
ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, label='Línea base')
ax.text(x1, y1, "P1", fontsize=9, ha='right', va='top', color='black', fontweight='bold')
ax.text(x2, y2, "P2", fontsize=9, ha='left', va='bottom', color='black', fontweight='bold')

# Línea offset
color = 'r' if "Derecha" in lado else 'b'
ax.plot([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]], color=color, linestyle='--', linewidth=2, label='Línea offset')
ax.text(P1_offset[0], P1_offset[1], "P1′", fontsize=9, ha='right', va='top', color=color, fontweight='bold')
ax.text(P2_offset[0], P2_offset[1], "P2′", fontsize=9, ha='left', va='bottom', color=color, fontweight='bold')

# Punto P
ax.scatter(xp, yp, color='green', s=80, marker='o', label='Punto verificación')
ax.text(xp, yp, "P", fontsize=9, ha='left', va='bottom', color='green', fontweight='bold')

# Línea perpendicular desde P al eje base (visual)
# Ecuación de la línea base: (y - y1) = m(x - x1)
# Pendiente perpendicular: -1/m
if dx != 0:
    m_base = dy / dx
    m_perp = -1 / m_base
    # Intersección punto-perpendicular
    x_inter = (m_perp * xp - yp - m_base * x1 + y1) / (m_perp - m_base)
    y_inter = m_base * (x_inter - x1) + y1
    ax.plot([xp, x_inter], [yp, y_inter], 'g:', linewidth=1.5, label='Línea perpendicular')
    ax.scatter(x_inter, y_inter, color='orange', s=50)
else:
    ax.plot([x1, xp], [y1, yp], 'g:', linewidth=1.5)

# Arco de 90° entre base y offset
radio = dist_offset * 0.6
start_angle = angulo_base
end_angle = angulo_base + 90 if "Izquierda" in lado else angulo_base - 90
arc = Arc((x1, y1), width=radio, height=radio, angle=0,
          theta1=min(start_angle, end_angle),
          theta2=max(start_angle, end_angle),
          color='orange', lw=2)
ax.add_patch(arc)
ax.text(x1 + ux_dir * radio * 0.6 + ux_perp * radio * 0.6,
        y1 + uy_dir * radio * 0.6 + uy_perp * radio * 0.6,
        "90°", fontsize=10, color='orange', fontweight='bold')

# Configuración
ax.set_aspect('equal', adjustable='datalim')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.grid(True)
ax.legend()

st.pyplot(fig)

st.caption("💡 Se muestra la línea base, offset, punto P y la perpendicular. Los ángulos y distancias se calculan con precisión topográfica.")
