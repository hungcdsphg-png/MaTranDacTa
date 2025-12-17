import streamlit as st
import pandas as pd
import pdfplumber
import docx
import os
import json
from io import BytesIO
from dotenv import load_dotenv
from openai import OpenAI

# =============================
# STREAMLIT CONFIG
# =============================
st.set_page_config(
    page_title="Trợ lý Ma Trận Đặc Tả",
    layout="wide"
)

# =============================
# LOAD ENV
# =============================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ Chưa cấu hình OPENAI_API_KEY trong Secrets")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL_NAME = "gpt-4.1"

# =============================
# FILE EXTRACT
# =============================
def extract_text(uploaded_file):
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                t = page.extract_text()
                if t:
                    text += f"\n--- Trang {i+1} ---\n{t}"
        return text.strip()

    elif name.endswith(".docx"):
        doc = docx.Document(BytesIO(file_bytes))
        texts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                texts.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(texts)

    elif name.endswith(".xlsx") or name.endswith(".xls"):
        df = pd.read_excel(BytesIO(file_bytes))
        return df.to_csv(index=False)

    else:
        return file_bytes.decode("utf-8", errors="ignore")

# =============================
# UI
# =============================
st.title("🧠 TRỢ LÍ MA TRẬN ĐẶC TẢ")

ref_files = st.file_uploader(
    "Upload tài liệu tham chiếu",
    type=["pdf", "docx", "xlsx", "xls", "txt", "csv"],
    accept_multiple_files=True
)

ref_text = st.text_area("Hoặc dán nội dung", height=150)

template_text = st.text_area(
    "Khung ma trận",
    value="STT, Nội dung kiến thức, Chuẩn đánh giá, Nhận biết, Thông hiểu, Vận dụng, Tổng",
    height=120
)

reference_contents = []
if ref_files:
    for f in ref_files:
        text = extract_text(f)
        if text and len(text) > 50:
            reference_contents.append(f"\n=== FILE: {f.name} ===\n{text}")
            with st.expander(f"📄 Xem trước {f.name}"):
                st.text(text[:800])
        else:
            st.warning(f"⚠️ {f.name} không trích xuất được text")

# =============================
# GENERATE
# =============================
if st.button("🚀 TẠO MA TRẬN"):

    if not reference_contents and not ref_text.strip():
        st.error("❌ Chưa có dữ liệu")
        st.stop()

    prompt = f"""
Bạn là chuyên gia khảo thí.

TRẢ VỀ JSON DUY NHẤT:

{{
  "headers": ["STT", "..."],
  "rows": [
    ["1", "..."]
  ]
}}

QUY TẮC:
- TẤT CẢ giá trị là STRING
- Không markdown
- Không giải thích

=== KHUNG MA TRẬN ===
{template_text}

=== DỮ LIỆU ===
{ref_text}

{"".join(reference_contents)}
"""

    with st.spinner("GPT-4.1 đang xử lý..."):
        response = client.responses.create(
            model=MODEL_NAME,
            input=prompt,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "matrix",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "headers": {"type": "array", "items": {"type": "string"}},
                            "rows": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        },
                        "required": ["headers", "rows"]
                    }
                }
            }
        )

        result = json.loads(response.output_text)
        df = pd.DataFrame(result["rows"], columns=result["headers"])

        st.success("✅ Tạo thành công")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇️ Tải CSV",
            df.to_csv(index=False).encode("utf-8-sig"),
            "Ma_Tran_Dac_Ta.csv",
            "text/csv"
        )
