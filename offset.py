import streamlit as st
import math
import matplotlib.pyplot as plt

# =====================================
# Función auxiliar
# =====================================
def a_sexagesimal(grados):
    g = int(grados)
    m = int((grados - g) * 60)
    s = (grados - g - m/60) * 3600
    return g, m, s

def distancia_punto_linea(x1, y1, x2, y2, xp, yp):
    """Distancia perpendicular de un punto a una línea definida por P1-P2"""
    num = abs((x2 - x1) * (y1 - yp) - (x1 - xp) * (y2 - y1))
    den = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return num / den

# =====================================
# Interfaz principal
# =====================================
st.title("📐 Offset, Verificación y Distancia Perpendicular")
st.write("""
Calcula una **línea offset** a partir de una línea base, y permite verificar un **punto de rectificación**, mostrando:
- Si está **alineado o perpendicular (90°)** a la línea base y offset.
- La **distancia perpendicular real (m)** hacia ambas líneas.
""")

# =====================================
# Entradas
# =====================================
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
# Cálculos base
# =====================================
dx = x2 - x1
dy = y2 - y1
L = math.sqrt(dx**2 + dy**2)

ux_dir = dx / L
uy_dir = dy / L

# Vector perpendicular según el lado
if "Izquierda" in lado:
    ux_perp = -uy_dir
    uy_perp = ux_dir
else:
    ux_perp = uy_dir
    uy_perp = -ux_dir

# Puntos del offset
offset_x = ux_perp * dist_offset
offset_y = uy_perp * dist_offset

P1_offset = (x1 + offset_x, y1 + offset_y)
P2_offset = (x2 + offset_x, y2 + offset_y)

# =====================================
# Ángulos y diferencias
# =====================================
angulo_base = math.degrees(math.atan2(dy, dx)) % 360
angulo_offset = math.degrees(math.atan2(uy_perp, ux_perp)) % 360
angulo_punto = math.degrees(math.atan2(yp - y1, xp - x1)) % 360

diff_base = abs(angulo_base - angulo_punto)
if diff_base > 180:
    diff_base = 360 - diff_base

diff_offset = abs(angulo_offset - angulo_punto)
if diff_offset > 180:
    diff_offset = 360 - diff_offset

# Conversión sexagesimal
g1, m1, s1 = a_sexagesimal(diff_base)
g2, m2, s2 = a_sexagesimal(diff_offset)

# =====================================
# Distancias perpendiculares
# =====================================
dist_base = distancia_punto_linea(x1, y1, x2, y2, xp, yp)
dist_offset_line = distancia_punto_linea(P1_offset[0], P1_offset[1], P2_offset[0], P2_offset[1], xp, yp)

# =====================================
# Resultados
# =====================================
st.subheader("📍 Coordenadas calculadas")
st.write(f"**Línea base:** P1({x1:.3f}, {y1:.3f}) → P2({x2:.3f}, {y2:.3f})")
st.write(f"**Línea offset ({lado}):** P1({P1_offset[0]:.3f}, {P1_offset[1]:.3f}) → P2({P2_offset[0]:.3f}, {P2_offset[1]:.3f})")

st.markdown("---")
st.subheader("📏 Verificación del punto de rectificación")
st.write(f"**Punto:** ({xp:.3f}, {yp:.3f})")

st.write(f"- Diferencia con línea base: {diff_base:.6f}° → {g1}°{m1:02d}′{s1:05.2f}″")
if abs(diff_base) < 0.0001:
    st.success("✅ El punto está alineado con la línea base.")
elif abs(diff_base - 90) < 0.0001:
    st.success("✅ El punto está a 90° exactos respecto a la línea base.")
else:
    st.warning(f"⚠️ Desviación angular respecto a base: {diff_base:.4f}°")

st.write(f"- Diferencia con línea offset: {diff_offset:.6f}° → {g2}°{m2:02d}′{s2:05.2f}″")
if abs(diff_offset) < 0.0001:
    st.info("✅ El punto está alineado con la línea offset.")
elif abs(diff_offset - 90) < 0.0001:
    st.info("✅ El punto está a 90° exactos respecto a la línea offset.")
else:
    st.warning(f"⚠️ Desviación angular respecto al offset: {diff_offset:.4f}°")

st.markdown("---")
st.subheader("📏 Distancia perpendicular del punto")
st.write(f"- A la **línea base:** {dist_base:.3f} m")
st.write(f"- A la **línea offset:** {dist_offset_line:.3f} m")

if abs(dist_base - dist_offset) < 0.05:
    st.success("✅ El punto está prácticamente sobre la línea offset.")
elif dist_base < dist_offset:
    st.warning("📉 El punto está **antes** del offset (más cerca de la línea base).")
else:
    st.warning("📈 El punto está **más allá** del offset (pasado los 10 m).")

# =====================================
# Visualización gráfica
# =====================================
st.subheader("📊 Visualización gráfica")

fig, ax = plt.subplots(figsize=(7, 7))

# Línea base
ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, label='Línea base')

# Línea offset
color = 'r' if "Derecha" in lado else 'b'
ax.plot([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]], color=color, linestyle='--', linewidth=2, label='Línea offset')

# Punto de verificación
ax.scatter(xp, yp, color='green', s=80, marker='o', label='Punto de verificación')

# Línea perpendicular desde punto a base
ax.plot([xp, xp], [yp, yp], 'g:')
ax.plot([x1, xp], [y1, yp], 'g:', linewidth=1)

ax.set_aspect('equal', adjustable='datalim')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.legend()
ax.grid(True)
st.pyplot(fig)

st.caption("💡 Se muestran los ángulos, alineaciones y distancias perpendiculares desde el punto hacia las líneas base y offset.")
