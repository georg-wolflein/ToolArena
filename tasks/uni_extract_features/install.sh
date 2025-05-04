#! /bin/bash
set -e

git clone https://github.com/mahmoodlab/UNI /workspace/UNI
cd /workspace/UNI && git checkout 42715ef

# Insert commands here to install dependencies and setup the environment...
pip install -e /workspace/UNI
huggingface-cli download MahmoodLab/UNI pytorch_model.bin --local-dir /workspace/UNI/assets/ckpts/uni