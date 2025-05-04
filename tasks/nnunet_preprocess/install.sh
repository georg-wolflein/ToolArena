#! /bin/bash
set -e

git clone https://github.com/MIC-DKFZ/nnUNet /workspace/nnUNet
cd /workspace/nnUNet && git checkout 58a3b12

pip install torch torchvision
pip install -e /workspace/nnUNet
