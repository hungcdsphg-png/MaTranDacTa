import streamlit as st
import pandas as pd
import io

from docx import Document
import pdfplumber

st.set_page_config(page_title="Tạo ma trận bản đặc tả", layout="wide")

st.title("Tạo ma trận bản đặc tả")
st.write("Upload **1 trong 3 file: Excel / Word / PDF** để tạo ma trận")

# =========================
# 1. UPLOAD FILE
# =========================
uploaded_file = st.file_uploader(
    "Tải file mẫu (Excel, Word, PDF)",
    type=["xlsx", "docx", "pdf"],
    accept_multiple_files=False
)

if not uploaded_file:
    st.warning("Vui lòng upload ít nhất 1 file.")
    st.stop()

file_name = uploaded_file.name.lower()

# =========================
# 2. HÀM ĐỌC FILE
# =========================
def read_excel(file):
    return pd.read_excel(file)

def read_word(file):
    doc = Document(file)
    text = []
    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text.strip())
    return "\n".join(text)

def read_pdf(file):
    text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text.append(t)
    return "\n".join(text)

# =========================
# 3. PHÂN LOẠI FILE
# =========================
raw_text = ""
df_input = None

if file_name.endswith(".xlsx"):
    df_input = read_excel(uploaded_file)
    st.success("Đã đọc file Excel")

elif file_name.endswith(".docx"):
    raw_text = read_word(uploaded_file)
    st.success("Đã đọc file Word")

elif file_name.endswith(".pdf"):
    raw_text = read_pdf(uploaded_file)
    st.success("Đã đọc file PDF")

# =========================
# 4. TẠO KHUNG MA TRẬN CHUẨN
# =========================
def create_matrix_template():
    columns = [
        "TT",
        "Kĩ năng",
        "Đơn vị kiến thức",
        "Mức độ đánh giá",
        "Biết",
        "Hiểu",
        "Vận dụng",
        "Hình thức",
        "Số câu",
        "Số điểm"
    ]
    return pd.DataFrame(columns=columns)

df_matrix = create_matrix_template()

# =========================
# 5. SINH DỮ LIỆU (RULE + AI HOÁ DẦN)
# =========================
if df_input is not None:
    # Trường hợp Excel: lấy dữ liệu trực tiếp
    df_matrix = df_input.copy()

else:
    # Trường hợp Word / PDF: tạo skeleton từ text
    lines = raw_text.split("\n")

    rows = []
    tt = 1
    for line in lines:
        if len(line) > 20:
            rows.append({
                "TT": tt,
                "Kĩ năng": "Đọc hiểu",
                "Đơn vị kiến thức": line[:60],
                "Mức độ đánh giá": "Hiểu nội dung",
                "Biết": 1,
                "Hiểu": 0,
                "Vận dụng": 0,
                "Hình thức": "TN",
                "Số câu": 1,
                "Số điểm": 0.25
            })
            tt += 1
        if tt > 5:
            break

    df_matrix = pd.DataFrame(rows)

# =========================
# 6. HIỂN THỊ & TẢI VỀ
# =========================
st.subheader("Ma trận bản đặc tả (có thể chỉnh sửa)")
edited_df = st.data_editor(df_matrix, num_rows="dynamic")

output = io.BytesIO()
edited_df.to_excel(output, index=False)
output.seek(0)

st.download_button(
    "Tải ma trận Excel",
    data=output,
    file_name="ma_tran_ban_dac_ta.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
