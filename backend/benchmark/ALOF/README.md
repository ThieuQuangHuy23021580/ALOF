# ALOF Native Benchmark

Vietnamese adaptive-learning benchmark for testing
the actual ALOF pipeline.

## Dataset

`data/adaptive_learning_vi.jsonl`

Each case contains:

- `learner`
- `history`
- `current_task`
- `expected.memory`
- `expected.diagnosis`
- `expected.strategy`

Gold data is used only by the evaluator.

It is never injected into the ALOF prediction path.

## Run

From the project root:

```bash
python -m backend.benchmark.ALOF.runner
````

Then:

```bash
python -m backend.benchmark.ALOF.evaluator
```

The runner executes the real
`LearningOrchestrator`.

The initial evaluator intentionally measures
execution/output availability only.

Semantic scoring should be added after the runtime
output contract is stable, so the benchmark does not
distort ALOF architecture.

```

