#! /bin/bash
set -e

git clone https://github.com/KatherLab/STAMP /workspace/STAMP
cd /workspace/STAMP && git checkout 0042e6f

apt-get update && apt-get install -y libgl1-mesa-glx
pip install -e ".[ctranspath]"
