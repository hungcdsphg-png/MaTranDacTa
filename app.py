import streamlit as st
import pandas as pd
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
import io

st.set_page_config(page_title="Tạo ma trận bản đặc tả", layout="wide")

st.title("Tạo ma trận bản đặc tả")
st.write("Upload **Excel / Word / PDF** để tạo khung ma trận. Có thể upload thêm file nội dung (Word / PDF / Ảnh) để điền dữ liệu.")

# =============================
# HÀM ĐỌC FILE
# =============================

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

def read_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

# =============================
# UPLOAD FILE MẪU
# =============================

st.header("1. Upload file MẪU (bắt buộc)")

template_file = st.file_uploader(
    "Upload Excel / Word / PDF ma trận mẫu",
    type=["xlsx", "docx", "pdf"],
    accept_multiple_files=False
)

if not template_file:
    st.warning("⚠️ Bạn phải upload **ÍT NHẤT 1 file mẫu** để tiếp tục")
    st.stop()

# =============================
# XỬ LÍ FILE MẪU
# =============================

template_text = ""
template_df = None

if template_file.name.endswith(".xlsx"):
    template_df = read_excel(template_file)
    st.success("Đã đọc file Excel mẫu")
    st.dataframe(template_df)

elif template_file.name.endswith(".docx"):
    template_text = read_word(template_file)
    st.success("Đã đọc file Word mẫu")
    st.text_area("Nội dung Word", template_text, height=200)

elif template_file.name.endswith(".pdf"):
    template_text = read_pdf(template_file)
    st.success("Đã đọc file PDF mẫu")
    st.text_area("Nội dung PDF", template_text, height=200)

# =============================
# TẠO KHUNG MA TRẬN (NẾU KHÔNG PHẢI EXCEL)
# =============================

st.header("2. Tạo khung ma trận")

if template_df is None:
    st.info("Không phải Excel → tạo khung ma trận mặc định")

    template_df = pd.DataFrame(columns=[
        "TT", "Kĩ năng", "Đơn vị kiến thức",
        "Biết", "Hiểu", "Vận dụng",
        "Hình thức", "Số câu", "Số điểm"
    ])

st.dataframe(template_df)

# =============================
# UPLOAD FILE NỘI DUNG
# =============================

st.header("3. Upload file NỘI DUNG (không bắt buộc)")

content_files = st.file_uploader(
    "Upload Word / PDF / Ảnh để AI điền nội dung",
    type=["docx", "pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)

content_text = ""

if content_files:
    for file in content_files:
        if file.name.endswith(".docx"):
            content_text += read_word(file)
        elif file.name.endswith(".pdf"):
            content_text += read_pdf(file)
        else:
            content_text += read_image(file)

    st.success("Đã đọc nội dung từ file upload")
    st.text_area("Nội dung tổng hợp", content_text, height=200)

# =============================
# GIẢ LẬP AI ĐIỀN MA TRẬN
# =============================

st.header("4. Tạo ma trận bản đặc tả")

if st.button("Tạo ma trận"):
    df = template_df.copy()

    if "Kĩ năng" in df.columns:
        df.loc[len(df)] = [
            1,
            "Đọc hiểu",
            "Văn bản văn học",
            2,
            1,
            1,
            "Trắc nghiệm",
            4,
            2.5
        ]

    st.success("Đã tạo ma trận")
    st.dataframe(df)

    # DOWNLOAD
    output = io.BytesIO()
    df.to_excel(output, index=False)
    st.download_button(
        "Tải ma trận Excel",
        data=output.getvalue(),
        file_name="ma_tran_ban_dac_ta.xlsx"
    )
