#! /bin/bash
set -e

git clone https://github.com/wasserth/TotalSegmentator /workspace/TotalSegmentator
cd /workspace/TotalSegmentator && git checkout 5b1a4f0
pip install -e /workspace/TotalSegmentator