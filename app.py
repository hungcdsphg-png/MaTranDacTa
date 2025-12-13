import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from config import SUBJECT_LEVEL_MAP


INPUT_FILE = "input/ma_tran_mau.xlsx"
OUTPUT_DOC = "output/ma_tran_doc_hieu.xlsx"
OUTPUT_VIET = "output/ma_tran_viet.xlsx"
OUTPUT_ALL = "output/ma_tran_tong_hop.xlsx"


YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")


def read_input(file_path):
    return pd.read_excel(file_path)


def calculate_totals(df):
    df["Tổng số câu"] = df["Biết"] + df["Hiểu"] + df["VD"]
    df["Tổng điểm"] = df["Tổng số câu"] * df["Điểm/câu"]
    return df


def split_matrix(df):
    df_doc = df[df["Kĩ năng"].str.contains("Đọc", case=False, na=False)]
    df_viet = df[df["Kĩ năng"].str.contains("Viết", case=False, na=False)]
    return df_doc, df_viet


def export_excel(df, file_path):
    df.to_excel(file_path, index=False)


def highlight_columns(file_path, col_names):
    wb = load_workbook(file_path)
    ws = wb.active

    header = {cell.value: cell.column for cell in ws[1]}

    for name in col_names:
        if name in header:
            col_idx = header[name]
            for row in range(1, ws.max_row + 1):
                ws.cell(row=row, column=col_idx).fill = YELLOW_FILL

    wb.save(file_path)


def main():
    df = read_input(INPUT_FILE)
    df = calculate_totals(df)

    df_doc, df_viet = split_matrix(df)

    export_excel(df, OUTPUT_DOC)
    export_excel(df, OUTPUT_VIET)
    export_excel(df, OUTPUT_ALL)

    # Cột giữ nguyên màu vàng theo file mẫu
    yellow_cols = ["Kĩ năng", "Đơn vị kiến thức", "Hình thức"]

    highlight_columns(OUTPUT_DOC, yellow_cols)
    highlight_columns(OUTPUT_VIET, yellow_cols)
    highlight_columns(OUTPUT_ALL, yellow_cols)

    print("Hoàn thành tạo ma trận đặc tả")


if __name__ == "__main__":
    main()
