# Build Guide

## Why This Structure

This project is organized as a reproducible pipeline instead of a single script. The goal is to keep extraction, feature engineering, training, and scoring clearly separated so each stage can be improved independently.

## Directory Structure

```text
New Salesforce 2/
├─ scoring/
│  ├─ config.py
│  ├─ sf_client.py
│  ├─ extract_data.py
│  ├─ features.py
│  ├─ train_model.py
│  └─ score_opportunities.py
├─ data/
│  ├─ raw/
│  └─ scored/
├─ models/
├─ run_pipeline.py
├─ requirements.txt
├─ config.template.json
├─ config.json
└─ README.md
```

## Build Flow

1. Configuration
- `config.template.json` provides the required shape.
- User copies it to `config.json` and fills their own Salesforce credentials and settings.
- No code edits are required for a new org.

2. Extraction Stage
- `scoring/extract_data.py` reads closed and open opportunities from Salesforce.
- Outputs are written to `data/raw/` as CSV artifacts.

3. Feature Stage
- `scoring/features.py` defines consistent feature transformations used by both training and inference.
- This avoids training-serving skew.

4. Training Stage
- `scoring/train_model.py` trains a scikit-learn model and writes:
  - `models/opportunity_win_model.joblib`
  - `models/training_metrics.json`
- Includes fallback behavior for very small or single-class datasets so the pipeline remains runnable.

5. Scoring Stage
- `scoring/score_opportunities.py` scores current open opportunities.
- Writes ranked results to `data/scored/open_opportunities_scored.csv`.
- Optional advanced `--push` writes probabilities back to Salesforce custom field.

6. Orchestration
- `run_pipeline.py` executes extract -> train -> score in one command.
- Keeps execution simple for portfolio reviewers and users.

## Design Choices

- Separation of concerns: each file has one clear responsibility.
- Artifact visibility: every stage writes inspectable outputs.
- Config-driven portability: any user can run with their own Salesforce org.
- Safe defaults: dry-run scoring by default, explicit flag required to push updates.
- Practical default deliverable: scored opportunity ranking in an external file.
- Security flexibility: supports both external reporting and confidential in-CRM write-back modes.

## How To Explain In Portfolio

This project demonstrates end-to-end applied machine learning in a CRM workflow, with production-style organization: config-driven setup, modular pipeline stages, traceable data/model artifacts, and optional system write-back.

In security-sensitive environments, optional write-back allows organizations to avoid distributing confidential prediction reports outside Salesforce and instead keep access governed by existing CRM permissions.
