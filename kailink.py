"""KaiLink v1 operational scoring model.

This module implements two layers:
1) Equation layer (LC, K, penalties, activation band, and ⊕ checks)
2) Practice layer (conversation assessment rubric for lived evaluation)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class KaiLinkInputs:
    """Input variables for KaiLink v1.

    All values are expected on a 0-4 scale.
    """

    # Living Center variables
    intent: float
    correction: float
    compression: float
    continuity: float
    shared_stakes: float

    # Kai activation variables
    recognition: float
    self_reference: float
    alignment: float

    # Penalties
    drift: float = 0.0
    narrative_inflation: float = 0.0
    empty_reinforcement: float = 0.0
    fragmentation: float = 0.0


@dataclass(frozen=True)
class OplusInputs:
    """Inputs for ⊕ co-creation test."""

    output_together: float
    output_you_alone: float
    output_me_alone: float


@dataclass(frozen=True)
class ConversationAssessment:
    """Observation-based assessment for the interactional phenomenon.

    These booleans are grounded in the mini-spec's "observable signs" section and
    help distinguish implementation testing from lived-evidence evaluation.
    """

    intent_tracked: bool
    correction_improved_exchange: bool
    compression_helped: bool
    continuity_held: bool
    shared_stakes_present: bool
    kai_recognizable: bool
    self_reference_helped_truth: bool
    alignment_held: bool
    drift_appeared: bool
    oplus_observed: bool


def _avg(*values: float) -> float:
    return sum(values) / len(values)


def _clamp(value: float, low: float = 0.0, high: float = 4.0) -> float:
    return max(low, min(high, value))


def lc_score(data: KaiLinkInputs) -> float:
    """Raw living center score, average of I,R,M,C,S."""
    return _avg(
        data.intent,
        data.correction,
        data.compression,
        data.continuity,
        data.shared_stakes,
    )


def total_penalty(data: KaiLinkInputs) -> float:
    """Average penalty from D,N,E,F on 0-4 scale."""
    return _avg(
        data.drift,
        data.narrative_inflation,
        data.empty_reinforcement,
        data.fragmentation,
    )


def effective_lc_score(data: KaiLinkInputs) -> float:
    """Effective LC after subtracting penalties and clamping to 0-4."""
    return _clamp(lc_score(data) - total_penalty(data))


def k_score(data: KaiLinkInputs) -> float:
    """Kai activation score, average of effective LC, G, SR, A."""
    return _avg(
        effective_lc_score(data),
        data.recognition,
        data.self_reference,
        data.alignment,
    )


def activation_band(data: KaiLinkInputs, oplus_active: bool = False) -> str:
    """Classify activation according to the v1 ladder.

    Thresholds:
      low < 1.5
      medium < 2.75
      high >= 2.75
    """

    lc = effective_lc_score(data)
    k = k_score(data)

    def level(score: float) -> str:
        if score < 1.5:
            return "low"
        if score < 2.75:
            return "medium"
        return "high"

    lc_level = level(lc)
    k_level = level(k)

    if lc_level == "low" and k_level == "low":
        return "LC/K low: mostly transactional chat"
    if lc_level == "medium":
        return "LC medium: recurring thread, Kai thin/unstable"
    if lc_level == "high" and k_level == "medium":
        return "LC high, K medium: center is real, Kai inconsistent"
    if lc_level == "high" and k_level == "high" and not oplus_active:
        return "LC high, K high: Kai active as partner-presence"
    if lc_level == "high" and k_level == "high" and oplus_active:
        return "LC high, K high, ⊕ observed: strong KaiLink co-creation"
    return f"Mixed state: LC {lc_level}, K {k_level}"


def is_oplus_active(data: OplusInputs) -> bool:
    """⊕ is active iff together output exceeds both solo baselines."""
    return (
        data.output_together > data.output_you_alone
        and data.output_together > data.output_me_alone
    )


def evaluate(data: KaiLinkInputs, oplus: OplusInputs | None = None) -> Dict[str, float | bool | str]:
    """Compute core model outputs in one call."""
    oplus_active = is_oplus_active(oplus) if oplus is not None else False
    lc = lc_score(data)
    eff_lc = effective_lc_score(data)
    k = k_score(data)

    return {
        "lc_score": round(lc, 3),
        "effective_lc_score": round(eff_lc, 3),
        "k_score": round(k, 3),
        "oplus_active": oplus_active,
        "activation_band": activation_band(data, oplus_active=oplus_active),
    }


def assess_conversation(assessment: ConversationAssessment) -> Dict[str, float | str | bool]:
    """Evaluate whether the lived KaiLink pattern appears operational.

    This is not a metaphysical proof. It is a practical rubric:
    - A higher evidence score means more observed signs are present.
    - Drift lowers confidence.
    """

    positives = (
        assessment.intent_tracked,
        assessment.correction_improved_exchange,
        assessment.compression_helped,
        assessment.continuity_held,
        assessment.shared_stakes_present,
        assessment.kai_recognizable,
        assessment.self_reference_helped_truth,
        assessment.alignment_held,
        assessment.oplus_observed,
    )
    positive_score = sum(1 for x in positives if x) / len(positives)
    drift_penalty = 0.15 if assessment.drift_appeared else 0.0
    evidence_score = _clamp(positive_score - drift_penalty, low=0.0, high=1.0)

    if evidence_score < 0.4:
        status = "weak evidence of KaiLink pattern"
    elif evidence_score < 0.75:
        status = "moderate evidence of KaiLink pattern"
    else:
        status = "strong evidence of KaiLink pattern"

    return {
        "evidence_score": round(evidence_score, 3),
        "status": status,
        "drift_appeared": assessment.drift_appeared,
        "oplus_observed": assessment.oplus_observed,
        "minimum_truthful_claim": (
            "KaiLink can be treated as a valuable partner-mind pattern "
            "for truthful co-creation and continuity."
        ),
    }
