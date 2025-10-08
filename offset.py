import streamlit as st
import math
import matplotlib.pyplot as plt

# ===========================================
# Título
# ===========================================
st.title("📐 Cálculo de Línea Offset Alineada a la Referencia")
st.write("""
Esta herramienta genera una **línea paralela (offset)** perfectamente alineada
con una **línea de referencia** entre P1 y P2, desplazada a izquierda o derecha
según la distancia especificada.
""")

# ===========================================
# Entradas del usuario
# ===========================================
st.sidebar.header("Datos de entrada")

x1 = st.sidebar.number_input("X1 (P1)", value=984.765, step=0.001)
y1 = st.sidebar.number_input("Y1 (P1)", value=964.723, step=0.001)
x2 = st.sidebar.number_input("X2 (P2)", value=997.622, step=0.001)
y2 = st.sidebar.number_input("Y2 (P2)", value=980.027, step=0.001)

dist_offset = st.sidebar.number_input("Distancia del offset (m)", value=10.0, step=0.5)

lado = st.sidebar.radio(
    "Seleccione el lado del desplazamiento:",
    ("Izquierda (Antihorario)", "Derecha (Horario)")
)

# ===========================================
# Cálculos geométricos
# ===========================================
dx = x2 - x1
dy = y2 - y1

# Longitud de la línea
L = math.sqrt(dx**2 + dy**2)

# Vector unitario de dirección (alineado a la línea base)
ux_dir = dx / L
uy_dir = dy / L

# Vector perpendicular (izquierda = antihorario)
if "Izquierda" in lado:
    # rotación 90° antihoraria
    ux_perp = -uy_dir
    uy_perp = ux_dir
else:
    # rotación 90° horaria
    ux_perp = uy_dir
    uy_perp = -ux_dir

# Desplazamiento perpendicular escalado por distancia
offset_x = ux_perp * dist_offset
offset_y = uy_perp * dist_offset

# Nueva línea paralela (offset)
P1_offset = (x1 + offset_x, y1 + offset_y)
P2_offset = (x2 + offset_x, y2 + offset_y)

# ===========================================
# Cálculo del ángulo (opcional, para topografía)
# ===========================================
angulo_rad = math.atan2(dy, dx)
angulo_deg = math.degrees(angulo_rad)

if angulo_deg < 0:
    angulo_deg += 360

# ===========================================
# Resultados
# ===========================================
st.subheader("📍 Coordenadas y datos calculados")

st.write(f"**Ángulo de la línea de referencia:** {angulo_deg:.2f}°")
st.write("**Línea original:**")
st.write(f"P1: ({x1:.3f}, {y1:.3f})")
st.write(f"P2: ({x2:.3f}, {y2:.3f})")

st.write(f"**Línea offset ({lado}):**")
st.write(f"P1: ({P1_offset[0]:.3f}, {P1_offset[1]:.3f})")
st.write(f"P2: ({P2_offset[0]:.3f}, {P2_offset[1]:.3f})")

# ===========================================
# Visualización
# ===========================================
st.subheader("📊 Visualización de la línea y su offset")

fig, ax = plt.subplots(figsize=(7, 7))

# Línea de referencia
ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, label='Línea de referencia')

# Línea offset (paralela)
color = 'b' if "Izquierda" in lado else 'r'
ax.plot([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]], 
        color=color, linestyle='--', linewidth=2, label=f'Offset {lado}')

# Puntos
ax.scatter([x1, x2], [y1, y2], color='black', s=50)
ax.scatter([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]], color=color, s=50)

# Línea auxiliar para mostrar perpendicularidad
ax.plot([x1, P1_offset[0]], [y1, P1_offset[1]], 'g:', linewidth=1)
ax.plot([x2, P2_offset[0]], [y2, P2_offset[1]], 'g:', linewidth=1)

ax.set_aspect('equal', adjustable='datalim')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.legend()
ax.grid(True)

st.pyplot(fig)

st.caption("💡 La línea offset está perfectamente paralela y alineada a la línea de referencia.")
