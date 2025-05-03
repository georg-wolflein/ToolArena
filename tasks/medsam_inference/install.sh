#! /bin/bash
set -e

git clone https://github.com/bowang-lab/MedSAM /workspace/MedSAM
cd /workspace/MedSAM && git checkout b9db486

pip install /workspace/MedSAM
pip install "torch==2.7.0" "torchvision==0.22.0"
uvx gdown --fuzzy 'https://drive.google.com/uc?id=1UAmWL88roYR7wKlnApw5Bcuzf2iQgk6_' -O /workspace/MedSAM/medsam_vit_b.pth