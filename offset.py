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

def formato_grados_minutos_segundos(grados):
    """Convierte grados decimales a formato ° ′ ″ con 3 decimales en segundos"""
    g = int(grados)
    m = int((grados - g) * 60)
    s = (grados - g - m/60) * 3600
    return f"{g}° {m}′ {s:.3f}″"

def mostrar_3_decimales(valor):
    return f"{valor:.3f}"

# =====================================
# Interfaz
# =====================================
st.title("📐 Offset y Verificación de Perpendicularidad con Múltiples Puntos")

st.sidebar.header("Datos de la línea base")
x1 = st.sidebar.number_input("X1 (P1)", value=984.765, step=0.001, format="%.3f")
y1 = st.sidebar.number_input("Y1 (P1)", value=964.723, step=0.001, format="%.3f")
x2 = st.sidebar.number_input("X2 (P2)", value=997.622, step=0.001, format="%.3f")
y2 = st.sidebar.number_input("Y2 (P2)", value=980.027, step=0.001, format="%.3f")

st.sidebar.header("Offset")
dist_offset = st.sidebar.number_input("Distancia del offset (m)", value=10.0, step=0.001, format="%.3f")
lado = st.sidebar.radio("Lado del offset", ("Izquierda (Antihorario)", "Derecha (Horario)"))

st.sidebar.header("Puntos de verificación")
num_puntos = st.sidebar.number_input("Cantidad de puntos de verificación", min_value=1, max_value=5, value=1, step=1)
puntos = []
for i in range(num_puntos):
    st.sidebar.markdown(f"**Punto {i+1}**")
    xp_i = st.sidebar.number_input(f"X{i+1}", value=992.420, step=0.001, format="%.3f")
    yp_i = st.sidebar.number_input(f"Y{i+1}", value=958.290, step=0.001, format="%.3f")
    puntos.append((xp_i, yp_i))

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

# Coordenadas del offset
offset_x = ux_perp * dist_offset
offset_y = uy_perp * dist_offset
P1_offset = (x1 + offset_x, y1 + offset_y)
P2_offset = (x2 + offset_x, y2 + offset_y)

# Ángulo entre base y offset
v_base = (dx, dy)
v_offset = (P2_offset[0]-P1_offset[0], P2_offset[1]-P1_offset[1])
angulo_entre = angulo_entre_vectores(v_base, v_offset)

# =====================================
# Evaluación de los puntos
# =====================================
tolerancia = 0.1  # grados
resultados = []
for (xp, yp) in puntos:
    v_point_base = (xp - x1, yp - y1)
    ang_base = angulo_entre_vectores(v_base, v_point_base)
    perp_base = abs(ang_base - 90) <= tolerancia
    
    v_point_offset = (xp - P1_offset[0], yp - P1_offset[1])
    ang_offset = angulo_entre_vectores(v_offset, v_point_offset)
    perp_offset = abs(ang_offset - 90) <= tolerancia
    
    dist_base = distancia_punto_linea(x1, y1, x2, y2, xp, yp)
    dist_offset_line = distancia_punto_linea(P1_offset[0], P1_offset[1], P2_offset[0], P2_offset[1], xp, yp)
    
    resultados.append({
        "coord": (xp, yp),
        "ang_base": ang_base,
        "perp_base": perp_base,
        "dist_base": dist_base,
        "ang_offset": ang_offset,
        "perp_offset": perp_offset,
        "dist_offset": dist_offset_line
    })

# =====================================
# Resultados en la app
# =====================================
st.subheader("📏 Resultados")
st.write(f"**Línea base:** P1({mostrar_3_decimales(x1)}, {mostrar_3_decimales(y1)}) → P2({mostrar_3_decimales(x2)}, {mostrar_3_decimales(y2)})")
st.write(f"**Línea offset ({lado}):** P1′({mostrar_3_decimales(P1_offset[0])}, {mostrar_3_decimales(P1_offset[1])}) → P2′({mostrar_3_decimales(P2_offset[0])}, {mostrar_3_decimales(P2_offset[1])})")
st.write(f"- Ángulo entre línea base y offset: **{formato_grados_minutos_segundos(angulo_entre)}**")
if abs(angulo_entre - 90) < 0.01:
    st.success("✅ Línea offset perpendicular a la base.")
else:
    st.warning("⚠️ Línea offset no perpendicular a la base.")

st.markdown("---")
st.subheader("📏 Puntos de verificación")
for idx, r in enumerate(resultados):
    st.write(f"**Punto {idx+1}: ({mostrar_3_decimales(r['coord'][0])}, {mostrar_3_decimales(r['coord'][1])})**")
    st.write(f"- Ángulo con base: {formato_grados_minutos_segundos(r['ang_base'])} | Distancia perpendicular: {mostrar_3_decimales(r['dist_base'])} m")
    st.write(f"- Ángulo con offset: {formato_grados_minutos_segundos(r['ang_offset'])} | Distancia perpendicular: {mostrar_3_decimales(r['dist_offset'])} m")
    if r["perp_base"]:
        st.success("✅ Perpendicular a la línea base")
    else:
        st.error("❌ No perpendicular a la línea base")
    if r["perp_offset"]:
        st.success("✅ Perpendicular a la línea offset")
    else:
        st.error("❌ No perpendicular a la línea offset")
    st.markdown("---")

# =====================================
# Gráfico
# =====================================
fig, ax = plt.subplots(figsize=(8,8))
ax.plot([x1, x2],[y1, y2],'k-', linewidth=2,label='Línea base')
ax.plot([P1_offset[0],P2_offset[0]],[P1_offset[1],P2_offset[1]], color='b' if "Izquierda" in lado else 'r', linestyle='--', linewidth=2,label='Línea offset')
ax.text(x1, y1, "P1", fontsize=9)
ax.text(x2, y2, "P2", fontsize=9)
ax.text(P1_offset[0], P1_offset[1], "P1′", fontsize=9)
ax.text(P2_offset[0], P2_offset[1], "P2′", fontsize=9)

# Dibujar puntos de verificación
for r in resultados:
    xp, yp = r["coord"]
    color = 'green' if r["perp_base"] else 'red'
    ax.scatter(xp, yp, color=color, s=80)
    ax.text(xp, yp, "P", fontsize=9, ha='left', va='bottom', color=color)
    
ax.set_aspect('equal', adjustable='datalim')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.grid(True)
ax.legend()
st.pyplot(fig)
st.caption("💡 Verde = perpendicular, Rojo = no perpendicular. Coordenadas con 3 decimales.")
