import json
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from app.dataset import load_preprocessed_data, compute_per_stage_baselines
from app.models.baseline_model import BaselineBagOfStagesModel
from app.models.ngram_model import SequentialNGramModel
from app.models.prefixspan_model import SequentialPrefixSpanModel

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

def train_and_benchmark_all():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    df = load_preprocessed_data()
    baselines_info = compute_per_stage_baselines(df)
    
    X_text = df["Sequence_Text"].values
    X_seqs = df["Sequence_List"].values
    y = df["Quality_Failure"].values
    
    X_text_train, X_text_test, X_seqs_train, X_seqs_test, y_train, y_test = train_test_split(
        X_text, X_seqs, y, test_size=0.20, random_state=42, stratify=y
    )
    
    model_baseline = BaselineBagOfStagesModel()
    model_baseline.fit(X_text_train, y_train)
    model_baseline.save(os.path.join(ARTIFACTS_DIR, "model_baseline.joblib"))
    
    model_ngram = SequentialNGramModel()
    model_ngram.fit(X_text_train, y_train)
    model_ngram.save(os.path.join(ARTIFACTS_DIR, "model_ngram.joblib"))
    
    model_prefixspan = SequentialPrefixSpanModel(
        min_support_ratio=0.04,
        min_len=2,
        max_len=5,
        lift_threshold=1.8,
        min_confidence=0.55
    )
    model_prefixspan.fit(X_seqs_train, y_train)
    model_prefixspan.save(os.path.join(ARTIFACTS_DIR, "model_prefixspan.json"))
    
    models = [
        ("model_1_baseline", "Model 1: Unordered Bag-of-Stages (Random Forest)", model_baseline, X_text_train, X_text_test, "text"),
        ("model_2_ngram", "Model 2: Sequential N-Gram ML (Gradient Boosting)", model_ngram, X_text_train, X_text_test, "text"),
        ("model_3_prefixspan", "Model 3: Sequential Mining Discovery (PrefixSpan + Lift)", model_prefixspan, X_seqs_train, X_seqs_test, "seq")
    ]
    
    benchmark_results = {}
    
    for key, name, model, x_tr, x_te, m_type in models:
        y_train_pred = model.predict(x_tr)
        y_test_pred = model.predict(x_te)
        
        y_train_proba = model.predict_proba(x_tr)[:, 1] if hasattr(model, "predict_proba") else y_train_pred
        y_test_proba = model.predict_proba(x_te)[:, 1] if hasattr(model, "predict_proba") else y_test_pred
        
        train_acc = float(accuracy_score(y_train, y_train_pred))
        test_acc = float(accuracy_score(y_test, y_test_pred))
        
        test_prec = float(precision_score(y_test, y_test_pred, zero_division=0))
        test_rec = float(recall_score(y_test, y_test_pred, zero_division=0))
        test_f1 = float(f1_score(y_test, y_test_pred, zero_division=0))
        
        try:
            test_auc = float(roc_auc_score(y_test, y_test_proba))
        except Exception:
            test_auc = 0.5
            
        cm = confusion_matrix(y_test, y_test_pred).tolist()
        
        acc_gap = abs(train_acc - test_acc)
        if acc_gap > 0.08:
            fit_assessment = "Overfitting Risk"
        elif test_acc < 0.65:
            fit_assessment = "Underfitting Risk"
        else:
            fit_assessment = "Optimal (Balanced Generalization)"
            
        benchmark_results[key] = {
            "key": key,
            "name": name,
            "paradigm": model.paradigm,
            "explainability": model.explainability,
            "train_accuracy": round(train_acc, 4),
            "test_accuracy": round(test_acc, 4),
            "accuracy_gap": round(acc_gap, 4),
            "precision": round(test_prec, 4),
            "recall": round(test_rec, 4),
            "f1_score": round(test_f1, 4),
            "roc_auc": round(test_auc, 4),
            "confusion_matrix": cm,
            "fit_assessment": fit_assessment
        }
        
    benchmark_payload = {
        "metadata": {
            "total_samples": len(df),
            "train_samples": len(y_train),
            "test_samples": len(y_test),
            "overall_failure_rate": baselines_info["overall_baseline_failure_rate"]
        },
        "models": benchmark_results,
        "stage_baselines": baselines_info["stage_baselines"],
        "mined_rules": model_prefixspan.rules[:50],
        "earliest_predictive_handoff": model_prefixspan.rules[0]["earliest_predictive_handoff"] if model_prefixspan.rules else "N/A",
        "highest_risk_sequence": model_prefixspan.rules[0]["sequence"] if model_prefixspan.rules else "N/A"
    }
    
    with open(os.path.join(ARTIFACTS_DIR, "benchmark_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(benchmark_payload, f, indent=2)
        
    return benchmark_payload

if __name__ == "__main__":
    results = train_and_benchmark_all()
    print("=" * 80)
    print("MODEL BENCHMARK RESULTS (VERIFYING OPTIMAL FIT):")
    print("=" * 80)
    for k, m in results["models"].items():
        print(f"[{m['name']}]")
        print(f"  Train Acc: {m['train_accuracy']:.2%} | Test Acc: {m['test_accuracy']:.2%} | Gap: {m['accuracy_gap']:.2%}")
        print(f"  Precision: {m['precision']:.2%} | Recall: {m['recall']:.2%} | F1: {m['f1_score']:.2%} | AUC: {m['roc_auc']:.4f}")
        print(f"  Assessment: {m['fit_assessment']}")
        print("-" * 80)
