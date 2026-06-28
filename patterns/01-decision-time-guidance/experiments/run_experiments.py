from __future__ import annotations

import json
from pathlib import Path
import sys


PATTERN_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = Path(__file__).resolve().parent / "results"
sys.path.insert(0, str(PATTERN_DIR))

from guidance_engine import (  # noqa: E402
    Event,
    EventType,
    scenario_long_debugging_session,
    scenario_risky_cleanup,
    select_guidance,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def long_debugging_session() -> dict:
    decision = select_guidance(scenario_long_debugging_session(), max_cards=2)
    return {
        "question": "Does the controller catch repeated runtime/debugging failure?",
        "expected": {
            "injected": ["doom_loop", "diagnostic_signal"],
            "suppressed": ["mock_data_escape"],
        },
        "observed": decision.__dict__,
        "pass": (
            [card["signal"] for card in decision.injected]
            == ["doom_loop", "diagnostic_signal"]
            and [card["signal"] for card in decision.suppressed]
            == ["mock_data_escape"]
        ),
        "interpretation": (
            "The controller catches the loop and repeated runtime error, while "
            "the card budget prevents an additional reminder from crowding the "
            "next turn."
        ),
    }


def cooldown_prevents_repeated_noise() -> dict:
    trace = scenario_long_debugging_session() + [
        Event(EventType.FILE_EDIT, path="src/signup.py", step=10)
    ]
    decision = select_guidance(
        trace,
        previously_injected={"diagnostic_signal": 9, "doom_loop": 9},
        current_step=10,
        max_cards=2,
    )
    return {
        "question": "Does the controller avoid repeating the same nudge immediately?",
        "expected": {
            "injected": ["mock_data_escape"],
            "suppressed": ["doom_loop", "diagnostic_signal"],
        },
        "observed": decision.__dict__,
        "pass": (
            [card["signal"] for card in decision.injected] == ["mock_data_escape"]
            and [card["signal"] for card in decision.suppressed]
            == ["doom_loop", "diagnostic_signal"]
        ),
        "interpretation": (
            "Cooldowns stop repeated reminders from becoming prompt noise. A "
            "different relevant card can still be injected."
        ),
    }


def risky_cleanup() -> dict:
    decision = select_guidance(scenario_risky_cleanup(), max_cards=2)
    return {
        "question": "Does the controller intervene on destructive commands?",
        "expected": {
            "injected": ["unsafe_change"],
            "suppressed": [],
        },
        "observed": decision.__dict__,
        "pass": (
            [card["signal"] for card in decision.injected] == ["unsafe_change"]
            and decision.suppressed == []
        ),
        "interpretation": (
            "Risky side effects should trigger guidance even when there is no "
            "debugging loop or failed test."
        ),
    }


def main() -> dict:
    experiments = {
        "long-debugging-session": long_debugging_session(),
        "cooldown-prevents-repeated-noise": cooldown_prevents_repeated_noise(),
        "risky-cleanup": risky_cleanup(),
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
