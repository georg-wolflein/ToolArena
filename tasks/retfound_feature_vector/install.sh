#! /bin/bash
set -e

git clone https://github.com/rmaphoh/RETFound_MAE /workspace/RETFound
cd /workspace/RETFound && git checkout 897d71c

pip install "torch==2.3.1" "torchvision==0.18.1" "torchaudio==2.3.1" "huggingface-hub==0.23.5"
pip install -r /workspace/RETFound/requirements.txt

mkdir -p /workspace/pretrained_models

huggingface-cli download YukunZhou/RETFound_mae_natureCFP RETFound_mae_natureCFP.pth --local-dir /workspace/pretrained_models
