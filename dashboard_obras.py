
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

# Normalizar nombres de columna
df.columns = df.columns.str.strip()

# Mostrar columnas exactas para depuración
st.write("Columnas exactas:", [repr(col) for col in df.columns])

# Selector de municipio
municipios = df['Municipio'].dropna().unique()
municipio = st.selectbox("Selecciona un municipio", sorted(municipios))
df_mun = df[df['Municipio'] == municipio]

# Buscar automáticamente la columna de inversión
col_monto = [col for col in df.columns if "monto" in col.lower()][0]
df_mun[col_monto] = pd.to_numeric(df_mun[col_monto], errors='coerce')
total_inversion = df_mun[col_monto].sum()

# Resumen
num_obras = df_mun.shape[0]
st.subheader(f"Resumen de {municipio}")
st.write(f"**Número de obras:** {num_obras}")
st.write(f"**Total de inversión:** ${total_inversion:,.2f}")

# Fichas por obra
st.subheader("Obras en el municipio")
for i, row in df_mun.iterrows():
    color = "#F8F8F8" if i % 2 == 0 else "#EDE7F6"
    with st.container():
        st.markdown(f'''
        <div style='background-color:{color}; padding:15px; border-radius:10px;'>
        <b>Nombre del plantel:</b> {row['Nombre del Plantel']}<br>
        <b>CCT:</b> {row['CCT']}<br>
        <b>Localidad:</b> {row['Localidad']}<br>
        <b>Programa:</b> {row['Programa']}<br>
        <b>Descripción de la obra:</b> {row['Descripción de la obra']}<br>
        <b>Tipo:</b> {row['Tipo']}<br>
        <b>Nivel:</b> {row['Nivel']}<br>
        <b>Modalidad:</b> {row['Modalidad']}<br>
        <b>Matrícula:</b> {row['Matrícula']} alumnos<br>
        <b>Avance físico:</b> {row['Avance Fisico']}<br>
        <b>Observaciones:</b> {row['Observaciones']}<br>
        <b>Latitud / Longitud:</b> {row['Latitud']} / {row['Longitud']}
        </div><br>
        ''', unsafe_allow_html=True)

# PDF generator
def generar_pdf(data, municipio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, f"Reporte de obras - {municipio}", ln=True, align='C')
    pdf.set_font("Arial", "", 10)

    for i, row in data.iterrows():
        pdf.multi_cell(0, 10, f'''
Nombre del Plantel: {row['Nombre del Plantel']}
CCT: {row['CCT']}
Localidad: {row['Localidad']}
Programa: {row['Programa']}
Descripción de la obra: {row['Descripción de la obra']}
Tipo: {row['Tipo']}
Nivel: {row['Nivel']}
Modalidad: {row['Modalidad']}
Matrícula: {row['Matrícula']} alumnos
Avance físico: {row['Avance Fisico']}
Observaciones: {row['Observaciones']}
Latitud: {row['Latitud']}
Longitud: {row['Longitud']}
-----------------------------
''')
    return pdf.output(dest='S').encode('latin1')

if st.button("📥 Descargar PDF"):
    pdf_bytes = generar_pdf(df_mun, municipio)
    st.download_button("Descargar reporte", data=pdf_bytes, file_name=f"reporte_{municipio}.pdf", mime="application/pdf")
