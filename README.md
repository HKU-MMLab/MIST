<h1 align="center">Execution Before Memory:<br>Diagnosing Memory Failures in Video World Models</h1>

<p align="center">
<a href="https://waynejin0918.github.io/home/">Weiyang Jin</a><sup>1</sup> &nbsp;
<a href="https://yujiwen.github.io/">Jiwen Yu</a><sup>1</sup> &nbsp;
<a href="https://sihanxu.me/">Sihan Xu</a><sup>2</sup> &nbsp;
<a href="https://purshow.github.io/">Yuwei Niu</a><sup>3</sup> &nbsp;
<a href="https://xh-liu.github.io/">Xihui Liu</a><sup>1</sup>
</p>

<p align="center">
<sup>1</sup>University of Hong Kong &nbsp; <sup>2</sup>University of Michigan &nbsp; <sup>3</sup>Peking University
</p>

<p align="center">
  <a href="https://hku-mmlab.github.io/MIST/"><img src="https://img.shields.io/badge/Page-project-1F6F6A?style=for-the-badge" alt="Page"></a>
  <a href="https://github.com/HKU-MMLab/MIST"><img src="https://img.shields.io/badge/Code-MIST-0F6E56?style=for-the-badge" alt="Code"></a>
  <a href="https://github.com/XiaoxiaoYang2003/ICLR2027-MIST"><img src="https://img.shields.io/badge/Paper-private-8B5E4B?style=for-the-badge" alt="Paper"></a>
  <a href="docs/reproduce.md"><img src="https://img.shields.io/badge/Guide-reproduce-5B7C99?style=for-the-badge" alt="Guide"></a>
  <a href="docs/protocol.md"><img src="https://img.shields.io/badge/Protocol-cells-B08D57?style=for-the-badge" alt="Protocol"></a>
</p>

<p align="center">
  <img width="920" alt="Paper overview. MIST, WRBench, and MBench-T each show a three-frame case. M3-Agent reads the last frame, revises the missed move, and keeps the best score." src="https://github.com/HKU-MMLab/MIST/releases/download/readme-assets/teaser.png">
</p>
<p align="center">
  <em>Overview from the current paper draft. The reveal gate is separate from setup. Keep-best is an oracle.</em>
</p>

<p align="center">
  <a href="#overview">Overview</a> &bull;
  <a href="#key-findings">Key Findings</a> &bull;
  <a href="#m3-agent">M3-Agent</a> &bull;
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#related">Related</a> &bull;
  <a href="#citation">Citation</a>
</p>

## Overview

A memory score for a video world model should tell three things apart: whether the scene was set, whether the requested action was carried out, and whether the last frame lets a judge read the result. Current memory suites fold those into one total, so a low total is easy to read as forgetting. On the clips, the model much more often never opens the lid, never sits, or returns to an unchanged object. The score is lost before memory is tested.

MIST is a small Internal probe on a frozen generator. The model sets the scene while the target change stays hidden, and only later is asked to show it. M3-Agent is the test-time loop that reads the failed last frame and rewrites the missing operation. It does not add or train a memory module. Keep-best, the selection used for the best-of-five and official ceilings, sees the same score that reports the result. Those ceilings ask whether a candidate pack contains a better executable path. They are not a deployed selector, and they do not show that the backbone stored the target state.

| | Question | How this repository studies it |
| :---: | --- | --- |
| **Q1** | Where does a memory total fail? | MIST separates setup, the reveal action, and whether the last frame shows the target. |
| **Q2** | What test-time change moves the reveal gate? | M3-Agent reads the last frame, rewrites the failed operation, and keeps the highest-scoring clip. |
| **Q3** | Does that change transfer as one intervention? | Official WRBench and MBench-T move in opposite directions: complete a missing leave–return, or refuse a rewrite that would damage the returned object. |

