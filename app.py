import streamlit as st
import pandas as pd
from io import BytesIO

from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


st.set_page_config(page_title="Ma trận đặc tả", layout="wide")
st.title("Ứng dụng tạo Ma trận bản đặc tả")

# ======================
# UPLOAD FILES
# ======================
st.header("1. Upload dữ liệu")

excel_file = st.file_uploader("Upload file Excel (bắt buộc)", type=["xlsx"])
word_file = st.file_uploader("Upload file Word (tham khảo)", type=["docx"])
pdf_file = st.file_uploader("Upload file PDF (tham khảo)", type=["pdf"])

if excel_file is None:
    st.warning("Vui lòng upload file Excel")
    st.stop()

# ======================
# READ EXCEL
# ======================
df = pd.read_excel(excel_file)

required_cols = {"Biết", "Hiểu", "VD", "Điểm/câu", "Kĩ năng"}
if not required_cols.issubset(df.columns):
    st.error("File Excel thiếu cột bắt buộc")
    st.stop()

# ======================
# PROCESS
# ======================
df["Tổng số câu"] = df["Biết"] + df["Hiểu"] + df["VD"]
df["Tổng điểm"] = df["Tổng số câu"] * df["Điểm/câu"]

df_doc = df[df["Kĩ năng"].str.contains("Đọc", case=False, na=False)]
df_viet = df[df["Kĩ năng"].str.contains("Viết", case=False, na=False)]

st.success("Xử lý dữ liệu thành công")

st.subheader("Xem trước dữ liệu")
st.dataframe(df)

# ======================
# EXPORT EXCEL
# ======================
def export_excel(dataframe):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer

# ======================
# EXPORT WORD
# ======================
def export_word(dataframe):
    doc = Document()
    doc.add_heading("MA TRẬN BẢN ĐẶC TẢ", level=1)

    table = doc.add_table(rows=1, cols=len(dataframe.columns))
    for i, col in enumerate(dataframe.columns):
        table.rows[0].cells[i].text = col

    for _, row in dataframe.iterrows():
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ======================
# EXPORT PDF
# ======================
def export_pdf(dataframe):
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("MA TRẬN BẢN ĐẶC TẢ", styles["Title"]))

    for _, row in dataframe.iterrows():
        text = " | ".join([str(v) for v in row])
        content.append(Paragraph(text, styles["Normal"]))

    pdf = SimpleDocTemplate(buffer)
    pdf.build(content)

    buffer.seek(0)
    return buffer

# ======================
# DOWNLOAD
# ======================
st.header("2. Tải kết quả")

col1, col2, col3 = st.columns(3)

with col1:
    st.download_button(
        "Tải Excel",
        export_excel(df),
        file_name="ma_tran_dac_ta.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    st.download_button(
        "Tải Word",
        export_word(df),
        file_name="ma_tran_dac_ta.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

with col3:
    st.download_button(
        "Tải PDF",
        export_pdf(df),
        file_name="ma_tran_dac_ta.pdf",
        mime="application/pdf"
    )
