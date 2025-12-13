import streamlit as st
import pandas as pd
import io

# ===============================
# CẤU HÌNH TRANG
# ===============================
st.set_page_config(
    page_title="Tạo ma trận đặc tả",
    layout="wide"
)

st.title("ỨNG DỤNG TẠO MA TRẬN ĐẶC TẢ")
st.write("Upload **Excel / Word / PDF** (bắt buộc ít nhất 1 file)")

# ===============================
# PHẦN 1. UPLOAD FILE (1 Ô DUY NHẤT)
# ===============================
uploaded_files = st.file_uploader(
    label="Upload file dữ liệu (Excel / Word / PDF)",
    type=["xlsx", "docx", "pdf"],
    accept_multiple_files=True
)

# ===============================
# KIỂM TRA ĐIỀU KIỆN BẮT BUỘC
# ===============================
if not uploaded_files:
    st.error("❌ Bạn phải upload ít nhất **1 file** (Excel / Word / PDF) để tiếp tục.")
    st.stop()

# ===============================
# PHÂN LOẠI FILE
# ===============================
excel_file = None
word_files = []
pdf_files = []

for file in uploaded_files:
    if file.name.endswith(".xlsx"):
        excel_file = file
    elif file.name.endswith(".docx"):
        word_files.append(file)
    elif file.name.endswith(".pdf"):
        pdf_files.append(file)

# ===============================
# HIỂN THỊ TRẠNG THÁI UPLOAD
# ===============================
st.success("✅ Upload thành công!")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Excel")
    if excel_file:
        st.write(f"✔ {excel_file.name}")
    else:
        st.warning("Chưa có file Excel")

with col2:
    st.subheader("📄 Word (tham khảo)")
    if word_files:
        for f in word_files:
            st.write(f"✔ {f.name}")
    else:
        st.write("Không có")

with col3:
    st.subheader("📕 PDF (tham khảo)")
    if pdf_files:
        for f in pdf_files:
            st.write(f"✔ {f.name}")
    else:
        st.write("Không có")

# ===============================
# KIỂM TRA CÓ FILE EXCEL HAY CHƯA
# ===============================
if excel_file is None:
    st.warning(
        "⚠️ Chưa có file Excel.\n\n"
        "👉 Bạn **vẫn có thể upload Word/PDF để tham khảo**, "
        "nhưng **không thể tạo ma trận** nếu thiếu Excel."
    )
    st.stop()

# ===============================
# ĐỌC FILE EXCEL
# ===============================
try:
    df_input = pd.read_excel(excel_file)
    st.subheader("📑 Dữ liệu Excel đã upload")
    st.dataframe(df_input, use_container_width=True)

except Exception as e:
    st.error("❌ Không đọc được file Excel.")
    st.exception(e)
    st.stop()

# ===============================
# NÚT TIẾP TỤC XỬ LÝ
# ===============================
st.divider()

if st.button("➡️ Tiếp tục tạo ma trận đặc tả"):
    st.success("Sẵn sàng sang bước tạo khung ma trận theo file mẫu 🚀")
