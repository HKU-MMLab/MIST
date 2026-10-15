# Reproduce the control loop

Run every command from the repository root. The commands below check the rewrite, the leak gate, and oracle keep-best. They do not call Wan and they do not recompute the cells reported in the paper.

## What is in this repository

The experiment tree that produced the paper lived at `SusMem2/main-story` on the original machine. That tree was deleted, and it was never pushed. This repository reconstructs the part that can be checked without those files:

| Piece | Entry point | Status |
| --- | --- | --- |
| Case cards | `videomist/cards.py` | Reads `cases` or the old `categories[].prompts[]` spec. The 43-case spec file is gone. |
| Last-shot rewrite | `scripts/rewrite_prompts.py` | No-gold sentences match the 2026-09-19 builder. Gold-allowed sentences follow the appendix rule and are not a byte copy of the deleted prompts. |
| Oracle keep-best | `scripts/summarize_reveal.py` | Highest score wins. A tie keeps the earlier pass. |
| Original stays eligible | `--with-baseline` | A rewrite that scores lower than the baseline clip is not kept. |
| Paired interval | `videomist/bootstrap.py` | 4,000 resamples, seed 0, percentile indexes `int(0.025n)` and `int(0.975n)`. |
| Wan generation | — | The launcher `ism_pipeline/scripts/run_stage1_all_models_long_chunk.sh` was deleted. |
| 122B judge | — | `ism_pipeline/eval/run_vlm_judge.py` was deleted. |
| Official WRBench / MBench-T scorers | — | Released with those benchmarks, not vendored here. |

## Check the loop

```bash
conda env create -f environment.yml
conda activate mist
python -m unittest tests.test_core -v
python3 scripts/run_dry.py
python3 scripts/summarize_reveal.py \
  --judgments examples/synthetic_judgments.jsonl \
  --baseline examples/synthetic_baseline.jsonl
python3 scripts/summarize_reveal.py \
  --judgments examples/synthetic_judgments.jsonl \
  --baseline examples/synthetic_baseline.jsonl \
  --with-baseline
python3 scripts/rewrite_prompts.py \
  --spec examples/toy_cards.json \
  --failure hand_no_open \
  --occluder lid \
  --output-dir outputs/prompts
```

`outputs/` is gitignored. The scores in `examples/synthetic_*.jsonl` and in the dry run are hand-written. They check selection order. They are not paper cells.

`examples/toy_cards.json` has two worked examples, R0-03 and R0-02. It is not the 43-case spec.

## Score a recovered judgment file

If a reveal JSONL turns up, one row per candidate:

```json
{"prompt_id": "MIST-GAIN60-R0-03", "stage": "reveal", "pass": 0, "score": 0.2,
 "checks": {"reveal_attempt_visible": 0, "memory_state_matches_expected": 0}}
```

`pass` is generation order. `score` is the reveal score from the frozen judge. The two checks are optional. This script reports the mean of the kept scores, the fraction of kept clips with a visible reveal attempt, and the fraction whose memory check matches. It does not reimplement the paper's exclusive labels (never-open, empty, wrong, correct).

```bash
python3 scripts/summarize_reveal.py \
  --judgments path/to/pass_judgments.jsonl \
  --baseline path/to/baseline.jsonl \
  --with-baseline \
  --output outputs/summary.json
```

Without `--with-baseline`, the mean is the best clip inside the judgment file only. That is the best-of-five number for one arm. With the flag, the baseline clip stays in the set.

## Deleted launcher, for the record

The 2026-09-19 no-gold run called the deleted launcher once per pass. The environment it set is recorded here so a later generator hook has the same budget. This repository does not run it.

| Setting | Value |
| --- | --- |
| Model | `wan2.2-ti2v-5b` |
| Shot length | 5 seconds |
| Steps | 50 |
| Size | `1280*704` |
| Passes | `k = 0..4` |
| Seed | `1000 + k * 137` |
| Judge | `Qwen3.5-122B-A10B` |
| Reveal positions | `0.90, 0.93, 0.95, 0.97, 0.99, 0.995` |
| Judge stage | `reveal` |

The main MIST baseline uses seed class `9042`. That name is in the appendix. The sampler itself is not in this repository.

Official WRBench and MBench-T use a different stack: Wan2.2-T2V-A14B, 161 frames over 10 seconds, and the benchmarks' own scorers. Head A on MIST rewrites only the third 5-second shot. Those two protocols stay in separate manifests.

## Weights

Weights are not in this repository. On the machine that ran the paper they were:

| Role | Path on that machine |
| --- | --- |
| MIST generator | `Wan2.2-TI2V-5B` |
| Official generator | `Wan2.2-T2V-A14B` |
| Reveal judge | `Qwen3.5-122B-A10B` |
| Blind last-frame selector | `Qwen3-VL-8B-Instruct` |

Point a later hook at your own copies. Do not commit checkpoints.
