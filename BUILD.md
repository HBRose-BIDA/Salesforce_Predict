# Build Guide

## Why This Structure

This project is built as a modular, reproducible pipeline instead of a single script. Each stage is isolated so extraction, features, model training, and scoring can evolve independently.

This repository is a blueprint and source package. Use this guide to create the local runtime project structure.

## Target Local Project Layout

```text
Salesforce_Predict/
├─ .gitignore
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
├─ docs/
├─ models/
├─ README.md
├─ BUILD.md
├─ RUN.md
├─ run_pipeline.py
├─ requirements.txt
├─ config.template.json
```

## Where To Put Code

Place files exactly as follows:

- Pipeline package code goes under `scoring/`.
- Orchestration entry point stays at root: `run_pipeline.py`.
- User-facing docs stay at root: `README.md`, `BUILD.md`, `RUN.md`.
- Config template stays at root: `config.template.json`.
- Runtime output folders stay at root: `data/raw/`, `data/scored/`, `models/`.

The runtime project should contain folder structure and source code, not local runtime artifacts.

## Pipeline Build Flow

1. Configuration

- `config.template.json` defines the expected settings.
- User copies it to `config.json` and fills org-specific values.
- No code changes are required for a different Salesforce org.

2. Extraction

- `scoring/extract_data.py` pulls closed and open Opportunities from Salesforce.
- Writes source artifacts to `data/raw/`.

3. Feature Engineering

- `scoring/features.py` applies shared transforms for training and inference.
- This keeps feature behavior consistent across stages.

4. Training

- `scoring/train_model.py` builds and saves the model to `models/opportunity_win_model.joblib`.
- Writes training diagnostics to `models/training_metrics.json`.
- Handles low-data scenarios with fallback modes so pipeline execution does not break.

5. Scoring

- `scoring/score_opportunities.py` scores open opportunities.
- Writes ranked output to `data/scored/open_opportunities_scored.csv`.
- Optional advanced mode: `--push` writes scores back to a Salesforce Opportunity field.

6. Orchestration

- `run_pipeline.py` runs extract -> train -> score.
- Supported parameters:
  - `--limit <N>` limits number of open opportunities scored.
  - `--push` enables Salesforce write-back.

## Output Artifacts

- `data/raw/closed_opportunities.csv`
- `data/raw/open_opportunities.csv`
- `models/opportunity_win_model.joblib`
- `models/training_metrics.json`
- `data/scored/open_opportunities_scored.csv`

## Deployment Modes

- External analytics mode (default): produce scored files only.
- Confidential CRM mode (optional): push scores back into Salesforce for in-CRM access control.

## Portfolio Positioning

This implementation demonstrates practical ML system design in a CRM context: config-driven onboarding, modular pipeline stages, traceable artifacts, and optional enterprise integration back into Salesforce.
