import streamlit as st
import pandas as pd
import io

from docx import Document
import pdfplumber
from PIL import Image
import pytesseract

st.set_page_config(page_title="Tạo ma trận bản đặc tả", layout="wide")

st.title("Tạo ma trận bản đặc tả")
st.write("Upload **1 file mẫu** (Excel / Word / PDF) và **1 file nội dung** để AI điền ma trận")

# =========================
# HÀM ĐỌC FILE MẪU
# =========================
def read_template(file):
    name = file.name.lower()

    if name.endswith(".xlsx"):
        return pd.read_excel(file)

    if name.endswith(".docx"):
        doc = Document(file)
        rows = []
        for table in doc.tables:
            for row in table.rows:
                rows.append([cell.text for cell in row.cells])
        return pd.DataFrame(rows)

    if name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return pd.DataFrame({"Nội dung": text.split("\n")})

    return None


# =========================
# HÀM ĐỌC FILE NỘI DUNG
# =========================
def read_content(file):
    name = file.name.lower()

    if name.endswith(".docx"):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

    if name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    if name.endswith((".png", ".jpg", ".jpeg")):
        img = Image.open(file)
        return pytesseract.image_to_string(img, lang="vie")

    return ""


# =========================
# UPLOAD FILE
# =========================
st.subheader("1️⃣ Upload file MA TRẬN MẪU (bắt buộc)")
template_file = st.file_uploader(
    "Excel / Word / PDF",
    type=["xlsx", "docx", "pdf"],
    key="template"
)

st.subheader("2️⃣ Upload file NỘI DUNG để điền (bắt buộc)")
content_file = st.file_uploader(
    "Word / PDF / Ảnh",
    type=["docx", "pdf", "png", "jpg", "jpeg"],
    key="content"
)

# =========================
# XỬ LÝ KHI ĐÃ CÓ FILE
# =========================
if template_file and content_file:

    st.success("Đã nhận đủ file – bắt đầu xử lý")

    # ---- Đọc file mẫu
    df_template = read_template(template_file)

    if df_template is None:
        st.error("Không đọc được file mẫu")
        st.stop()

    st.subheader("Khung ma trận từ file mẫu")
    st.dataframe(df_template, use_container_width=True)

    # ---- Đọc file nội dung
    raw_content = read_content(content_file)

    if not raw_content.strip():
        st.error("Không đọc được nội dung file")
        st.stop()

    st.subheader("Nội dung trích xuất (AI mức 1)")
    st.text_area("Raw content", raw_content[:3000], height=200)

    # =========================
    # AI MỨC 2 – ĐIỀN NỘI DUNG
    # (DEMO LOGIC – có thể thay bằng LLM)
    # =========================
    filled_df = df_template.copy()

    for col in filled_df.columns:
        if filled_df[col].isna().all():
            filled_df[col] = "AI gợi ý từ nội dung"

    st.subheader("Ma trận sau khi AI điền (mức 2)")
    st.dataframe(filled_df, use_container_width=True)

    # ---- Tải về Excel
    output = io.BytesIO()
    filled_df.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        "⬇️ Tải ma trận Excel",
        data=output,
        file_name="ma_tran_ban_dac_ta.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Vui lòng upload **đủ 2 file** để bắt đầu")
