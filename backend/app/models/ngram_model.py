import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import Pipeline

class SequentialNGramModel:
    def __init__(self):
        self.pipeline = Pipeline([
            ("vectorizer", TfidfVectorizer(
                ngram_range=(1, 3),
                token_pattern=r"\S+",
                lowercase=False
            )),
            ("classifier", GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.06,
                max_depth=3,
                min_samples_split=6,
                min_samples_leaf=3,
                subsample=0.85,
                random_state=42
            ))
        ])
        self.model_name = "Model 2: Sequential N-Gram Discriminative ML (Gradient Boosting)"
        self.paradigm = "Sequential Transition Modeling"
        self.explainability = "N-Gram Transition Weights (Opaque Root Cause)"

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
        
        vectorizer = self.pipeline.named_steps["vectorizer"]
        classifier = self.pipeline.named_steps["classifier"]
        
        feature_names = vectorizer.get_feature_names_out()
        tfidf_vec = vectorizer.transform([text]).toarray()[0]
        importances = classifier.feature_importances_
        
        active_transitions = []
        for idx, (val, imp) in enumerate(zip(tfidf_vec, importances)):
            if val > 0:
                feat = feature_names[idx]
                if " " in feat:
                    score = val * imp
                    active_transitions.append({
                        "transition": feat.replace(" ", " -> "),
                        "relevance_score": round(float(score), 4)
                    })
                    
        active_transitions.sort(key=lambda item: item["relevance_score"], reverse=True)
        
        return {
            "model_name": self.model_name,
            "paradigm": self.paradigm,
            "predicted_failure": prediction,
            "failure_probability": round(proba, 4),
            "risk_status": "HIGH_RISK" if proba >= 0.5 else "LOW_RISK",
            "strength": "Accurately models ordered multi-step transitions via TF-IDF n-grams.",
            "limitation": "High predictive accuracy, but does not provide regulatory white-box lift rules or exact earliest predictive handoff pinpointing.",
            "top_active_transitions": active_transitions[:3]
        }

    def save(self, filepath):
        joblib.dump(self.pipeline, filepath)

    def load(self, filepath):
        self.pipeline = joblib.load(filepath)
        return self
