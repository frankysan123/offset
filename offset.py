import streamlit as st
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import hashlib

# Configuración de página
st.set_page_config(page_title="Offset CAD", layout="centered")
st.title("Offset y Ángulo Interno Visual (Estilo AutoCAD)")

# Funciones auxiliares
def distancia_punto_linea(x1, y1, x2, y2, xp, yp):
    num = abs((x2 - x1)*(y1 - yp) - (x1 - xp)*(y2 - y1))
    den = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return num / den if den > 1e-10 else 0

def angulo_entre_vectores(v1, v2):
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    if mag1 < 1e-10 or mag2 < 1e-10:
        return 0
    cosang = max(min(dot / (mag1 * mag2), 1), -1)
    return math.degrees(math.acos(cosang))

def mostrar_3_decimales(valor):
    return f"{valor:.3f}"

@st.cache_data
def calcular_offset(x1, y1, x2, y2, dist_offset, lado):
    dx = x2 - x1
    dy = y2 - y1
    L = math.sqrt(dx**2 + dy**2)
    if L < 1e-6:
        return None, None, None
    ux_dir = dx / L
    uy_dir = dy / L
    ux_perp = -uy_dir if "Izquierda" in lado else uy_dir
    uy_perp = ux_dir if "Izquierda" in lado else -ux_dir
    P1_offset = (x1 + ux_perp * dist_offset, y1 + uy_perp * dist_offset)
    P2_offset = (x2 + ux_perp * dist_offset, y2 + uy_perp * dist_offset)
    return P1_offset, P2_offset, L

@st.cache_data(show_spinner=False)
def generar_grafico_cached(_hash, x1, y1, x2, y2, P1o, P2o, puntos_verif, lado_str, L):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1.5, label='Línea base', zorder=5)
    color_offset = 'blue' if "Izquierda" in lado_str else 'red'
    ax.plot([P1o[0], P2o[0]], [P1o[1], P2o[1]], color=color_offset, linestyle='--', linewidth=1.5,
            label=f'Offset ({lado_str})', zorder=5)
    
    dx, dy = x2 - x1, y2 - y1
    scale = 0.3
    ax.annotate('', xy=(x1 + dx*scale, y1 + dy*scale), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='black', lw=1))
    ax.annotate('', xy=(P1o[0] + dx*scale, P1o[1] + dy*scale), xytext=(P1o[0], P1o[1]),
                arrowprops=dict(arrowstyle='->', color=color_offset, lw=1))
    
    ax.text(x1, y1, "  P1", fontsize=9, color='black', ha='left', va='bottom')
    ax.text(x2, y2, "  P2", fontsize=9, color='black', ha='left', va='bottom')
    ax.text(P1o[0], P1o[1], "  P1′", fontsize=9, color=color_offset, ha='left', va='bottom')
    ax.text(P2o[0], P2o[1], "  P2′", fontsize=9, color=color_offset, ha='left', va='bottom')
    
    radio = L * 0.2
    dx_perp = P1o[0] - x1
    dy_perp = P1o[1] - y1
    ang_base = math.degrees(math.atan2(dy, dx))
    ang_perp = math.degrees(math.atan2(dy_perp, dx_perp))
    diff = (ang_perp - ang_base + 180) % 360 - 180
    if "Derecha" in lado_str:
        diff = -abs(diff) if diff > 0 else diff
    theta2 = ang_base + diff
    
    arc = Arc((x1, y1), radio*2, radio*2, angle=0, theta1=ang_base, theta2=theta2,
              color='orange', linewidth=1.5, zorder=4)
    ax.add_patch(arc)
    
    mid_angle = math.radians(ang_base + diff/2)
    x_text = x1 + (radio * 0.7) * math.cos(mid_angle)
    y_text = y1 + (radio * 0.7) * math.sin(mid_angle)
    ax.text(x_text, y_text, "90°", fontsize=9, color='orange', ha='center', va='center')
    
    if puntos_verif:
        for i, (xp, yp) in enumerate(puntos_verif):
            ax.scatter(xp, yp, color='green', s=80, zorder=6, edgecolors='black', linewidth=0.5)
            ax.text(xp, yp, f"  P{i+1}", fontsize=8, color='green', ha='left', va='bottom')
    
    ax.set_aspect('equal', adjustable='datalim')
    ax.grid(True, alpha=0.2)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.legend(loc='upper left')
    ax.set_title("Offset paralelo", pad=10)
    return fig

# Interfaz
if 'puntos' not in st.session_state:
    st.session_state.puntos = []
