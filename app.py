import streamlit as st
import io
import re
import zipfile
from PyPDF2 import PdfReader, PdfWriter


# --- Extraer DNI ---
def extraer_dni(texto: str) -> str:
    patron = r"\b([XYZ]?\d{7,8}[A-Z])\b"
    m = re.search(patron, texto)
    if m:
        return m.group(1).upper()
    return "SIN_DNI"


# --- Extraer periodo YYYY-MM ---
def extraer_periodo(texto: str) -> str:
    patron = r"\d{1,2}\s+([A-ZÁÉÍÓÚ]{3})\s+(\d{2})"
    m = re.search(patron, texto)
    if not m:
        return "0000-00"

    mes_txt = m.group(1)
    anio = int("20" + m.group(2))

    meses = {
        "ENE": "01", "FEB": "02", "MAR": "03", "ABR": "04",
        "MAY": "05", "JUN": "06", "JUL": "07", "AGO": "08",
        "SEP": "09", "OCT": "10", "NOV": "11", "DIC": "12"
    }

    mes = meses.get(mes_txt, "00")
    return f"{anio}-{mes}"


# --- Streamlit APP ---
st.title("📄 Separador de Nóminas PDF – Arendel Tools")
uploaded_file = st.file_uploader("Sube el PDF con las nóminas", type=["pdf"])

if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    total_pages = len(pdf_reader.pages)
    
    st.info(f"📑 El PDF tiene {total_pages} páginas.")

    if st.button("Generar PDFs individuales y descargar ZIP"):
        
        # Barra de progreso
        progress = st.progress(0)
        status = st.empty()

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for i, page in enumerate(pdf_reader.pages):

                # Mensaje dinámico
                status.text(f"Procesando página {i+1} de {total_pages}…")

                texto = page.extract_text() or ""
                dni = extraer_dni(texto)
                periodo = extraer_periodo(texto)

                filename = f"NOMINA_{periodo}_{dni}.pdf"

                writer = PdfWriter()
                writer.add_page(page)

                pdf_bytes = io.BytesIO()
                writer.write(pdf_bytes)
                pdf_bytes.seek(0)

                zipf.writestr(filename, pdf_bytes.read())

                # Update progress bar
                progress.progress((i + 1) / total_pages)

        zip_buffer.seek(0)

        st.success("✔ Proceso finalizado.")
        st.download_button(
            label="⬇️ Descargar ZIP con nóminas separadas",
            data=zip_buffer,
            file_name="nominas_separadas.zip",
            mime="application/zip"
        )