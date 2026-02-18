import streamlit as st
import pandas as pd
import os
from datetime import date
from fpdf import FPDF

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Agenda Docente Pro", layout="wide")

def aplicar_estilo():
    st.markdown("""
        <style>
        .main { background-color: #f5f7f9; }
        .stButton>button { background-color: #4CAF50; color: white; border-radius: 8px; width: 100%; }
        .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
        </style>
        """, unsafe_allow_html=True)

aplicar_estilo()

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo):
        return pd.read_csv(archivo)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_datos(df, archivo):
    df.to_csv(archivo, index=False)

def dar_color_nota(valor):
    colores = {"S": "#2ecc71", "MB": "#a2d149", "B": "#f1c40f", "R": "#e74c3c"}
    color = colores.get(valor, "")
    return f'background-color: {color}; color: {"white" if valor in ["S","R"] else "black"}'

# --- INICIALIZACIÓN ---
df_alumnos = cargar_datos("alumnos.csv", ["ID", "Nombre", "Apellido"])
df_asistencia = cargar_datos("asistencia.csv", ["Fecha", "Alumno", "Estado"])
df_seguimiento = cargar_datos("seguimiento.csv", ["Fecha", "Alumno", "Materia", "Avance", "Observaciones"])
df_notas = cargar_datos("notas.csv", ["Alumno", "Trimestre", "Materia", "Nota"])

# --- INTERFAZ ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=100)
menu = ["Alumnos", "Asistencia", "Seguimiento Semanal", "Calificaciones", "Reporte Final"]
choice = st.sidebar.selectbox("MENÚ", menu)

if choice == "Alumnos":
    st.header("👥 Registro de Alumnos")
    n = st.text_input("Nombre")
    a = st.text_input("Apellido")
    if st.button("Registrar"):
        nuevo = pd.DataFrame({"ID": [len(df_alumnos)+1], "Nombre": [n], "Apellido": [a]})
        df_alumnos = pd.concat([df_alumnos, nuevo], ignore_index=True)
        guardar_datos(df_alumnos, "alumnos.csv")
        st.success("Registrado")
    st.table(df_alumnos)

elif choice == "Asistencia":
    st.header("📅 Asistencia")
    fecha = st.date_input("Fecha", date.today())
    lista = (df_alumnos['Nombre'] + " " + df_alumnos['Apellido']).tolist()
    with st.form("asist"):
        cambios = []
        for al in lista:
            p = st.checkbox(al, value=True)
            cambios.append({"Fecha": fecha, "Alumno": al, "Estado": "P" if p else "A"})
        if st.form_submit_button("Guardar"):
            df_asistencia = pd.concat([df_asistencia, pd.DataFrame(cambios)], ignore_index=True)
            guardar_datos(df_asistencia, "asistencia.csv")
            st.success("Guardado")

elif choice == "Seguimiento Semanal":
    st.header("📝 Avances MAT/PDL")
    lista = (df_alumnos['Nombre'] + " " + df_alumnos['Apellido']).tolist()
    al = st.selectbox("Alumno", lista)
    mat = st.selectbox("Materia", ["Matemática", "Prácticas del Lenguaje"])
    av = st.radio("Avance", ["✅ Logrado", "🔄 En proceso", "⚠️ Sin cambios"])
    obs = st.text_area("Notas")
    if st.button("Guardar Seguimiento"):
        nue = pd.DataFrame({"Fecha":[date.today()], "Alumno":[al], "Materia":[mat], "Avance":[av], "Observaciones":[obs]})
        df_seguimiento = pd.concat([df_seguimiento, nue], ignore_index=True)
        guardar_datos(df_seguimiento, "seguimiento.csv")
        st.success("Guardado")

elif choice == "Calificaciones":
    st.header("📊 Notas Conceptuales")
    lista = (df_alumnos['Nombre'] + " " + df_alumnos['Apellido']).tolist()
    col1, col2, col3 = st.columns(3)
    al = col1.selectbox("Alumno", lista)
    tri = col2.selectbox("Trimestre", ["1°", "2°", "3°"])
    not_c = col3.selectbox("Nota", ["S", "MB", "B", "R"])
    area = st.selectbox("Área", ["Matemática", "Prácticas del Lenguaje", "Naturales", "Sociales", "Ed. Física", "Artística"])
    if st.button("Cargar Nota"):
        nue = pd.DataFrame({"Alumno":[al], "Trimestre":[tri], "Materia":[area], "Nota":[not_c]})
        df_notas = pd.concat([df_notas, nue], ignore_index=True)
        guardar_datos(df_notas, "notas.csv")
        st.success("Nota cargada")

elif choice == "Reporte Final":
    st.header("📋 Ficha del Alumno")
    lista = (df_alumnos['Nombre'] + " " + df_alumnos['Apellido']).tolist()
    al_rep = st.selectbox("Seleccionar Alumno", lista)
    
    # Mostrar Notas con colores
    n_al = df_notas[df_notas['Alumno'] == al_rep]
    if not n_al.empty:
        pivot = n_al.pivot(index='Materia', columns='Trimestre', values='Nota')
        st.dataframe(pivot.style.applymap(dar_color_nota))
    
    # Mostrar Seguimiento
    s_al = df_seguimiento[df_seguimiento['Alumno'] == al_rep]
    for _, r in s_al.iterrows():
        st.info(f"{r['Fecha']} - {r['Materia']}: {r['Avance']}\n{r['Observaciones']}")
