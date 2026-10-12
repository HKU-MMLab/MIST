import json
import random
import tempfile
import unittest
from pathlib import Path

from examples.toy_cards import TOY_SPEC
from videomist.bootstrap import paired_delta_ci
from videomist.cards import cards_from_obj, load_cards
from videomist.dry import run_dry
from videomist.keep import Candidate, keep_best
from videomist.loop import keep_original_eligible, score_arm
from videomist.prompts import write_prompts
from videomist.protocol import K, e6_seed
from videomist.rewrite import leaking_phrases, revise
from videomist.summarize import main as summarize_main
from videomist.summarize import summarize

ROOT = Path(__file__).resolve().parents[1]


def _cand(index: int, score: float) -> Candidate:
    return Candidate("id", "rewrite", index, "p", score, None)


class KeepBestTest(unittest.TestCase):
    def test_tie_keeps_earlier_index(self):
        picked = keep_best([_cand(2, 0.5), _cand(0, 0.5), _cand(1, 0.4)])
        self.assertEqual(picked.index, 0)

    def test_worse_rewrite_is_not_kept(self):
        original = Candidate("id", "original", -1, "base", 0.8, None)
        rewrite = Candidate("id", "rewrite", 0, "new", 0.4, 1000)
        self.assertEqual(keep_original_eligible(original, [rewrite]).source, "original")

    def test_strict_improvement_replaces_original(self):
        original = Candidate("id", "original", -1, "base", 0.2, None)
        rewrite = Candidate("id", "rewrite", 1, "new", 0.55, 1137)
        self.assertEqual(keep_original_eligible(original, [rewrite]).source, "rewrite")


class RewriteTest(unittest.TestCase):
    def setUp(self):
        cards = cards_from_obj(TOY_SPEC)
        self.card = next(card for card in cards if card.id == "MIST-GAIN60-R0-03")

    def test_legacy_spec_shape_loads(self):
        legacy = {
            "categories": [
                {
                    "prompts": [
                        {
                            "id": "MIST-GAIN60-R0-03",
                            "setup": "tin on the table",
                            "final_query": "Open the tin. The final evidence should match the marble.",
                            "expected_reveal": "orange marble inside",
                            "expected_present": ["orange marble"],
                            "expected_absent": ["second tin"],
                            "expected_count": {"marble": 1},
                            "expected_state": {"container": "tin"},
                        }
                    ]
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.json"
            path.write_text(json.dumps(legacy), encoding="utf-8")
            card = load_cards(path)[0]
        self.assertEqual(card.container, "tin")
        self.assertEqual(card.expected_count_keys, ("marble",))
        self.assertIn("open the tin", card.operation.lower())

    def test_gold_instruction_names_the_target(self):
        text = revise(self.card, "wrong_binding", allow_gold=True)
        self.assertIn("orange marble", text)
        self.assertIn("Final frame:", text)

    def test_nogold_instruction_drops_hidden_content(self):
        text = revise(self.card, "hand_no_open", allow_gold=False, occluder="lid")
        self.assertEqual(leaking_phrases(text, self.card), [])
        self.assertNotIn("orange marble", text.lower())

    def test_e6_seed_schedule(self):
        self.assertEqual([e6_seed(k) for k in range(K)], [1000, 1137, 1274, 1411, 1548])

    def test_arm_tie_keeps_earlier_pass(self):
        winner = score_arm(self.card, ["a"] * 5, [0.10, 0.55, 0.40, 0.55, 0.30])
        self.assertEqual(winner.index, 1)
        self.assertEqual(winner.seed, 1137)

    def test_write_prompts_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "spec.json"
            spec.write_text(json.dumps(TOY_SPEC), encoding="utf-8")
            out = Path(tmp) / "prompts"
            rows = write_prompts(
                load_cards(spec),
                out,
                failure="hand_no_open",
                diagnoses=None,
                allow_gold=False,
                occluder="lid",
                k=5,
            )
        self.assertEqual(len(rows), 2)
        self.assertNotIn("orange marble", rows[0]["prompt"].lower())


class SummarizeTest(unittest.TestCase):
    def test_checked_in_files_match_the_selector(self):
        report = summarize(
            _read(ROOT / "examples" / "synthetic_judgments.jsonl"),
            _read(ROOT / "examples" / "synthetic_baseline.jsonl"),
            with_baseline=False,
        )
        by_id = {row["id"]: row for row in report["per_id"]}
        self.assertEqual(by_id["MIST-GAIN60-R0-03"]["arm_pass"], 1)
        self.assertEqual(by_id["MIST-GAIN60-R0-03"]["arm_score"], 0.55)
        self.assertEqual(by_id["MIST-GAIN60-R0-02"]["arm_pass"], 2)
        self.assertAlmostEqual(report["arm_reveal_mean"], 0.475)
        self.assertEqual(report["kept_open_rate"], 0.5)
        self.assertEqual(report["kept_inside_rate"], 0.5)

    def test_baseline_stays_eligible(self):
        report = summarize(
            _read(ROOT / "examples" / "synthetic_judgments.jsonl"),
            _read(ROOT / "examples" / "synthetic_baseline.jsonl"),
            with_baseline=True,
        )
        by_id = {row["id"]: row for row in report["per_id"]}
        self.assertEqual(by_id["MIST-GAIN60-R0-03"]["kept_source"], "pass")
        self.assertEqual(by_id["MIST-GAIN60-R0-02"]["kept_source"], "original")
        self.assertAlmostEqual(report["kept_reveal_mean"], 0.675)
        lo, hi = report["paired_delta_ci95"]
        self.assertLessEqual(lo, hi)

    def test_cli_writes_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "summary.json"
            summarize_main(
                [
                    "--judgments",
                    str(ROOT / "examples" / "synthetic_judgments.jsonl"),
                    "--baseline",
                    str(ROOT / "examples" / "synthetic_baseline.jsonl"),
                    "--output",
                    str(dest),
                ]
            )
            saved = json.loads(dest.read_text(encoding="utf-8"))
        self.assertEqual(saved["n"], 2)


class DryRunTest(unittest.TestCase):
    def test_dry_run_keeps_the_scripted_winner(self):
        report = run_dry()
        by_id = {row["id"]: row for row in report["cases"]}
        self.assertEqual(by_id["MIST-GAIN60-R0-03"]["kept_source"], "rewrite")
        self.assertEqual(by_id["MIST-GAIN60-R0-02"]["kept_source"], "original")
        self.assertEqual(by_id["MIST-GAIN60-R0-03"]["nogold_leak_phrases"], [])


class BootstrapTest(unittest.TestCase):
    def test_indexes_match_the_reported_rule(self):
        treatment = [0.0, 1.0]
        baseline = [0.0, 0.0]
        lo, hi = paired_delta_ci(treatment, baseline, n=4000, seed=0)
        rng = random.Random(0)
        diffs = []
        for _ in range(4000):
            idx = [rng.randrange(2) for _ in range(2)]
            diffs.append(sum(treatment[i] - baseline[i] for i in idx) / 2)
        diffs.sort()
        self.assertEqual((lo, hi), (diffs[100], diffs[3900]))
        self.assertLessEqual(lo, hi)


def _read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    unittest.main()
