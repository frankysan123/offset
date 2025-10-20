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

def angulo_entre_vectores(v1, v2):
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    if mag1 == 0 or mag2 == 0:
        return 0
    cosang = dot / (mag1 * mag2)
    cosang = max(min(cosang, 1), -1)
    ang = math.degrees(math.acos(cosang))
    return ang

def mostrar_3_decimales(valor):
    return f"{valor:.3f}"

# =====================================
# Interfaz principal
# =====================================
st.title("📐 Offset y Ángulo Interno Visual (Tipo AutoCAD)")

# --- Línea base ---
st.sidebar.header("Línea base")
x1 = st.sidebar.number_input("X1 (P1)", value=984.765, step=0.001, format="%.3f")
y1 = st.sidebar.number_input("Y1 (P1)", value=964.723, step=0.001, format="%.3f")
x2 = st.sidebar.number_input("X2 (P2)", value=997.622, step=0.001, format="%.3f")
y2 = st.sidebar.number_input("Y2 (P2)", value=980.027, step=0.001, format="%.3f")

# --- Offset ---
st.sidebar.header("Offset")
dist_offset = st.sidebar.number_input("Distancia del offset (m)", value=10.0, step=0.001, format="%.3f")
lado = st.sidebar.radio("Lado del offset", ("Izquierda (Antihorario)", "Derecha (Horario)"))

# --- Puntos de verificación (opcionales) ---
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
# Cálculos base y offset
# =====================================
dx = x2 - x1
dy = y2 - y1
L = math.sqrt(dx**2 + dy**2)

if L == 0:
    st.warning("⚠️ Ingresa dos puntos distintos para la línea base.")
    st.stop()

ux_dir = dx / L
uy_dir = dy / L

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

v_base = (dx, dy)
v_offset = (P2_offset[0]-P1_offset[0], P2_offset[1]-P1_offset[1])
angulo_entre = angulo_entre_vectores(v_base, v_offset)

# =====================================
# Mostrar resultados generales
# =====================================
st.subheader("📏 Resultados generales")

st.write(f"**Línea base:** P1({mostrar_3_decimales(x1)}, {mostrar_3_decimales(y1)}) → P2({mostrar_3_decimales(x2)}, {mostrar_3_decimales(y2)})")
st.write(f"**Línea offset ({lado}):** P1′({mostrar_3_decimales(P1_offset[0])}, {mostrar_3_decimales(P1_offset[1])}) → P2′({mostrar_3_decimales(P2_offset[0])}, {mostrar_3_decimales(P2_offset[1])})")

ang_interno = abs(90 - angulo_entre)
st.write(f"**Ángulo interno entre base y offset:** {angulo_entre:.2f}°")
if abs(angulo_entre - 90) > 0.01:
    st.warning(f"⚠️ Desviación de {ang_interno:.2f}° respecto a 90°")
else:
    st.success("✅ Ángulo interno correcto (90°)")

# =====================================
# Puntos de verificación (si hay)
# =====================================
resultados = []
if len(puntos) > 0:
    st.markdown("---")
    st.subheader("📍 Puntos de verificación")

    for idx, (xp, yp) in enumerate(puntos):
        v_point_base = (xp - x1, yp - y1)
        ang_base = angulo_entre_vectores(v_base, v_point_base)
        v_point_offset = (xp - P1_offset[0], yp - P1_offset[1])
        ang_offset = angulo_entre_vectores(v_offset, v_point_offset)
        dist_base = distancia_punto_linea(x1, y1, x2, y2, xp, yp)
        dist_offset_line = distancia_punto_linea(P1_offset[0], P1_offset[1], P2_offset[0], P2_offset[1], xp, yp)

        resultados.append({
            "coord": (xp, yp),
            "ang_base": ang_base,
            "dist_base": dist_base,
            "ang_offset": ang_offset,
            "dist_offset": dist_offset_line
        })

        st.write(f"**Punto {idx+1}: ({mostrar_3_decimales(xp)}, {mostrar_3_decimales(yp)})**")
        st.write(f"- Ángulo con base: {ang_base:.2f}° | Distancia: {mostrar_3_decimales(dist_base)} m")
        st.write(f"- Ángulo con offset: {ang_offset:.2f}° | Distancia: {mostrar_3_decimales(dist_offset_line)} m")

# =====================================
# Gráfico (con arco de ángulo)
# =====================================
fig, ax = plt.subplots(figsize=(8, 8))

# Dibujar línea base y offset
ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, label='Línea base')
ax.plot([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]],
        color='b' if "Izquierda" in lado else 'r', linestyle='--', linewidth=2, label='Línea offset')

# Etiquetas de puntos principales
ax.text(x1, y1, "P1", fontsize=9, color='black')
ax.text(x2, y2, "P2", fontsize=9, color='black')
ax.text(P1_offset[0], P1_offset[1], "P1′", fontsize=9, color='blue' if "Izquierda" in lado else 'red')
ax.text(P2_offset[0], P2_offset[1], "P2′", fontsize=9, color='blue' if "Izquierda" in lado else 'red')

# --- Dibuja el arco del ángulo entre base y offset ---
radio_arco = L * 0.2  # tamaño relativo al largo de la línea base
ang_base_deg = math.degrees(math.atan2(dy, dx))
ang_offset_deg = math.degrees(math.atan2(v_offset[1], v_offset[0]))

start_angle = ang_base_deg
end_angle = ang_offset_deg
if end_angle < start_angle:
    start_angle, end_angle = end_angle, start_angle

arc = Arc((x1, y1), width=radio_arco, height=radio_arco,
          angle=0, theta1=start_angle, theta2=end_angle, color='orange', linewidth=2)
ax.add_patch(arc)

# Colocar texto del ángulo en el gráfico
ang_text = f"{angulo_entre:.2f}°"
mid_angle_rad = math.radians((start_angle + end_angle) / 2)
x_text = x1 + (radio_arco * 0.7) * math.cos(mid_angle_rad)
y_text = y1 + (radio_arco * 0.7) * math.sin(mid_angle_rad)
ax.text(x_text, y_text, ang_text, fontsize=10, color='orange', fontweight='bold')

# Puntos de verificación
if len(resultados) > 0:
    for idx, r in enumerate(resultados):
        xp, yp = r["coord"]
        ax.scatter(xp, yp, color='green', s=80)
        ax.text(xp, yp, f"P{idx+1}", fontsize=9, ha='left', va='bottom', color='green')

ax.set_aspect('equal', adjustable='datalim')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.grid(True)
ax.legend()
st.pyplot(fig)

st.caption("💡 Ahora el gráfico incluye un arco de ángulo entre la línea base y el offset.")
