import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import json

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="TRỢ LÍ MA TRẬN ĐẶC TẢ",
    page_icon="📝",
    layout="wide"
)

# --- CSS TÙY CHỈNH (FONT TIMES NEW ROMAN) ---
# Ép toàn bộ giao diện dùng font Times New Roman
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Times New Roman', serif;
    }
    
    h1, h2, h3 {
        font-family: 'Times New Roman', serif;
        font-weight: bold;
        color: #0e4d92;
    }
    
    .stButton>button {
        font-family: 'Times New Roman', serif;
        font-weight: bold;
    }
    
    .stTextInput>div>div>input {
        font-family: 'Times New Roman', serif;
    }
    
    .stTextArea>div>div>textarea {
        font-family: 'Times New Roman', serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HÀM XỬ LÝ EXCEL ---
def to_excel(df):
    """Chuyển DataFrame thành file Excel với định dạng đẹp"""
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='MaTranDacTa')
    workbook = writer.book
    worksheet = writer.sheets['MaTranDacTa']

    # Định dạng
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1,
        'font_name': 'Times New Roman',
        'font_size': 12
    })
    
    cell_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top',
        'border': 1,
        'font_name': 'Times New Roman',
        'font_size': 12
    })

    # Áp dụng định dạng cho header và cột
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(col_num, col_num, 20, cell_format) # Set width chung

    # Chỉnh độ rộng cụ thể cho cột nội dung dài
    worksheet.set_column('A:A', 15, cell_format) # Kĩ năng
    worksheet.set_column('B:B', 20, cell_format) # Đơn vị kiến thức
    worksheet.set_column('C:C', 50, cell_format) # Mức độ đánh giá (Quan trọng nhất)
    
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def create_template():
    """Tạo file mẫu khung ma trận"""
    data = {
        "Kĩ năng": ["Đọc hiểu", "Viết"],
        "Đơn vị kiến thức": ["Văn bản văn học", "Viết bài văn..."],
        "Mức độ đánh giá / Yêu cầu cần đạt": ["Nhận biết: ...", "Thông hiểu: ..."],
        "Số câu TN": [2, 0],
        "Số câu TL": [1, 1],
        "Điểm số": [2.0, 3.0]
    }
    df = pd.DataFrame(data)
    return to_excel(df)

