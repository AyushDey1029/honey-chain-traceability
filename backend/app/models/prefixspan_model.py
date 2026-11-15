import json
import numpy as np

class SequentialPrefixSpanModel:
    def __init__(self, min_support_ratio=0.04, min_len=2, max_len=5, lift_threshold=1.8, min_confidence=0.55):
        self.min_support_ratio = min_support_ratio
        self.min_len = min_len
        self.max_len = max_len
        self.lift_threshold = lift_threshold
        self.min_confidence = min_confidence
        self.rules = []
        self.overall_baseline = 0.28
        self.model_name = "Model 3: Sequential Mining Discovery Engine (PrefixSpan + Lift Ranker)"
        self.paradigm = "White-Box Sequential Pattern Mining"
        self.explainability = "100% White-Box (Earliest Predictive Handoff Localization)"

    def _is_subsequence(self, pattern, sequence):
        it = iter(sequence)
        return all(item in it for item in pattern)

    def _mine_prefixspan(self, db, min_sup):
        results = []
        def _mine(projected_db, prefix):
            if len(prefix) >= self.min_len:
                results.append((len(projected_db), prefix))
            if len(prefix) >= self.max_len:
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
                if len(new_proj) >= min_sup:
                    _mine(new_proj, prefix + [item])

        initial_items = {}
        for seq in db:
            seen = set()
            for i, item in enumerate(seq):
                if item not in seen:
                    seen.add(item)
                    if item not in initial_items:
                        initial_items[item] = []
                    initial_items[item].append((seq, i + 1))

        for item, new_proj in initial_items.items():
            if len(new_proj) >= min_sup:
                _mine(new_proj, [item])

        return results

    def fit(self, sequence_lists, labels):
        labels_arr = np.array(labels)
        self.overall_baseline = float(labels_arr.mean()) if len(labels_arr) > 0 else 0.28
        total_batches = len(sequence_lists)
        
        failed_indices = [idx for idx, val in enumerate(labels_arr) if val == 1]
        failed_sequences = [sequence_lists[idx] for idx in failed_indices]
        
        min_sup_count = max(4, int(len(failed_sequences) * self.min_support_ratio))
        mined_patterns = self._mine_prefixspan(failed_sequences, min_sup_count)
        
        rules_list = []
        seen = set()
        
        for sup_fail, pattern in mined_patterns:
            if len(pattern) < self.min_len:
                continue
            key = tuple(pattern)
            if key in seen:
                continue
            seen.add(key)
            
            in_all = [self._is_subsequence(pattern, seq) for seq in sequence_lists]
            count_total = sum(in_all)
            count_fail = sum(1 for idx, match in enumerate(in_all) if match and labels_arr[idx] == 1)
            
            confidence = (count_fail / count_total) if count_total > 0 else 0.0
            lift = (confidence / self.overall_baseline) if self.overall_baseline > 0 else 0.0
            support = count_fail / total_batches
            
            rules_list.append({
                "sequence": " -> ".join(pattern),
                "sequence_list": pattern,
                "sequence_length": len(pattern),
                "earliest_predictive_handoff": pattern[0],
                "support": round(support, 4),
                "support_count": count_fail,
                "total_batches_matched": count_total,
                "confidence": round(confidence, 4),
                "lift": round(lift, 4)
            })
            
        rules_list.sort(key=lambda r: (r["lift"], r["support"], r["confidence"]), reverse=True)
        self.rules = rules_list
        return self

    def predict_sequence(self, sequence_list):
        matched = []
        for r in self.rules:
            if r["lift"] >= self.lift_threshold and r["confidence"] >= self.min_confidence and self._is_subsequence(r["sequence_list"], sequence_list):
                matched.append(r)
                
        if matched:
            matched.sort(key=lambda item: item["lift"], reverse=True)
            worst = matched[0]
            pred = 1
            proba = worst["confidence"]
            status = "CRITICAL_RISK"
            root_cause = worst["earliest_predictive_handoff"]
            explanation = f"Matched critical high-lift sequence: '{worst['sequence']}'. Earliest predictive handoff is '{root_cause}' with {worst['lift']}x baseline failure risk."
            action = f"Immediate Smart Contract Alert: Halt batch packaging, isolate batch, and enforce NMR spectroscopy testing at stage '{worst['sequence_list'][-1]}'."
        else:
            worst = None
            pred = 0
            proba = self.overall_baseline * 0.45
            status = "LOW_RISK"
            root_cause = None
            explanation = "Sequence does not contain any mined high-lift risk patterns. Normal transit degradation expected."
            action = "Batch approved for standard Honey Chain blockchain dispatch."

        return {
            "model_name": self.model_name,
            "paradigm": self.paradigm,
            "predicted_failure": pred,
            "failure_probability": round(proba, 4),
            "risk_status": status,
            "matched_rules_count": len(matched),
            "worst_rule": worst,
            "earliest_predictive_handoff": root_cause,
            "explanation": explanation,
            "smart_contract_action": action
        }

    def predict(self, sequence_lists):
        preds = []
        for seq in sequence_lists:
            res = self.predict_sequence(seq)
            preds.append(res["predicted_failure"])
        return np.array(preds)

    def predict_proba(self, sequence_lists):
        probas = []
        for seq in sequence_lists:
            res = self.predict_sequence(seq)
            p = res["failure_probability"]
            probas.append([1.0 - p, p])
        return np.array(probas)

    def save(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "overall_baseline": self.overall_baseline,
                "lift_threshold": self.lift_threshold,
                "min_confidence": self.min_confidence,
                "rules": self.rules
            }, f, indent=2)

    def load(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.overall_baseline = data["overall_baseline"]
            self.lift_threshold = data.get("lift_threshold", 1.8)
            self.min_confidence = data.get("min_confidence", 0.55)
            self.rules = data["rules"]
        return self
