#! /bin/bash
set -e

git clone https://github.com/KatherLab/EAGLE.git /workspace/EAGLE
cd /workspace/EAGLE
git checkout simple_feature_extraction
nvcc --version
pip install uv
pip install h5py
uv venv --python=3.11
source .venv/bin/activate
uv pip install hatchling editables
uv pip install -r requirements.txt
ulimit -n 8192
uv pip install gdown
mkdir -p /workspace/EAGLE/model_weights
gdown https://drive.google.com/uc?id=10bJq_ayX97_1w95omN8_mESrYAGIBAPb -O /workspace/EAGLE/model_weights/CHIEF_pretraining.pth