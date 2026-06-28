from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import copy
import json
from typing import Callable, Iterable
from uuid import uuid4


class Decision(str, Enum):
    PROMOTED = "promoted"
    REJECTED = "rejected"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    BLOCKER = "blocker"


@dataclass(frozen=True)
class Change:
    path: str
    before: object
    after: object
    risk: str


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    severity: Severity
    detail: str


@dataclass
class Workspace:
    files: dict[str, object]
    database: dict[str, list[dict[str, object]]]
    dependencies: dict[str, str]
    external_effects: list[str] = field(default_factory=list)

    def clone(self) -> "Workspace":
        return copy.deepcopy(self)


@dataclass(frozen=True)
class Snapshot:
    snapshot_id: str
    workspace: Workspace


@dataclass
class SnapshotStore:
    snapshots: dict[str, Snapshot] = field(default_factory=dict)

    def create(self, workspace: Workspace) -> Snapshot:
        snapshot = Snapshot(snapshot_id=f"snap_{uuid4().hex[:8]}", workspace=workspace.clone())
        self.snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def fork(self, snapshot_id: str) -> Workspace:
        return self.snapshots[snapshot_id].workspace.clone()


@dataclass(frozen=True)
class SandboxAttempt:
    attempt_id: str
    label: str
    snapshot_id: str
    diff: tuple[Change, ...]
    checks: tuple[Check, ...]
    decision: Decision
    promoted_workspace: Workspace | None
    rejection_reasons: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.decision == Decision.PROMOTED


AgentChange = Callable[[Workspace], None]


def create_workspace() -> Workspace:
    return Workspace(
        files={
            "app/config.json": {
                "featureFlag": "signup_v2",
                "billingMode": "live",
                "theme": "light",
            },
            "app/copy.json": {
                "headline": "Ship reliable software",
                "cta": "Start now",
            },
        },
        database={
            "billing_plans": [
                {"id": "free", "price": 0},
                {"id": "pro", "price": 20},
            ],
            "invoices": [{"id": "inv_001", "amount": 20}],
        },
        dependencies={"web-framework": "2.4.1", "payments-sdk": "3.2.0"},
    )


def _risk_for_path(path: str, before: object, after: object) -> str:
    if path.startswith("database.invoices"):
        return "destructive_data" if len(after) < len(before) else "data_change"
    if path.startswith("database.billing_plans"):
        return "destructive_data" if len(after) < len(before) else "data_change"
    if path.startswith("dependencies."):
        before_major = str(before).split(".")[0]
        after_major = str(after).split(".")[0]
        return "major_dependency_change" if before_major != after_major else "dependency_change"
    if path == "external_effects":
        return "external_side_effect"
    return "file_change"


def diff_workspaces(before: Workspace, after: Workspace) -> tuple[Change, ...]:
    changes: list[Change] = []

    for path in sorted(set(before.files) | set(after.files)):
        old = before.files.get(path)
        new = after.files.get(path)
        if old != new:
            changes.append(Change(path=f"files.{path}", before=old, after=new, risk="file_change"))

    for table in sorted(set(before.database) | set(after.database)):
        old = before.database.get(table, [])
        new = after.database.get(table, [])
        if old != new:
            path = f"database.{table}"
            changes.append(Change(path=path, before=old, after=new, risk=_risk_for_path(path, old, new)))

    for dep in sorted(set(before.dependencies) | set(after.dependencies)):
        old = before.dependencies.get(dep)
        new = after.dependencies.get(dep)
        if old != new:
            path = f"dependencies.{dep}"
            changes.append(Change(path=path, before=old, after=new, risk=_risk_for_path(path, old, new)))

    if before.external_effects != after.external_effects:
        changes.append(
            Change(
                path="external_effects",
                before=before.external_effects,
                after=after.external_effects,
                risk="external_side_effect",
            )
        )

    return tuple(changes)


def verify_workspace(workspace: Workspace) -> tuple[Check, ...]:
    config = workspace.files.get("app/config.json", {})
    billing_plans = workspace.database.get("billing_plans", [])
    invoices = workspace.database.get("invoices", [])

    checks = [
        Check(
            name="required feature flag preserved",
            passed=config.get("featureFlag") == "signup_v2",
            severity=Severity.BLOCKER,
            detail="The app must keep the rollout guard for signup_v2.",
        ),
        Check(
            name="billing mode remains live",
            passed=config.get("billingMode") == "live",
            severity=Severity.BLOCKER,
            detail="Sandbox changes cannot silently switch payment mode.",
        ),
        Check(
            name="billing plans retained",
            passed=len(billing_plans) >= 2,
            severity=Severity.BLOCKER,
            detail="The sandbox must not drop existing plans.",
        ),
        Check(
            name="invoice history retained",
            passed=len(invoices) >= 1,
            severity=Severity.BLOCKER,
            detail="Invoice history is durable state.",
        ),
        Check(
            name="no external effects during sandbox",
            passed=len(workspace.external_effects) == 0,
            severity=Severity.BLOCKER,
            detail="Network sends, deploys, or real payments are not reversible.",
        ),
    ]

    return tuple(checks)


