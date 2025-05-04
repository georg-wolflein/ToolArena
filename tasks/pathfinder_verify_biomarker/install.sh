#! /bin/bash
set -e

git clone https://github.com/LiangJunhao-THU/PathFinderCRC /workspace/PathFinder
cd /workspace/PathFinder && git checkout 093d77b

pip install "pandas==2.2.3" "numpy==2.2.5" "lifelines==0.30.0" "matplotlib==3.10.1"