# --- HÀM GỌI GEMINI AI ---
def generate_matrix_content(api_key, subject, grade, topic, user_notes):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Đóng vai trò là một chuyên gia giáo dục tiểu học/trung học tại Việt Nam, am hiểu chương trình GDPT 2018.
    Hãy tạo nội dung cho "Bảng đặc tả đề kiểm tra" môn {subject} Lớp {grade}, nội dung kiểm tra về: "{topic}".
    
    Yêu cầu cụ thể:
    1. Dựa trên cấu trúc chuẩn: Kĩ năng, Đơn vị kiến thức, Mức độ đánh giá (Nhận biết, Thông hiểu, Vận dụng), Số câu hỏi, Điểm số.
    2. Lưu ý từ người dùng: {user_notes}
    3. Output phải là định dạng JSON List, mỗi item là một dòng trong bảng, không có markdown code block (```json).
    4. Các trường trong JSON: "ki_nang", "don_vi_kien_thuc", "yeu_cau_can_dat", "so_cau_tn", "so_cau_tl", "diem_so".
    5. Nội dung cột "yeu_cau_can_dat" phải chi tiết, ví dụ: "Nhận biết: Xác định được nhân vật...", "Thông hiểu: Hiểu được ý nghĩa...".
    
    Ví dụ cấu trúc JSON output mong muốn:
    [
        {{"ki_nang": "Đọc hiểu", "don_vi_kien_thuc": "Truyện kể", "yeu_cau_can_dat": "Nhận biết: ...", "so_cau_tn": 2, "so_cau_tl": 0, "diem_so": 1.0}},
        ...
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        # Làm sạch chuỗi phản hồi phòng trường hợp AI thêm markdown
        content = response.text.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        data = json.loads(content)
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Lỗi khi gọi AI: {e}")
        return None

# --- GIAO DIỆN CHÍNH ---

# 1. HEADER
st.title("TRỢ LÍ MA TRẬN ĐẶC TẢ 🏫")
st.markdown("---")

# SIDEBAR: Cấu hình
with st.sidebar:
    st.header("⚙️ Cấu hình hệ thống")
    api_key = st.text_input("Nhập Google Gemini API Key", type="password", help="Lấy key tại aistudio.google.com")
    st.info("Hệ thống sử dụng AI để tự động điền nội dung đặc tả dựa trên yêu cầu của giáo viên.")
    
    st.markdown("---")
    st.write("**Hướng dẫn:**")
    st.write("1. Tải khung mẫu (nếu cần tham khảo).")
    st.write("2. Nhập thông tin môn học, khối lớp.")
    st.write("3. Nhấn 'Tạo nội dung' để AI làm việc.")
    st.write("4. Tải file Excel hoàn chỉnh.")

# 2. PHẦN THÂN: Dữ liệu tham chiếu & Mẫu
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Dữ liệu tham chiếu & Mẫu")
    st.markdown("""
    Hệ thống đã được nạp cấu trúc khung ma trận chuẩn (dựa trên mẫu Trường TH Bình Thuận).
    Bạn có thể tải file khung mẫu trắng tại đây để xem cấu trúc các cột.
    """)
    
    template_file = create_template()
    st.download_button(
        label="⬇️ Tải file Khung Ma Trận Mẫu (.xlsx)",
        data=template_file,
        file_name="khung_ma_tran_mau.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    st.subheader("💡 Nhập liệu thông tin")
    st.markdown("Điền thông tin để AI hỗ trợ viết nội dung.")

# 3. PHẦN NHẬP LIỆU TẠO MA TRẬN
st.markdown("---")
with st.container():
    st.header("🛠️ Tạo Ma Trận Đặc Tả Mới")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        subject = st.text_input("Môn học", value="Tiếng Việt")
    with c2:
        grade = st.selectbox("Khối lớp", ["Lớp 1", "Lớp 2", "Lớp 3", "Lớp 4", "Lớp 5"])
    with c3:
        exam_type = st.text_input("Loại bài kiểm tra", value="Giữa học kì 1")
    
    topic = st.text_area("Nội dung/Chủ đề kiểm tra (Càng chi tiết AI làm càng tốt)", 
                         value="Đọc hiểu văn bản truyện; Viết bài văn tả cảnh đồng lúa.",
                         height=100)
    
    user_notes = st.text_input("Ghi chú thêm cho AI (Tùy chọn)", placeholder="Ví dụ: Tăng cường câu hỏi vận dụng, tỉ lệ trắc nghiệm 60%")

    generate_btn = st.button("✨ TẠO NỘI DUNG MA TRẬN (AI)", type="primary")

# 4. XỬ LÝ VÀ HIỂN THỊ KẾT QUẢ
if generate_btn:
    if not api_key:
        st.warning("Vui lòng nhập Gemini API Key ở thanh bên trái trước!")
    else:
        with st.spinner("Đang kết nối với Google Gemini để phân tích và soạn thảo..."):
            # Gọi hàm AI
            df_result = generate_matrix_content(api_key, subject, grade, f"{exam_type} - {topic}", user_notes)
            
            if df_result is not None:
                # Đổi tên cột cho đẹp (Mapping từ JSON key sang Tiếng Việt)
                df_result.columns = ["Kĩ năng", "Đơn vị kiến thức", "Mức độ đánh giá / Yêu cầu cần đạt", "Số câu TN", "Số câu TL", "Điểm số"]
                
                st.session_state['df_result'] = df_result
                st.success("Đã tạo xong nội dung!")

# Hiển thị kết quả nếu đã có trong session
if 'df_result' in st.session_state:
    st.markdown("---")
    st.subheader("📊 Kết quả Ma trận đặc tả")
    
    # Cho phép sửa dữ liệu trực tiếp trên bảng
    edited_df = st.data_editor(
        st.session_state['df_result'],
        num_rows="dynamic",
        use_container_width=True,
        height=400
    )
    
    st.markdown("### 📥 Xuất dữ liệu")
    col_dl1, col_dl2 = st.columns([1, 4])
    
    excel_data = to_excel(edited_df)
    
    with col_dl1:
        st.download_button(
            label="⬇️ Tải xuống file Excel (.xlsx)",
            data=excel_data,
            file_name=f"Ma_tran_dac_ta_{subject}_{grade}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    with col_dl2:
        st.write("*File Excel đã được định dạng font Times New Roman và căn chỉnh lề.*")
