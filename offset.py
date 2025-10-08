import streamlit as st
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

# =====================================
# Funciones auxiliares
# =====================================
def distancia_punto_linea(x1, y1, x2, y2, xp, yp):
    num = abs((x2 - x1)*(y1 - yp) - (x1 - xp)*(y2 - y1))
    den = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return num / den

# =====================================
# Interfaz
# =====================================
st.title("📐 Offset con Verificación de 90° y Punto de Rectificación")

st.sidebar.header("Datos de la línea base")

x1 = st.sidebar.number_input("X1 (P1)", value=984.765, step=0.001)
y1 = st.sidebar.number_input("Y1 (P1)", value=964.723, step=0.001)
x2 = st.sidebar.number_input("X2 (P2)", value=997.622, step=0.001)
y2 = st.sidebar.number_input("Y2 (P2)", value=980.027, step=0.001)

st.sidebar.header("Datos del offset")
dist_offset = st.sidebar.number_input("Distancia del offset (m)", value=10.0, step=0.5)
lado = st.sidebar.radio("Lado del offset", ("Izquierda (Antihorario)", "Derecha (Horario)"))

st.sidebar.header("Punto de verificación")
xp = st.sidebar.number_input("X del punto", value=992.420, step=0.001)
yp = st.sidebar.number_input("Y del punto", value=958.290, step=0.001)

# =====================================
# Cálculos
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

# Offset
offset_x = ux_perp * dist_offset
offset_y = uy_perp * dist_offset

P1_offset = (x1 + offset_x, y1 + offset_y)
P2_offset = (x2 + offset_x, y2 + offset_y)

# Ángulos
angulo_base = math.degrees(math.atan2(dy, dx)) % 360

# Distancias perpendiculares
dist_base = distancia_punto_linea(x1, y1, x2, y2, xp, yp)
dist_offset_line = distancia_punto_linea(P1_offset[0], P1_offset[1], P2_offset[0], P2_offset[1], xp, yp)

# =====================================
# Resultados
# =====================================
st.subheader("📍 Coordenadas calculadas")
st.write(f"**Línea base:** P1({x1:.3f}, {y1:.3f}) → P2({x2:.3f}, {y2:.3f})")
st.write(f"**Línea offset ({lado}):** P1′({P1_offset[0]:.3f}, {P1_offset[1]:.3f}) → P2′({P2_offset[0]:.3f}, {P2_offset[1]:.3f})")
st.write(f"**Punto de verificación (P):** ({xp:.3f}, {yp:.3f})")

st.subheader("📏 Distancias perpendiculares")
st.write(f"- A la línea base: {dist_base:.3f} m")
st.write(f"- A la línea offset: {dist_offset_line:.3f} m")

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

# Punto de verificación
ax.scatter(xp, yp, color='green', s=80, marker='o', label='Punto verificación')
ax.text(xp, yp, "P", fontsize=9, ha='left', va='bottom', color='green', fontweight='bold')

# Arco de 90°
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

# Ajustes del gráfico
ax.set_aspect('equal', adjustable='datalim')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.grid(True)
ax.legend()

st.pyplot(fig)

st.caption("💡 Muestra P1, P2, P1′, P2′, el punto de verificación (P) y el ángulo de 90° entre la línea base y la línea offset.")
