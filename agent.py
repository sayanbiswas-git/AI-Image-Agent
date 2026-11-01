import argparse
import os
import re
import uuid
import time

from config import RAW_DIR, PROCESSED_DIR, REPORT_PATH
from excel_io import read_food_items, write_report
from image_search import search_food_images, download_image
from image_quality import evaluate_image
from image_processor import process_image
from drive_upload import upload_to_drive

def safe_filename(name: str) -> str:
    return re.sub(r'[\/*?:"<>|]', "", name).strip()

def process_one_item(dish_name: str) -> dict:
    row = {
        "Food Item": dish_name,
        "Image Found": False,
        "Image Processed": False,
        "Uploaded": False,
        "Source": "",
        "Drive Link": "",
        "Status": "Failed",
        "Failure Reason": "",
    }

    candidates = search_food_images(dish_name)
    if not candidates:
        row["Status"] = "Failed"
        row["Failure Reason"] = "No search results returned"
        return row

    chosen_raw_path = None
    chosen_url = None
    unique_id = uuid.uuid4().hex[:6]

    for idx, cand_url in enumerate(candidates):
        safe_name = safe_filename(dish_name)
        raw_target = os.path.join(RAW_DIR, f"{safe_name}_{unique_id}_{idx}.jpg")
        
        if not download_image(cand_url, raw_target):
            continue

        eval_res = evaluate_image(raw_target, dish_name)
        if eval_res.get("accept", False):
            chosen_raw_path = raw_target
            chosen_url = cand_url
            row["Image Found"] = True
            row["Source"] = f'=HYPERLINK("{chosen_url.strip()}", "Source Link")'
            break

    if not chosen_raw_path:
        row["Status"] = "Failed"
        row["Failure Reason"] = "No image passed quality gate"
        return row

    processed_path = os.path.join(PROCESSED_DIR, f"{safe_filename(dish_name)}_{unique_id}.jpg")
    if not process_image(chosen_raw_path, processed_path):
        row["Status"] = "Failed"
        row["Failure Reason"] = "Processing error"
        return row

    row["Image Processed"] = True

    try:
        drive_filename = f"{safe_filename(dish_name)}_{unique_id}.jpg"
        drive_link = upload_to_drive(processed_path, drive_filename)
        if drive_link:
            row["Uploaded"] = True
            row["Drive Link"] = f'=HYPERLINK("{drive_link.strip()}", "Open in Drive")'
            row["Status"] = "Success"
        else:
            row["Status"] = "Failed"
            row["Failure Reason"] = "Upload returned no link"
    except Exception as e:
        row["Status"] = "Failed"
        row["Failure Reason"] = f"Upload error: {e}"

    return row

def run(input_path: str):
    import pandas as pd # Import pandas to read our progress
    
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    dishes = read_food_items(input_path)
    print(f"Loaded {len(dishes)} food items from {input_path}")
    
    results = []
    completed_dishes = set()

    # --- THE FIX: Load memory of what we already did ---
    if os.path.exists(REPORT_PATH):
        try:
            old_df = pd.read_excel(REPORT_PATH)
            for _, row in old_df.iterrows():
                results.append(row.to_dict()) # Keep old data
                if row.get("Status") == "Success":
                    completed_dishes.add(row.get("Food Item"))
            print(f"Found {len(completed_dishes)} already completed dishes. Skipping them!")
        except Exception as e:
            pass
    # --------------------------------------------------

    print("Running in ultra-safe sequential mode to prevent API bans...\n")

    for i, dish in enumerate(dishes, start=1):
        # Skip if already done!
        if dish in completed_dishes:
            print(f"[{i}/{len(dishes)}] Skipping: {dish} (Already processed)")
            continue

        print(f"[{i}/{len(dishes)}] Processing: {dish}...")
        try:
            res = process_one_item(dish)
            results.append(res)
            print(f"   -> Result: {res['Status']} | Reason: {res['Failure Reason']}")
        except Exception as e:
            print(f"   -> Unhandled exception: {e}")
            results.append({"Food Item": dish, "Status": "Failed", "Failure Reason": f"Unhandled exception: {e}"})
        
        time.sleep(2)

    write_report(results, REPORT_PATH)
    print(f"\nDone! Report written to {REPORT_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="restaurant_menu_small.xlsx")
    args = parser.parse_args()
    run(args.input)