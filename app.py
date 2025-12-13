import streamlit as st
import pandas as pd
import pdfplumber
import docx
from PIL import Image
import pytesseract
import io

st.set_page_config(page_title="Tạo ma trận bản đặc tả", layout="wide")
st.title("Tạo ma trận bản đặc tả")

# ---------------------------
# UTILS
# ---------------------------

def read_excel(file):
    return pd.read_excel(file)

def read_word_tables(file):
    doc = docx.Document(file)
    tables = []
    for table in doc.tables:
        data = []
        for row in table.rows:
            data.append([cell.text.strip() for cell in row.cells])
        tables.append(pd.DataFrame(data[1:], columns=data[0]))
    return tables

def read_pdf_tables(file):
    tables = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                df = pd.DataFrame(table[1:], columns=table[0])
                tables.append(df)
    return tables

def read_image_text(file):
    img = Image.open(file)
    return pytesseract.image_to_string(img, lang="vie")

def extract_text(file, file_type):
    if file_type == "pdf":
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    elif file_type == "docx":
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file_type == "image":
        return read_image_text(file)

def auto_fill_matrix(df, content_text):
    for col in df.columns:
        if "Biết" in col:
            df[col] = "Nhận biết nội dung từ tài liệu"
        elif "Hiểu" in col:
            df[col] = "Giải thích / phân tích nội dung"
        elif "VD" in col or "Vận dụng" in col:
            df[col] = "Vận dụng nội dung vào tình huống"
    return df

# ---------------------------
# UI UPLOAD
# ---------------------------

st.subheader("1️⃣ Upload FILE MẪU MA TRẬN (BẮT BUỘC 1 FILE)")
template_file = st.file_uploader(
    "Chấp nhận Excel / Word / PDF",
    type=["xlsx", "docx", "pdf"]
)

st.subheader("2️⃣ Upload FILE NỘI DUNG (để điền dữ liệu)")
content_file = st.file_uploader(
    "Word / PDF / Ảnh",
    type=["docx", "pdf", "png", "jpg", "jpeg"]
)

# ---------------------------
# PROCESS
# ---------------------------

if template_file and content_file:
    st.success("Đã nhận đủ file, đang xử lí...")

    # --- Đọc file mẫu ---
    if template_file.name.endswith(".xlsx"):
        matrix_df = read_excel(template_file)
    elif template_file.name.endswith(".docx"):
        tables = read_word_tables(template_file)
        matrix_df = tables[0]
    else:
        tables = read_pdf_tables(template_file)
        matrix_df = tables[0]

    st.subheader("📋 Khung ma trận từ file mẫu")
    st.dataframe(matrix_df)

    # --- Đọc file nội dung ---
    if content_file.name.endswith(".pdf"):
        content_text = extract_text(content_file, "pdf")
    elif content_file.name.endswith(".docx"):
        content_text = extract_text(content_file, "docx")
    else:
        content_text = extract_text(content_file, "image")

    st.subheader("📄 Nội dung trích xuất")
    st.text_area("Nội dung", content_text[:3000])

    # --- AI điền ma trận (rule-based, sẵn sàng thay bằng LLM) ---
    filled_df = auto_fill_matrix(matrix_df.copy(), content_text)

    st.subheader("✅ Ma trận sau khi điền")
    st.dataframe(filled_df)

    # --- Download ---
    output = io.BytesIO()
    filled_df.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        "⬇️ Tải ma trận Excel",
        output,
        file_name="ma_tran_ban_dac_ta.xlsx"
    )

else:
    st.info("Vui lòng upload **ít nhất 1 file mẫu** và **1 file nội dung**")