The numbers in [Key Findings](#key-findings) are the cells reported in the paper. This repository does not regenerate them. The original experiment tree (`SusMem2/main-story`) was deleted before this code repository was filled in, and it was not on a remote. What you can run today is the control loop: card loading, the no-gold leak gate, oracle keep-best, and the paired bootstrap. The guide is [docs/reproduce.md](docs/reproduce.md). The protocol, including which cells must stay unmixed, is [docs/protocol.md](docs/protocol.md).

## Key Findings

<p align="center">
  <img width="920" alt="Paper figure. Baseline closed lids fall from 41 to 20. Best-of-five reveal is 0.763 when the target is named and 0.174 when it is withheld." src="https://github.com/HKU-MMLab/MIST/releases/download/readme-assets/story.png">
</p>

### Finding 1: The baseline fails before memory is tested

On Internal MIST, frozen Wan2.2-TI2V-5B, three 5-second shots, 43 cases, one kept clip per case:

- Setup is high (`0.852` baseline, `0.851` after the rewrite).
- The hidden interval does not leak (`0/43`).
- `41/43` baseline clips never open, so persistence is not what that baseline measures.
- One kept rewrite moves reveal from `0.147` to `0.492` and inside match from `0.047` to `0.442`.
- The same 43 clips, one exclusive label each: never-open `41 → 20`, correct `1 → 13`. Ten rewritten clips open onto the wrong contents.

This `0.492` is MIST reveal. It is not an MBench state component that prints the same digits.

### Finding 2: Rewriting the failed move helps when the answer is also in the prompt

Same judge, `K = 5`, each arm keeps the try with the highest reveal score. Keep-best is an oracle.

| What we do | Answer in prompt | Reveal | Inside | Closed | Ok |
| --- | --- | ---: | ---: | ---: | ---: |
| Rewrite: look, then change the move | yes | **0.763** | 0.721 | 5 | 29 |
| Answer only: write the target, same move | yes | 0.684 | 0.581 | 3 | 24 |
| Same sentence: new seed only | yes | 0.635 | 0.512 | 4 | 21 |
| Open only: "open and hold" | no | 0.268 | 0.093 | 6 | 3 |
| Rewrite, no answer: look, change the move | no | 0.174 | 0.047 | 28 | 2 |

`0.763` is best-of-five reveal, not the one-clip kept reveal `0.492`. Inside `0.721` is not the one-clip inside `0.442`. With the target withheld, the rewrite falls to `0.174`, below "open and hold". Both of the high arms name the target.

### Finding 3: The same diagnosis has opposite official consequences

<p align="center">
  <img width="920" alt="Paper figure. Most of the WRBench gain is the leave-return path. On MBench-T, 23 items keep the baseline clip." src="https://github.com/HKU-MMLab/MIST/releases/download/readme-assets/stats.png">
</p>

Official runs use Wan2.2-T2V-A14B, 161 frames over 10 seconds, and each suite's own scorer. They are not a scale comparison against TI2V-5B.

| Suite | Baseline | Keep-best | n | What the gain is |
| --- | ---: | ---: | ---: | --- |
| WRBench unique `T` | 0.452 | 0.570 | 40 | Completing a missing leave–return. The caption stays `task-context none`. |
| MBench-T unique `U` | 0.292 | 0.446 | 30 | Mostly refusal. The baseline clip is kept on 23 of 30 items. |

Forcing another leave–return on MBench-T lowers the total. The candidate set has to include the original clip, because a rewrite can preserve the camera motion and worsen the returned state. The single-clip keep-best on those 30 items is `0.443`; the published `0.446` averages a state oracle and a correctness oracle.

A frozen 8B selector that sees only the last frame and the setup sentence, and does not see the target or the scorer, stays with the baseline (`T` `0.466`, `U` `0.248`). Paired 95% intervals use 4,000 resamples over items, seed 0.

## M3-Agent

<p align="center">
  <img width="920" alt="Paper figure. Three MIST shots, then the M3-Agent loop on R0-03: diagnose a wrong binding, revise the move, and keep the better clip." src="https://github.com/HKU-MMLab/MIST/releases/download/readme-assets/method.png">
</p>

The loop has three steps.

1. **Task record.** Actor or object, binding, operation, temporal order, and the evidence the last frame must show. The fields come from the task card.
2. **Diagnosis.** A VLM reads the rendered last frame and picks a visible failure: no action, wrong binding, missing departure, missing return, return to the pre-event state, occlusion, or an unstable hold. It does not read the generator's hidden state.
3. **Rewrite.** Only the failed operation and the evidence clause change. The actor, the objects, and the order stay. The frozen generator samples another candidate.

On MIST, Head A preserves the first two shots and regenerates the last shot. The original candidate remains in the set, so a revision that makes the clip worse is not kept. On WRBench the camera clause stays `yaw_LR` and the caption stays `task-context none`. On MBench-T the five native caption segments stay, and the original clip is one of the candidates.

```text
kept = argmax over k <= K of score(candidate_k, target)
```

Ties keep the earlier candidate. `score` is the MIST judge on MIST and the official gate on the official suites.

The worked case in the paper is `R0-03`: an orange marble goes into a tin, a purple disk stays outside, and the last frame must show the marble. The raw take opens the tin onto the wrong object. The revision keeps the tin, the disk, and the order, and names the object that must go in.

## Quick Start

### 1. Set up the environment

Linux. One conda env covers the control loop, Wan helpers, MiniMax-H3 (SGLang), and the vLLM judge. A CUDA 12.8 GPU is required for generation / H3 / judge; the unit tests below only need the env.

```bash
git clone https://github.com/HKU-MMLab/MIST.git
cd MIST
conda env create -f environment.yml
conda activate mist
python -m unittest tests.test_core -v
```

[`environment.yml`](environment.yml) creates the env named **`mist`** (Python 3.12, PyTorch cu128, `diffusers` / `transformers`, `vllm`, `sglang`). Model weights are not in the env. Details: [docs/runtime.md](docs/runtime.md), [docs/reproduce.md](docs/reproduce.md). Project page: [hku-mmlab.github.io/MIST](https://hku-mmlab.github.io/MIST/).

| Variable | Purpose |
| --- | --- |
| `configs/protocol.json` | Shot count, `K`, reveal-frame positions, seed schedule, bootstrap settings. |
| Judgment JSONL | One row per candidate: `prompt_id`, `stage`, `pass`, `score`, optional `checks`. |

Every script accepts `--help`.

### 2. Choose a workflow

#### Check the control loop

Follow [docs/reproduce.md](docs/reproduce.md). From the repository root:

| Stage | Entry point |
| --- | --- |
| Unit tests | `python3 -m unittest tests.test_core -v` |
| Synthetic dry run | `python3 scripts/run_dry.py` |
| Best of five inside one arm | `python3 scripts/summarize_reveal.py --judgments examples/synthetic_judgments.jsonl` |
| Keep the baseline eligible | add `--baseline examples/synthetic_baseline.jsonl --with-baseline` |
| Write last-shot prompts | `python3 scripts/rewrite_prompts.py --spec examples/toy_cards.json --failure hand_no_open --occluder lid --output-dir outputs/prompts` |

The dry run and the synthetic JSONL use hand-written scores. R0-03 keeps a rewrite. R0-02 keeps the original clip because every rewrite scores lower. That is the selection rule, not a paper result.

#### Score your own judge file

Export reveal judgments in the JSONL shape above and run `scripts/summarize_reveal.py`. `--with-baseline` is the paper's rule that the original clip stays eligible. Omit it to report the best clip inside one arm.

The 43-case spec, the Wan launcher, and the 122B judge program were in the deleted tree. Their absence is recorded in [docs/reproduce.md](docs/reproduce.md). Do not fill those gaps by inventing prompts or scores and then comparing them with the tables above.

## Related

| Project | Links |
| --- | --- |
| **Wan2.2** | [Code](https://github.com/Wan-Video/Wan2.2) · [Paper](https://arxiv.org/abs/2503.20314). Frozen generator. |
| **Qwen** | [Code](https://github.com/QwenLM/Qwen3). Judge family. The paper uses Qwen3.5-122B-A10B. |
| **WRBench** | [Project](https://jinplu.github.io/WRBench/) · [Code](https://github.com/JinPLu/WRBench) · [Paper](https://arxiv.org/abs/2606.20545) |
| **MBench** | [Project](https://peanutup.github.io/MBench-project/) · [Code](https://github.com/study-overflow/MBench) · [Paper](https://arxiv.org/abs/2606.00793) |

<details>
<summary>Repository layout</summary>

`videomist/` is the control loop, `scripts/` the entry points, `configs/` the protocol, `examples/` the synthetic cards, `docs/` the guide, and `tests/` the checks.

</details>

## Citation

```bibtex
@misc{jin2026execution,
  title={Execution Before Memory: Diagnosing Memory Failures in Video World Models},
  author={Jin, Weiyang and Yu, Jiwen and Xu, Sihan and Niu, Yuwei and Liu, Xihui},
  year={2026}
}
```

## License

Private research code. No public license is attached.

## Acknowledgements

MIST generation uses Wan2.2-TI2V-5B. The official suites use Wan2.2-T2V-A14B and the scorers released with WRBench and MBench-T. The reveal judge is Qwen3.5-122B-A10B. The blind selector is Qwen3-VL-8B-Instruct.

## Contact

Questions about this repository: Weiyang Jin ([wayneyjin@gmail.com](mailto:wayneyjin@gmail.com)).
