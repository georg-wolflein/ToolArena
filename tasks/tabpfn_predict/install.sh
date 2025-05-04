#! /bin/bash
set -e

git clone https://github.com/PriorLabs/TabPFN /workspace/TabPFN
cd /workspace/TabPFN && git checkout e8744e4

pip install -e /workspace/TabPFN
