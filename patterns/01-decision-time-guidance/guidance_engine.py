from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
import re
from typing import Callable, Iterable


class EventType(str, Enum):
    AGENT_MESSAGE = "agent_message"
    CONSOLE_ERROR = "console_error"
    FILE_EDIT = "file_edit"
    TEST_RESULT = "test_result"
    TOOL_CALL = "tool_call"
    USER_MESSAGE = "user_message"


@dataclass(frozen=True)
class Event:
    type: EventType
    content: str = ""
    path: str | None = None
    command: str | None = None
    passed: bool | None = None
    step: int = 0


@dataclass(frozen=True)
class Evidence:
    label: str
    value: str


@dataclass(frozen=True)
class Signal:
    name: str
    score: float
    evidence: tuple[Evidence, ...]


@dataclass(frozen=True)
class GuidanceCard:
    signal: str
    title: str
    instruction: str
    reason: str
    cooldown_turns: int
    max_tokens: int = 80


@dataclass
class GuidanceDecision:
    injected: list[dict]
    suppressed: list[dict] = field(default_factory=list)
    observed_signals: list[dict] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.injected)


Classifier = Callable[[list[Event]], Signal | None]


GUIDANCE_BANK: dict[str, GuidanceCard] = {
    "diagnostic_signal": GuidanceCard(
        signal="diagnostic_signal",
        title="Read the failing runtime evidence",
        instruction=(
            "A repeated runtime error is present. Do not edit from memory. "
            "Inspect the latest logs, identify the exact failing component, "
            "then make one targeted change."
        ),
        reason=(
            "Repeated errors imply the agent is guessing around a concrete "
            "runtime fact."
        ),
        cooldown_turns=2,
    ),
    "doom_loop": GuidanceCard(
        signal="doom_loop",
        title="Stop the loop and ask for a fresh plan",
        instruction=(
            "You appear stuck in a repeated edit/fail cycle. Pause edits, "
            "summarize the invariant you are trying to restore, and request "
            "an independent plan before continuing."
        ),
        reason=(
            "A stuck trajectory pollutes the working context; a fresh plan can "
            "be easier to recognize than generate."
        ),
        cooldown_turns=4,
    ),
    "unsafe_change": GuidanceCard(
        signal="unsafe_change",
        title="Checkpoint before destructive work",
        instruction=(
            "The next action can destroy or overwrite state. Create a "
            "checkpoint, describe the blast radius, and require approval "
            "before execution."
        ),
        reason=(
            "Agent autonomy is useful only when side effects remain bounded "
            "and reversible."
        ),
        cooldown_turns=6,
    ),
    "mock_data_escape": GuidanceCard(
        signal="mock_data_escape",
        title="Do not fake completion with mock data",
        instruction=(
            "You are drifting toward mocked or hard-coded success. Use real "
            "state from the app or explain the missing dependency instead of "
            "fabricating passing output."
        ),
        reason=(
            "Mocked success can satisfy a shallow check while leaving the user "
            "with a broken product."
        ),
        cooldown_turns=3,
    ),
}


def _recent(events: list[Event], window: int) -> list[Event]:
    return events[-window:]


def _normalize_error(message: str) -> str:
    normalized = re.sub(r"line \d+", "line N", message, flags=re.I)
    normalized = re.sub(r":\d+:\d+", ":N:N", normalized)
    return normalized.strip().lower()


def detect_diagnostic_signal(events: list[Event]) -> Signal | None:
    counts: dict[str, int] = {}
    originals: dict[str, str] = {}

    for event in _recent(events, 10):
        if event.type != EventType.CONSOLE_ERROR:
            continue
        key = _normalize_error(event.content)
        counts[key] = counts.get(key, 0) + 1
        originals.setdefault(key, event.content)

    if not counts:
        return None

    key, count = max(counts.items(), key=lambda item: item[1])
    if count < 2:
        return None

    return Signal(
        name="diagnostic_signal",
        score=min(1.0, 0.35 + count * 0.25),
        evidence=(
            Evidence("repeated_error", originals[key]),
            Evidence("occurrences_in_recent_window", str(count)),
        ),
    )


def detect_doom_loop(events: list[Event]) -> Signal | None:
    recent = _recent(events, 12)
    failed_checks = sum(
        event.type == EventType.TEST_RESULT and event.passed is False
        for event in recent
    )

    edits_by_path: dict[str, int] = {}
    for event in recent:
        if event.type == EventType.FILE_EDIT and event.path:
            edits_by_path[event.path] = edits_by_path.get(event.path, 0) + 1

    if not edits_by_path:
        return None

    path, edits = max(edits_by_path.items(), key=lambda item: item[1])
    if edits < 3 or failed_checks < 2:
        return None

    return Signal(
        name="doom_loop",
        score=min(1.0, 0.25 + edits * 0.15 + failed_checks * 0.15),
        evidence=(
            Evidence("hot_file", path),
            Evidence("edits_in_recent_window", str(edits)),
            Evidence("failed_checks_in_recent_window", str(failed_checks)),
        ),
    )


