#! /bin/bash
set -e

git clone https://github.com/AnswerDotAI/ModernBERT /workspace/ModernBERT
cd /workspace/ModernBERT && git checkout 8c57a0f

pip install -r /workspace/ModernBERT/requirements-cpu.txt

# # We need specific versions of transformers and torch
# #   transformers issue: https://huggingface.co/answerdotai/ModernBERT-base/discussions/3#6764f047eef1e726f2100ca3
# #   torch issue:        https://github.com/pytorch/pytorch/issues/120233#issuecomment-2639054555
pip install "transformers==4.48" "torch==2.6.0" torchvision