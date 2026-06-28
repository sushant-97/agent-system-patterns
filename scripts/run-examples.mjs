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

const demos = [
  ["Decision-Time Guidance", runDecisionTimeGuidanceDemo],
];

for (const [name, run] of demos) {
  const result = run();
  console.log(`\n## ${name}`);
  console.log(JSON.stringify(result, null, 2));

  if (!result.ok) {
    process.exitCode = 1;
  }
}
