#! /bin/bash
set -e

git clone https://github.com/lilab-stanford/MUSK /workspace/MUSK
cd /workspace/MUSK && git checkout e1699c2

# The requirements.txt is broken, so we install the dependencies manually
# pip install -r /workspace/MUSK/requirements.txt

pip install torch torchvision numpy huggingface-hub pandas timm fairscale einops safetensors
pip install -e /workspace/MUSK
huggingface-cli download xiangjx/musk --local-dir ~/.cache