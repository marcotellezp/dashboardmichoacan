
import streamlit as st
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Obras por Municipio", layout="wide")

# Logo y título
st.image("logo-mich-mejor.png", width=250)
st.title("Dashboard de Obras por Municipio - Michoacán es Mejor")

# Cargar datos desde Google Sheets
sheet_url = "https://docs.google.com/spreadsheets/d/1fHtIMMQJd6LkDuDgFJGacxe4FTJL8r6Egy4CWeyu0y0/export?format=csv&id=1fHtIMMQJd6LkDuDgFJGacxe4FTJL8r6Egy4CWeyu0y0"
df = pd.read_csv(sheet_url)
df.columns = df.columns.str.strip()

# Selector de municipio
municipios = df['Municipio'].dropna().unique()
municipio = st.selectbox("Selecciona un municipio", sorted(municipios))
df_mun = df[df['Municipio'] == municipio]

# Buscar columna de inversión
col_monto_candidates = [col for col in df.columns if "monto" in col.lower()]
if col_monto_candidates:
    col_monto = col_monto_candidates[0]
    try:
        df_mun[col_monto] = (
            df_mun[col_monto]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
            .replace("", "0")
            .astype(float)
        )
        total_inversion = df_mun[col_monto].sum()
    except Exception as e:
        st.error(f"No se pudo calcular la inversión: {e}")
        total_inversion = 0
else:
    st.warning("⚠️ No se encontró ninguna columna que contenga 'monto'. Revisa tu hoja de cálculo.")
    total_inversion = 0

# Desglose por programa
desglose_text = []
if 'Programa' in df_mun.columns:
    desglose = df_mun.groupby('Programa')[col_monto].agg(['count', 'sum']).reset_index()
    for _, row in desglose.iterrows():
        programa = row['Programa']
        obras = int(row['count'])
        monto = row['sum']
        desglose_text.append(f"{programa}: {obras} obra{'s' if obras != 1 else ''} ${monto:,.2f}")

# Mostrar resumen en app
st.subheader(f"Resumen de {municipio}")
st.write(f"**Número de obras:** {df_mun.shape[0]}")
st.write(f"**Total de inversión:** ${total_inversion:,.2f}")
st.markdown("**Desglose por programa:**")
for linea in desglose_text:
    st.write(linea)

# Mostrar obras en pantalla
st.subheader(f"Obras en el municipio de {municipio}")
for i, row in df_mun.iterrows():
    monto_individual = row[col_monto] if col_monto in row else 0
    st.markdown(f"""
**Nombre del Plantel:** {row['Nombre del Plantel']}  
**CCT:** {row['CCT']}  
**Localidad:** {row['Localidad']}  
**Programa:** {row['Programa']}  
**Inversión estimada:** ${monto_individual:,.2f}  
**Descripción de la obra:** {row['Descripción de la obra']}  
**Tipo:** {row['Tipo']}  
**Nivel:** {row['Nivel']}  
**Modalidad:** {row['Modalidad']}  
**Matrícula:** {row['Matrícula']} alumnos  
**Avance físico:** {row['Avance Fisico']}  
**Observaciones:** {row['Observaciones']}  
**Latitud / Longitud:** {row['Latitud']} / {row['Longitud']}
---
""", unsafe_allow_html=True)
