import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Ma trận đặc tả", layout="wide")

YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")


# ----------------- CORE FUNCTIONS -----------------

def calculate_totals(df):
    df["Tổng số câu"] = df["Biết"] + df["Hiểu"] + df["VD"]
    df["Tổng điểm"] = df["Tổng số câu"] * df["Điểm/câu"]
    return df


def split_matrix(df):
    df_doc = df[df["Kĩ năng"].str.contains("Đọc", case=False, na=False)]
    df_viet = df[df["Kĩ năng"].str.contains("Viết", case=False, na=False)]
    return df_doc, df_viet


def export_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer


def highlight_excel(buffer, yellow_cols):
    wb = load_workbook(buffer)
    ws = wb.active
    header = {cell.value: cell.column for cell in ws[1]}

    for col in yellow_cols:
        if col in header:
            idx = header[col]
            for row in range(1, ws.max_row + 1):
                ws.cell(row=row, column=idx).fill = YELLOW_FILL

    out = BytesIO()
    wb.save(out)
    out.seek(0)
    return out


def export_word(df):
    doc = Document()
    doc.add_heading("MA TRẬN BẢN ĐẶC TẢ", level=1)

    table = doc.add_table(rows=1, cols=len(df.columns))
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = str(col)

    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def export_pdf(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = [Paragraph("MA TRẬN BẢN ĐẶC TẢ", styles["Title"])]

    for _, row in df.iterrows():
        text = " | ".join(str(v) for v in row.values)
        elements.append(Paragraph(text, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ----------------- STREAMLIT UI -----------------

st.title("📊 TẠO MA TRẬN ĐẶC TẢ (Excel / Word / PDF)")

st.markdown("### 1️⃣ Upload dữ liệu")
excel_file = st.file_uploader("Upload file Excel (bắt buộc)", type=["xlsx"])
word_file = st.file_uploader("Upload file Word (tham khảo)", type=["docx"])
pdf_file = st.file_uploader("Upload file PDF (tham khảo)", type=["pdf"])

if excel_file:
    df = pd.read_excel(excel_file)
    df = calculate_totals(df)

    st.success("Đã đọc dữ liệu Excel")

    df_doc, df_viet = split_matrix(df)

    st.markdown("### 2️⃣ Xem trước dữ liệu")
    st.dataframe(df)

    yellow_cols = ["Kĩ năng", "Đơn vị kiến thức", "Hình thức"]

    st.markdown("### 3️⃣ Tải kết quả")

    col1, col2, col3 = st.columns(3)

    with col1:
        excel_out = highlight_excel(export_excel(df), yellow_cols)
        st.download_button("⬇️ Excel", excel_out, "ma_tran.xlsx")

    with col2:
        word_out = export_word(df)
        st.download_button("⬇️ Word", word_out, "ma_tran.docx")

    with col3:
        pdf_out = export_pdf(df)
        st.download_button("⬇️ PDF", pdf_out, "ma_tran.pdf")
