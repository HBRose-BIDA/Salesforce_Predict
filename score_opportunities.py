from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd

from scoring.config import load_config
from scoring.features import build_feature_frame
from scoring.sf_client import get_salesforce_client


DATA_RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_SCORED_DIR = Path(__file__).resolve().parent.parent / "data" / "scored"
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"


def push_scores_to_salesforce(scored_df: pd.DataFrame, field_api_name: str) -> int:
    config = load_config()
    sf = get_salesforce_client(config)

    updates = 0
    for row in scored_df.itertuples(index=False):
        sf.Opportunity.update(
            row.Id,
            {field_api_name: float(row.PredictedWinProbabilityPercent)},
        )
        updates += 1

    return updates


def main() -> None:
    parser = argparse.ArgumentParser(description="Score open opportunities with the trained model.")
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push scored probabilities back to Salesforce.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional max number of opportunities to score/update.",
    )
    args = parser.parse_args()

    open_path = DATA_RAW_DIR / "open_opportunities.csv"
    model_path = MODEL_DIR / "opportunity_win_model.joblib"

    if not open_path.exists():
        raise FileNotFoundError("Missing open opportunities data. Run extraction first.")
    if not model_path.exists():
        raise FileNotFoundError("Missing model artifact. Run training first.")

    open_df = pd.read_csv(open_path)
    if args.limit > 0:
        open_df = open_df.head(args.limit).copy()

    features = build_feature_frame(open_df)

    model = joblib.load(model_path)
    proba_matrix = model.predict_proba(features)
    classes = list(getattr(model, "classes_", []))
    if len(classes) == 2:
        positive_index = classes.index(1)
        probabilities = proba_matrix[:, positive_index] * 100.0
    elif len(classes) == 1:
        only_class = int(classes[0])
        probabilities = proba_matrix[:, 0] * 100.0 if only_class == 1 else (1.0 - proba_matrix[:, 0]) * 100.0
    else:
        raise ValueError("Unexpected class layout in trained model.")

    scored = open_df[["Id", "Name", "StageName", "Amount"]].copy()
    scored["PredictedWinProbabilityPercent"] = probabilities.round(2)
    scored.sort_values("PredictedWinProbabilityPercent", ascending=False, inplace=True)

    DATA_SCORED_DIR.mkdir(parents=True, exist_ok=True)
    scored_path = DATA_SCORED_DIR / "open_opportunities_scored.csv"
    scored.to_csv(scored_path, index=False)

    print(f"Saved scored opportunities to {scored_path}")
    print(scored.head(10).to_string(index=False))

    if args.push:
        config = load_config()
        updated = push_scores_to_salesforce(scored, config.predicted_win_field)
        print(
            f"Updated {updated} opportunities in Salesforce field "
            f"'{config.predicted_win_field}'."
        )
    else:
        print("Dry run only. Add --push to update Salesforce.")


if __name__ == "__main__":
    main()
