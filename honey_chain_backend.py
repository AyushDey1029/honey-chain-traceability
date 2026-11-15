import hashlib
import json
import os
import random
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
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
            "Baseline_Failure_Rate": round(stage_fail_rate, 4),
        }
    )

df_stage_baselines = pd.DataFrame(stage_baseline_records).sort_values(
    by="Baseline_Failure_Rate", ascending=False
).reset_index(drop=True)

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
            "Sequence_List": pattern,
            "Sequence_Length": len(pattern),
            "First_Handoff": pattern[0],
            "Support": round(support, 4),
            "Support_Count": count_fail,
            "Total_Batches": count_total,
            "Confidence": round(confidence, 4),
            "Lift": round(lift, 4),
        }
    )

df_risk_sequences = pd.DataFrame(metrics_records)
df_ranked = df_risk_sequences.sort_values(
    by=["Lift", "Support", "Confidence"], ascending=[False, False, False]
).reset_index(drop=True)

df_elevated_risks = df_ranked[df_ranked["Lift"] >= 1.5].reset_index(drop=True)

earliest_predictive_handoff = df_ranked.iloc[0]["First_Handoff"] if not df_ranked.empty else "N/A"
highest_risk_sequence = df_ranked.iloc[0]["Sequence"] if not df_ranked.empty else "N/A"

blockchain_ledger = []
genesis_block = {
    "index": 0,
    "timestamp": time.time(),
    "batch_id": "GENESIS",
    "stage": "HoneyChain_Genesis",
    "previous_hash": "0" * 64,
    "hash": hashlib.sha256("GENESIS_BLOCK".encode("utf-8")).hexdigest(),
}
blockchain_ledger.append(genesis_block)

def add_blockchain_record(batch_id, stage):
    prev_block = blockchain_ledger[-1]
    raw_payload = f"{len(blockchain_ledger)}:{time.time()}:{batch_id}:{stage}:{prev_block['hash']}"
    block_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
    new_block = {
        "index": len(blockchain_ledger),
        "timestamp": time.time(),
        "batch_id": batch_id,
        "stage": stage,
        "previous_hash": prev_block["hash"],
        "hash": block_hash,
    }
    blockchain_ledger.append(new_block)
    return new_block

def evaluate_batch_sequence(sequence):
    matched_risks = []
    for _, row in df_elevated_risks.iterrows():
        if is_subsequence(row["Sequence_List"], sequence):
            matched_risks.append(row.to_dict())

    if matched_risks:
        worst_pattern = matched_risks[0]
        root_cause = worst_pattern["First_Handoff"]
        confidence = worst_pattern["Confidence"]
        lift = worst_pattern["Lift"]
        status = "CRITICAL_RISK"
        recommendation = f"Halt packaging. Trigger mandatory NMR spectroscopic analysis. Root trigger: {root_cause}."
    else:
        worst_pattern = None
        root_cause = None
        confidence = overall_baseline_failure_rate
        lift = 1.0
        status = "SAFE_LOW_RISK"
        recommendation = "Sequence complies with standard handling guidelines. Proceed to automated dispatch."

    return {
        "status": status,
        "sequence": sequence,
        "matched_critical_patterns_count": len(matched_risks),
        "worst_risk_pattern": worst_pattern,
        "earliest_predictive_handoff": root_cause,
        "predicted_failure_probability": round(confidence, 4),
        "risk_lift_multiplier": round(lift, 4),
        "recommended_intervention": recommendation,
    }

class HoneyChainRequestHandler(BaseHTTPRequestHandler):
    def _send_json_response(self, data, status_code=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "/dashboard":
            if os.path.exists("honey_traceability_dashboard.html"):
                with open("honey_traceability_dashboard.html", "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self._send_json_response({"error": "Dashboard not found. Run dashboard generator first."}, 404)
        elif self.path == "/api/status":
            self._send_json_response(
                {
                    "system": "Honey Chain Sequence Mining Discovery Engine",
                    "hackathon": "Smart India Hackathon 2026",
                    "problem_statement_id": "SIH26021",
                    "ministry": "Ministry of MSME",
                    "total_batches_analyzed": total_batches,
                    "overall_baseline_failure_rate": round(overall_baseline_failure_rate, 4),
                    "mined_critical_sequences_count": len(df_ranked),
                    "elevated_risk_patterns_count": len(df_elevated_risks),
                    "earliest_predictive_handoff": earliest_predictive_handoff,
                    "highest_risk_sequence": highest_risk_sequence,
                }
            )
        elif self.path == "/api/baselines":
            self._send_json_response(df_stage_baselines.to_dict(orient="records"))
        elif self.path == "/api/risk-sequences":
            self._send_json_response(df_ranked.head(50).to_dict(orient="records"))
        elif self.path == "/api/blockchain":
            self._send_json_response(blockchain_ledger)
        else:
            self._send_json_response({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except Exception:
            self._send_json_response({"error": "Invalid JSON"}, 400)
            return

        if self.path == "/api/evaluate-batch":
            sequence = payload.get("sequence", [])
            if not isinstance(sequence, list) or not sequence:
                self._send_json_response({"error": "Payload must include a non-empty sequence list"}, 400)
                return
            result = evaluate_batch_sequence(sequence)
            self._send_json_response(result)
        elif self.path == "/api/record-handoff":
            batch_id = payload.get("batch_id")
            stage = payload.get("stage")
            if not batch_id or not stage:
                self._send_json_response({"error": "Payload must include batch_id and stage"}, 400)
                return
            block = add_blockchain_record(batch_id, stage)
            self._send_json_response({"message": "Handoff recorded on HoneyChain ledger", "block": block})
        else:
            self._send_json_response({"error": "Endpoint not found"}, 404)

def run_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, HoneyChainRequestHandler)
    print("=" * 80)
    print(f"HONEY CHAIN TRACEABILITY ENGINE ACTIVE AT http://localhost:{port}/")
    print(f"Earliest Predictive Handoff: {earliest_predictive_handoff}")
    print("=" * 80)
    return httpd

if __name__ == "__main__":
    server = run_server(8080)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

