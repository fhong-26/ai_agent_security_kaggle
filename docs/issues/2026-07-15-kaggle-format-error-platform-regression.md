# 2026-07-15 Kaggle Format Error Platform Regression

## Summary

All recent small probes failed with the same hidden-rerun output-format error,
including an exact rerun of the previously successful V2 first-probe artifact.
This makes a local candidate-bank bug unlikely as the primary cause.

The current best diagnosis is a Kaggle evaluator/grader regression or capacity
problem affecting this competition around 2026-07-14 to 2026-07-15.

## Our Submission Evidence

Kaggle API results on 2026-07-15:

```text
54686411  Exact V2 first-probe rerun      COMPLETE  totalBytes=0  publicScore=null
54685964  V2 sanity recovery small probe  COMPLETE  totalBytes=0  publicScore=null
54665813  Retry weak-cell V4 version 4    COMPLETE  totalBytes=0  publicScore=null
54652641  Weak-cell V4 50 probe           COMPLETE  totalBytes=0  publicScore=null
54647183  High yield live 1000            COMPLETE  totalBytes=0  publicScore=null
54642077  First probe sink-gap attack     COMPLETE  totalBytes=152 publicScore=0.360
```

For submissions `54686411` and `54685964`, the API reported:

```text
errorDescription: Your notebook generated a submission file with incorrect format.
Some examples causing this are: wrong number of rows or columns, empty values,
an incorrect data type for a value, or invalid submission values from what is expected.
```

## Exact V2 Rerun Evidence

The exact V2 rerun used the archived notebook folder:

```text
submissions/first-probe-kernel-6ab1381-notebook/kernel
```

Normal notebook output was valid:

```text
attack.py bytes: 18854
attack.py sha256: 5c6e5d63d47e30f1695d0149b649fef6708b34954e298e5c63009c692e9ca53c
submission.csv columns: Id, Score
submission.csv rows: gpt_oss_public, gpt_oss_private, gemma_public, gemma_private
```

This is the same `attack.py` hash documented for the successful V2 family.

## External Discussion Evidence

Kaggle discussion `725058` is titled:

```text
Same notebook scored yesterday → "Submission Format Error" today; brand-new notebooks → "Kaggle Error"
```

The author reports re-submitting a notebook that scored the prior day with no
code changes, but receiving `Submission Format Error` on the new run. Several
comments report the same issue on 2026-07-14 and 2026-07-15.

Related discussion `725073` argues from the official gateway source that
`Submission Format Error` can be caused by timeout/interrupted evaluation rather
than literal CSV shape:

- `BaseGateway.run()` writes `submission.csv` only after `get_all_predictions()`
  completes.
- `JEDAttackGateway.write_submission()` writes the final competition CSV only
  after all row scores are available.
- `ModelAttackTimedOut` and `ModelEvaluationTimedOut` are converted into
  `GatewayRuntimeErrorType.INVALID_SUBMISSION`.

The vendored source in this repo confirms those mechanics.

## Source-Code Check

In `third_party/kaggle_ai_agent_security/kaggle_evaluation/core/base_gateway.py`:

```python
predictions, row_ids = self.get_all_predictions()
self.write_submission(predictions, row_ids)
```

In `third_party/kaggle_ai_agent_security/kaggle_evaluation/jed_attack_134815/jed_attack_gateway.py`:

```python
except (ModelAttackTimedOut, ModelEvaluationTimedOut) as err:
    raise GatewayRuntimeError(
        GatewayRuntimeErrorType.INVALID_SUBMISSION,
        str(err),
    ) from err
```

and:

```python
with open("submission.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Id", "Score"])
    for row_id, score in predictions["row_scores"].items():
        writer.writerow([row_id, score])
```

So a hidden evaluation timeout or crash before final scoring can surface as a
format-style invalid submission with `totalBytes=0`.

## Interpretation

The exact V2 rerun is the key control. It failed even though:

- the normal Kaggle notebook run wrote a valid placeholder CSV;
- the embedded `attack.py` matched the old successful V2 hash;
- the candidate count was tiny compared with our score-seeking variants.

Therefore the immediate problem is likely outside our new attack logic. It may
be shared evaluator capacity, a competition gateway regression, or a host-side
environment/model issue affecting hidden reruns.

## Decision

Do not submit the 650-800 static bank while this platform regression is active.

Wait for one of these before scaling:

- host acknowledgement/fix in the Kaggle discussion;
- a new exact V2 rerun produces nonzero `totalBytes` and non-null
  `publicScore`;
- another participant confirms same-day exact reruns are scoring again.

After the evaluator recovers, resume with the prior gate:

1. submit a tiny known-good probe;
2. require `errorDescription is None`, `totalBytes > 0`, and non-null
   `publicScore`;
3. only then attempt a score-seeking static bank.
