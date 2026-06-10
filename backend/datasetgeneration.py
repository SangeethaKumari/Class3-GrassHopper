import os
import time
import json
import pandas as pd
import io
from google import genai
from google.genai import types

# 1. API Key (Ensure your key is inside the quotes)
client = genai.Client(api_key="AIzaSyAhoIyCxP-5vtfGf8DKXQj2FxXI2T_sWy8")

categories = [
    "Diabetes", "Arthritis", "COPD/Respiratory", 
    "Eye Condition", "Cardiovascular", "Neurological"
]

output_dir = "category_batches"
os.makedirs(output_dir, exist_ok=True)

def load_prompt_from_file(filename="healthcalssificationprompt.md"):
    try:    
        with open(filename, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return ""

BASE_PROMPT = load_prompt_from_file("healthcalssificationprompt.md")

def generate_category_csv(category, count):
    # (Same prompt logic as before...)
    try:
        final_prompt = BASE_PROMPT.format(category=category, count=count)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=final_prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                temperature=0.7
            )
        )
        
        data = json.loads(response.text)
        df_temp = pd.DataFrame(data)

        if not df_temp.empty:
            # 1. Look for the columns we want, regardless of what else is there
            # We use a case-insensitive search to be safe
            cols = {c.lower(): c for c in df_temp.columns}
            
            # 2. Extract only the 3 essential fields
            # We use .get() to avoid errors if a column is missing
            notes_col = cols.get('patient_notes', cols.get('notes', df_temp.columns[0]))
            reason_col = cols.get('reasoning', cols.get('reason', df_temp.columns[1]))
            label_col = cols.get('label', cols.get('category', df_temp.columns[2]))
            
            # 3. Create a clean version with exactly 3 columns
            df_clean = df_temp[[notes_col, reason_col, label_col]].copy()
            df_clean.columns = ['patient_notes', 'reasoning', 'label']
            return df_clean

        return df_temp
    except Exception as e:
        print(f"  [!] Generation failed for {category}: {e}")
        return pd.DataFrame()

print("--- Starting Resumable Generation ---")

for cat in categories:
    safe_name = cat.replace("/", "_").lower()
    file_path = os.path.join(output_dir, f"{safe_name}.csv")

    if os.path.exists(file_path):
        print(f"  [~] Skipping {cat}: File exists.")
        continue

    print(f"  [+] Generating {cat}...")
    batch_df = generate_category_csv(cat, 34)
    
    if not batch_df.empty:
        batch_df.to_csv(file_path, index=False)
        print(f"  [✓] Saved {len(batch_df)} samples to {file_path}")
    
    time.sleep(2) 

print("\n--- Merging all categories ---")
all_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".csv")]

if all_files:
    # Read all CSVs and combine
    df_list = [pd.read_csv(f) for f in all_files]
    final_df = pd.concat(df_list, ignore_index=True)
    
    # Standardize column naming one last time before deduplication
    final_df.columns = ['patient_notes', 'reasoning', 'label']
    
    # Remove duplicates and shuffle for the hackathon
    final_df = final_df.drop_duplicates(subset=['patient_notes'])
    final_df = final_df.sample(frac=1).reset_index(drop=True)
    
    final_df.to_csv("hackathon_final_200.csv", index=False)
    print(f"Done! Created master file with {len(final_df)} unique, shuffled samples.")
else:
    print("No files found to merge.")