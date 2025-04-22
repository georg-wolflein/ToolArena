#! /bin/bash
set -e

git clone https://github.com/wallet-maker/cytopus /workspace/Cytopus
cd /workspace/Cytopus && git checkout 638dd91

pip install -e .
pip install pyvis pandas numpy matplotlib setuptools
