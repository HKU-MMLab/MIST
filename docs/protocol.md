# Protocol

MIST asks three questions of one clip, separately: whether the scene was set, whether the requested change was carried out, and whether the last frame shows the result. M3-Agent (Make the Missing Move) is the test-time loop that tries to carry out a change the first clip missed. It does not add or train a memory module.

## Three steps

1. A task record lists the actor or object, its binding, the operation, the temporal order, and the evidence that must appear in the last frame. These fields come from the task card.
2. A VLM reads the rendered last frame and assigns a visible failure. The appendix labels are `no_action`, `wrong_binding`, `missing_departure`, `missing_return`, `return_intact`, `occlusion`, and `unstable_hold`. Diagnosis reads pixels, not the generator's hidden state.
3. The rewrite may change the failed operation and the final-frame evidence clause. It keeps the actor, the objects, and the order. The frozen generator then samples another candidate.

On MIST, Head A keeps the first two 5-second shots and rewrites only the last shot. `K = 5`. The reveal prompt for the arms that name the target may include the target state. The no-gold arm bans `expected_present`, `expected_absent`, and the keys of `expected_count`.

The no-gold failure labels are the narrower set used by that run: `no_hand`, `hand_no_open`, `wrong_object`, `already_open`, with occluder `lid`, `cup`, `box`, `board`, or `cover`.

## Keep-best

Given candidates in generation order, keep the clip with the highest score. If two scores tie, keep the earlier index. The score is the same check that reports the result: the MIST judge on MIST, and the official gates on WRBench and MBench-T.

The original clip stays eligible. A rewrite that scores lower is not the one that is kept. That selection sees the target and the scorer. It is an oracle coverage estimate: it asks whether the candidate pack contains a better executable path. It is not a deployed critic, and the score is not trained back into the generator.

```text
kept = argmax_k score(x_k, target)
```

## Two populations that share a digit

MIST kept reveal `0.492` and an MBench state component that also prints `0.492` are different cells. Do not add them. Best-of-five reveal `0.763` is not the one-clip kept reveal `0.492`. Best-of-five inside `0.721` is not the one-clip inside `0.442`.

## Reported cells

These numbers are copied from the paper so the code has a legend. Running this repository does not produce them.

### MIST, one kept clip per case, Wan TI2V-5B, three 5-second shots, n = 43

| | Base | Rewrite |
| --- | ---: | ---: |
| Setup | 0.852 | 0.851 |
| Reveal | 0.147 | 0.492 |
| Inside match | 0.047 | 0.442 |
| Never opens | 41 | 20 |
| Empty or blocked | 1 | 0 |
| Opens, wrong inside | 0 | 10 |
| Correct | 1 | 13 |

Leak before the reveal shot is 0/43 on this setup. The baseline never-open count is 41/43, so persistence is not what that baseline measures.

### MIST, best of five tries, same judge

Each arm keeps, per case, the try whose last frame the judge scores highest.

| What we do | Answer in prompt | Reveal | Inside | Closed | Ok |
| --- | --- | ---: | ---: | ---: | ---: |
| Rewrite: look, then change the move | yes | 0.763 | 0.721 | 5 | 29 |
| Answer only: write the target, same move | yes | 0.684 | 0.581 | 3 | 24 |
| Same sentence: new seed only | yes | 0.635 | 0.512 | 4 | 21 |
| Open only: "open and hold" | no | 0.268 | 0.093 | 6 | 3 |
| Rewrite, no answer: look, change the move | no | 0.174 | 0.047 | 28 | 2 |

The `0.763` arm names the target. With the target withheld, the same rewrite is `0.174`. Both of the high arms depend on naming the target, and keep-best sees the judge.

### Official suites

Same diagnosis, opposite consequences. The generator, duration, and scorer differ from MIST, so the rows are not a scale comparison.

| Suite | Baseline | Keep-best | n | What moves |
| --- | ---: | ---: | ---: | --- |
| WRBench unique T | 0.452 | 0.570 | 40 | Completing a missing leave–return. Caption stays `task-context none`. Camera stays `yaw_LR`. |
| MBench-T unique U | 0.292 | 0.446 | 30 | Mostly refusal. The baseline clip is kept on 23 of 30 items. |

The published MBench-T `0.446` averages a state oracle and a correctness oracle. The single-clip keep-best on the same items is `0.443`.

A frozen Qwen3-VL-8B that sees only the last frame and the setup sentence, and does not see the target or the scorer, does not separate from the baseline (`T` `0.466`, `U` `0.248`). The intervals are paired differences from the baseline, 4,000 resamples, seed 0.

## Cells that stay out of this package

Packed 15-second MiniMax-H3 pilots are a different experiment from the TI2V-5B stitch. They are not an input to `summarize_reveal.py`, and their numbers are not mixed into the tables above.
