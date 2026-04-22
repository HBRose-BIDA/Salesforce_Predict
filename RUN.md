# Run Guide

This guide is focused on pipeline execution and Salesforce-specific configuration.

## Security Deployment Modes

- Default mode: produce an external scored file and do not update Salesforce.
- Optional confidential mode: write scores back to Salesforce when teams want report data to stay inside CRM security boundaries.

Choose the mode that matches your organization's confidentiality requirements.

## 1. Configure

Copy template to local config:

```powershell
Copy-Item .\config.template.json .\config.json
```

Then update `config.json` with your Salesforce org values:
- username
- password
- security_token
- predicted_win_field (your Opportunity custom field API name)

## 2. Run Full Pipeline (Dry Run)

Dry run does extraction, training, and scoring to CSV without writing back to Salesforce.

```powershell
python run_pipeline.py --limit 25
```

Primary output:
- `data/scored/open_opportunities_scored.csv`

Output files:
- `data/raw/closed_opportunities.csv`
- `data/raw/open_opportunities.csv`
- `models/opportunity_win_model.joblib`
- `models/training_metrics.json`
- `data/scored/open_opportunities_scored.csv`

## 3. Optional Advanced: Push Scores to Salesforce

Only use this if your org has a writable Opportunity field for predictions:

```powershell
python run_pipeline.py --push
```

## 4. Run Stages Individually

```powershell
python -m scoring.extract_data
python -m scoring.train_model
python -m scoring.score_opportunities --limit 25
python -m scoring.score_opportunities --push
```

## Common Notes

- If your org has very little closed-opportunity history, model quality will be limited.
- Start with dry run and inspect `models/training_metrics.json` before pushing.
- `config.json` is local and should not be committed.
