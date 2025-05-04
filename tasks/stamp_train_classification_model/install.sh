#! /bin/bash
set -e

git clone https://github.com/KatherLab/STAMP /workspace/STAMP
cd /workspace/STAMP && git checkout 97522aa

apt update && apt install -y libgl1 libglx-mesa0 libglib2.0-0
pip install -e "/workspace/STAMP[ctranspath]"
