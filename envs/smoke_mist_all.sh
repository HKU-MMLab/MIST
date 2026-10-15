#!/usr/bin/env bash
set -euo pipefail
PY="${MIST_PY:-/pfs/echo_folder/weiyang/Miniconda3/envs/mist-all/bin/python}"
echo "using ${PY}"
"${PY}" - <<'PY'
import importlib

def check(name, attr="__version__"):
    mod = importlib.import_module(name)
    ver = getattr(mod, attr, "ok")
    print(f"OK  {name:14s} {ver}")
    return mod

check("torch")
check("transformers")
check("vllm")
check("diffusers")
check("einops")
check("cv2", "__version__")
try:
    check("sglang")
except Exception as e:
    print(f"WARN sglang: {e}")
print("smoke done")
PY
