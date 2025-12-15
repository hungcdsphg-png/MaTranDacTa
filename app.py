import streamlit as st
from utils.read_reference import read_pdf_text
from utils.matrix_builder import load_matrix_template, fill_matrix
from utils.export_excel import export_excel

st.set_page_config(page_title="TRỢ LÍ MA TRẬN ĐẶC TẢ", layout="wide")

# ===== HEADER =====
st.markdown(
    "<h1 style='text-align:center; font-family:Times New Roman;'>"
    "TRỢ LÍ MA TRẬN ĐẶC TẢ</h1>",
    unsafe_allow_html=True
)

# ===== THÂN APP =====
st.header("📚 DỮ LIỆU THAM CHIẾU (TỪ GITHUB)")

with st.expander("📌 Nguồn tham chiếu đang sử dụng"):
    st.write("- Chương trình GDPT 2018")
    st.write("- SGK + SGV Tiếng Việt 2")
    st.write("- Ma trận bản đặc tả mẫu")

lesson = st.text_input("Nhập bài học (VD: Bài 1 – Tôi là học sinh lớp 2)")

if st.button("🚀 TẠO MA TRẬN ĐẶC TẢ"):
    with st.spinner("AI đang tạo ma trận..."):
        ref_text = (
            read_pdf_text("data/CT_TONG_THE.pdf")
            + read_pdf_text("data/SGK_TV2_T1.pdf")
            + read_pdf_text("data/SGV_TV2_T1.pdf")
        )

        df = load_matrix_template()
        df_filled = fill_matrix(df, ref_text, lesson)

        st.success("✅ Tạo ma trận thành công!")
        st.dataframe(df_filled, use_container_width=True)

        export_excel(df_filled, "MA_TRAN_DAC_TA.xlsx")

# ===== FOOTER =====
st.header("⬇️ TẢI FILE MA TRẬN")
with open("MA_TRAN_DAC_TA.xlsx", "rb") as f:
    st.download_button(
        "📥 Tải ma trận đặc tả (Excel)",
        f,
        file_name="MA_TRAN_DAC_TA.xlsx"
    )
