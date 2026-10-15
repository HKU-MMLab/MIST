#!/usr/bin/env bash
# Build / refresh the single MIST runtime env: mist-all
# Base: vllm_qwen (judge). Layer: SGLang (H3) + Wan helper wheels.
set -euo pipefail

ROOT="${MIST_HOME:-/pfs/echo_folder/weiyang}"
CONDA_ROOT="${ROOT}/Miniconda3"
ENV_NAME="${MIST_ENV_NAME:-mist-all}"
ENV_DIR="${CONDA_ROOT}/envs/${ENV_NAME}"
H3_SITE="${ROOT}/.venv-minimax-h3/lib/python3.12/site-packages"
REPO="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck disable=SC1091
source "${CONDA_ROOT}/etc/profile.d/conda.sh"
export PATH="${CONDA_ROOT}/bin:${PATH}"

if [[ ! -x "${ENV_DIR}/bin/python" ]]; then
  echo "[mist-all] clone vllm_qwen → ${ENV_NAME}"
  conda create -y -n "${ENV_NAME}" --clone vllm_qwen
else
  echo "[mist-all] reuse existing ${ENV_DIR}"
fi

PY="${ENV_DIR}/bin/python"
PIP="${ENV_DIR}/bin/pip"

echo "[mist-all] layer Wan helpers (no torch downgrade)"
"${PIP}" install -q --upgrade \
  ftfy easydict opencv-python-headless \
  'imageio[ffmpeg]' omegaconf dashscope

# Prefer already-built SGLang from the old H3 venv when present.
mkdir -p "${ENV_DIR}/lib/python3.12/site-packages"
if [[ -d "${H3_SITE}/sglang" ]]; then
  echo "[mist-all] sitecustomize prepends H3 SGLang stack: ${H3_SITE}"
  cat > "${ENV_DIR}/lib/python3.12/site-packages/sitecustomize.py" <<'PY'
"""MIST mist-all: prefer MiniMax-H3 SGLang site-packages when present."""
from __future__ import annotations

import sys
from pathlib import Path

_H3 = Path("/pfs/echo_folder/weiyang/.venv-minimax-h3/lib/python3.12/site-packages")
if _H3.is_dir():
    p = str(_H3)
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
PY
else
  echo "[mist-all] H3 site-packages missing; pip install sglang[all] (slow)"
  "${PIP}" install -q 'sglang[all]'
fi

# Retarget broken .venv-minimax-h3 python → mist-all (wrapper, not symlink:
# a symlink makes CPython treat .venv-minimax-h3 as the active venv and drop vllm).
if [[ -d "${ROOT}/.venv-minimax-h3/bin" ]]; then
  echo "[mist-all] wrap .venv-minimax-h3/bin/python → mist-all"
  cat > "${ROOT}/.venv-minimax-h3/bin/python" <<EOF
#!/usr/bin/env bash
exec ${PY} "\$@"
EOF
  chmod +x "${ROOT}/.venv-minimax-h3/bin/python"
  ln -sfn python "${ROOT}/.venv-minimax-h3/bin/python3"
  ln -sfn python "${ROOT}/.venv-minimax-h3/bin/python3.12"
fi

"${PY}" - <<'PY'
import importlib
for m in ("torch", "transformers", "vllm", "diffusers", "einops"):
    mod = importlib.import_module(m)
    print(f"  {m}: {getattr(mod, '__version__', 'ok')}")
try:
    import sglang
    print(f"  sglang: {getattr(sglang, '__version__', 'ok')}")
except Exception as e:
    print(f"  sglang: FAIL {e}")
print("mist-all ready")
PY

"${PIP}" freeze > "${REPO}/envs/mist-all.freeze.txt"
echo "[mist-all] wrote ${REPO}/envs/mist-all.freeze.txt"
echo "[mist-all] smoke: bash ${REPO}/envs/smoke_mist_all.sh"
