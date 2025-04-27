#! /bin/bash
set -e

git clone https://github.com/KatherLab/COBRA.git /workspace/COBRA
cd /workspace/COBRA
nvcc --version
pip install uv
pip install pyyaml h5py
uv venv --python=3.11
source .venv/bin/activate
uv pip install hatchling editables pyyaml
uv pip install torch==2.4.1 setuptools packaging wheel numpy==2.0.0
uv sync --no-build-isolation
ulimit -n 8192