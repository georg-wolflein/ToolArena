#! /bin/bash
set -e

git clone https://github.com/facebookresearch/esm /workspace/ESM
cd /workspace/ESM && git checkout 2b36991

pip install -e .
pip install torch
