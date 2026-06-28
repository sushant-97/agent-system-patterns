from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import copy
import json
from typing import Callable


class StepType(str, Enum):
    VISIT = "visit"
    FILL = "fill"
    CLICK = "click"
    ASSERT_TEXT = "assert_text"
    ASSERT_STATE = "assert_state"
    ASSERT_LOG = "assert_log"


class Severity(str, Enum):
    INFO = "info"
    BLOCKER = "blocker"


@dataclass(frozen=True)
class VerificationStep:
    type: StepType
    target: str
    value: object | None = None
    description: str = ""


@dataclass(frozen=True)
class Evidence:
    step: str
    passed: bool
    observed: object
    expected: object
    severity: Severity


@dataclass(frozen=True)
class Scenario:
    name: str
    intent: str
    steps: tuple[VerificationStep, ...]


@dataclass
class Application:
    route: str = "/"
    fields: dict[str, str] = field(default_factory=dict)
    screen_text: list[str] = field(default_factory=list)
    state: dict[str, object] = field(default_factory=lambda: {"users": []})
    logs: list[str] = field(default_factory=list)
    handlers: dict[str, Callable[["Application"], None]] = field(default_factory=dict)

    def clone(self) -> "Application":
        cloned = copy.deepcopy(self)
        cloned.handlers = self.handlers.copy()
        return cloned

    def visit(self, route: str) -> None:
        self.route = route
        if route == "/signup":
            self.screen_text = ["Create account", "Email", "Submit"]
        self.logs.append(f"visit:{route}")

    def fill(self, field: str, value: str) -> None:
        self.fields[field] = value
        self.logs.append(f"fill:{field}")

    def click(self, target: str) -> None:
        handler = self.handlers.get(target)
        if handler:
            handler(self)
        else:
            self.logs.append(f"missing-handler:{target}")


@dataclass(frozen=True)
class VerificationReport:
    scenario: str
    passed: bool
    evidence: tuple[Evidence, ...]

    @property
    def failed_evidence(self) -> tuple[Evidence, ...]:
        return tuple(item for item in self.evidence if not item.passed)


def create_potemkin_signup_app() -> Application:
    app = Application()

    def submit(application: Application) -> None:
        email = application.fields.get("email", "")
        application.screen_text.append(f"Thanks, {email}")
        application.logs.append("submit:signup:displayed-message-only")

    app.handlers["submit-signup"] = submit
    return app


def create_working_signup_app() -> Application:
    app = Application()

    def submit(application: Application) -> None:
        email = application.fields.get("email", "")
        application.state["users"].append({"email": email})
        application.screen_text.append(f"Confirmation sent to {email}")
        application.logs.append("submit:signup:persisted-user")

    app.handlers["submit-signup"] = submit
    return app


def signup_scenario(include_behavioral_checks: bool = True) -> Scenario:
    success_text = "Confirmation sent" if include_behavioral_checks else "Thanks"
    steps = [
        VerificationStep(StepType.VISIT, "/signup", description="Open signup page"),
        VerificationStep(StepType.ASSERT_TEXT, "Create account", description="Signup title renders"),
        VerificationStep(StepType.FILL, "email", "alex@example.com", "Enter email"),
        VerificationStep(StepType.CLICK, "submit-signup", description="Submit signup"),
        VerificationStep(StepType.ASSERT_TEXT, success_text, description="Success feedback appears"),
    ]

    if include_behavioral_checks:
        steps.extend(
            [
                VerificationStep(
                    StepType.ASSERT_STATE,
                    "users.email",
                    "alex@example.com",
                    "Submitted email is persisted",
                ),
                VerificationStep(
                    StepType.ASSERT_LOG,
                    "submit:signup:persisted-user",
                    description="Persistence path executed",
                ),
            ]
        )

    return Scenario(
        name="signup flow",
        intent="A user can submit an email and become a persisted signup user.",
        steps=tuple(steps),
    )


def _assert_text(app: Application, expected_text: str) -> Evidence:
    observed = " | ".join(app.screen_text)
    return Evidence(
        step=f"assert_text:{expected_text}",
        passed=expected_text.lower() in observed.lower(),
        observed=observed,
        expected=expected_text,
        severity=Severity.BLOCKER,
    )


def _assert_state(app: Application, target: str, expected: object) -> Evidence:
    if target == "users.email":
        observed = [user.get("email") for user in app.state.get("users", [])]
        passed = expected in observed
    else:
        observed = app.state.get(target)
        passed = observed == expected

    return Evidence(
        step=f"assert_state:{target}",
        passed=passed,
        observed=observed,
        expected=expected,
        severity=Severity.BLOCKER,
    )


def _assert_log(app: Application, expected: str) -> Evidence:
    return Evidence(
        step=f"assert_log:{expected}",
        passed=expected in app.logs,
        observed=list(app.logs),
        expected=expected,
        severity=Severity.BLOCKER,
    )


def run_scenario(app: Application, scenario: Scenario) -> VerificationReport:
    app_under_test = app.clone()
    evidence: list[Evidence] = []

    for step in scenario.steps:
        if step.type == StepType.VISIT:
            app_under_test.visit(str(step.target))
            evidence.append(Evidence("visit", True, app_under_test.route, step.target, Severity.INFO))
        elif step.type == StepType.FILL:
            app_under_test.fill(step.target, str(step.value))
            evidence.append(Evidence(f"fill:{step.target}", True, app_under_test.fields.get(step.target), step.value, Severity.INFO))
        elif step.type == StepType.CLICK:
            app_under_test.click(step.target)
            evidence.append(Evidence(f"click:{step.target}", True, list(app_under_test.logs), f"clicked {step.target}", Severity.INFO))
        elif step.type == StepType.ASSERT_TEXT:
            evidence.append(_assert_text(app_under_test, step.target))
        elif step.type == StepType.ASSERT_STATE:
            evidence.append(_assert_state(app_under_test, step.target, step.value))
        elif step.type == StepType.ASSERT_LOG:
            evidence.append(_assert_log(app_under_test, step.target))

    return VerificationReport(
        scenario=scenario.name,
        passed=all(item.passed for item in evidence if item.severity == Severity.BLOCKER),
        evidence=tuple(evidence),
    )


def repair_application(app: Application, report: VerificationReport) -> Application:
    failed_steps = {item.step for item in report.failed_evidence}
    repaired = app.clone()

    if "assert_state:users.email" in failed_steps or any(step.startswith("assert_log:submit:signup:persisted-user") for step in failed_steps):
        working = create_working_signup_app()
        repaired.handlers["submit-signup"] = working.handlers["submit-signup"]

    return repaired


def evidence_to_dict(item: Evidence) -> dict:
    return {
        "step": item.step,
        "passed": item.passed,
        "observed": item.observed,
        "expected": item.expected,
        "severity": item.severity.value,
    }


def report_to_dict(report: VerificationReport) -> dict:
    return {
        "scenario": report.scenario,
        "passed": report.passed,
        "evidence": [evidence_to_dict(item) for item in report.evidence],
    }


def run_demo() -> dict:
    broken_app = create_potemkin_signup_app()
    shallow = run_scenario(broken_app, signup_scenario(include_behavioral_checks=False))
    before = run_scenario(broken_app, signup_scenario(include_behavioral_checks=True))
    repaired_app = repair_application(broken_app, before)
    after = run_scenario(repaired_app, signup_scenario(include_behavioral_checks=True))

    return {
        "ok": shallow.passed and not before.passed and after.passed,
        "shallow_verification": report_to_dict(shallow),
        "behavioral_before_repair": report_to_dict(before),
        "behavioral_after_repair": report_to_dict(after),
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
