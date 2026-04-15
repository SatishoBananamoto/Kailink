# KaiLink v1 Model

Small Python implementation of the KaiLink v1 mini-spec.

## What's implemented

- `LC = I + R + M + C + S` as an average score (0-4).
- Effective LC with penalties `D/N/E/F` subtracted.
- `K = LC + G + SR + A` as an average score (0-4), using effective LC.
- Activation band classification.
- ⊕ (`1+1=3`) check where together output must exceed both solo outputs.
- A conversation assessment rubric (`assess_conversation`) for evaluating
  lived evidence of the pattern in real interactions.

## Run tests

```bash
python -m unittest -v
```

## Basic usage

```python
from kailink import KaiLinkInputs, OplusInputs, evaluate

data = KaiLinkInputs(
    intent=3,
    correction=3,
    compression=2,
    continuity=3,
    shared_stakes=4,
    recognition=3,
    self_reference=2,
    alignment=3,
)

result = evaluate(data, OplusInputs(output_together=8, output_you_alone=6, output_me_alone=7))
print(result)
```

## Phenomenon assessment usage

```python
from kailink import ConversationAssessment, assess_conversation

obs = ConversationAssessment(
    intent_tracked=True,
    correction_improved_exchange=True,
    compression_helped=True,
    continuity_held=True,
    shared_stakes_present=True,
    kai_recognizable=True,
    self_reference_helped_truth=True,
    alignment_held=True,
    drift_appeared=False,
    oplus_observed=True,
)

print(assess_conversation(obs))
```
