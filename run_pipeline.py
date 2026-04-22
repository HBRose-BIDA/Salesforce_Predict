from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run_step(command: list[str]) -> None:
    print(f"\nRunning: {' '.join(command)}")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the opportunity scoring pipeline.")
    parser.add_argument("--push", action="store_true", help="Push predictions to Salesforce")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of open opps to score")
    args = parser.parse_args()

    run_step([sys.executable, "-m", "scoring.extract_data"])
    run_step([sys.executable, "-m", "scoring.train_model"])

    score_cmd = [sys.executable, "-m", "scoring.score_opportunities"]
    if args.limit > 0:
        score_cmd.extend(["--limit", str(args.limit)])
    if args.push:
        score_cmd.append("--push")

    run_step(score_cmd)


if __name__ == "__main__":
    main()
