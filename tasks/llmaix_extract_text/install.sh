#! /bin/bash
# set -e

git clone https://github.com/KatherLab/LLMAIx /workspace/LLMAIx
cd /workspace/LLMAIx && git checkout 66f834b

apt update
apt install tesseract-ocr-* ocrmypdf -y

pip install --break-system-packages -r requirements_api.txt