import streamlit as st
import pandas as pd
from io import BytesIO
from config import TT32_LEVELS

from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Tạo ma trận đặc tả TT32", layout="wide")

st.title("Ứng dụng tạo ma trận đặc tả theo Thông tư 32")

# =========================
# 1. CHỌN MÔN – KHỐI – KÌ
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    subject = st.selectbox("Chọn môn học", list(TT32_LEVELS.keys()))

with col2:
    grade = st.selectbox("Chọn khối", ["1","2","3","4","5","6","7","8","9","10","11","12"])

with col3:
    semester = st.selectbox("Chọn học kì", ["Giữa kì I", "Cuối kì I", "Giữa kì II", "Cuối kì II"])

st.divider()

# =========================
# 2. UPLOAD FILE (1 Ô DUY NHẤT)
# =========================
uploaded_file = st.file_uploader(
    "Upload 1 file mẫu (Excel / Word / PDF)",
    type=["xlsx", "docx", "pdf"]
)

if uploaded_file is None:
    st.warning("⚠️ Bạn phải upload ít nhất 1 file (Excel / Word / PDF)")
    st.stop()

file_type = uploaded_file.name.split(".")[-1]

st.success(f"Đã nhận file: {uploaded_file.name}")

# =========================
# 3. ĐỌC FILE
# =========================
if file_type == "xlsx":
    df = pd.read_excel(uploaded_file)

elif file_type in ["docx", "pdf"]:
    st.info("📌 File Word/PDF chỉ dùng làm mẫu tham khảo")
    df = pd.DataFrame(columns=[
        "Kĩ năng", "Đơn vị kiến thức", "Biết", "Hiểu", "Vận dụng", "Điểm/câu"
    ])

# =========================
# 4. CHUẨN HÓA BIẾT – HIỂU – VD
# =========================
for col in ["Biết", "Hiểu", "Vận dụng"]:
    if col not in df.columns:
        df[col] = 0

if "Điểm/câu" not in df.columns:
    df["Điểm/câu"] = 1

df["Tổng số câu"] = df["Biết"] + df["Hiểu"] + df["Vận dụng"]
df["Tổng điểm"] = df["Tổng số câu"] * df["Điểm/câu"]

# =========================
# 5. TÁCH ĐỌC HIỂU / VIẾT
# =========================
df_doc = df[df["Kĩ năng"].str.contains("Đọc", na=False)]
df_viet = df[df["Kĩ năng"].str.contains("Viết", na=False)]

# =========================
# 6. HIỂN THỊ
# =========================
st.subheader("Ma trận tổng hợp")
st.dataframe(df)

st.subheader("Ma trận Đọc hiểu")
st.dataframe(df_doc)

st.subheader("Ma trận Viết")
st.dataframe(df_viet)

# =========================
# 7. XUẤT FILE
# =========================
def export_excel(dataframe):
    output = BytesIO()
    dataframe.to_excel(output, index=False)
    return output.getvalue()

def export_word(dataframe):
    doc = Document()
    doc.add_heading("Ma trận đặc tả", level=1)
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

def export_pdf(dataframe):
    output = BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output)
    elements = [Paragraph("Ma trận đặc tả", styles["Title"])]

    for _, row in dataframe.iterrows():
        elements.append(Paragraph(str(list(row)), styles["Normal"]))

    doc.build(elements)
    return output.getvalue()

st.divider()
st.subheader("Tải kết quả")

col1, col2, col3 = st.columns(3)

with col1:
    st.download_button(
        "⬇️ Excel",
        export_excel(df),
        file_name="ma_tran.xlsx"
    )

with col2:
    st.download_button(
        "⬇️ Word",
        export_word(df),
        file_name="ma_tran.docx"
    )

with col3:
    st.download_button(
        "⬇️ PDF",
        export_pdf(df),
        file_name="ma_tran.pdf"
    )
