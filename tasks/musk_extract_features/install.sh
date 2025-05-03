#! /bin/bash
set -e

git clone https://github.com/lilab-stanford/MUSK /workspace/MUSK
cd /workspace/MUSK && git checkout e1699c2

# The requirements.txt is broken, so we install the dependencies manually
# pip install -r /workspace/MUSK/requirements.txt

pip install "torch==2.7.0" "torchvision==0.22.0" "numpy==2.2.5" "huggingface-hub==0.30.2" "pandas==2.2.3" "timm==1.0.15" "fairscale==0.4.13" "einops==0.8.1" "safetensors==0.5.3"
pip install -e /workspace/MUSK
huggingface-cli download xiangjx/musk --local-dir ~/.cache