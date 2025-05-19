import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns

import matplotlib.pyplot as plt

st.set_page_config(page_title="Exceso de Masa", layout="centered")
st.title("🌍 Calculadora de Exceso de Masa Gravimétrica")

# Subida de archivo
uploaded_file = st.file_uploader("📤 Sube el archivo Excel con la matriz de anomalías de Bouguer", type=["xlsx"])

# Parámetros de espaciado
dx = st.number_input("🔧 Valor de dx (espaciado horizontal)", value=0.25168)
dy = st.number_input("🔧 Valor de dy (espaciado vertical)", value=0.248899)

# Métodos numéricos
def simpson(y, h):
    n = len(y)
    if n < 2:
        return 0.0
    if n % 2 == 1:
        s = y[0] + y[-1] + 4 * sum(y[1:-1:2]) + 2 * sum(y[2:-2:2])
        return s * h / 3.0
    else:
        area = simpson(y[:-3], h)
        area1 = 3 * h / 8 * (y[-4] + 3*y[-3] + 3*y[-2] + y[-1])
        return area + area1

def trapezoidal(y, h):
    return (y[0] + y[-1]) / 2.0 * h + sum(y[1:-1]) * h

# Lógica principal
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        ab = np.flipud(df.to_numpy())  # Inversión vertical como en Fortran
        m, n = ab.shape

        st.subheader("📊 Vista previa de la matriz original (sin invertir)")
        st.dataframe(df)

        st.subheader("📉 Matriz invertida usada en los cálculos")
        st.dataframe(ab)

        st.write(f"📐 Dimensiones: {m} filas × {n} columnas")

        # Visualización como mapa de calor
        st.subheader("🌡️ Mapa de calor de anomalías de Bouguer")
        fig, ax = plt.subplots()
        sns.heatmap(ab, cmap="coolwarm", ax=ax, cbar_kws={"label": "Microgales"})
        st.pyplot(fig)

        # Cálculos
        sum1 = np.array([simpson(ab[:, j], dy) for j in range(n)])
        sum2 = np.array([trapezoidal(ab[:, j], dy) for j in range(n)])

        area_simpson = simpson(sum1, dx)
        area_trapezoidal = trapezoidal(sum2, dx)

        factor = 1.0 / (8.0 * np.arctan(1.0) * 0.006672)
        cc1 = factor * area_simpson
        cc2 = factor * area_trapezoidal

        st.success(f"💡 Exceso de Masa (Simpson): **{cc1:.5e} Toneladas**")
        st.success(f"💡 Exceso de Masa (Trapecio): **{cc2:.5e} Toneladas**")

        # Descarga del resultado
        resultado = f"EXCESO DE MASA: (SIMPSON)={cc1:.5e} Ton  TRAPE={cc2:.5e} Ton\n"
        st.download_button("📥 Descargar resultado", resultado, file_name="resultado.txt")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
