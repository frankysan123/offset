import streamlit as st
import math
import matplotlib.pyplot as plt

# --- Funciones auxiliares ---
def grados_a_dms(grados):
    grados_abs = abs(grados)
    g = int(grados_abs)
    m = int((grados_abs - g) * 60)
    s = round(((grados_abs - g) * 60 - m) * 60, 2)
    signo = "-" if grados < 0 else ""
    return f"{signo}{g}°{m}′{s}″"

def calcular_offset(x1, y1, x2, y2, distancia_offset):
    # Calcular azimut de la línea base
    dx = x2 - x1
    dy = y2 - y1
    azimut_base = math.degrees(math.atan2(dx, dy))  # Norte = 0°, sentido horario
    
    # Offset teórico a 90° exactos
    azimut_offset = azimut_base + 90
    x_offset = x2 + distancia_offset * math.sin(math.radians(azimut_offset))
    y_offset = y2 + distancia_offset * math.cos(math.radians(azimut_offset))
    
    return azimut_base, x_offset, y_offset

def desviacion_angular_y_lineal(angulo_real):
    # Calcular diferencia con 90°
    diferencia = 90 - angulo_real
    diferencia_segundos = diferencia * 3600  # a segundos de arco
    return diferencia, diferencia_segundos

# --- Interfaz Streamlit ---
st.title("🧭 Cálculo de Offset y Desviación Angular")

col1, col2 = st.columns(2)
with col1:
    x1 = st.number_input("X1 (m)", value=0.0)
    y1 = st.number_input("Y1 (m)", value=0.0)
    distancia_offset = st.number_input("Distancia del offset (m)", value=8.03)

with col2:
    x2 = st.number_input("X2 (m)", value=0.0)
    y2 = st.number_input("Y2 (m)", value=100.0)
    angulo_real = st.number_input("Ángulo interno real (°)", value=90.0, format="%.6f")

if st.button("Calcular Offset"):
    # Calcular el offset teórico
    azimut_base, x_offset, y_offset = calcular_offset(x1, y1, x2, y2, distancia_offset)
    
    # Desviación angular y lineal
    diferencia, diferencia_segundos = desviacion_angular_y_lineal(angulo_real)
    desviacion_lineal_mm = distancia_offset * math.tan(math.radians(abs(diferencia))) * 1000

    # --- Resultados numéricos ---
    st.subheader("📏 Resultados:")
    st.write(f"**Ángulo real:** {grados_a_dms(angulo_real)}")
    st.write(f"**Desviación angular:** {round(abs(diferencia_segundos), 2)}″")
    st.write(f"**Desviación lineal:** {round(desviacion_lineal_mm, 2)} mm (en {distancia_offset} m)")
    st.write(f"**Coordenadas del offset:** X = {round(x_offset, 3)}, Y = {round(y_offset, 3)}")

    # --- Gráfico ---
    fig, ax = plt.subplots()
    ax.plot([x1, x2], [y1, y2], 'b-', label='Línea Base')
    ax.plot([x2, x_offset], [y2, y_offset], 'r--', label='Offset')
    ax.scatter([x1, x2, x_offset], [y1, y2, y_offset], color='black')

    # Etiquetas de puntos
    ax.text(x1, y1, f"({x1:.2f}, {y1:.2f})", fontsize=8, ha='right')
    ax.text(x2, y2, f"({x2:.2f}, {y2:.2f})", fontsize=8, ha='left')
    ax.text(x_offset, y_offset, f"({x_offset:.2f}, {y_offset:.2f})", fontsize=8, ha='left', color='red')

    # Mostrar ángulo y desviaciones
    texto = f"Ángulo: {grados_a_dms(angulo_real)}\nΔ = {round(abs(diferencia_segundos), 2)}″\nError = {round(desviacion_lineal_mm, 2)} mm"
    ax.text(x2, y2, texto, fontsize=9, color='purple', ha='center', va='bottom')

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("Gráfico del Offset y Desviación")
    ax.legend()
    ax.axis('equal')
    st.pyplot(fig)
