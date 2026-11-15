import hashlib
import json
import os
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.models.baseline_model import BaselineBagOfStagesModel
from app.models.ngram_model import SequentialNGramModel
from app.models.prefixspan_model import SequentialPrefixSpanModel
from app.trainer import train_and_benchmark_all, ARTIFACTS_DIR

app = FastAPI(
    title="Honey Chain Sequence Mining Discovery API",
    description="Smart India Hackathon 2026 (SIH26021) - Traceability Sequence Risk Discovery Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SequencePredictRequest(BaseModel):
    sequence: List[str]

class BlockchainRecordRequest(BaseModel):
    batch_id: str
    stage: str
    sequence: Optional[List[str]] = None

model_baseline = None
model_ngram = None
model_prefixspan = None

blockchain_ledger = [
    {
        "index": 0,
        "timestamp": 1773000000.0,
        "batch_id": "GENESIS",
        "stage": "HoneyChain_Genesis",
        "status": "APPROVED",
        "smart_contract_action": "Initial ledger genesis verification complete",
        "previous_hash": "0" * 64,
        "hash": hashlib.sha256("HONEY_CHAIN_GENESIS_ROOT".encode("utf-8")).hexdigest()
    }
]

def add_blockchain_record(batch_id, stage, status, action):
    prev_block = blockchain_ledger[-1]
    ts = time.time()
    raw = f"{len(blockchain_ledger)}:{ts}:{batch_id}:{stage}:{status}:{prev_block['hash']}"
    cur_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    block = {
        "index": len(blockchain_ledger),
        "timestamp": ts,
        "batch_id": batch_id,
        "stage": stage,
        "status": status,
        "smart_contract_action": action,
        "previous_hash": prev_block["hash"],
        "hash": cur_hash
    }
    blockchain_ledger.append(block)
    return block

def get_or_load_models():
    global model_baseline, model_ngram, model_prefixspan
    baseline_path = os.path.join(ARTIFACTS_DIR, "model_baseline.joblib")
    ngram_path = os.path.join(ARTIFACTS_DIR, "model_ngram.joblib")
    prefixspan_path = os.path.join(ARTIFACTS_DIR, "model_prefixspan.json")
    
    if not (os.path.exists(baseline_path) and os.path.exists(ngram_path) and os.path.exists(prefixspan_path)):
        train_and_benchmark_all()
        
    if model_baseline is None:
        model_baseline = BaselineBagOfStagesModel().load(baseline_path)
    if model_ngram is None:
        model_ngram = SequentialNGramModel().load(ngram_path)
    if model_prefixspan is None:
        model_prefixspan = SequentialPrefixSpanModel().load(prefixspan_path)
        
    return model_baseline, model_ngram, model_prefixspan

@app.on_event("startup")
def startup_event():
    get_or_load_models()

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "Honey Chain Sequence Mining API"}

@app.get("/api/benchmark")
def get_benchmark():
    metrics_path = os.path.join(ARTIFACTS_DIR, "benchmark_metrics.json")
    if not os.path.exists(metrics_path):
        train_and_benchmark_all()
    with open(metrics_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/baselines")
def get_baselines():
    data = get_benchmark()
    return {
        "overall_baseline_failure_rate": data["metadata"]["overall_failure_rate"],
        "stage_baselines": data["stage_baselines"]
    }

@app.get("/api/mined-rules")
def get_mined_rules():
    data = get_benchmark()
    return {
        "earliest_predictive_handoff": data["earliest_predictive_handoff"],
        "highest_risk_sequence": data["highest_risk_sequence"],
        "mined_rules": data["mined_rules"]
    }

@app.get("/api/stages")
def get_available_stages():
    data = get_benchmark()
    stages = [item["Stage"] for item in data["stage_baselines"]]
    return {"stages": stages}

@app.get("/api/blockchain")
def get_blockchain_ledger():
    return {"ledger": blockchain_ledger, "total_blocks": len(blockchain_ledger)}

@app.post("/api/blockchain/record")
def record_handoff(req: BlockchainRecordRequest):
    m1, m2, m3 = get_or_load_models()
    seq = req.sequence or [req.stage]
    eval_res = m3.predict_sequence(seq)
    
    if eval_res["risk_status"] == "CRITICAL_RISK":
        status = "FLAGGED_HIGH_RISK"
        action = f"Escrow Locked: Smart contract halted payment release. Root trigger detected at '{eval_res['earliest_predictive_handoff']}'."
    else:
        status = "COMPLIANT_APPROVED"
        action = "Automated Handoff Verified: Escrow balance transitioned to next milestone."
        
    block = add_blockchain_record(req.batch_id, req.stage, status, action)
    return {"message": "Handoff successfully mined on HoneyChain", "block": block, "evaluation": eval_res}

@app.post("/api/predict")
def predict_sequence(req: SequencePredictRequest):
    if not req.sequence:
        raise HTTPException(status_code=400, detail="Sequence cannot be empty")
        
    m1, m2, m3 = get_or_load_models()
    
    res_m1 = m1.evaluate_sequence(req.sequence)
    res_m2 = m2.evaluate_sequence(req.sequence)
    res_m3 = m3.predict_sequence(req.sequence)
    
    consensus_risk = (res_m1["predicted_failure"] + res_m2["predicted_failure"] + res_m3["predicted_failure"]) >= 2
    avg_probability = round((res_m1["failure_probability"] + res_m2["failure_probability"] + res_m3["failure_probability"]) / 3.0, 4)
    
    return {
        "sequence": req.sequence,
        "consensus_risk": "HIGH_RISK" if consensus_risk else "LOW_RISK",
        "average_failure_probability": avg_probability,
        "earliest_predictive_handoff": res_m3["earliest_predictive_handoff"],
        "smart_contract_recommendation": res_m3["smart_contract_action"],
        "model_comparisons": {
            "model_1_baseline": res_m1,
            "model_2_ngram": res_m2,
            "model_3_prefixspan": res_m3
        }
    }

@app.post("/api/retrain")
def retrain_models():
    new_metrics = train_and_benchmark_all()
    global model_baseline, model_ngram, model_prefixspan
    model_baseline = None
    model_ngram = None
    model_prefixspan = None
    get_or_load_models()
    return {"message": "Retraining completed successfully", "metrics": new_metrics["models"]}

dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")
