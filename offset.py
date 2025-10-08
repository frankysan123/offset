import streamlit as st
import math
import matplotlib.pyplot as plt

# ===========================================
# Título y descripción
# ===========================================
st.title("📐 Cálculo de Línea Offset (una línea de referencia)")
st.write("""
Esta aplicación calcula una **línea paralela (offset)** a partir de una **línea base**
definida por dos puntos P1 y P2, una distancia y el lado del desplazamiento.
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
# Cálculos
# ===========================================
dx = x2 - x1
dy = y2 - y1

# Vector perpendicular antihorario
vx = -dy
vy = dx

mag = math.sqrt(vx**2 + vy**2)

ux = (vx / mag) * dist_offset
uy = (vy / mag) * dist_offset

# Calcular puntos desplazados
if "Izquierda" in lado:
    P1_offset = (x1 - ux, y1 + uy)
    P2_offset = (x2 - ux, y2 + uy)
else:
    P1_offset = (x1 + ux, y1 - uy)
    P2_offset = (x2 + ux, y2 - uy)

# ===========================================
# Resultados numéricos
# ===========================================
st.subheader("📍 Coordenadas calculadas")

st.write("**Línea de referencia (original):**")
st.write(f"P1: ({x1:.3f}, {y1:.3f})")
st.write(f"P2: ({x2:.3f}, {y2:.3f})")

st.write(f"**Línea Offset ({lado}):**")
st.write(f"P1: ({P1_offset[0]:.3f}, {P1_offset[1]:.3f})")
st.write(f"P2: ({P2_offset[0]:.3f}, {P2_offset[1]:.3f})")

# ===========================================
# Visualización gráfica
# ===========================================
st.subheader("📊 Visualización gráfica")

fig, ax = plt.subplots(figsize=(6, 6))

# Línea original
ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, label='Línea original')

# Línea offset
ax.plot(
    [P1_offset[0], P2_offset[0]],
    [P1_offset[1], P2_offset[1]],
    'r--' if "Derecha" in lado else 'b--',
    linewidth=2,
    label=f'Línea offset ({lado})'
)

# Puntos
ax.scatter([x1, x2], [y1, y2], color='black', s=40, label="Puntos originales")
ax.scatter([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]],
           color='red' if "Derecha" in lado else 'blue', s=40, label="Puntos offset")

# Etiquetas
ax.text(x1, y1, "P1", fontsize=9, ha="right")
ax.text(x2, y2, "P2", fontsize=9, ha="right")

ax.set_aspect('equal', adjustable='datalim')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.grid(True)
ax.legend()
st.pyplot(fig)

st.caption("💡 Ingresa coordenadas y elige el lado del offset para visualizar el resultado.")
