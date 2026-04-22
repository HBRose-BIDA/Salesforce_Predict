from __future__ import annotations

import pandas as pd

MODEL_INPUT_COLUMNS = [
    "Amount",
    "Probability",
    "SalesCycleDays",
    "HasOpportunityLineItem",
    "Type",
    "LeadSource",
    "StageName",
    "ForecastCategoryName",
    "CloseMonth",
]

NUMERIC_COLUMNS = ["Amount", "Probability", "SalesCycleDays", "HasOpportunityLineItem"]
CATEGORICAL_COLUMNS = ["Type", "LeadSource", "StageName", "ForecastCategoryName", "CloseMonth"]


def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()

    for column in ["Amount", "Probability"]:
        work[column] = pd.to_numeric(work[column], errors="coerce").fillna(0.0)

    work["HasOpportunityLineItem"] = (
        work["HasOpportunityLineItem"].fillna(False).astype(bool).astype(int)
    )

    created = pd.to_datetime(work["CreatedDate"], errors="coerce", utc=True)
    close = pd.to_datetime(work["CloseDate"], errors="coerce", utc=True)

    work["SalesCycleDays"] = (close - created).dt.days.fillna(0).clip(lower=0)
    work["CloseMonth"] = close.dt.month.fillna(0).astype(int).astype(str)

    for column in ["Type", "LeadSource", "StageName", "ForecastCategoryName"]:
        work[column] = work[column].fillna("Unknown")

    return work[MODEL_INPUT_COLUMNS]
