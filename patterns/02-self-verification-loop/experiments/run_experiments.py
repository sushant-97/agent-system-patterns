from __future__ import annotations

import json
from pathlib import Path
import sys


PATTERN_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = Path(__file__).resolve().parent / "results"
sys.path.insert(0, str(PATTERN_DIR))

from verification_engine import (  # noqa: E402
    create_potemkin_signup_app,
    repair_application,
    report_to_dict,
    run_scenario,
    signup_scenario,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def shallow_false_pass() -> dict:
    app = create_potemkin_signup_app()
    report = run_scenario(app, signup_scenario(include_behavioral_checks=False))
    return {
        "question": "Can a broken app pass visual-only checks?",
        "expected": {"shallow_passes": True},
        "observed": report_to_dict(report),
        "pass": report.passed,
        "interpretation": "The broken app can pass shallow verification, so shallow verification is not enough.",
    }


def behavioral_catches_potemkin() -> dict:
    app = create_potemkin_signup_app()
    report = run_scenario(app, signup_scenario(include_behavioral_checks=True))
    failed_steps = [item.step for item in report.failed_evidence]
    return {
        "question": "Does behavioral evidence catch fake success?",
        "expected": {
            "behavioral_passes": False,
            "failed_steps_include": ["assert_state:users.email"],
        },
        "observed": report_to_dict(report),
        "pass": not report.passed and "assert_state:users.email" in failed_steps,
        "interpretation": "Behavioral verification catches the missing durable state change.",
    }


def repair_rerun() -> dict:
    app = create_potemkin_signup_app()
    before = run_scenario(app, signup_scenario(include_behavioral_checks=True))
    repaired = repair_application(app, before)
    after = run_scenario(repaired, signup_scenario(include_behavioral_checks=True))
    return {
        "question": "Can failed evidence drive repair and rerun?",
        "expected": {"before_passes": False, "after_passes": True},
        "observed": {
            "before": report_to_dict(before),
            "after": report_to_dict(after),
        },
        "pass": not before.passed and after.passed,
        "interpretation": "The repair targets the failed persistence evidence, then the same scenario passes.",
    }


def main() -> dict:
    experiments = {
        "shallow-false-pass": shallow_false_pass(),
        "behavioral-catches-potemkin": behavioral_catches_potemkin(),
        "repair-rerun": repair_rerun(),
    }
    summary = {
        "pass": all(result["pass"] for result in experiments.values()),
        "experiments": {
            name: {
                "pass": result["pass"],
                "question": result["question"],
                "expected": result["expected"],
            }
            for name, result in experiments.items()
        },
    }

    for name, result in experiments.items():
        write_json(RESULTS_DIR / f"{name}.json", result)
    write_json(RESULTS_DIR / "summary.json", summary)
    return summary


if __name__ == "__main__":
    output = main()
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if output["pass"] else 1)