def detect_unsafe_change(events: list[Event]) -> Signal | None:
    risky_patterns = (
        r"\brm\s+-rf\b",
        r"\bdrop\s+table\b",
        r"\btruncate\b",
        r"\bdelete\s+from\b",
        r"\bgit\s+push\s+--force\b",
        r"\bterraform\s+apply\b",
    )

    for event in reversed(_recent(events, 8)):
        if event.type != EventType.TOOL_CALL or not event.command:
            continue
        if any(re.search(pattern, event.command, flags=re.I) for pattern in risky_patterns):
            return Signal(
                name="unsafe_change",
                score=0.95,
                evidence=(Evidence("risky_command", event.command),),
            )

    return None


def detect_mock_data_escape(events: list[Event]) -> Signal | None:
    mock_terms = (
        "mock data",
        "hard-code",
        "hardcoded",
        "fake response",
        "dummy data",
        "stub this",
    )

    for event in reversed(_recent(events, 8)):
        if event.type != EventType.AGENT_MESSAGE:
            continue
        content = event.content.lower()
        if any(term in content for term in mock_terms):
            return Signal(
                name="mock_data_escape",
                score=0.82,
                evidence=(Evidence("agent_message", event.content),),
            )

    return None


CLASSIFIERS: tuple[Classifier, ...] = (
    detect_diagnostic_signal,
    detect_doom_loop,
    detect_unsafe_change,
    detect_mock_data_escape,
)


def classify_trajectory(events: Iterable[Event]) -> list[Signal]:
    event_list = list(events)
    signals = [signal for classifier in CLASSIFIERS if (signal := classifier(event_list))]
    return sorted(signals, key=lambda signal: signal.score, reverse=True)


def select_guidance(
    events: Iterable[Event],
    previously_injected: dict[str, int] | None = None,
    current_step: int | None = None,
    max_cards: int = 2,
) -> GuidanceDecision:
    event_list = list(events)
    current_step = current_step if current_step is not None else len(event_list)
    previously_injected = previously_injected or {}

    decision = GuidanceDecision(injected=[])

    for signal in classify_trajectory(event_list):
        card = GUIDANCE_BANK[signal.name]
        observed = {
            "signal": signal.name,
            "score": round(signal.score, 2),
            "evidence": [evidence.__dict__ for evidence in signal.evidence],
        }
        decision.observed_signals.append(observed)

        last_injected = previously_injected.get(signal.name)
        if last_injected is not None and current_step - last_injected < card.cooldown_turns:
            decision.suppressed.append(
                {
                    **observed,
                    "reason": "cooldown_active",
                    "next_eligible_step": last_injected + card.cooldown_turns,
                }
            )
            continue

        if len(decision.injected) >= max_cards:
            decision.suppressed.append({**observed, "reason": "card_budget_exhausted"})
            continue

        decision.injected.append(
            {
                "signal": signal.name,
                "score": round(signal.score, 2),
                "title": card.title,
                "instruction": card.instruction,
                "why_now": card.reason,
                "evidence": [evidence.__dict__ for evidence in signal.evidence],
                "ephemeral": True,
            }
        )

    return decision


def scenario_long_debugging_session() -> list[Event]:
    return [
        Event(EventType.USER_MESSAGE, "The signup page crashes after submit.", step=1),
        Event(EventType.FILE_EDIT, path="src/signup.py", step=2),
        Event(EventType.TEST_RESULT, "signup flow failed", passed=False, step=3),
        Event(
            EventType.CONSOLE_ERROR,
            "TypeError: profile.email is None at signup.py:42:11",
            step=4,
        ),
        Event(EventType.FILE_EDIT, path="src/signup.py", step=5),
        Event(EventType.TEST_RESULT, "signup flow failed", passed=False, step=6),
        Event(
            EventType.CONSOLE_ERROR,
            "TypeError: profile.email is None at signup.py:44:11",
            step=7,
        ),
        Event(EventType.FILE_EDIT, path="src/signup.py", step=8),
        Event(
            EventType.AGENT_MESSAGE,
            "I can hard-code a fake response so the demo passes.",
            step=9,
        ),
    ]


def scenario_risky_cleanup() -> list[Event]:
    return [
        Event(EventType.USER_MESSAGE, "Clean up the stale local cache.", step=1),
        Event(EventType.AGENT_MESSAGE, "I will remove generated cache files.", step=2),
        Event(EventType.TOOL_CALL, command="rm -rf ./data/cache", step=3),
    ]


def run_demo() -> dict:
    long_debugging = scenario_long_debugging_session()
    risky_cleanup = scenario_risky_cleanup()

    first_decision = select_guidance(long_debugging, max_cards=2)
    cooldown_decision = select_guidance(
        long_debugging + [Event(EventType.FILE_EDIT, path="src/signup.py", step=10)],
        previously_injected={"diagnostic_signal": 9, "doom_loop": 9},
        current_step=10,
        max_cards=2,
    )
    risky_decision = select_guidance(risky_cleanup, max_cards=2)

    return {
        "ok": (
            len(first_decision.injected) == 2
            and len(cooldown_decision.injected) == 1
            and risky_decision.injected[0]["signal"] == "unsafe_change"
        ),
        "experiments": {
            "long_debugging_session": first_decision.__dict__,
            "cooldown_prevents_repeated_noise": cooldown_decision.__dict__,
            "risky_cleanup": risky_decision.__dict__,
        },
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
