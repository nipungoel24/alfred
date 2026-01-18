import os
import pandas as pd
from data_loader import clean_and_load_emails

# 1. Setup Paths
INPUT_PATH = r"C:\Kaam_Dhanda\AssistfAI\data\dataset_emails - Sheet1.csv"
OUTPUT_PATH = r"C:\Kaam_Dhanda\AssistfAI\Data_clean\cleaned_emails_export.csv"

def run_test_and_export():
    print(f"📂 Reading Raw File: {INPUT_PATH}")

    if not os.path.exists(INPUT_PATH):
        print("❌ Error: Input file not found.")
        return

    try:
        # 2. Process the file using your robust loader
        with open(INPUT_PATH, 'rb') as f:
            print("⏳ Parsing data...")
            email_records = clean_and_load_emails(f)

        if not email_records:
            print("❌ Error: No data returned from loader.")
            return

        # 3. Convert to DataFrame
        print(f"✅ Successfully parsed {len(email_records)} records.")
        df = pd.DataFrame(email_records)

        # 4. Export to new CSV
        print(f"💾 Saving to: {OUTPUT_PATH}")
        # index=False prevents pandas from adding an extra row number column
        # encoding='utf-8-sig' ensures Excel opens it correctly with all symbols
        df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')

        print("-" * 50)
        print("🚀 DONE! You can now open 'cleaned_emails_export.csv'.")
        print("-" * 50)
        
        # 5. Quick Preview
        print("🔎 Preview of First Row:")
        print(df.iloc[0])

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    run_test_and_export()
    