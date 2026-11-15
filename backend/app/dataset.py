import os
import random
import pandas as pd

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_honey_traceability.csv")

def ensure_dataset(file_path=None):
    if file_path is None:
        file_path = DATASET_PATH
    
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    if os.path.exists(file_path):
        return file_path
        
    random.seed(42)
    harvest_stages = ["Apiary_Harvest_Modern", "Apiary_Harvest_Traditional", "Cooperative_Collection"]
    transit_stages = ["Cold_Chain_Transit", "Ambient_Trucking", "Solar_Exposed_Transit"]
    processing_stages = ["Vacuum_Dehydration", "High_Heat_Liquefaction", "Gentle_Centrifugation", "Enzyme_Safe_Filtration"]
    storage_stages = ["Cold_Storage_Holding", "Ambient_Warehouse", "Galvanized_Drum_Storage"]
    testing_stages = ["NMR_Testing_Passed", "Pollen_Analysis_Passed", "Testing_Bypassed"]
    packaging_stages = ["Glass_Jar_Bottling", "Bulk_Export_Drumming"]
    
    records = []
    for idx in range(1, 1201):
        batch_id = f"HONEY-BATCH-{idx:04d}"
        h = random.choice(harvest_stages)
        t = random.choice(transit_stages)
        p = random.choice(processing_stages)
        s = random.choice(storage_stages)
        test = random.choice(testing_stages)
        pack = random.choice(packaging_stages)
        seq = [h, t, p, s, test, pack]
        
        prob = 0.04
        if t == "Solar_Exposed_Transit" and p == "High_Heat_Liquefaction":
            prob += 0.65
        elif p == "High_Heat_Liquefaction" and s == "Ambient_Warehouse":
            prob += 0.55
        elif s == "Galvanized_Drum_Storage":
            prob += 0.35
        elif test == "Testing_Bypassed":
            prob += 0.30
            
        fail = 1 if random.random() < min(prob, 0.98) else 0
        records.append({"Batch_ID": batch_id, "Handling_Sequence": ",".join(seq), "Quality_Failure": fail})
        
    df = pd.DataFrame(records)
    df.to_csv(file_path, index=False)
    return file_path

def load_preprocessed_data(file_path=None):
    target_path = ensure_dataset(file_path)
    df = pd.read_csv(target_path)
    df["Handling_Sequence"] = df["Handling_Sequence"].astype(str)
    df["Sequence_List"] = df["Handling_Sequence"].apply(
        lambda s: [item.strip() for item in s.split(",") if item.strip()]
    )
    df["Sequence_Text"] = df["Sequence_List"].apply(lambda items: " ".join(items))
    return df

def compute_per_stage_baselines(df):
    total_batches = len(df)
    overall_failure_rate = float(df["Quality_Failure"].mean())
    all_stages = sorted(list({stage for seq in df["Sequence_List"] for stage in seq}))
    
    records = []
    for stage in all_stages:
        mask = df["Sequence_List"].apply(lambda seq: stage in seq)
        batch_count = int(mask.sum())
        fail_count = int((mask & (df["Quality_Failure"] == 1)).sum())
        rate = (fail_count / batch_count) if batch_count > 0 else 0.0
        records.append({
            "Stage": stage,
            "Total_Batches": batch_count,
            "Failed_Batches": fail_count,
            "Baseline_Failure_Rate": round(rate, 4),
            "Elevated_Risk": rate > overall_failure_rate
        })
        
    df_baselines = pd.DataFrame(records).sort_values(by="Baseline_Failure_Rate", ascending=False).reset_index(drop=True)
    return {
        "overall_baseline_failure_rate": round(overall_failure_rate, 4),
        "total_batches": total_batches,
        "total_failures": int(df["Quality_Failure"].sum()),
        "stage_baselines": df_baselines.to_dict(orient="records")
    }

