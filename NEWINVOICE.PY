import pandas as pd
from openpyxl import load_workbook
from num2words import num2words
import os
import re

def get_next_bill_number(output_dir):
    """Folder check karke agla bill number suggest karega"""
    if not os.path.exists(output_dir):
        return 1
    
    files = os.listdir(output_dir)
    numbers = []
    
    # Files mein se number nikalne ke liye (KDL_INV_25-26_102.xlsx -> 102)
    for f in files:
        match = re.search(r'_(\d+)\.xlsx$', f)
        if match:
            numbers.append(int(match.group(1)))
            
    return max(numbers) + 1 if numbers else 1

def generate_invoice_files():
    # --- Paths ---
    patient_file = r"c:\Users\Administrator\Desktop\BILLING\FEB-2026.xlsx"
    template_file = r"c:\Users\Administrator\Desktop\BILLING\INVOICE_FORMET.xlsx"
    output_dir = r"c:\Users\Administrator\Desktop\BILLING\FINAL_INVOICES"

    os.makedirs(output_dir, exist_ok=True)

    # --- Smart Counter Logic ---
    suggested_start = get_next_bill_number(output_dir)
    print(f"\n📊 System detected last bill. Suggested start: {suggested_start}")
    
    user_input = input(f"Enter starting bill number (Press Enter for {suggested_start}): ").strip()
    
    if user_input == "":
        bill_counter = suggested_start
    else:
        try:
            bill_counter = int(user_input)
        except ValueError:
            print("❌ Invalid number! Using suggested start.")
            bill_counter = suggested_start

    # --- Load Data ---
    df = pd.read_excel(patient_file, sheet_name="Invoice Detail")
    grouped = df.groupby(['SubCentreName', 'Sub Category'])

    for (subcentre, sub_category), group in grouped:
        bill_no = f"KDL/INV/25-26/{bill_counter:03d}"
        
        invoice_to = group['Invoice to'].iloc[0]
        address = group['Address'].iloc[0]
        count = len(group)
        net_amount = int(group['Amount'].sum())

        amount_words = num2words(net_amount, lang='en_IN').title() + " Rupees Only"

        # ---- Load Template ----
        wb = load_workbook(template_file)
        ws = wb.active

        # ---- Fill Invoice Main Sheet ----
        ws["A10"] = invoice_to
        ws["A11"] = sub_category
        ws["A12"] = subcentre
        ws["A13"] = address
        ws["E10"] = bill_no
        ws["C20"] = count
        ws["E20"] = net_amount
        ws["A44"] = f"Amount (in Words): {amount_words}"
        ws["E9"] = Invoice_Date
        # ---- Detail Sheet ----
        detail_ws = wb["Deatial"] # Aapke template ke hisab se spelling 'Deatial' rakhi hai

        if detail_ws.max_row > 1:
            detail_ws.delete_rows(2, detail_ws.max_row)

        headers = []
        col = 1
        while detail_ws.cell(row=1, column=col).value:
            headers.append(detail_ws.cell(row=1, column=col).value)
            col += 1

        last_row_idx = 2
        for row_idx, (_, row) in enumerate(group.iterrows(), start=2):
            for col_idx, header in enumerate(headers, start=1):
                if header in group.columns:
                    detail_ws.cell(row=row_idx, column=col_idx).value = row[header]
            last_row_idx = row_idx

        # ---- Add Note After Data ----
        note_row = last_row_idx + 2
        detail_ws.cell(row=note_row, column=1).value = "Note: Certified that all above patients are shown on the NVHCP Portal"

        # ---- Save File ----
        file_name = f"KDL_INV_25-26_{bill_counter:03d}.xlsx"
        wb.save(os.path.join(output_dir, file_name))

        print(f"✅ Generated: {file_name}")
        bill_counter += 1

    print(f"\n✨ Done! All invoices saved in: {output_dir}")

if __name__ == "__main__":
    generate_invoice_files()