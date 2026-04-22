from __future__ import annotations

from pathlib import Path

import pandas as pd

from scoring.config import load_config
from scoring.sf_client import get_salesforce_client


DATA_RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def _flatten_records(records: list[dict]) -> list[dict]:
    return [{k: v for k, v in row.items() if k != "attributes"} for row in records]


def fetch_historical_opportunities(history_years: int) -> pd.DataFrame:
    config = load_config()
    sf = get_salesforce_client(config)

    query = (
        "SELECT Id, Name, Amount, Probability, Type, LeadSource, StageName, "
        "ForecastCategoryName, IsWon, IsClosed, HasOpportunityLineItem, CreatedDate, CloseDate "
        "FROM Opportunity "
        "WHERE IsClosed = true "
        f"AND CloseDate = LAST_N_YEARS:{history_years}"
    )

    result = sf.query_all(query)
    return pd.DataFrame(_flatten_records(result["records"]))


def fetch_open_opportunities() -> pd.DataFrame:
    config = load_config()
    sf = get_salesforce_client(config)

    query = (
        "SELECT Id, Name, Amount, Probability, Type, LeadSource, StageName, "
        "ForecastCategoryName, HasOpportunityLineItem, CreatedDate, CloseDate "
        "FROM Opportunity "
        "WHERE IsClosed = false"
    )

    result = sf.query_all(query)
    return pd.DataFrame(_flatten_records(result["records"]))


def main() -> None:
    config = load_config()
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

    historical = fetch_historical_opportunities(config.history_years)
    open_deals = fetch_open_opportunities()

    historical_path = DATA_RAW_DIR / "closed_opportunities.csv"
    open_path = DATA_RAW_DIR / "open_opportunities.csv"

    historical.to_csv(historical_path, index=False)
    open_deals.to_csv(open_path, index=False)

    print(f"Saved {len(historical)} historical rows to {historical_path}")
    print(f"Saved {len(open_deals)} open rows to {open_path}")


if __name__ == "__main__":
    main()
