import os
import random
import pandas as pd

if not os.path.exists("synthetic_honey_traceability.csv"):
    random.seed(42)
    harvest_stages = ["Apiary_Harvest_Modern", "Apiary_Harvest_Traditional", "Cooperative_Collection"]
    transit_stages = ["Cold_Chain_Transit", "Ambient_Trucking", "Solar_Exposed_Transit"]
    processing_stages = ["Vacuum_Dehydration", "High_Heat_Liquefaction", "Gentle_Centrifugation", "Enzyme_Safe_Filtration"]
    storage_stages = ["Cold_Storage_Holding", "Ambient_Warehouse", "Galvanized_Drum_Storage"]
    testing_stages = ["NMR_Testing_Passed", "Pollen_Analysis_Passed", "Testing_Bypassed"]
    packaging_stages = ["Glass_Jar_Bottling", "Bulk_Export_Drumming"]
    data = []
    for idx in range(1, 1001):
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
        data.append({"Batch_ID": batch_id, "Handling_Sequence": ",".join(seq), "Quality_Failure": fail})
    pd.DataFrame(data).to_csv("synthetic_honey_traceability.csv", index=False)

df = pd.read_csv("synthetic_honey_traceability.csv")
df["Handling_Sequence"] = df["Handling_Sequence"].astype(str)
df["Sequence_List"] = df["Handling_Sequence"].apply(
    lambda seq_str: [item.strip() for item in seq_str.split(",") if item.strip()]
)

total_batches = len(df)
total_failures = int(df["Quality_Failure"].sum())
overall_baseline_failure_rate = float(df["Quality_Failure"].mean())

all_stages = sorted(list({stage for seq in df["Sequence_List"] for stage in seq}))
stage_baseline_records = []
for stage in all_stages:
    mask = df["Sequence_List"].apply(lambda seq: stage in seq)
    stage_batch_count = int(mask.sum())
    stage_fail_count = int((mask & (df["Quality_Failure"] == 1)).sum())
    stage_fail_rate = (stage_fail_count / stage_batch_count) if stage_batch_count > 0 else 0.0
    stage_baseline_records.append(
        {
            "Stage": stage,
            "Total_Batches": stage_batch_count,
            "Failed_Batches": stage_fail_count,
            "Baseline_Failure_Rate": stage_fail_rate,
        }
    )

df_stage_baselines = pd.DataFrame(stage_baseline_records).sort_values(
    by="Baseline_Failure_Rate", ascending=False
).reset_index(drop=True)

print("=" * 80)
print(f"OVERALL BASELINE FAILURE RATE: {overall_baseline_failure_rate:.4f} ({total_failures}/{total_batches} batches)")
print("=" * 80)
print("MANDATORY BASELINE PER-STAGE FAILURE RATES:")
print(df_stage_baselines.to_string(index=False))
print("=" * 80)

try:
    from prefixspan import PrefixSpan
except ImportError:
    class PrefixSpan:
        def __init__(self, db):
            self.db = db
            self.minlen = 1
            self.maxlen = 1000

        def frequent(self, minsup):
            results = []

            def _mine(projected_db, prefix):
                if len(prefix) >= self.minlen:
                    results.append((len(projected_db), prefix))
                if len(prefix) >= self.maxlen:
                    return
                items = {}
                for seq, start_idx in projected_db:
                    seen = set()
                    for i in range(start_idx, len(seq)):
                        item = seq[i]
                        if item not in seen:
                            seen.add(item)
                            if item not in items:
                                items[item] = []
                            items[item].append((seq, i + 1))
                for item, new_proj in items.items():
                    if len(new_proj) >= minsup:
                        _mine(new_proj, prefix + [item])

            initial_items = {}
            for seq in self.db:
                seen = set()
                for i, item in enumerate(seq):
                    if item not in seen:
                        seen.add(item)
                        if item not in initial_items:
                            initial_items[item] = []
                        initial_items[item].append((seq, i + 1))

            for item, new_proj in initial_items.items():
                if len(new_proj) >= minsup:
                    _mine(new_proj, [item])

            return results

failed_batches_df = df[df["Quality_Failure"] == 1]
failed_sequences = failed_batches_df["Sequence_List"].tolist()

ps = PrefixSpan(failed_sequences)
ps.minlen = 2
min_support_count = max(5, int(len(failed_sequences) * 0.05))
mined_patterns = ps.frequent(min_support_count)

def is_subsequence(sub, seq):
    it = iter(seq)
    return all(x in it for x in sub)

metrics_records = []
seen_patterns = set()

for sup_fail, pattern in mined_patterns:
    if len(pattern) < 2:
        continue
    pattern_tuple = tuple(pattern)
    if pattern_tuple in seen_patterns:
        continue
    seen_patterns.add(pattern_tuple)

    is_in_batch = df["Sequence_List"].apply(lambda seq: is_subsequence(pattern, seq))
    count_total = int(is_in_batch.sum())
    count_fail = int((is_in_batch & (df["Quality_Failure"] == 1)).sum())

    confidence = (count_fail / count_total) if count_total > 0 else 0.0
    lift = (confidence / overall_baseline_failure_rate) if overall_baseline_failure_rate > 0 else 0.0
    support = count_fail / total_batches

    metrics_records.append(
        {
            "Sequence": " -> ".join(pattern),
            "Sequence_Length": len(pattern),
            "First_Handoff": pattern[0],
            "Support": support,
            "Support_Count": count_fail,
            "Total_Batches": count_total,
            "Confidence": confidence,
            "Lift": lift,
        }
    )

df_risk_sequences = pd.DataFrame(metrics_records)
df_ranked = df_risk_sequences.sort_values(
    by=["Lift", "Support", "Confidence"], ascending=[False, False, False]
).reset_index(drop=True)

print("TOP 15 CRITICAL RISK SEQUENCES:")
print(df_ranked.head(15).to_string(index=False))
print("=" * 80)

if not df_ranked.empty:
    highest_risk_row = df_ranked.iloc[0]
    earliest_predictive_handoff = highest_risk_row["First_Handoff"]
    print("HIGHEST-RISK SEQUENCE:", highest_risk_row["Sequence"])
    print("LIFT:", f"{highest_risk_row['Lift']:.4f}")
    print("CONFIDENCE:", f"{highest_risk_row['Confidence']:.4f}")
    print("SUPPORT:", f"{highest_risk_row['Support']:.4f}", f"({highest_risk_row['Support_Count']} failed batches)")
    print("EARLIEST PREDICTIVE HANDOFF:", earliest_predictive_handoff)
    print("=" * 80)

