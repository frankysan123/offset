import streamlit as st
import math
import matplotlib.pyplot as plt

# ============================
# CONFIGURACIÓN INICIAL
# ============================
st.title("📐 Calculadora de Offset para Polilíneas")
st.write("""
Esta aplicación calcula líneas paralelas (offsets izquierda y derecha)
a una polilínea definida por una lista de puntos.
Ideal para topografía, diseño vial o delimitación de linderos.
""")

st.sidebar.header("Parámetros de entrada")

# ============================
# Entrada de puntos
# ============================
st.sidebar.write("Ingrese las coordenadas de la polilínea (X, Y):")
points_text = st.sidebar.text_area(
    "Formato: una pareja por línea, separada por coma.\nEjemplo:\n984.765,964.723\n997.622,980.027\n1010.300,990.500",
    value="984.765,964.723\n997.622,980.027\n1010.300,990.500",
    height=150
)

dist_offset = st.sidebar.number_input("Distancia del Offset (m)", value=10.0, step=0.5)

# ============================
# Conversión de texto a lista de puntos
# ============================
points = []
for line in points_text.strip().split("\n"):
    try:
        x_str, y_str = line.strip().split(",")
        points.append((float(x_str), float(y_str)))
    except:
        pass

if len(points) < 2:
    st.warning("⚠️ Ingrese al menos dos puntos para formar una línea.")
    st.stop()

# ============================
# CÁLCULO DE OFFSETS
# ============================

def offset_segment(p1, p2, dist):
    """Calcula los puntos desplazados a la izquierda y derecha de un segmento."""
    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1

    # Vector perpendicular antihorario (izquierda)
    vx = -dy
    vy = dx

    mag = math.sqrt(vx**2 + vy**2)
    ux = (vx / mag) * dist
    uy = (vy / mag) * dist

    # Izquierda
    p1_izq = (x1 - ux, y1 + uy)
    p2_izq = (x2 - ux, y2 + uy)

    # Derecha
    p1_der = (x1 + ux, y1 - uy)
    p2_der = (x2 + ux, y2 - uy)

    return p1_izq, p2_izq, p1_der, p2_der

# Generar offsets de todos los tramos
left_points = []
right_points = []

for i in range(len(points) - 1):
    p1 = points[i]
    p2 = points[i + 1]

    p1_izq, p2_izq, p1_der, p2_der = offset_segment(p1, p2, dist_offset)

    if i == 0:
        left_points.append(p1_izq)
        right_points.append(p1_der)
    left_points.append(p2_izq)
    right_points.append(p2_der)

# ============================
# MOSTRAR RESULTADOS NUMÉRICOS
# ============================
st.subheader("📍 Coordenadas de los Offsets")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Línea Izquierda (Antihorario)**")
    for i, p in enumerate(left_points, start=1):
        st.write(f"P{i}: ({p[0]:.3f}, {p[1]:.3f})")

with col2:
    st.markdown("**Línea Derecha (Horario)**")
    for i, p in enumerate(right_points, start=1):
        st.write(f"P{i}: ({p[0]:.3f}, {p[1]:.3f})")

# ============================
# GRÁFICO
# ============================
st.subheader("📊 Visualización de Polilínea y Offsets")

fig, ax = plt.subplots(figsize=(7, 7))

# Línea original
x_vals = [p[0] for p in points]
y_vals = [p[1] for p in points]
ax.plot(x_vals, y_vals, 'k-', linewidth=2, label='Línea Original')

# Línea izquierda
x_left = [p[0] for p in left_points]
y_left = [p[1] for p in left_points]
ax.plot(x_left, y_left, 'b--', linewidth=2, label='Offset Izquierda')

# Línea derecha
x_right = [p[0] for p in right_points]
y_right = [p[1] for p in right_points]
ax.plot(x_right, y_right, 'r--', linewidth=2, label='Offset Derecha')

# Puntos
ax.scatter(x_vals, y_vals, color='black', s=40)
ax.scatter(x_left, y_left, color='blue', s=40)
ax.scatter(x_right, y_right, color='red', s=40)

# Configuración del gráfico
ax.set_aspect('equal', adjustable='datalim')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.grid(True)
ax.legend()

st.pyplot(fig)

st.caption("💡 Modifica los puntos o la distancia de offset para ver los cambios instantáneamente.")
