import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

class BaselineBagOfStagesModel:
    def __init__(self):
        self.pipeline = Pipeline([
            ("vectorizer", CountVectorizer(token_pattern=r"\S+", binary=True)),
            ("classifier", RandomForestClassifier(
                n_estimators=100,
                max_depth=6,
                min_samples_split=6,
                min_samples_leaf=3,
                random_state=42
            ))
        ])
        self.model_name = "Model 1: Unordered Bag-of-Stages Baseline (Random Forest)"
        self.paradigm = "Order-Blind Classical ML"
        self.explainability = "Feature Importance (No Sequence Attribution)"

    def fit(self, X_train, y_train):
        self.pipeline.fit(X_train, y_train)
        return self

    def predict(self, X):
        return self.pipeline.predict(X)

    def predict_proba(self, X):
        return self.pipeline.predict_proba(X)

    def evaluate_sequence(self, sequence_list):
        text = " ".join(sequence_list)
        proba = float(self.pipeline.predict_proba([text])[0][1])
        prediction = int(proba >= 0.5)
        
        feature_names = self.pipeline.named_steps["vectorizer"].get_feature_names_out()
        importances = self.pipeline.named_steps["classifier"].feature_importances_
        
        present_stages = set(sequence_list)
        stage_contributions = []
        for name, imp in zip(feature_names, importances):
            if name in present_stages:
                stage_contributions.append({"stage": name, "importance": round(float(imp), 4)})
                
        stage_contributions.sort(key=lambda item: item["importance"], reverse=True)
        
        return {
            "model_name": self.model_name,
            "paradigm": self.paradigm,
            "predicted_failure": prediction,
            "failure_probability": round(proba, 4),
            "risk_status": "HIGH_RISK" if proba >= 0.5 else "LOW_RISK",
            "limitation": "Assumes stages are order-independent; cannot distinguish between forward and reverse handoff sequences.",
            "top_stage_contributions": stage_contributions[:3]
        }

    def save(self, filepath):
        joblib.dump(self.pipeline, filepath)

    def load(self, filepath):
        self.pipeline = joblib.load(filepath)
        return self
