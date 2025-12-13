import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract


st.set_page_config(page_title="Ma trận đặc tả AI", layout="wide")


# -------------------------
# UTILITIES
# -------------------------

def read_excel(file):
    return pd.read_excel(file)


def read_word(file):
    doc = Document(file)
    text = []
    for p in doc.paragraphs:
        if p.text.strip():
            text.append(p.text.strip())
    return "\n".join(text)


def read_pdf(file):
    reader = PdfReader(file)
    text = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text.append(t)
    return "\n".join(text)


def read_image(file):
    img = Image.open(file)
    return pytesseract.image_to_string(img, lang="vie+eng")


def extract_text(file, file_type):
    if file_type == "excel":
        df = read_excel(file)
        return df, ""
    if file_type == "word":
        return None, read_word(file)
    if file_type == "pdf":
        return None, read_pdf(file)
    if file_type == "image":
        return None, read_image(file)


# -------------------------
# AI FILL LEVEL 1
# -------------------------

def ai_fill_level_1(df, content_text):
    df = df.copy()
    df["Mức độ đánh giá"] = content_text[:300]
    return df


# -------------------------
# AI FILL LEVEL 2 (BIẾT – HIỂU – VD)
# -------------------------

def ai_fill_level_2(df):
    df = df.copy()
    df["Biết"] = 1
    df["Hiểu"] = 1
    df["VD"] = 1
    df["Tổng số câu"] = df["Biết"] + df["Hiểu"] + df["VD"]
    df["Tổng điểm"] = df["Tổng số câu"] * 0.25
    return df


# -------------------------
# STREAMLIT UI
# -------------------------

st.title("AI tạo ma trận đặc tả")

st.header("1. Upload file MẪU (Word / Excel / PDF)")

sample_file = st.file_uploader(
    "Bắt buộc chọn 1 file",
    type=["xlsx", "docx", "pdf"]
)

st.header("2. Upload file NỘI DUNG (Word / PDF / Ảnh – không bắt buộc)")

content_file = st.file_uploader(
    "File để AI điền nội dung",
    type=["docx", "pdf", "png", "jpg", "jpeg"]
)

if sample_file:
    try:
        file_name = sample_file.name.lower()

        if file_name.endswith(".xlsx"):
            df_sample = read_excel(sample_file)
            content_text = ""

        elif file_name.endswith(".docx"):
            df_sample = pd.DataFrame({
                "Kĩ năng": ["Đọc hiểu", "Viết"],
                "Đơn vị kiến thức": ["Văn bản", "Tập làm văn"]
            })
            content_text = read_word(sample_file)

        elif file_name.endswith(".pdf"):
            df_sample = pd.DataFrame({
                "Kĩ năng": ["Đọc hiểu", "Viết"],
                "Đơn vị kiến thức": ["Văn bản", "Tập làm văn"]
            })
            content_text = read_pdf(sample_file)

        else:
            st.error("File mẫu không hợp lệ")
            st.stop()

        if content_file:
            name = content_file.name.lower()
            if name.endswith(".docx"):
                content_text += "\n" + read_word(content_file)
            elif name.endswith(".pdf"):
                content_text += "\n" + read_pdf(content_file)
            else:
                content_text += "\n" + read_image(content_file)

        st.subheader("Ma trận gốc")
        st.dataframe(df_sample)

        if st.button("AI điền nội dung – MỨC 1"):
            df_lv1 = ai_fill_level_1(df_sample, content_text)
            st.subheader("Kết quả MỨC 1")
            st.dataframe(df_lv1)

        if st.button("AI điền nội dung – MỨC 2 (Biết – Hiểu – VD)"):
            df_lv2 = ai_fill_level_2(df_sample)
            st.subheader("Kết quả MỨC 2")
            st.dataframe(df_lv2)

            buffer = BytesIO()
            df_lv2.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                "Tải ma trận Excel",
                buffer,
                file_name="ma_tran_dac_ta.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error("Có lỗi xảy ra")
        st.code(str(e))
