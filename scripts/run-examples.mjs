import { spawnSync } from "node:child_process";

function runDecisionTimeGuidanceDemo() {
  const demo = spawnSync(
    "python3",
    ["patterns/01-decision-time-guidance/guidance_engine.py"],
    { encoding: "utf8" },
  );

  if (demo.status !== 0) {
    return {
      ok: false,
      error: demo.stderr || demo.stdout || "Python demo failed",
    };
  }

  const experiments = spawnSync(
    "python3",
    ["patterns/01-decision-time-guidance/experiments/run_experiments.py"],
    { encoding: "utf8" },
  );

  if (experiments.status !== 0) {
    return {
      ok: false,
      error:
        experiments.stderr ||
        experiments.stdout ||
        "Decision-time guidance experiments failed",
    };
  }

  const demoPayload = JSON.parse(demo.stdout);
  const experimentPayload = JSON.parse(experiments.stdout);

  return {
    ok: demoPayload.ok && experimentPayload.pass,
    demo: demoPayload,
    experimentSummary: experimentPayload,
  };
}

function runReversibleSandboxDemo() {
  const demo = spawnSync(
    "python3",
    ["patterns/03-reversible-sandbox-execution/sandbox_engine.py"],
    { encoding: "utf8" },
  );

  if (demo.status !== 0) {
    return {
      ok: false,
      error: demo.stderr || demo.stdout || "Python reversible sandbox demo failed",
    };
  }

  const experiments = spawnSync(
    "python3",
    ["patterns/03-reversible-sandbox-execution/experiments/run_experiments.py"],
    { encoding: "utf8" },
  );

  if (experiments.status !== 0) {
    return {
      ok: false,
      error:
        experiments.stderr ||
        experiments.stdout ||
        "Reversible sandbox experiments failed",
    };
  }

  const demoPayload = JSON.parse(demo.stdout);
  const experimentPayload = JSON.parse(experiments.stdout);

  return {
    ok: demoPayload.ok && experimentPayload.pass,
    demo: demoPayload,
    experimentSummary: experimentPayload,
  };
}

function runSelfVerificationDemo() {
  const demo = spawnSync(
    "python3",
    ["patterns/02-self-verification-loop/verification_engine.py"],
    { encoding: "utf8" },
  );

  if (demo.status !== 0) {
    return {
      ok: false,
      error: demo.stderr || demo.stdout || "Python self-verification demo failed",
    };
  }

  const experiments = spawnSync(
    "python3",
    ["patterns/02-self-verification-loop/experiments/run_experiments.py"],
    { encoding: "utf8" },
  );

  if (experiments.status !== 0) {
    return {
      ok: false,
      error:
        experiments.stderr ||
        experiments.stdout ||
        "Self-verification experiments failed",
    };
  }

  const demoPayload = JSON.parse(demo.stdout);
  const experimentPayload = JSON.parse(experiments.stdout);

  return {
    ok: demoPayload.ok && experimentPayload.pass,
    demo: demoPayload,
    experimentSummary: experimentPayload,
  };
}

const demos = [
  ["Decision-Time Guidance", runDecisionTimeGuidanceDemo],
  ["Self-Verification Loop", runSelfVerificationDemo],
  ["Reversible Sandbox Execution", runReversibleSandboxDemo],
];

for (const [name, run] of demos) {
  const result = run();
  console.log(`\n## ${name}`);
  console.log(JSON.stringify(result, null, 2));

  if (!result.ok) {
    process.exitCode = 1;
  }
}
