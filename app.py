import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from docx import Document
import pdfplumber

# =========================
# CẤU HÌNH
# =========================
st.set_page_config(page_title="Tạo ma trận đặc tả", layout="wide")

YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

# =========================
# HÀM NHẬN DIỆN FILE
# =========================
def get_file_type(file):
    if file.name.endswith(".xlsx"):
        return "excel"
    if file.name.endswith(".docx"):
        return "word"
    if file.name.endswith(".pdf"):
        return "pdf"
    return None

# =========================
# HÀM ĐỌC FILE
# =========================
def read_excel(file):
    return pd.read_excel(file)

def read_word(file):
    doc = Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text

def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# =========================
# TÍNH TỔNG
# =========================
def calculate_totals(df):
    df["Tổng số câu"] = df["Biết"] + df["Hiểu"] + df["VD"]
    df["Tổng điểm"] = df["Tổng số câu"] * df["Điểm/câu"]
    return df

# =========================
# TÁCH ĐỌC / VIẾT
# =========================
def split_matrix(df):
    doc = df[df["Kĩ năng"].str.contains("Đọc", case=False, na=False)]
    viet = df[df["Kĩ năng"].str.contains("Viết", case=False, na=False)]
    return doc, viet

# =========================
# TÔ CỘT VÀNG
# =========================
def highlight_excel(file_bytes, yellow_cols):
    wb = load_workbook(file_bytes)
    ws = wb.active
    headers = {cell.value: cell.column for cell in ws[1]}

    for col in yellow_cols:
        if col in headers:
            idx = headers[col]
            for r in range(1, ws.max_row + 1):
                ws.cell(row=r, column=idx).fill = YELLOW_FILL

    output = BytesIO()
    wb.save(output)
    return output.getvalue()

# =========================
# GIAO DIỆN STREAMLIT
# =========================
st.title("📊 TẠO MA TRẬN ĐẶC TẢ ")

st.markdown("### 1️⃣ Upload dữ liệu (bắt buộc)")

uploaded_file = st.file_uploader(
    "Upload **1 trong 3 loại file: Excel / Word / PDF**",
    type=["xlsx", "docx", "pdf"],
    accept_multiple_files=False
)

# =========================
# KIỂM TRA BẮT BUỘC UPLOAD
# =========================
if uploaded_file is None:
    st.warning("⚠️ Bạn phải upload ít nhất **1 file (Excel / Word / PDF)** để tiếp tục.")
    st.stop()

# =========================
# XỬ LÝ FILE
# =========================
file_type = get_file_type(uploaded_file)

st.success(f"✅ Đã nhận file: {uploaded_file.name}")

# =========================
# TRƯỜNG HỢP EXCEL (CHÍNH)
# =========================
if file_type == "excel":
    st.markdown("### 2️⃣ Xử lý dữ liệu từ Excel")

    df = read_excel(uploaded_file)
    st.dataframe(df, use_container_width=True)

    required_cols = {"Kĩ năng", "Biết", "Hiểu", "VD", "Điểm/câu"}
    if not required_cols.issubset(df.columns):
        st.error("❌ File Excel thiếu cột bắt buộc")
        st.stop()

    df = calculate_totals(df)
    df_doc, df_viet = split_matrix(df)

    # Xuất Excel
    output_all = BytesIO()
    df.to_excel(output_all, index=False)

    output_doc = BytesIO()
    df_doc.to_excel(output_doc, index=False)

    output_viet = BytesIO()
    df_viet.to_excel(output_viet, index=False)

    # Tô cột vàng
    yellow_cols = ["Kĩ năng", "Đơn vị kiến thức", "Hình thức"]
    final_all = highlight_excel(BytesIO(output_all.getvalue()), yellow_cols)

    st.markdown("### 3️⃣ Tải kết quả")

    st.download_button(
        "⬇️ Tải ma trận tổng (Excel)",
        data=final_all,
        file_name="ma_tran_tong_hop.xlsx"
    )

# =========================
# WORD / PDF CHỈ THAM KHẢO MẪU
# =========================
else:
    st.info("📘 File Word / PDF chỉ dùng để **tham khảo mẫu**")
    content = read_word(uploaded_file) if file_type == "word" else read_pdf(uploaded_file)
    st.text_area("Nội dung trích xuất", content[:3000], height=300)
