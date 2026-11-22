# Honey Chain: AI Sequence Mining in Honey Traceability Records

[![Smart India Hackathon 2026](https://img.shields.io/badge/SIH-2026-orange.svg)](https://sih.gov.in)
[![Problem Statement](https://img.shields.io/badge/PS%20ID-SIH26021-blue.svg)](https://sih.gov.in)
[![Ministry](https://img.shields.io/badge/Ministry-MSME-green.svg)](https://msme.gov.in)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb.svg)](https://react.dev)
[![PrefixSpan](https://img.shields.io/badge/Mining-PrefixSpan-yellow.svg)](https://github.com/chuanconggao/PrefixSpan-py)

> **Honey Chain**: A blockchain-based system for honey traceability and smart beekeeping management with sequential pattern mining discovery for downstream quality problem prevention.

---

## Executive Overview

Traceability systems record chronological handoffs across beekeepers, field transit, heating vats, warehouses, testing labs, and packaging lines. However, standard classifiers fail to model multi-stage degradation chains:
1. **Order-Blind ML (Bag-of-Stages)** treats stage presence without chronological order, suffering from low recall (23.5%).
2. **Black-Box Deep Learning** outputs failure probabilities but cannot provide regulatory root-cause attribution to isolate negligent contractors.
3. **Honey Chain Sequence Mining Engine (PrefixSpan + Lift Ranker)** mines high-lift sequential patterns, calculates Support, Confidence, and Lift over baseline, and programmatically isolates the **Earliest Predictive Handoff** to trigger automated blockchain smart contract escrow locks.

---

## 3-Model Benchmark Comparison (Zero Overfitting / Underfitting)

All models were evaluated on an **unseen 80/20 stratified split** (960 train / 240 test batches). Regularized parameters ensure a generalization gap **under 6%** across all models:

| Model Paradigm | Train Accuracy | Test Accuracy (Unseen) | Generalization Gap | Precision | Recall | F1-Score | Fit Assessment |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model 1: Unordered Bag-of-Stages** *(Random Forest)* | 78.44% | **76.25%** | **2.19%** | 76.19% | 23.53% | 35.96% | **Optimal (Balanced)** |
| **Model 2: Sequential N-Gram ML** *(Gradient Boosting)* | 82.08% | **76.25%** | **5.83%** | 66.67% | 32.35% | 43.56% | **Optimal (Balanced)** |
| **Model 3: Sequential Mining Discovery** *(PrefixSpan + Lift)* | 74.17% | **69.58%** | **4.58%** | 46.75% | **52.94%** | **49.66%** | **Optimal (Balanced)** |

### Key Discovery Finding:
* **Highest-Risk Handling Sequence**:  
  `Solar_Exposed_Transit` $\to$ `High_Heat_Liquefaction` $\to$ `Cold_Storage_Holding` $\to$ `Bulk_Export_Drumming`
* **Risk Multiplier (Lift)**: **3.29x** over normal baseline failure rate.
* **Earliest Predictive Handoff**: `Solar_Exposed_Transit` (initiating upstream trigger).

---

## System Architecture

```
c:\Projects\unsupervised\
├── backend/
│   ├── app/
│   │   ├── dataset.py               # Data ingestion & unconditional baseline calculator
│   │   ├── trainer.py               # 80/20 stratified training & benchmark pipeline
│   │   ├── main.py                  # FastAPI server with dual REST & React static hosting
│   │   └── models/
│   │       ├── baseline_model.py    # Model 1: CountVectorizer + Regularized RF
│   │       ├── ngram_model.py       # Model 2: (1,3)-Gram TF-IDF + GBDT
│   │       └── prefixspan_model.py  # Model 3: PrefixSpan + Lift Ranker Engine
│   └── artifacts/
│       ├── benchmark_metrics.json   # Serialized benchmark scorecard
│       ├── model_baseline.joblib
│       ├── model_ngram.joblib
│       └── model_prefixspan.json
├── frontend/                        # React 18 + Vite dashboard
│   ├── src/components/
│   │   ├── Navbar.jsx               # Tab navigation & live retrain trigger
│   │   ├── BenchmarkView.jsx        # Model comparison matrix & confusion matrices
│   │   ├── SimulatorView.jsx        # Interactive pathway builder & root-cause highlighter
│   │   ├── BaselinesView.jsx        # Mandatory unconditional per-stage failure rates
│   │   ├── MinedRulesView.jsx       # Searchable PrefixSpan rules (Support, Conf, Lift)
│   │   └── BlockchainView.jsx       # SHA-256 Honey Chain blocks & smart contract escrow
│   └── dist/                        # Production compiled frontend bundle
├── start_system.bat                 # One-click Windows batch launcher
├── start_system.ps1                 # One-click PowerShell launcher
└── FACULTY_PRESENTATION_GUIDE.md    # Presentation script & defense guide
```

---

## Quickstart Guide

### 1. One-Click Launch (All-in-One Presentation Mode)
Run the PowerShell launcher:
```powershell
.\start_system.ps1
```
*Or double-click `start_system.bat` in Windows Explorer.*

Access the full interactive dashboard at:
```
http://localhost:8000
```

### 2. Manual Installation & Development Mode

#### Backend Setup
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Set python path and start FastAPI
$env:PYTHONPATH = "backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Development (Vite Hot-Reloading)
```bash
cd frontend
npm install
npm run dev
```
Access the Vite dev server at `http://localhost:5173` (requests automatically proxy to `:8000`).

---

## API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/benchmark` | Comparative evaluation metrics & confusion matrices |
| `GET` | `/api/baselines` | Mandatory per-stage baseline failure rates |
| `GET` | `/api/mined-rules` | Top mined PrefixSpan sequential rules with Lift |
| `POST` | `/api/predict` | Multi-model consensus prediction & root-cause detection |
| `GET` | `/api/blockchain` | Cryptographic SHA-256 Honey Chain audit ledger |
| `POST` | `/api/blockchain/record`| Commit new handoff block & trigger smart contract checks |
| `POST` | `/api/retrain` | Retrain all 3 models and recompute metrics |

---

## License

Developed for **Smart India Hackathon 2026** (Problem Statement ID: **SIH26021**).  
Ministry of Micro, Small & Medium Enterprises (MSME).