if 'num_puntos' not in st.session_state:
    st.session_state.num_puntos = 0

st.sidebar.header("Línea base")
x1 = st.sidebar.number_input("X1 (P1)", value=984.765, step=0.001, format="%.3f", key="x1")
y1 = st.sidebar.number_input("Y1 (P1)", value=964.723, step=0.001, format="%.3f", key="y1")
x2 = st.sidebar.number_input("X2 (P2)", value=997.622, step=0.001, format="%.3f", key="x2")
y2 = st.sidebar.number_input("Y2 (P2)", value=980.027, step=0.001, format="%.3f", key="y2")

st.sidebar.header("Offset")
dist_offset = st.sidebar.number_input("Distancia (m)", value=10.0, step=0.001, format="%.3f", key="dist")
lado = st.sidebar.radio("Lado", ("Izquierda (Antihorario)", "Derecha (Horario)"), key="lado")

st.sidebar.header("Puntos de verificación")
num_puntos = st.sidebar.number_input("Cantidad", min_value=0, max_value=5, value=st.session_state.num_puntos, step=1, key="num_puntos_input")
if st.sidebar.button("Actualizar puntos"):
    if num_puntos != st.session_state.num_puntos:
        if num_puntos > st.session_state.num_puntos:
            st.session_state.puntos.extend([(0.0, 0.0)] * (num_puntos - st.session_state.num_puntos))
        else:
            st.session_state.puntos = st.session_state.puntos[:num_puntos]
        st.session_state.num_puntos = num_puntos

puntos = []
for i in range(st.session_state.num_puntos):
    col1, col2 = st.sidebar.columns(2)
    with col1:
        xp = st.number_input(f"X{i+1}", value=st.session_state.puntos[i][0], step=0.001, format="%.3f", key=f"xp_{i}")
    with col2:
        yp = st.number_input(f"Y{i+1}", value=st.session_state.puntos[i][1], step=0.001, format="%.3f", key=f"yp_{i}")
    puntos.append((xp, yp))
    st.session_state.puntos[i] = (xp, yp)

# Cálculos
result = calcular_offset(x1, y1, x2, y2, dist_offset, lado)
if result[0] is None:
    st.warning("Ingresa dos puntos distintos.")
    st.stop()
P1_offset, P2_offset, L = result

datos_clave = (x1, y1, x2, y2, dist_offset, lado, tuple(tuple(p) for p in puntos))
hash_datos = hashlib.md5(str(datos_clave).encode()).hexdigest()

# Resultados
st.subheader("Resultados")
st.write(f"**Base:** P1({mostrar_3_decimales(x1)}, {mostrar_3_decimales(y1)}) → P2({mostrar_3_decimales(x2)}, {mostrar_3_decimales(y2)})")
st.write(f"**Offset:** P1′({mostrar_3_decimales(P1_offset[0])}, {mostrar_3_decimales(P1_offset[1])}) → P2′({mostrar_3_decimales(P2_offset[0])}, {mostrar_3_decimales(P2_offset[1])})")

angulo = angulo_entre_vectores((x2 - x1, y2 - y1), (P2_offset[0] - P1_offset[0], P2_offset[1] - P1_offset[1]))
angulo = 90.0 if abs(angulo - 90) < 0.01 else angulo
st.write(f"**Ángulo interno:** {angulo:.3f}°")
if abs(angulo - 90) < 0.01:
    st.success("Ángulo paralelo: 90.000°")
else:
    st.warning(f"Desviación: {abs(angulo - 90):.3f}°")

if puntos:
    st.markdown("---")
    st.subheader("Puntos de verificación")
    for i, (xp, yp) in enumerate(puntos):
        d_base = distancia_punto_linea(x1, y1, x2, y2, xp, yp)
        d_offset = distancia_punto_linea(P1_offset[0], P1_offset[1], P2_offset[0], P2_offset[1], xp, yp)
        st.write(f"**P{i+1}:** ({mostrar_3_decimales(xp)}, {mostrar_3_decimales(yp)})")
        st.write(f"→ Dist. base: {mostrar_3_decimales(d_base)} m | Dist. offset: {mostrar_3_decimales(d_offset)} m")

# Gráfico
with st.spinner("Generando gráfico..."):
    fig = generar_grafico_cached(hash_datos, x1, y1, x2, y2, P1_offset, P2_offset, puntos, lado, L)
    st.pyplot(fig, use_container_width=True)

st.caption("Optimizado: Gráfico en caché, sin recargas innecesarias.")