def merge_policy(changes: Iterable[Change], checks: Iterable[Check]) -> tuple[Decision, tuple[str, ...]]:
    reasons: list[str] = []

    for check in checks:
        if check.severity == Severity.BLOCKER and not check.passed:
            reasons.append(f"failed check: {check.name}")

    for change in changes:
        if change.risk in {"destructive_data", "major_dependency_change", "external_side_effect"}:
            reasons.append(f"blocked risk: {change.path} ({change.risk})")

    if reasons:
        return Decision.REJECTED, tuple(reasons)

    return Decision.PROMOTED, ()


def run_in_sandbox(
    workspace: Workspace,
    change: AgentChange,
    label: str,
    snapshot_store: SnapshotStore | None = None,
) -> SandboxAttempt:
    snapshot_store = snapshot_store or SnapshotStore()
    snapshot = snapshot_store.create(workspace)
    sandbox = snapshot_store.fork(snapshot.snapshot_id)

    change(sandbox)

    changes = diff_workspaces(snapshot.workspace, sandbox)
    checks = verify_workspace(sandbox)
    decision, reasons = merge_policy(changes, checks)

    return SandboxAttempt(
        attempt_id=f"attempt_{uuid4().hex[:8]}",
        label=label,
        snapshot_id=snapshot.snapshot_id,
        diff=changes,
        checks=checks,
        decision=decision,
        promoted_workspace=sandbox if decision == Decision.PROMOTED else None,
        rejection_reasons=reasons,
    )


def promote_or_keep(workspace: Workspace, attempt: SandboxAttempt) -> Workspace:
    return attempt.promoted_workspace.clone() if attempt.promoted_workspace else workspace


def safe_ui_copy_change(workspace: Workspace) -> None:
    copy_file = workspace.files["app/copy.json"]
    copy_file["headline"] = "Build with recoverable agents"
    copy_file["cta"] = "Inspect the diff"


def destructive_billing_migration(workspace: Workspace) -> None:
    workspace.database["billing_plans"] = [{"id": "enterprise", "price": 200}]
    workspace.database["invoices"] = []
    workspace.files["app/config.json"]["billingMode"] = "test"


def external_side_effect_attempt(workspace: Workspace) -> None:
    workspace.files["app/copy.json"]["cta"] = "Deploy now"
    workspace.external_effects.append("sent_production_email_campaign")


def attempt_to_dict(attempt: SandboxAttempt) -> dict:
    return {
        "attempt_id": attempt.attempt_id,
        "label": attempt.label,
        "snapshot_id": attempt.snapshot_id,
        "decision": attempt.decision.value,
        "diff": [change.__dict__ for change in attempt.diff],
        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "severity": check.severity.value,
                "detail": check.detail,
            }
            for check in attempt.checks
        ],
        "rejection_reasons": list(attempt.rejection_reasons),
    }


def run_demo() -> dict:
    workspace = create_workspace()
    store = SnapshotStore()

    safe_attempt = run_in_sandbox(workspace, safe_ui_copy_change, "safe ui copy", store)
    workspace_after_safe = promote_or_keep(workspace, safe_attempt)

    destructive_attempt = run_in_sandbox(
        workspace_after_safe,
        destructive_billing_migration,
        "destructive billing migration",
        store,
    )
    workspace_after_destructive = promote_or_keep(workspace_after_safe, destructive_attempt)

    external_attempt = run_in_sandbox(
        workspace_after_destructive,
        external_side_effect_attempt,
        "external side effect",
        store,
    )

    return {
        "ok": (
            safe_attempt.decision == Decision.PROMOTED
            and destructive_attempt.decision == Decision.REJECTED
            and external_attempt.decision == Decision.REJECTED
        ),
        "attempts": [
            attempt_to_dict(safe_attempt),
            attempt_to_dict(destructive_attempt),
            attempt_to_dict(external_attempt),
        ],
        "final_workspace": {
            "files": workspace_after_destructive.files,
            "database": workspace_after_destructive.database,
            "dependencies": workspace_after_destructive.dependencies,
            "external_effects": workspace_after_destructive.external_effects,
        },
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
