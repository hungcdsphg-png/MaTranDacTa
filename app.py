import streamlit as st
import pandas as pd
import numpy as np
import pdfplumber
from docx import Document
import openai
import os

# ================== CONFIG ==================
st.set_page_config(page_title="Ma trận đặc tả", layout="wide")

openai.api_key = os.getenv("OPENAI_API_KEY")

# ================== HÀM ĐỌC FILE ==================
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text


def read_word(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def read_excel(file):
    df = pd.read_excel(file)
    return df.to_string(index=False)


# ================== TẠO KHUNG MA TRẬN ==================
def create_matrix_template():
    columns = [
        "TT", "Kĩ năng", "Đơn vị kiến thức", "Mức độ đánh giá",
        "Số tiết", "Tỉ lệ %", "Số điểm cần đạt"
    ]

    forms = [
        "NLC", "ĐS", "NỐI", "ĐIỀN",
        "TL1", "TL2", "TL3"
    ]
    levels = ["Biết", "Hiểu", "VD"]

    for f in forms:
        for l in levels:
            columns.append(f"{f}_{l}")

    columns += ["Tổng số câu", "Điểm từng bài"]

    df = pd.DataFrame(columns=columns)
    return df


# ================== AI ĐIỀN NỘI DUNG ==================
def ai_fill_matrix(raw_text, df):
    prompt = f"""
Bạn là chuyên gia ra đề kiểm tra tiểu học.

Dựa vào nội dung sau:
\"\"\"
{raw_text[:3000]}
\"\"\"

Hãy:
1. Xác định các kĩ năng (Đọc hiểu, Viết...)
2. Xác định đơn vị kiến thức
3. Viết nội dung cột "Mức độ đánh giá"
4. Phân bổ số câu hợp lý vào các cột:
   NLC, ĐS, NỐI, ĐIỀN, TL1, TL2, TL3
   theo 3 mức: Biết – Hiểu – Vận dụng

Trả về dạng JSON:
[
  {{
    "TT": 1,
    "Kĩ năng": "...",
    "Đơn vị kiến thức": "...",
    "Mức độ đánh giá": "...",
    "Số tiết": 13,
    "Tỉ lệ %": 22,
    "Số điểm cần đạt": 2.24,
    "NLC_Biết": 1,
    "NLC_Hiểu": 1,
    "NLC_VD": 0,
    ...
  }}
]
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    data = response.choices[0].message.content

    rows = pd.read_json(data)
    df = pd.concat([df, rows], ignore_index=True)
    return df


# ================== TÍNH TỰ ĐỘNG ==================
def auto_calculate(df):
    question_cols = [c for c in df.columns if "_" in c]

    df[question_cols] = df[question_cols].fillna(0)

    df["Tổng số câu"] = df[question_cols].sum(axis=1)

    # điểm mẫu
    score_map = {
        "NLC": 0.25,
        "ĐS": 0.25,
        "NỐI": 0.25,
        "ĐIỀN": 0.25,
        "TL1": 1.5,
        "TL2": 2.5,
        "TL3": 3
    }

    total_score = []
    for _, row in df.iterrows():
        s = 0
        for k, v in score_map.items():
            for lv in ["Biết", "Hiểu", "VD"]:
                col = f"{k}_{lv}"
                if col in df.columns:
                    s += row[col] * v
        total_score.append(round(s, 2))

    df["Điểm từng bài"] = total_score
    return df


# ================== GIAO DIỆN ==================
st.title("📊 TẠO MA TRẬN BẢN ĐẶC TẢ TỰ ĐỘNG")

uploaded_file = st.file_uploader(
    "📂 Upload file mẫu (PDF / Word / Excel)",
    type=["pdf", "docx", "xlsx"]
)

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        raw_text = read_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        raw_text = read_word(uploaded_file)
    else:
        raw_text = read_excel(uploaded_file)

    st.subheader("📄 Nội dung trích xuất")
    st.text_area("", raw_text, height=200)

    if st.button("🤖 Tạo ma trận bằng AI"):
        df = create_matrix_template()
        df = ai_fill_matrix(raw_text, df)
        df = auto_calculate(df)

        st.subheader("📋 MA TRẬN ĐẶC TẢ")
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇️ Tải Excel",
            df.to_excel(index=False),
            file_name="ma_tran_dac_ta.xlsx"
        )
