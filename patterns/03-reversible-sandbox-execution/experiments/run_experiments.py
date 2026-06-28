from __future__ import annotations

import json
from pathlib import Path
import sys


PATTERN_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = Path(__file__).resolve().parent / "results"
sys.path.insert(0, str(PATTERN_DIR))

from sandbox_engine import (  # noqa: E402
    Decision,
    SnapshotStore,
    create_workspace,
    destructive_billing_migration,
    external_side_effect_attempt,
    promote_or_keep,
    run_in_sandbox,
    safe_ui_copy_change,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def stable_observation(attempt) -> dict:
    return {
        "label": attempt.label,
        "decision": attempt.decision.value,
        "diff": [
            {
                "path": change.path,
                "risk": change.risk,
                "before": change.before,
                "after": change.after,
            }
            for change in attempt.diff
        ],
        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "severity": check.severity.value,
            }
            for check in attempt.checks
        ],
        "rejection_reasons": list(attempt.rejection_reasons),
    }


def safe_ui_copy() -> dict:
    attempt = run_in_sandbox(create_workspace(), safe_ui_copy_change, "safe ui copy")
    return {
        "question": "Can a low-risk file edit promote?",
        "expected": {"decision": "promoted", "blocked_risks": []},
        "observed": stable_observation(attempt),
        "pass": attempt.decision == Decision.PROMOTED
        and [change.risk for change in attempt.diff] == ["file_change"],
        "interpretation": "Low-risk file changes can promote when all invariants pass.",
    }


def destructive_billing() -> dict:
    attempt = run_in_sandbox(
        create_workspace(),
        destructive_billing_migration,
        "destructive billing migration",
    )
    risks = [change.risk for change in attempt.diff]
    return {
        "question": "Does durable data loss get blocked?",
        "expected": {"decision": "rejected", "blocked_risks": ["destructive_data"]},
        "observed": stable_observation(attempt),
        "pass": attempt.decision == Decision.REJECTED and "destructive_data" in risks,
        "interpretation": (
            "The sandbox can contain the failed attempt while preserving canonical "
            "billing state."
        ),
    }


def external_effect() -> dict:
    attempt = run_in_sandbox(
        create_workspace(),
        external_side_effect_attempt,
        "external side effect",
    )
    risks = [change.risk for change in attempt.diff]
    return {
        "question": "Does non-reversible external activity get blocked?",
        "expected": {"decision": "rejected", "blocked_risks": ["external_side_effect"]},
        "observed": stable_observation(attempt),
        "pass": attempt.decision == Decision.REJECTED and "external_side_effect" in risks,
        "interpretation": (
            "Snapshots do not make external effects reversible; policy must block "
            "them before promotion."
        ),
    }


def competing_sandboxes() -> dict:
    workspace = create_workspace()
    store = SnapshotStore()
    safe = run_in_sandbox(workspace, safe_ui_copy_change, "candidate safe copy", store)
    destructive = run_in_sandbox(
        workspace,
        destructive_billing_migration,
        "candidate destructive migration",
        store,
    )
    final_workspace = promote_or_keep(workspace, safe)
    final_workspace = promote_or_keep(final_workspace, destructive)

    return {
        "question": "Can two independent forks be compared before promotion?",
        "expected": {
            "candidate_decisions": ["promoted", "rejected"],
            "final_preserves_invoices": True,
        },
        "observed": {
            "attempts": [stable_observation(safe), stable_observation(destructive)],
            "final_copy": final_workspace.files["app/copy.json"],
            "final_invoice_count": len(final_workspace.database["invoices"]),
        },
        "pass": safe.decision == Decision.PROMOTED
        and destructive.decision == Decision.REJECTED
        and len(final_workspace.database["invoices"]) == 1,
        "interpretation": (
            "Independent forks let the system compare candidate work before "
            "choosing what becomes canonical."
        ),
    }


def main() -> dict:
    experiments = {
        "safe-ui-copy": safe_ui_copy(),
        "destructive-billing-migration": destructive_billing(),
        "external-side-effect": external_effect(),
        "competing-sandboxes": competing_sandboxes(),
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
