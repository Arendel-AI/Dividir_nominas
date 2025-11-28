import streamlit as st
import io
import re
import zipfile
import unicodedata
from PyPDF2 import PdfReader, PdfWriter

# --- Función para limpiar nombres de archivo ---
def limpiar_nombre(nombre: str) -> str:
    nombre = nombre.strip().upper()
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
    nombre = re.sub(r'[^A-Z0-9 _-]', '', nombre)
    nombre = nombre.replace(" ", "_")
    return nombre

# --- Función para extraer nombre del texto ---
def extraer_nombre(texto: str) -> str:
    # Ejemplo: "TRABAJADOR/A CATEGORIA NºMATRIC ... \nJUAN PEREZ GOMEZ PERSONAL ..."
    patron = r"TRABAJADOR/A.*?\n\s*([A-ZÁÉÍÓÚÑ ]{5,})\s+PERSONAL"
    m = re.search(patron, texto, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None

# --- App Streamlit ---
st.set_page_config(page_title="Separador de Nóminas PDF", page_icon="📄", layout="centered")

st.title("Separador de Nóminas PDF – Arendel Tools")
st.write("Sube un PDF con múltiples nóminas y esta herramienta generará un PDF por trabajador.")

uploaded_file = st.file_uploader("Sube el PDF con las nóminas", type=["pdf"])

if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    st.info(f"El PDF tiene {len(pdf_reader.pages)} páginas.")
    progreso = st.progress(0)
    trabajadores = {}
    
    for i, page in enumerate(pdf_reader.pages):
        texto = page.extract_text() or ""
        nombre = extraer_nombre(texto)
        if not nombre:
            nombre = f"Pagina_{i+1}"
        nombre_limpio = limpiar_nombre(nombre)
        
        # Añadir página al grupo del trabajador
        if nombre_limpio not in trabajadores:
            trabajadores[nombre_limpio] = []
        trabajadores[nombre_limpio].append(i)
        progreso.progress((i+1)/len(pdf_reader.pages))

    st.success(f"Se detectaron {len(trabajadores)} trabajadores únicos.")

    if st.button("Generar PDFs individuales y descargar ZIP"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for nombre, paginas in trabajadores.items():
                writer = PdfWriter()
                for p in paginas:
                    writer.add_page(pdf_reader.pages[p])
                pdf_bytes = io.BytesIO()
                writer.write(pdf_bytes)
                pdf_bytes.seek(0)
                zipf.writestr(f"{nombre}.pdf", pdf_bytes.read())
        zip_buffer.seek(0)
        st.download_button(
            label="Descargar ZIP con nóminas separadas",
            data=zip_buffer,
            file_name="nominas_separadas.zip",
            mime="application/zip"
        )