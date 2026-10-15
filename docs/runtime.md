# Runtime (`environment.yml` → env `mist`)

Project page: [hku-mmlab.github.io/MIST](https://hku-mmlab.github.io/MIST/).

## One-shot setup

```bash
git clone https://github.com/HKU-MMLab/MIST.git
cd MIST
conda env create -f environment.yml
conda activate mist
python -m unittest tests.test_core -v
```

This single env is intended to cover:

| Role | Packages |
|------|----------|
| Control loop | stdlib + this repo (`videomist`) |
| Wan helpers | `torch`, `diffusers`, `transformers`, `einops`, … |
| Judge | `vllm` |
| MiniMax-H3 | `sglang` |

Weights are **not** in the env. Point checkpoints via env vars / your launch scripts (see [reproduce.md](reproduce.md)).

## Lab machines under `/pfs/echo_folder/weiyang`

If you already built the local clone named `mist-all` from the paper tree, it is equivalent in role to this `mist` env. Prefer the public `environment.yml` on new machines:

```bash
conda activate mist
```

Optional smoke (imports only):

```bash
python - <<'PY'
import torch, transformers, diffusers, vllm, sglang
print(torch.__version__, transformers.__version__, vllm.__version__, sglang.__version__)
PY
```
