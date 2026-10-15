# Full runtime (`mist-all`)

Project page: [hku-mmlab.github.io/MIST](https://hku-mmlab.github.io/MIST/).

The lightweight `mist` env in `environment.yml` is only for the control-loop unit tests (no GPU, no Wan / H3 / vLLM).

For Wan generation, MiniMax-H3 (SGLang), and the VLM judge on one machine under `/pfs/echo_folder/weiyang`, use the unified conda env:

```bash
bash envs/bootstrap_mist_all.sh
source /pfs/echo_folder/weiyang/Miniconda3/etc/profile.d/conda.sh
conda activate mist-all
bash envs/smoke_mist_all.sh
```

| Role | Stack inside `mist-all` |
|------|-------------------------|
| Judge | vLLM + transformers 5.x |
| H3 | SGLang (prepended from `.venv-minimax-h3` site-packages) |
| Wan helpers | diffusers / einops / opencv / … |

Weights stay outside the env (see [reproduce.md](reproduce.md)).
