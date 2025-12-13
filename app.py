import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


st.set_page_config(page_title="Ma trận đặc tả", layout="wide")

st.title("Ứng dụng tạo Ma trận bản đặc tả")
st.caption("Upload Excel / Word / PDF – Xuất Excel / Word / PDF")

# ======================
# 1. UPLOAD (1 Ô – BẮT BUỘC)
# ======================
uploaded_files = st.file_uploader(
    "Upload file (Excel / Word / PDF)",
    type=["xlsx", "xls", "docx", "pdf"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.warning("⚠️ Bạn phải upload ít nhất 1 file (Excel / Word / PDF)")
    st.stop()

# ======================
# 2. PHÂN LOẠI FILE
# ======================
excel_files = [f for f in uploaded_files if f.name.endswith((".xlsx", ".xls"))]
word_files = [f for f in uploaded_files if f.name.endswith(".docx")]
pdf_files = [f for f in uploaded_files if f.name.endswith(".pdf")]

st.success(
    f"Đã upload: {len(excel_files)} Excel | {len(word_files)} Word | {len(pdf_files)} PDF"
)

# ======================
# 3. XỬ LÝ EXCEL (BẮT BUỘC CÓ ĐỂ TẠO MA TRẬN)
# ======================
if not excel_files:
    st.error("❌ Không có file Excel → Không thể tạo ma trận")
    st.stop()

df = pd.read_excel(excel_files[0])

required_cols = ["Biết", "Hiểu", "VD", "Điểm/câu"]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"❌ File Excel thiếu cột: {', '.join(missing)}")
    st.stop()

# ======================
# 4. XỬ LÝ DỮ LIỆU
# ======================
df["Tổng số câu"] = df["Biết"] + df["Hiểu"] + df["VD"]
df["Tổng điểm"] = df["Tổng số câu"] * df["Điểm/câu"]

st.subheader("Xem trước ma trận")
st.dataframe(df, use_container_width=True)

# ======================
# 5. XUẤT EXCEL
# ======================
def export_excel(dataframe):
    output = BytesIO()
    dataframe.to_excel(output, index=False)
    return output.getvalue()

# ======================
# 6. XUẤT WORD
# ======================
def export_word(dataframe):
    doc = Document()
    doc.add_heading("MA TRẬN BẢN ĐẶC TẢ", level=1)

    table = doc.add_table(rows=1, cols=len(dataframe.columns))
    for i, col in enumerate(dataframe.columns):
        table.rows[0].cells[i].text = col

    for _, row in dataframe.iterrows():
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)

    output = BytesIO()
    doc.save(output)
    return output.getvalue()

# ======================
# 7. XUẤT PDF
# ======================
def export_pdf(dataframe):
    output = BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output)

    elements = [Paragraph("MA TRẬN BẢN ĐẶC TẢ", styles["Title"])]

    for _, row in dataframe.iterrows():
        elements.append(
            Paragraph(" | ".join(map(str, row.values)), styles["Normal"])
        )

    doc.build(elements)
    return output.getvalue()

# ======================
# 8. NÚT TẢI FILE
# ======================
st.subheader("Tải kết quả")

col1, col2, col3 = st.columns(3)

with col1:
    st.download_button(
        "⬇️ Tải Excel",
        export_excel(df),
        file_name="ma_tran_dac_ta.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    st.download_button(
        "⬇️ Tải Word",
        export_word(df),
        file_name="ma_tran_dac_ta.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

with col3:
    st.download_button(
        "⬇️ Tải PDF",
        export_pdf(df),
        file_name="ma_tran_dac_ta.pdf",
        mime="application/pdf"
    )
