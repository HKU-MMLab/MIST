# MIST runtime: one env (`mist-all`)

Canonical path: `/pfs/echo_folder/weiyang` (old `/pfs/weiyang` symlink may disappear).

## Env

| Name | Path | Role |
|------|------|------|
| **mist-all** | `Miniconda3/envs/mist-all` | Wan generate + MiniMax-H3 (SGLang) + VLM judge (vLLM) |

Activate:

```bash
source /pfs/echo_folder/weiyang/Miniconda3/etc/profile.d/conda.sh
conda activate mist-all
```

Or call the binary directly:

```bash
PY=/pfs/echo_folder/weiyang/Miniconda3/envs/mist-all/bin/python
```

## Why this base

Stacks differ (Wan historically used torch 2.8 / transformers 4.53; H3 SGLang wants torch ≥2.11; vLLM judge is on torch 2.10 + transformers 5.x).  
`mist-all` is cloned from **`vllm_qwen`**, then H3 (SGLang) and Wan helper packages are layered on top so there is a single activate path.

Weights (not in the env):

- Wan2.2-TI2V-5B → `/pfs/echo_folder/weiyang/ckpt/Wan2.2-TI2V-5B`
- MiniMax-H3 → `/pfs/echo_folder/weiyang/MiniMax-H3`
- Judge → `/pfs/models/Qwen3.5-122B-A10B` (and 8B blind-select if used)

## Recreate / refresh

```bash
bash /pfs/echo_folder/weiyang/ICLR27-Video-MIST/envs/bootstrap_mist_all.sh
```

Export pins after a working smoke test:

```bash
/pfs/echo_folder/weiyang/Miniconda3/envs/mist-all/bin/pip freeze \
  > /pfs/echo_folder/weiyang/ICLR27-Video-MIST/envs/mist-all.freeze.txt
```

## Smoke

```bash
bash /pfs/echo_folder/weiyang/ICLR27-Video-MIST/envs/smoke_mist_all.sh
```
