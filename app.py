import streamlit as st
import pandas as pd
import io

# ====== IMPORT XỬ LÝ FILE ======
from docx import Document
import fitz  # PyMuPDF
from PIL import Image


# ================= UI =================
st.set_page_config(page_title="Tạo ma trận bản đặc tả", layout="wide")
st.title("Tạo ma trận bản đặc tả")

st.info("Bắt buộc tải lên **1 file mẫu (Excel / Word / PDF)**")


# ================= UPLOAD FILES =================
template_file = st.file_uploader(
    "📌 Tải file MA TRẬN MẪU",
    type=["xlsx", "docx", "pdf"],
    accept_multiple_files=False
)

content_files = st.file_uploader(
    "📌 Tải file NỘI DUNG (Word / PDF / Ảnh – không bắt buộc)",
    type=["docx", "pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True
)


# ================= HÀM ĐỌC FILE =================
def read_excel(file):
    return pd.read_excel(file)


def read_word(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def read_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def read_image(file):
    img = Image.open(file)
    return f"Ảnh kích thước {img.size}"


# ================= MAIN LOGIC =================
if template_file is None:
    st.warning("⛔ Vui lòng tải lên file mẫu trước")
    st.stop()

try:
    # ====== XỬ LÝ FILE MẪU ======
    suffix = template_file.name.split(".")[-1].lower()

    if suffix == "xlsx":
        df_template = read_excel(template_file)
        st.success("Đã đọc file Excel mẫu")
        st.dataframe(df_template.head())

    elif suffix == "docx":
        template_text = read_word(template_file)
        st.success("Đã đọc file Word mẫu")
        st.text_area("Nội dung mẫu", template_text[:2000])

        # Tạo khung DataFrame mẫu (ví dụ)
        df_template = pd.DataFrame(columns=[
            "Kĩ năng", "Đơn vị kiến thức", "Biết", "Hiểu", "Vận dụng", "Điểm"
        ])

    elif suffix == "pdf":
        template_text = read_pdf(template_file)
        st.success("Đã đọc file PDF mẫu")
        st.text_area("Nội dung mẫu", template_text[:2000])

        df_template = pd.DataFrame(columns=[
            "Kĩ năng", "Đơn vị kiến thức", "Biết", "Hiểu", "Vận dụng", "Điểm"
        ])

    else:
        st.error("Định dạng file mẫu không hợp lệ")
        st.stop()

    # ====== XỬ LÝ FILE NỘI DUNG ======
    extracted_text = ""

    if content_files:
        for f in content_files:
            ext = f.name.split(".")[-1].lower()
            if ext == "docx":
                extracted_text += read_word(f)
            elif ext == "pdf":
                extracted_text += read_pdf(f)
            elif ext in ["png", "jpg", "jpeg"]:
                extracted_text += read_image(f)

        st.success("Đã đọc file nội dung bổ sung")

    # ====== GIẢ LẬP AI ĐIỀN MA TRẬN ======
    if st.button("⚙️ Tạo ma trận"):
        df_result = df_template.copy()

        if len(df_result.columns) > 0:
            df_result.loc[0] = [
                "Đọc hiểu",
                "Văn bản văn học",
                2,
                1,
                1,
                4
            ]

        st.success("Hoàn thành tạo ma trận")
        st.dataframe(df_result)

        # ====== DOWNLOAD ======
        buffer = io.BytesIO()
        df_result.to_excel(buffer, index=False)
        st.download_button(
            "📥 Tải ma trận Excel",
            data=buffer.getvalue(),
            file_name="ma_tran_ban_dac_ta.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

except Exception as e:
    st.error("❌ Có lỗi xảy ra khi xử lý file")
    st.exception(e)
