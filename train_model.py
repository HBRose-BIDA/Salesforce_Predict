from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from scoring.config import load_config
from scoring.features import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, build_feature_frame


DATA_RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"


def build_training_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_COLUMNS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def main() -> None:
    config = load_config()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    historical_path = DATA_RAW_DIR / "closed_opportunities.csv"
    if not historical_path.exists():
        raise FileNotFoundError(
            "Missing historical data. Run `python -m scoring.extract_data` first."
        )

    df = pd.read_csv(historical_path)
    y = df["IsWon"].astype(int)
    x = build_feature_frame(df)

    class_counts = y.value_counts(dropna=False).to_dict()
    unique_classes = int(y.nunique())

    metrics = {
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows_total": int(len(df)),
        "class_counts": {str(k): int(v) for k, v in class_counts.items()},
        "recommended_min_closed_records": int(config.min_closed_records),
    }

    if unique_classes < 2:
        # Low-data fallback: produce a deterministic baseline model so scoring can continue.
        observed_class = int(y.iloc[0])
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), NUMERIC_COLUMNS),
                ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
            ]
        )
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "classifier",
                    DummyClassifier(strategy="constant", constant=observed_class),
                ),
            ]
        )
        pipeline.fit(x, y)
        metrics["training_mode"] = "fallback_single_class"
        metrics["warning"] = (
            "Only one outcome class exists in closed opportunities. "
            "Model is a constant baseline until both won and lost examples are available."
        )
    elif len(df) < 10:
        pipeline = build_training_pipeline()
        pipeline.fit(x, y)
        proba = pipeline.predict_proba(x)[:, 1]
        preds = (proba >= 0.5).astype(int)
        metrics["training_mode"] = "low_data_in_sample"
        metrics["rows_train"] = int(len(x))
        metrics["rows_test"] = 0
        metrics["accuracy"] = float(accuracy_score(y, preds))
        metrics["roc_auc"] = float(roc_auc_score(y, proba))
        metrics["warning"] = (
            "Very small dataset. Metrics are in-sample only and likely optimistic."
        )
    else:
        x_train, x_test, y_train, y_test = train_test_split(
            x,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        pipeline = build_training_pipeline()
        pipeline.fit(x_train, y_train)

        proba = pipeline.predict_proba(x_test)[:, 1]
        preds = (proba >= 0.5).astype(int)

        metrics["training_mode"] = "standard_holdout"
        metrics["rows_train"] = int(len(x_train))
        metrics["rows_test"] = int(len(x_test))
        metrics["accuracy"] = float(accuracy_score(y_test, preds))
        metrics["roc_auc"] = float(roc_auc_score(y_test, proba))

    model_path = MODEL_DIR / "opportunity_win_model.joblib"
    metrics_path = MODEL_DIR / "training_metrics.json"

    joblib.dump(pipeline, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Saved model to {model_path}")
    print(f"Saved metrics to {metrics_path}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
