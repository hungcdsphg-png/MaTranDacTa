import streamlit as st
import pandas as pd
from io import BytesIO

from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from PyPDF2 import PdfReader

st.set_page_config(page_title="Tạo ma trận bản đặc tả", layout="wide")

st.title("Tạo ma trận bản đặc tả")
st.write("Upload Excel / Word / PDF (PDF & Word dùng để tham khảo mẫu)")

# ======================
# UPLOAD FILE
# ======================
uploaded_file = st.file_uploader(
    "Tải file ma trận mẫu",
    type=["xlsx", "xls", "docx", "pdf"]
)

if uploaded_file is None:
    st.stop()

file_name = uploaded_file.name.lower()

# ======================
# XỬ LÝ EXCEL (FILE CHÍNH)
# ======================
df = None

if file_name.endswith((".xlsx", ".xls")):
    df = pd.read_excel(uploaded_file)
    st.success("Đã đọc file Excel")
    st.dataframe(df)

# ======================
# WORD – CHỈ ĐỌC THAM KHẢO
# ======================
elif file_name.endswith(".docx"):
    doc = Document(uploaded_file)
    text = "\n".join(p.text for p in doc.paragraphs)
    st.info("Nội dung Word (tham khảo)")
    st.text(text[:3000])

# ======================
# PDF – CHỈ ĐỌC THAM KHẢO
# ======================
elif file_name.endswith(".pdf"):
    reader = PdfReader(uploaded_file)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    st.info("Nội dung PDF (tham khảo)")
    st.text(text[:3000])

# ======================
# NẾU CÓ EXCEL → XỬ LÝ
# ======================
if df is not None:
    required_cols = {"Biết", "Hiểu", "VD", "Điểm/câu"}

    if not required_cols.issubset(df.columns):
        st.error("File Excel thiếu cột: Biết, Hiểu, VD, Điểm/câu")
        st.stop()

    df["Tổng số câu"] = df["Biết"] + df["Hiểu"] + df["VD"]
    df["Tổng điểm"] = df["Tổng số câu"] * df["Điểm/câu"]

    st.subheader("Ma trận sau xử lý")
    st.dataframe(df)

    # ======================
    # XUẤT EXCEL
    # ======================
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)

    st.download_button(
        "Tải Excel",
        data=excel_buffer.getvalue(),
        file_name="ma_tran_dac_ta.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ======================
    # XUẤT WORD
    # ======================
    doc = Document()
    doc.add_heading("Ma trận bản đặc tả", level=1)

    table = doc.add_table(rows=1, cols=len(df.columns))
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col

    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)

    word_buffer = BytesIO()
    doc.save(word_buffer)

    st.download_button(
        "Tải Word",
        data=word_buffer.getvalue(),
        file_name="ma_tran_dac_ta.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # ======================
    # XUẤT PDF
    # ======================
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer)
    styles = getSampleStyleSheet()

    content = [Paragraph("Ma trận bản đặc tả", styles["Title"])]

    for col in df.columns:
        content.append(Paragraph(col, styles["Normal"]))

    pdf.build(content)

    st.download_button(
        "Tải PDF",
        data=pdf_buffer.getvalue(),
        file_name="ma_tran_dac_ta.pdf",
        mime="application/pdf"
    )
