import pandas as pd
import re

def clean_and_load_emails(uploaded_file):
    """
    Robust parser for 'Double-Quoted' CSV files.
    Splits the file based on the unique pattern of new rows: \n"digit,
    """
    try:
        # 1. Read the file as a single text string
        # We try multiple encodings to ensure we get the text
        content = None
        for enc in ['utf-8', 'cp1252', 'latin1']:
            try:
                uploaded_file.seek(0)
                content = uploaded_file.read().decode(enc)
                break
            except Exception:
                continue
        
        if content is None:
            print("❌ Error: Could not decode file with standard encodings.")
            return []

        # 2. Find all Row Starts
        # Pattern: Newline, followed by Quote, followed by Digits, followed by Comma.
        # This matches: \n"1,  and \n"2,  etc.
        # We use capturing group (\d+) to keep the ID.
        pattern = re.compile(r'\n"(\d+),')
        
        # Split the entire text by this pattern
        # parts[0] = Header
        # parts[1] = ID of email 1
        # parts[2] = Rest of email 1
        # parts[3] = ID of email 2
        # parts[4] = Rest of email 2 ...
        parts = pattern.split(content)
        
        data = []
        
        # Loop through the parts (stepping by 2 because split separates the capturing group)
        # We skip parts[0] (header)
        for i in range(1, len(parts), 2):
            email_id = parts[i]      # The digit (e.g., "1")
            rest_of_row = parts[i+1] # The rest of the line (e.g., "john.smith@... thread_001")
            
            # Clean the trailing quote/newline from the previous split
            rest_of_row = rest_of_row.strip()
            if rest_of_row.endswith('"'):
                rest_of_row = rest_of_row[:-1] # Remove the final closing quote of the row

            try:
                # 3. Parse the Known Columns (Comma Separated)
                # We strictly split from the RIGHT for the last 3 columns (Thread, Attach, Time)
                # We strictly split from the LEFT for the first 3 columns (Email, Name, Subject)
                # Everything remaining in the middle is the BODY.
                
                # Split from Right: thread_id, has_attachment, timestamp
                right_parts = rest_of_row.rsplit(',', 3)
                if len(right_parts) < 4:
                    print(f"⚠️ Skipping malformed row {email_id}")
                    continue
                    
                middle_chunk = right_parts[0] # Contains Sender...Body
                timestamp = right_parts[1]
                has_attachment = right_parts[2]
                thread_id = right_parts[3]
                
                # Split from Left: sender_email, sender_name, subject
                left_parts = middle_chunk.split(',', 3)
                if len(left_parts) < 4:
                     print(f"⚠️ Skipping malformed row {email_id} (left split)")
                     continue

                sender_email = left_parts[0]
                sender_name = left_parts[1]
                subject = left_parts[2]
                body_raw = left_parts[3]

                # 4. Clean the Body
                # Unescape double-double quotes ("") to single quotes (")
                body = body_raw.replace('""', '"')
                # If body is wrapped in quotes, strip them
                if body.startswith('"') and body.endswith('"'):
                    body = body[1:-1]

                # 5. Build Record
                record = {
                    "email_id": email_id,
                    "sender_email": sender_email,
                    "sender_name": sender_name,
                    "subject": subject,
                    "body": body,
                    "timestamp": timestamp,
                    "has_attachment": has_attachment,
                    "thread_id": thread_id
                }
                data.append(record)
                
            except Exception as e:
                print(f"❌ Error processing row {email_id}: {e}")

        print(f"✅ Successfully parsed {len(data)} emails.")
        return data

    except Exception as e:
        print(f"❌ Critical Error: {e}")
        return []