import streamlit as st
import math
import matplotlib.pyplot as plt

# ===========================================
# Título
# ===========================================
st.title("📐 Offset Alineado y Verificación de Ángulo 90°")
st.write("""
Esta herramienta calcula una **línea offset paralela** a una línea de referencia 
y verifica si el desplazamiento se realizó a **90° exactos (90°00′00″)** respecto 
a la línea base.
""")

# ===========================================
# Entradas
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
L = math.sqrt(dx**2 + dy**2)

# Vector unitario de la línea base
ux_dir = dx / L
uy_dir = dy / L

# Vector perpendicular según el lado
if "Izquierda" in lado:
    ux_perp = -uy_dir
    uy_perp = ux_dir
else:
    ux_perp = uy_dir
    uy_perp = -ux_dir

# Desplazamiento perpendicular escalado
offset_x = ux_perp * dist_offset
offset_y = uy_perp * dist_offset

# Puntos offset
P1_offset = (x1 + offset_x, y1 + offset_y)
P2_offset = (x2 + offset_x, y2 + offset_y)

# ===========================================
# Cálculo de ángulos
# ===========================================
# Ángulo de la línea de referencia
angulo_base = math.degrees(math.atan2(dy, dx))
if angulo_base < 0:
    angulo_base += 360

# Ángulo del vector de offset (perpendicular)
angulo_offset = math.degrees(math.atan2(uy_perp, ux_perp))
if angulo_offset < 0:
    angulo_offset += 360

# Diferencia angular absoluta
diferencia = abs(angulo_base - angulo_offset)
if diferencia > 180:
    diferencia = 360 - diferencia  # aseguro ángulo agudo

# ===========================================
# Conversión a grados, minutos y segundos
# ===========================================
def a_sexagesimal(grados):
    g = int(grados)
    m = int((grados - g) * 60)
    s = (grados - g - m/60) * 3600
    return g, m, s

g, m, s = a_sexagesimal(diferencia)

# ===========================================
# Resultados
# ===========================================
st.subheader("📍 Coordenadas y resultados")

st.write(f"**Línea de referencia:** P1({x1:.3f}, {y1:.3f}) → P2({x2:.3f}, {y2:.3f})")
st.write(f"**Línea offset ({lado}):** P1({P1_offset[0]:.3f}, {P1_offset[1]:.3f}) → P2({P2_offset[0]:.3f}, {P2_offset[1]:.3f})")

st.markdown("---")
st.write(f"**Ángulo de la línea base:** {angulo_base:.4f}°")
st.write(f"**Ángulo del offset (perpendicular):** {angulo_offset:.4f}°")
st.write(f"**Diferencia angular:** {diferencia:.6f}°  → {g}°{m:02d}′{s:05.2f}″")

# Verificación de perpendicularidad
if abs(diferencia - 90) < 0.0001:
    st.success("✅ La línea de offset está a 90° exactos respecto a la línea base.")
else:
    st.warning(f"⚠️ La línea está desviada {abs(diferencia - 90):.6f}° de la perpendicular (90° exactos).")

# ===========================================
# Visualización gráfica
# ===========================================
st.subheader("📊 Visualización")

fig, ax = plt.subplots(figsize=(7, 7))
ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, label='Línea de referencia')
color = 'b' if "Izquierda" in lado else 'r'
ax.plot([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]], color=color, linestyle='--', linewidth=2, label=f'Offset {lado}')
ax.scatter([x1, x2, P1_offset[0], P2_offset[0]], [y1, y2, P1_offset[1], P2_offset[1]], s=50)

# Líneas auxiliares para mostrar perpendicularidad
ax.plot([x1, P1_offset[0]], [y1, P1_offset[1]], 'g:', linewidth=1)
ax.plot([x2, P2_offset[0]], [y2, P2_offset[1]], 'g:', linewidth=1)

ax.set_aspect('equal', adjustable='datalim')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.legend()
ax.grid(True)
st.pyplot(fig)

st.caption("💡 El programa calcula si el offset está a 90° exactos respecto a la línea base.")
