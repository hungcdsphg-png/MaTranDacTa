import streamlit as st
import pandas as pd
from io import BytesIO

from openpyxl import load_workbook
from openpyxl.styles import PatternFill

from docx import Document
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


# =========================
# CẤU HÌNH
# =========================
st.set_page_config(page_title="Ma trận đặc tả", layout="wide")

YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")


# =========================
# HÀM TẠO KHUNG MA TRẬN CHUẨN
# =========================
def create_matrix_frame(df_raw):
    required_cols = ["TT", "Kĩ năng", "Đơn vị kiến thức", "Hình thức", "Biết", "Hiểu", "VD", "Điểm/câu"]
    for col in required_cols:
        if col not in df_raw.columns:
            st.error(f"Thiếu cột bắt buộc: {col}")
            st.stop()

    df = df_raw.copy()

    df["Tổng số câu"] = df["Biết"] + df["Hiểu"] + df["VD"]
    df["Tổng điểm"] = df["Tổng số câu"] * df["Điểm/câu"]

    matrix_cols = [
        "TT", "Kĩ năng", "Đơn vị kiến thức", "Hình thức",
        "Biết", "Hiểu", "VD",
        "Tổng số câu", "Tổng điểm"
    ]

    return df[matrix_cols]


# =========================
# TÔ CỘT VÀNG (EXCEL)
# =========================
def highlight_excel(file_bytes):
    wb = load_workbook(file_bytes)
    ws = wb.active

    yellow_cols = ["Kĩ năng", "Đơn vị kiến thức", "Hình thức"]
    header = {cell.value: cell.column for cell in ws[1]}

    for col in yellow_cols:
        if col in header:
            idx = header[col]
            for row in range(1, ws.max_row + 1):
                ws.cell(row=row, column=idx).fill = YELLOW_FILL

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# =========================
# XUẤT WORD
# =========================
def export_word(df):
    doc = Document()
    doc.add_heading("MA TRẬN BẢN ĐẶC TẢ", level=1)

    table = doc.add_table(rows=1, cols=len(df.columns))
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col

    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output


# =========================
# XUẤT PDF
# =========================
def export_pdf(df):
    output = BytesIO()
    pdf = SimpleDocTemplate(output, pagesize=A4)

    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))

    pdf.build([table])
    output.seek(0)
    return output


# =========================
# GIAO DIỆN
# =========================
st.title("📊 TẠO MA TRẬN BẢN ĐẶC TẢ")

st.markdown("### 1️⃣ Upload dữ liệu (bắt buộc ít nhất 1 file)")

uploaded_files = st.file_uploader(
    "Upload Excel / Word / PDF",
    type=["xlsx", "xls", "docx", "pdf"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.warning("⚠️ Bạn phải upload ít nhất 1 file")
    st.stop()

excel_file = None

for f in uploaded_files:
    if f.name.endswith((".xlsx", ".xls")):
        excel_file = f

if excel_file is None:
    st.error("❌ Bắt buộc phải có FILE EXCEL để xử lý dữ liệu")
    st.stop()


# =========================
# XỬ LÝ EXCEL
# =========================
df_raw = pd.read_excel(excel_file)
df_matrix = create_matrix_frame(df_raw)

st.success("✅ Đã tạo ma trận theo file mẫu")
st.dataframe(df_matrix, use_container_width=True)


# =========================
# XUẤT FILE
# =========================
st.markdown("### 2️⃣ Tải kết quả")

# Excel
excel_out = BytesIO()
df_matrix.to_excel(excel_out, index=False)
excel_out.seek(0)
excel_out = highlight_excel(excel_out)

st.download_button(
    "⬇️ Tải Excel",
    excel_out,
    file_name="ma_tran_dac_ta.xlsx"
)

# Word
word_out = export_word(df_matrix)
st.download_button(
    "⬇️ Tải Word",
    word_out,
    file_name="ma_tran_dac_ta.docx"
)

# PDF
pdf_out = export_pdf(df_matrix)
st.download_button(
    "⬇️ Tải PDF",
    pdf_out,
    file_name="ma_tran_dac_ta.pdf"
)
