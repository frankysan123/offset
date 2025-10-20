import streamlit as st
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrowPatch

# =====================================
# Funciones auxiliares
# =====================================
def distancia_punto_linea(x1, y1, x2, y2, xp, yp):
    num = abs((x2 - x1)*(y1 - yp) - (x1 - xp)*(y2 - y1))
    den = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return num / den if den != 0 else 0

def angulo_entre_vectores(v1, v2):
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    if mag1 == 0 or mag2 == 0:
        return 0
    cosang = max(min(dot / (mag1 * mag2), 1), -1)
    return math.degrees(math.acos(cosang))

def mostrar_3_decimales(valor):
    return f"{valor:.3f}"

def agregar_flecha(ax, x, y, dx, dy, color, label=None):
    """Agrega una flecha direccional en la línea"""
    ax.annotate('', xy=(x + dx, y + dy), xytext=(x, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5),
                zorder=3)
    if label:
        mid_x = x + dx * 0.5
        mid_y = y + dy * 0.5
        ax.text(mid_x, mid_y, label, color=color, fontsize=8, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7, edgecolor=color))

# =====================================
# Interfaz principal
# =====================================
st.title("📐 Offset y Ángulo Interno Visual (Estilo AutoCAD)")

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

# --- Puntos de verificación ---
st.sidebar.header("Puntos de verificación (opcional)")
num_puntos = st.sidebar.number_input("Cantidad de puntos", min_value=0, max_value=5, value=0, step=1)

puntos = []
if num_puntos > 0:
    for i in range(num_puntos):
        st.sidebar.markdown(f"**Punto {i+1}**")
        xp_i = st.sidebar.number_input(f"X{i+1}", value=0.000, key=f"xp_{i}", step=0.001, format="%.3f")
        yp_i = st.sidebar.number_input(f"Y{i+1}", value=0.000, key=f"yp_{i}", step=0.001, format="%.3f")
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

# Vector unitario dirección
ux_dir = dx / L
uy_dir = dy / L

# Vector perpendicular unitario (90° exacto)
if "Izquierda" in lado:
    ux_perp = -uy_dir
    uy_perp = ux_dir
else:
    ux_perp = uy_dir
    uy_perp = -ux_dir

# Puntos offset
offset_x = ux_perp * dist_offset
offset_y = uy_perp * dist_offset
P1_offset = (x1 + offset_x, y1 + offset_y)
P2_offset = (x2 + offset_x, y2 + offset_y)

# Vectores
v_base = (dx, dy)
v_offset = (P2_offset[0] - P1_offset[0], P2_offset[1] - P1_offset[1])

# Ángulo entre base y offset (debe ser ~90°)
angulo_entre = angulo_entre_vectores(v_base, v_offset)

# =====================================
# Mostrar resultados
# =====================================
st.subheader("📏 Resultados generales")
st.write(f"**Línea base:** P1({mostrar_3_decimales(x1)}, {mostrar_3_decimales(y1)}) → P2({mostrar_3_decimales(x2)}, {mostrar_3_decimales(y2)})")
st.write(f"**Línea offset ({lado}):** P1′({mostrar_3_decimales(P1_offset[0])}, {mostrar_3_decimales(P1_offset[1])}) → P2′({mostrar_3_decimales(P2_offset[0])}, {mostrar_3_decimales(P2_offset[1])})")

# Forzamos 90° con redondeo
if abs(angulo_entre - 90) < 1e-10:
    angulo_entre = 90.0

st.write(f"**Ángulo interno:** {angulo_entre:.3f}°")
if abs(angulo_entre - 90) > 0.01:
    st.warning(f"⚠️ Desviación de {abs(angulo_entre - 90):.3f}° (posible error numérico)")
else:
    st.success("✅ Ángulo interno correcto: 90.000°")

