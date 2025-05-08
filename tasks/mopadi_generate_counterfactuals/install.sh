#! /bin/bash
set -e

git clone https://github.com/KatherLab/mopadi /workspace/mopadi
cd /workspace/mopadi && git checkout 4e76820

apt-get update && apt-get install -y libgl1 libglib2.0-0
pip install uv
pip install pyyaml
uv sync
source .venv/bin/activate
