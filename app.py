import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import io

st.set_page_config(page_title="Ma trận đặc tả", layout="wide")

st.title("Tạo ma trận bản đặc tả")

YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")


def calculate_totals(df):
    df["Tổng số câu"] = df["Biết"] + df["Hiểu"] + df["VD"]
    df["Tổng điểm"] = df["Tổng số câu"] * df["Điểm/câu"]
    return df


def split_matrix(df):
    df_doc = df[df["Kĩ năng"].str.contains("Đọc", case=False, na=False)]
    df_viet = df[df["Kĩ năng"].str.contains("Viết", case=False, na=False)]
    return df_doc, df_viet


def highlight_excel(buffer, yellow_cols):
    wb = load_workbook(buffer)
    ws = wb.active

    header = {cell.value: cell.column for cell in ws[1]}

    for col in yellow_cols:
        if col in header:
            col_idx = header[col]
            for row in range(1, ws.max_row + 1):
                ws.cell(row=row, column=col_idx).fill = YELLOW_FILL

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


uploaded_file = st.file_uploader(
    "Tải file Excel, PDF, Word ma trận mẫu",
    type=["xlsx, PDF, Word"]
)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df = calculate_totals(df)

        df_doc, df_viet = split_matrix(df)

        st.subheader("Ma trận tổng hợp")
        st.dataframe(df)

        def prepare_download(df_out, file_name):
            buffer = io.BytesIO()
            df_out.to_excel(buffer, index=False)
            buffer.seek(0)
            buffer = highlight_excel(buffer, ["Kĩ năng", "Đơn vị kiến thức", "Hình thức"])

            st.download_button(
                label=f"Tải {file_name}",
                data=buffer,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        prepare_download(df, "ma_tran_tong_hop.xlsx")
        prepare_download(df_doc, "ma_tran_doc_hieu.xlsx")
        prepare_download(df_viet, "ma_tran_viet.xlsx")

    except Exception as e:
        st.error(f"Lỗi xử lý file: {e}")
