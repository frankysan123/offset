import streamlit as st
import math
import matplotlib.pyplot as plt

# =====================================
# Funciones auxiliares
# =====================================

def angulo_entre_vectores(v1, v2):
    """Devuelve el ángulo en grados entre dos vectores (0–180°)."""
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.hypot(v1[0], v1[1])
    mag2 = math.hypot(v2[0], v2[1])
    if mag1 * mag2 == 0:
        return 0
    ang = math.degrees(math.acos(dot / (mag1 * mag2)))
    return ang

def punto_offset(x1, y1, x2, y2, distancia, lado):
    """Calcula los puntos desplazados (offset) a una distancia dada."""
    dx = x2 - x1
    dy = y2 - y1
    L = math.hypot(dx, dy)
    if L == 0:
        return (x1, y1), (x2, y2)
    if "Izquierda" in lado:
        ox = -dy / L * distancia
        oy = dx / L * distancia
    else:
        ox = dy / L * distancia
        oy = -dx / L * distancia
    return (x1 + ox, y1 + oy), (x2 + ox, y2 + oy)

# =====================================
# Interfaz principal
# =====================================

st.title("🧭 Generador de Offset y Ángulo Interno")

st.sidebar.header("Línea base")
x1 = st.sidebar.number_input("X1", value=1000.000, step=0.001, format="%.3f")
y1 = st.sidebar.number_input("Y1", value=1000.000, step=0.001, format="%.3f")
x2 = st.sidebar.number_input("X2", value=1020.000, step=0.001, format="%.3f")
y2 = st.sidebar.number_input("Y2", value=1000.000, step=0.001, format="%.3f")

st.sidebar.header("Offset")
dist_offset = st.sidebar.number_input("Distancia de offset (m)", value=5.000, step=0.001, format="%.3f")
lado = st.sidebar.radio("Lado del offset", ["Izquierda", "Derecha"])

# =====================================
# Cálculo de offset y ángulo
# =====================================

# Vectores base y offset
v_base = (x2 - x1, y2 - y1)
P1_offset, P2_offset = punto_offset(x1, y1, x2, y2, dist_offset, lado)
v_offset = (P2_offset[0] - P1_offset[0], P2_offset[1] - P1_offset[1])

# Ángulo entre base y offset (idealmente 90°)
v_perp = (-v_base[1], v_base[0])  # vector perpendicular teórico
angulo_real = angulo_entre_vectores(v_perp, v_offset)

# =====================================
# Gráfico
# =====================================

fig, ax = plt.subplots(figsize=(8,8))
ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, label='Línea base')
ax.plot([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]],
        color='b' if "Izquierda" in lado else 'r', linestyle='--', linewidth=2, label='Offset')

# Etiquetas
ax.text(x1, y1, "P1", fontsize=9)
ax.text(x2, y2, "P2", fontsize=9)
ax.text(P1_offset[0], P1_offset[1], "P1′", fontsize=9)
ax.text(P2_offset[0], P2_offset[1], "P2′", fontsize=9)

# Mostrar ángulo visualmente
ax.text((x1+x2)/2, (y1+y2)/2 + dist_offset/2,
        f"Ángulo: {angulo_real:.2f}°",
        fontsize=10, color='purple', ha='center', bbox=dict(facecolor='white', alpha=0.6))

ax.set_aspect('equal', 'box')
ax.legend()
ax.grid(True)

st.pyplot(fig)

# =====================================
# Resultados numéricos
# =====================================
st.subheader("📐 Resultados de cálculo")
st.write(f"**Ángulo interno entre línea base y offset:** {angulo_real:.2f}°")

if abs(angulo_real - 90) < 0.01:
    st.success("✅ El ángulo es perpendicular (≈ 90°).")
else:
    st.warning("⚠️ El ángulo no es exactamente 90°.")