# =====================================
# Puntos de verificación
# =====================================
resultados = []
if puntos:
    st.markdown("---")
    st.subheader("📍 Puntos de verificación")
    for idx, (xp, yp) in enumerate(puntos):
        dist_base = distancia_punto_linea(x1, y1, x2, y2, xp, yp)
        dist_offset = distancia_punto_linea(P1_offset[0], P1_offset[1], P2_offset[0], P2_offset[1], xp, yp)
        
        # Ángulo con la línea base
        v_to_point = (xp - x1, yp - y1)
        ang_base = angulo_entre_vectores(v_base, v_to_point)
        
        resultados.append({
            "coord": (xp, yp),
            "dist_base": dist_base,
            "dist_offset": dist_offset,
            "ang_base": ang_base
        })

        st.write(f"**Punto {idx+1}: ({mostrar_3_decimales(xp)}, {mostrar_3_decimales(yp)})**")
        st.write(f"- Distancia a base: {mostrar_3_decimales(dist_base)} m")
        st.write(f"- Distancia a offset: {mostrar_3_decimales(dist_offset)} m")

# =====================================
# Gráfico mejorado
# =====================================
fig, ax = plt.subplots(figsize=(10, 8))

# Líneas
ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, label='Línea base', zorder=5)
color_offset = 'blue' if "Izquierda" in lado else 'red'
ax.plot([P1_offset[0], P2_offset[0]], [P1_offset[1], P2_offset[1]], 
        color=color_offset, linestyle='--', linewidth=2, label=f'Offset ({lado})', zorder=5)

# Flechas direccionales
agregar_flecha(ax, x1, y1, dx*0.3, dy*0.3, 'black')
agregar_flecha(ax, P1_offset[0], P1_offset[1], dx*0.3, dy*0.3, color_offset)

# Etiquetas de puntos
ax.text(x1, y1, "  P1", fontsize=10, color='black', ha='left', va='bottom')
ax.text(x2, y2, "  P2", fontsize=10, color='black', ha='left', va='bottom')
ax.text(P1_offset[0], P1_offset[1], "  P1′", fontsize=10, color=color_offset, ha='left', va='bottom')
ax.text(P2_offset[0], P2_offset[1], "  P2′", fontsize=10, color=color_offset, ha='left', va='bottom')

# --- Arco de 90° en el lado correcto ---
radio_arco = L * 0.25
centro_arco = (x1, y1)  # desde P1

# Dirección del offset (hacia afuera)
dx_perp = P1_offset[0] - x1
dy_perp = P1_offset[1] - y1

# Ángulo de la base y del offset
ang_base = math.degrees(math.atan2(dy, dx))
ang_perp = math.degrees(math.atan2(dy_perp, dx_perp))

# Ajustar dirección del arco según lado
theta1 = ang_base
theta2 = ang_perp

# Asegurar que el arco sea de 90° en sentido correcto
diff = (theta2 - theta1 + 180) % 360 - 180
if "Derecha" in lado:
    diff = -abs(diff) if diff < 0 else -diff  # invertir sentido

theta2 = theta1 + diff

# Dibujar arco
arc = Arc(centro_arco, radio_arco*2, radio_arco*2, angle=0,
          theta1=theta1, theta2=theta2, color='orange', linewidth=2.5, zorder=4)
ax.add_patch(arc)

# Texto del ángulo
mid_angle = math.radians(theta1 + (theta2 - theta1)/2)
x_text = centro_arco[0] + (radio_arco * 0.7) * math.cos(mid_angle)
y_text = centro_arco[1] + (radio_arco * 0.7) * math.sin(mid_angle)
ax.text(x_text, y_text, "90°", fontsize=11, color='orange', fontweight='bold',
        ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

# Puntos de verificación
if resultados:
    for idx, r in enumerate(resultados):
        xp, yp = r["coord"]
        ax.scatter(xp, yp, color='green', s=100, zorder=6, edgecolors='black', linewidth=0.5)
        ax.text(xp, yp, f"  P{idx+1}", fontsize=9, color='green', ha='left', va='bottom')

# Configuración del gráfico
ax.set_aspect('equal', adjustable='datalim')
ax.grid(True, alpha=0.3)
ax.set_xlabel("X (metros)")
ax.set_ylabel("Y (metros)")
ax.legend(loc='upper left')
ax.set_title("Offset paralelo con ángulo interno de 90°", pad=20)

st.pyplot(fig)

st.caption("✨ **Mejorado:** Arco de 90° en lado correcto, flechas, etiquetas y precisión numérica.")
