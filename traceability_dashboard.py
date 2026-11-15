import json
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

earliest_predictive_handoff = df_ranked.iloc[0]["First_Handoff"] if not df_ranked.empty else "N/A"
highest_risk_sequence = df_ranked.iloc[0]["Sequence"] if not df_ranked.empty else "N/A"
highest_lift = float(df_ranked.iloc[0]["Lift"]) if not df_ranked.empty else 0.0
highest_confidence = float(df_ranked.iloc[0]["Confidence"]) if not df_ranked.empty else 0.0

baseline_json = df_stage_baselines.to_dict(orient="records")
risk_sequences_json = df_ranked.head(50).to_dict(orient="records")
all_stages_json = all_stages

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIH 2026 - Honey Traceability Sequence Mining Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --border: #334155;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --accent: #f59e0b;
            --danger: #ef4444;
            --success: #10b981;
            --info: #3b82f6;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg); color: var(--text-main); padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
        .badge { background: #3b82f620; color: #60a5fa; border: 1px solid #3b82f640; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }
        .grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
        .card-label { font-size: 13px; color: var(--text-sub); text-transform: uppercase; letter-spacing: 0.5px; }
        .card-val { font-size: 28px; font-weight: 700; margin-top: 8px; color: var(--text-main); }
        .card-val.warning { color: var(--accent); }
        .card-val.danger { color: var(--danger); }
        .card-val.success { color: var(--success); }
        .split-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }
        @media(max-width: 900px) { .split-grid { grid-template-columns: 1fr; } }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
        th { text-align: left; padding: 10px; background: #0f172a80; color: var(--text-sub); border-bottom: 1px solid var(--border); }
        td { padding: 10px; border-bottom: 1px solid var(--border); }
        tr:hover { background: #33415540; }
        .seq-pill { background: #f59e0b20; color: #fbbf24; border: 1px solid #f59e0b40; padding: 2px 8px; border-radius: 6px; font-family: monospace; font-size: 12px; }
        .handoff-root { background: #ef444420; color: #f87171; border: 1px solid #ef444440; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; }
        .interactive-section { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 24px; }
        .stages-select-box { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }
        .stage-btn { background: #0f172a; color: var(--text-main); border: 1px solid var(--border); padding: 8px 14px; border-radius: 8px; cursor: pointer; transition: 0.2s; font-size: 12px; }
        .stage-btn:hover { border-color: var(--accent); color: var(--accent); }
        .stage-btn.selected { background: var(--accent); color: #000; font-weight: 600; border-color: var(--accent); }
        .test-result-box { margin-top: 16px; padding: 16px; border-radius: 8px; border: 1px solid var(--border); background: #0f172a60; }
        .alert-high { border-color: var(--danger); background: #ef444415; color: #fca5a5; }
        .alert-safe { border-color: var(--success); background: #10b98115; color: #6ee7b7; }
        .chart-container { position: relative; height: 320px; width: 100%; }
        .table-wrap { max-height: 400px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h2>Honey Traceability Sequence Mining Platform</h2>
            <p style="color: var(--text-sub); font-size: 14px; margin-top: 4px;">Smart India Hackathon 2026 | PS ID: SIH26021 | Ministry of MSME</p>
        </div>
        <div class="badge">Honey Chain Discovery Engine</div>
    </div>

    <div class="grid-cards">
        <div class="card">
            <div class="card-label">Monitored Batches</div>
            <div class="card-val">""" + str(total_batches) + """</div>
        </div>
        <div class="card">
            <div class="card-label">Overall Baseline Failure Rate</div>
            <div class="card-val danger">""" + f"{overall_baseline_failure_rate:.2%}" + """</div>
        </div>
        <div class="card">
            <div class="card-label">Mined High-Risk Sequences</div>
            <div class="card-val warning">""" + str(len(df_ranked)) + """</div>
        </div>
        <div class="card">
            <div class="card-label">Earliest Predictive Handoff</div>
            <div class="card-val" style="font-size: 18px; color: #f87171; line-height: 1.3; margin-top: 14px;">""" + earliest_predictive_handoff + """</div>
        </div>
    </div>

    <div class="split-grid">
        <div class="card">
            <h3 style="margin-bottom: 12px;">Mandatory Per-Stage Baseline Failure Rates</h3>
            <div class="chart-container">
                <canvas id="baselineChart"></canvas>
            </div>
        </div>
        <div class="card">
            <h3 style="margin-bottom: 12px;">Stage Failure Likelihood Breakdown</h3>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Handoff Stage</th>
                            <th>Batches</th>
                            <th>Fails</th>
                            <th>Baseline Rate</th>
                        </tr>
                    </thead>
                    <tbody id="baselineTableBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="card" style="margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h3>Ranked Critical Risk Sequences (Sorted by Lift & Support)</h3>
            <span class="badge" style="background: #ef444420; color: #f87171; border-color: #ef444440;">High Quality Risk Precursors</span>
        </div>
        <div class="table-wrap" style="max-height: 450px;">
            <table>
                <thead>
                    <tr>
                        <th>Handling Sequence Pattern</th>
                        <th>Earliest Predictive Handoff</th>
                        <th>Length</th>
                        <th>Support</th>
                        <th>Confidence</th>
                        <th>Lift</th>
                    </tr>
                </thead>
                <tbody id="riskTableBody"></tbody>
            </table>
        </div>
    </div>

    <div class="interactive-section">
        <h3>Live Traceability Sequence Risk Predictor</h3>
        <p style="color: var(--text-sub); font-size: 13px; margin-top: 4px;">Select an ordered sequence of handoff nodes to predict downstream quality failure probability and check against mined high-risk subsequences.</p>
        <div class="stages-select-box" id="stageButtonsContainer"></div>
        <div style="display: flex; gap: 10px; margin-top: 12px;">
            <button class="stage-btn" style="background: #3b82f6; color: white;" onclick="evaluateCustomSequence()">Evaluate Sequence Risk</button>
            <button class="stage-btn" onclick="clearSelectedStages()">Clear Sequence</button>
        </div>
        <div id="evaluationResult" class="test-result-box" style="display: none;"></div>
    </div>

    <script>
        const baselineData = """ + json.dumps(baseline_json) + """;
        const riskData = """ + json.dumps(risk_sequences_json) + """;
        const allStages = """ + json.dumps(all_stages_json) + """;
        const overallBaseline = """ + str(overall_baseline_failure_rate) + """;

        const tbodyBaseline = document.getElementById("baselineTableBody");
        baselineData.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `<td><b>${item.Stage}</b></td><td>${item.Total_Batches}</td><td>${item.Failed_Batches}</td><td><span style="color: ${item.Baseline_Failure_Rate > overallBaseline ? '#ef4444' : '#10b981'}; font-weight: 600;">${(item.Baseline_Failure_Rate * 100).toFixed(2)}%</span></td>`;
            tbodyBaseline.appendChild(tr);
        });

        const ctx = document.getElementById("baselineChart").getContext("2d");
        new Chart(ctx, {
            type: "bar",
            data: {
                labels: baselineData.map(d => d.Stage),
                datasets: [{
                    label: "Per-Stage Failure Rate (%)",
                    data: baselineData.map(d => (d.Baseline_Failure_Rate * 100).toFixed(2)),
                    backgroundColor: baselineData.map(d => d.Baseline_Failure_Rate > overallBaseline ? "#ef4444" : "#3b82f6"),
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: "#94a3b8" }, grid: { color: "#33415540" } },
                    y: { ticks: { color: "#f8fafc", font: { size: 11 } }, grid: { display: false } }
                }
            }
        });

        const tbodyRisk = document.getElementById("riskTableBody");
        riskData.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><span class="seq-pill">${item.Sequence}</span></td>
                <td><span class="handoff-root">${item.First_Handoff}</span></td>
                <td>${item.Sequence_Length}</td>
                <td>${(item.Support * 100).toFixed(2)}% (${item.Support_Count})</td>
                <td><b style="color: #f59e0b;">${(item.Confidence * 100).toFixed(2)}%</b></td>
                <td><b style="color: #ef4444;">${item.Lift.toFixed(2)}x</b></td>
            `;
            tbodyRisk.appendChild(tr);
        });

        let currentSequence = [];
        const btnContainer = document.getElementById("stageButtonsContainer");
        allStages.forEach(stage => {
            const btn = document.createElement("button");
            btn.className = "stage-btn";
            btn.textContent = "+ " + stage;
            btn.onclick = () => {
                currentSequence.push(stage);
                renderSelectedStages();
            };
            btnContainer.appendChild(btn);
        });

        function renderSelectedStages() {
            const resBox = document.getElementById("evaluationResult");
            if (currentSequence.length === 0) {
                resBox.style.display = "none";
                return;
            }
            resBox.style.display = "block";
            resBox.className = "test-result-box";
            resBox.innerHTML = `<b>Current Handling Pathway:</b><br><div style="margin-top: 8px;"><span class="seq-pill">${currentSequence.join(" &rarr; ")}</span></div>`;
        }

        function clearSelectedStages() {
            currentSequence = [];
            renderSelectedStages();
        }

        function isSubsequence(sub, seq) {
            let i = 0;
            for (let j = 0; j < seq.length && i < sub.length; j++) {
                if (seq[j] === sub[i]) i++;
            }
            return i === sub.length;
        }

        function evaluateCustomSequence() {
            const resBox = document.getElementById("evaluationResult");
            if (currentSequence.length === 0) {
                alert("Please add at least one stage to evaluate.");
                return;
            }
            let matchingRisks = [];
            riskData.forEach(risk => {
                if (isSubsequence(risk.Sequence_List, currentSequence)) {
                    matchingRisks.push(risk);
                }
            });

            resBox.style.display = "block";
            if (matchingRisks.length > 0) {
                matchingRisks.sort((a, b) => b.Lift - a.Lift);
                const worst = matchingRisks[0];
                resBox.className = "test-result-box alert-high";
                resBox.innerHTML = `
                    <div style="font-size: 16px; font-weight: 700; color: #ef4444; margin-bottom: 8px;">
                        CRITICAL QUALITY RISK DETECTED
                    </div>
                    <div><b>Pathway:</b> <span class="seq-pill">${currentSequence.join(" &rarr; ")}</span></div>
                    <div style="margin-top: 8px;"><b>Matched High-Risk Subsequence:</b> <span style="color: #fbbf24;">${worst.Sequence}</span></div>
                    <div style="margin-top: 6px;"><b>Earliest Predictive Handoff:</b> <span class="handoff-root">${worst.First_Handoff}</span></div>
                    <div style="margin-top: 6px;"><b>Downstream Failure Probability (Confidence):</b> ${(worst.Confidence * 100).toFixed(2)}%</div>
                    <div style="margin-top: 4px;"><b>Risk Multiplier (Lift vs Baseline):</b> ${worst.Lift.toFixed(2)}x Baseline Failure Rate</div>
                `;
            } else {
                resBox.className = "test-result-box alert-safe";
                resBox.innerHTML = `
                    <div style="font-size: 16px; font-weight: 700; color: #10b981; margin-bottom: 8px;">
                        ACCEPTABLE SEQUENCE (LOW PREDICTED FAILURE RISK)
                    </div>
                    <div><b>Pathway:</b> <span class="seq-pill">${currentSequence.join(" &rarr; ")}</span></div>
                    <div style="margin-top: 8px;">No known high-lift failure patterns detected in this sequence. Expected failure rate remains below critical threshold.</div>
                `;
            }
        }
    </script>
</body>
</html>
"""

dashboard_file_path = "honey_traceability_dashboard.html"
with open(dashboard_file_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print("=" * 80)
print(f"TRACEABILITY DASHBOARD SUCCESSFULLY GENERATED: {dashboard_file_path}")
print(f"Total Batches Processed: {total_batches}")
print(f"Overall Baseline Failure Rate: {overall_baseline_failure_rate:.4f}")
print(f"Earliest Predictive Handoff: {earliest_predictive_handoff}")
print("=" * 80)

