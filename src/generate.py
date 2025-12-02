import pandas as pd
import json
from pathlib import Path

DATA_PATH = "data/players.csv"
CONFIG_PATH = "data/filters.json"
OUTPUT_DIR = Path("output/json")

def clean_value(val):
    if pd.isna(val):
        return None
    if isinstance(val, float) and val != val:
        return None
    return val

def generate_json_files():
    df = pd.read_csv(DATA_PATH, low_memory=False)

    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    generated_count = 0

    for item in config["filters"]:
        filename = item["file"]
        cond_str = item["cond"]
        sort_key = item["sort"]
        limit = item.get("limit")
        
        try:
            data = df.query(cond_str)
        except Exception as e:
            try:
                if "notna()" in cond_str:
                    col = cond_str.split(".")[0]
                    data = df[df[col].notna()]
                elif "isnull()" in cond_str:
                    col = cond_str.split(".")[0]
                    data = df[df[col].isnull() & (df["overall"] >= 75)] # Special free agent handling
                elif "potential - overall" in cond_str:
                     data = df[(df["potential"] - df["overall"]) >= 15] # No age limit here, applied later
                else:
                    data = df.query(cond_str)
            except:
                print(f"Error applying filter for {filename}: {e}. Skipping.")
                continue
        if "bargain" in filename:
            bargain_conf = config.get("bargain", {})
            max_val = bargain_conf.get("max_value_eur", 15_000_000)
            min_ovr = bargain_conf.get("min_overall", 82)
            data = data[(data["value_eur"] <= max_val) & (data["value_eur"] > 0) & (data["overall"] >= min_ovr)]
        data = data.sort_values(by=sort_key, ascending=False)
        if limit:
            data = data.head(limit)
        records = data.to_dict(orient="records")
        cleaned_records = []
        for record in records:
            cleaned = {k: clean_value(v) for k, v in record.items()}
            cleaned_records.append(cleaned)
        with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
            json.dump(cleaned_records, f, ensure_ascii=False, indent=None)
        generated_count += 1
    print(f"{generated_count} perfect JSON files generated (NaN -> null)")
if __name__ == "__main__":
    generate_json_files()