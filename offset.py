import streamlit as st
import math

# Función para convertir decimal a grados, minutos y segundos
def decimal_a_dms(decimal):
    grados = int(decimal)
    minutos_decimales = abs((decimal - grados) * 60)
    minutos = int(minutos_decimales)
    segundos = round((minutos_decimales - minutos) * 60, 2)
    return f"{grados}° {minutos}' {segundos}"""

# Función para calcular el offset y mostrar coordenadas X y Y
def calcular_offset(x1, y1, x2, y2, distancia_offset):
    dx = x2 - x1
    dy = y2 - y1
    longitud = math.sqrt(dx**2 + dy**2)

    # Coordenadas del offset (a la derecha de la línea base)
    offset_x1 = x1 + (dy / longitud) * distancia_offset
    offset_y1 = y1 - (dx / longitud) * distancia_offset
    offset_x2 = x2 + (dy / longitud) * distancia_offset
    offset_y2 = y2 - (dx / longitud) * distancia_offset

    # Cálculo del ángulo en decimal y conversión a DMS
    angulo_rad = math.atan2(dy, dx)
    angulo_dec = math.degrees(angulo_rad)
    angulo_dms = decimal_a_dms(angulo_dec)

    return (offset_x1, offset_y1, offset_x2, offset_y2, angulo_dms)

# Interfaz Streamlit
st.title("Cálculo de Línea Base y Offset (Topografía)")

st.subheader("Datos de entrada")
x1 = st.number_input("Coordenada X1 (punto inicial)", value=0.0)
y1 = st.number_input("Coordenada Y1 (punto inicial)", value=0.0)
x2 = st.number_input("Coordenada X2 (punto final)", value=100.0)
y2 = st.number_input("Coordenada Y2 (punto final)", value=0.0)
distancia_offset = st.number_input("Distancia de offset (m)", value=10.0)

if st.button("Calcular"):
    offset_x1, offset_y1, offset_x2, offset_y2, angulo_dms = calcular_offset(x1, y1, x2, y2, distancia_offset)

    st.subheader("Resultados")
    st.markdown("### Coordenadas Base:")
    st.write(f"Punto 1 → X = {x1:.2f}, Y = {y1:.2f}")
    st.write(f"Punto 2 → X = {x2:.2f}, Y = {y2:.2f}")

    st.markdown("### Coordenadas Offset:")
    st.write(f"Punto 1 → X = {offset_x1:.2f}, Y = {offset_y1:.2f}")
    st.write(f"Punto 2 → X = {offset_x2:.2f}, Y = {offset_y2:.2f}")

    st.markdown("### Ángulo de la Línea Base:")
    st.write(f"{angulo_dms}")
