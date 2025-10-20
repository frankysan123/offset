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

def distancia_punto_linea(x1, y1, x2, y2, xp, yp):
    """Distancia perpendicular de un punto a una línea."""
    num = abs((y2 - y1)*xp - (x2 - x1)*yp + x2*y1 - y2*x1)
    den = math.hypot(y2 - y1, x2 - x1)
    return num / den if den != 0 else 0

# =====================================
# Interfaz principal
# =====================================

st.title("🧭 Offset con Ángulo Interno y Puntos de Verificación")

# ---- Línea base ----
st.sidebar.header("Línea base")
x1 = st.sidebar.number_input("X1", value=1000.000, step=0.001, format="%.3f")
y1 = st.sidebar.number_input("Y1", value=1000.000, step=0.001, format="%.3f")
x2 = st.sidebar.number_input("X2", value=1020.000, step=0.001, format="%.3f")
y2 = st.sidebar.number_input("Y2", value=1000.000, step=0.001, format="%.3f")

# ---- Offset ----
st.sidebar.header("Offset")
dist_offset = st.sidebar.number_input("Distancia de offset (m)", value=5.000, step=0.001, format="%.3f")
lado = st.sidebar.radio("Lado del offset", ["Izquierda", "Derecha"])

# ---- Puntos de verificación ----
st.sidebar.header("Puntos de verificación (opcional)")
num_puntos = st.sidebar.number_input("Cantidad de puntos", min_value=0, max_value=5, value=0, step=1)

puntos = []
if num_puntos > 0:
    for i in range(num_puntos):
        st.sidebar.markdown(f"**Punto {i+1}**")
        xp_i = st.sidebar.number_input(f"X{i+1}", value=0.000, step=0.001, format="%.3f")
        yp_i = st.sidebar.number_input(f"Y{i+1}", value=0.000, step=0.001, format="%.3f")
        puntos.append((xp_i, yp_i))

# =====================================
# Cálculos
# =====================================

# Vectores base y offset
v_base = (x2 - x1, y2 - y1)
P1_offset, P2_offset = punto_offset(x1, y1, x2, y2, dist_offset, lado)
v_offset = (P2_offset[0] - P1_offset[0], P2_offset[1] - P1_offset[1])

# Ángulo interno (idealmente 90°)
v_perp = (-v_base[1], v_base[0])
angulo_real = angulo_entre_vectores(v_perp, v_offset)

# =====================================
# Gráfico
# =====================================

fig, ax = plt.subplots(figsize=(6,6))  # tamaño más compacto

# Dibujar línea base y offset
ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, label='Línea base')
ax.plot([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]],
        color='b' if "Izquierda" in lado else 'r', linestyle='--', linewidth=2, label='Offset')

# Etiquetas
ax.text(x1, y1, "P1", fontsize=9)
ax.text(x2, y2, "P2", fontsize=9)
ax.text(P1_offset[0], P1_offset[1], "P1′", fontsize=9)
ax.text(P2_offset[0], P2_offset[1], "P2′", fontsize=9)

# Dibujar puntos de verificación (si existen)
if len(puntos) > 0:
    for idx, (xp, yp) in enumerate(puntos):
        ax.scatter(xp, yp, color='green', s=60)
        ax.text(xp, yp, f"P{idx+1}", fontsize=8, ha='left', va='bottom', color='green')

# Mostrar texto del ángulo
ax.text((x1 + x2)/2, (y1 + y2)/2 + dist_offset/2,
        f"Ángulo interno: {angulo_real:.2f}°",
        fontsize=10, color='purple', ha='center', bbox=dict(facecolor='white', alpha=0.6))

ax.set_aspect('equal', 'box')
ax.legend()
ax.grid(True)

st.pyplot(fig)

# =====================================
# Resultados numéricos
# =====================================

st.subheader("📐 Resultados")
st.write(f"**Ángulo interno entre línea base y offset:** {angulo_real:.2f}°")

if abs(angulo_real - 90) < 0.01:
    st.success("✅ El ángulo es perpendicular (≈ 90°).")
else:
    st.warning(f"⚠️ El ángulo no es exactamente 90° (diferencia de {abs(90 - angulo_real):.2f}°).")
