import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font
from config import REPORT_PATH

def read_food_items(path: str, column: str = None) -> list[str]:
    df = pd.read_excel(path)

    # Clean up column header whitespaces
    df.columns = [str(c).strip() for c in df.columns]

    # Prioritize specific dish/item names over broad category names
    priority_columns = [
        "Item Name",
        "Food Item",
        "Dish Name",
        "Dish",
        "Item",
        "Menu Item",
    ]

    target_col = None

    if column and column in df.columns:
        target_col = column
    else:
        for candidate in priority_columns:
            if candidate in df.columns:
                target_col = candidate
                break

    # If no standard header is matched, avoid category columns if possible
    if not target_col:
        non_category_cols = [
            c for c in df.columns 
            if not any(cat in c.lower() for cat in ["category", "cat", "group", "type"])
        ]
        target_col = non_category_cols[0] if non_category_cols else df.columns[0]

    print(f"[excel] Reading dish names from column: '{target_col}'")

    items = df[target_col].dropna().astype(str).str.strip().tolist()
    return [i for i in items if i]

def write_report(rows: list[dict], path: str = REPORT_PATH) -> None:
    df = pd.DataFrame(rows)
    # 1. Save the basic data
    df.to_excel(path, index=False)
    
    # 2. Re-open and apply the blue underline styling
    try:
        wb = load_workbook(path)
        ws = wb.active
        link_font = Font(color="0563C1", underline="single") # Standard Excel hyperlink blue
        
        # Identify columns and widen them slightly for a clean look
        source_col, drive_col = None, None
        
        for col in range(1, ws.max_column + 1):
            header = ws.cell(row=1, column=col).value
            col_letter = ws.cell(row=1, column=col).column_letter
            
            if header == "Source":
                source_col = col
                ws.column_dimensions[col_letter].width = 15
            elif header == "Drive Link":
                drive_col = col
                ws.column_dimensions[col_letter].width = 18
            elif header == "Food Item":
                ws.column_dimensions[col_letter].width = 30
        
        # Apply the blue font to all the links in those columns
        for r in range(2, ws.max_row + 1):
            if source_col and ws.cell(row=r, column=source_col).value:
                ws.cell(row=r, column=source_col).font = link_font
            if drive_col and ws.cell(row=r, column=drive_col).value:
                ws.cell(row=r, column=drive_col).font = link_font
        
        wb.save(path)
    except Exception as e:
        print(f"[excel] Could not apply link styling: {e}")