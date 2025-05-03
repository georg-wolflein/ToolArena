#! /bin/bash
set -e

git clone https://github.com/pixas/MedSSS /workspace/MedSSS
cd /workspace/MedSSS && git checkout ebbfd02

pip install /workspace/MedSSS
huggingface-cli download meta-llama/Llama-3.1-8B-Instruct
huggingface-cli download pixas/MedSSS_Policy