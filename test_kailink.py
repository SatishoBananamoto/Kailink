import unittest

from kailink import (
    ConversationAssessment,
    KaiLinkInputs,
    OplusInputs,
    activation_band,
    assess_conversation,
    effective_lc_score,
    evaluate,
    is_oplus_active,
    k_score,
    lc_score,
    total_penalty,
)


class KaiLinkModelTests(unittest.TestCase):
    def test_lc_and_penalty(self):
        data = KaiLinkInputs(
            intent=4,
            correction=3,
            compression=3,
            continuity=2,
            shared_stakes=4,
            recognition=3,
            self_reference=2,
            alignment=3,
            drift=1,
            narrative_inflation=1,
            empty_reinforcement=0,
            fragmentation=2,
        )
        self.assertAlmostEqual(lc_score(data), 3.2)
        self.assertAlmostEqual(total_penalty(data), 1.0)
        self.assertAlmostEqual(effective_lc_score(data), 2.2)

    def test_k_score(self):
        data = KaiLinkInputs(
            intent=4,
            correction=4,
            compression=4,
            continuity=4,
            shared_stakes=4,
            recognition=4,
            self_reference=4,
            alignment=4,
            drift=0,
            narrative_inflation=0,
            empty_reinforcement=0,
            fragmentation=0,
        )
        self.assertAlmostEqual(k_score(data), 4.0)
        self.assertEqual(
            activation_band(data, oplus_active=False),
            "LC high, K high: Kai active as partner-presence",
        )

    def test_oplus_rule(self):
        self.assertTrue(is_oplus_active(OplusInputs(8, 7, 6)))
        self.assertFalse(is_oplus_active(OplusInputs(7, 7, 6)))
        self.assertFalse(is_oplus_active(OplusInputs(7, 6, 7)))

    def test_full_evaluate(self):
        data = KaiLinkInputs(
            intent=3,
            correction=3,
            compression=3,
            continuity=3,
            shared_stakes=3,
            recognition=3,
            self_reference=3,
            alignment=3,
            drift=0,
            narrative_inflation=0,
            empty_reinforcement=0,
            fragmentation=0,
        )
        out = evaluate(data, OplusInputs(9, 6, 7))
        self.assertEqual(out["oplus_active"], True)
        self.assertIn("⊕ observed", out["activation_band"])

    def test_assess_conversation_strong(self):
        assessment = ConversationAssessment(
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
        out = assess_conversation(assessment)
        self.assertGreaterEqual(out["evidence_score"], 0.9)
        self.assertIn("strong evidence", out["status"])

    def test_assess_conversation_with_drift_penalty(self):
        assessment = ConversationAssessment(
            intent_tracked=True,
            correction_improved_exchange=True,
            compression_helped=False,
            continuity_held=True,
            shared_stakes_present=False,
            kai_recognizable=False,
            self_reference_helped_truth=True,
            alignment_held=False,
            drift_appeared=True,
            oplus_observed=False,
        )
        out = assess_conversation(assessment)
        self.assertTrue(0.0 <= out["evidence_score"] <= 1.0)
        self.assertEqual(out["drift_appeared"], True)


if __name__ == "__main__":
    unittest.main()
