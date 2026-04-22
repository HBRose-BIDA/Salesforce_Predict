# Salesforce Opportunity Win Scoring

Bring-your-own-Salesforce-org pipeline for opportunity win-probability scoring.

Only one user-specific change is required: your local `config.json`.

For implementation structure and pipeline design details, see [BUILD.md](BUILD.md).
For step-by-step execution commands, see [RUN.md](RUN.md).

## Quick Start

1. Copy `config.template.json` to `config.json` and enter your Salesforce values.
2. Run the full pipeline:

```powershell
python run_pipeline.py --limit 25
```

3. Review scored output file:

- `data/scored/open_opportunities_scored.csv`

4. Optional advanced integration: push predictions back to Salesforce:

```powershell
python run_pipeline.py --push
```

## Security Deployment Modes

This project supports two valid operating modes:

- External analytics mode (default): keep results in local output files for review.
- Confidential CRM mode (optional): write predictions back into Salesforce to keep sensitive scores inside Salesforce security controls.

Use the mode that fits your governance requirements.

## Optional Salesforce Write-Back Setup

Write-back is optional. Only configure this if you want scores stored on Opportunity records.

Create a custom Opportunity field for predictions:

- API name example: `Predicted_Win_Probability__c`
- Type: Percent

Set that field API name in `config.json` under `predicted_win_field`.
