#! /bin/bash
set -e

git clone https://github.com/brentp/cyvcf2 /workspace/cyvcf2
cd /workspace/cyvcf2 && git checkout main && git checkout 541ab16

# Insert commands here to install dependencies and setup the environment...
pip install cyvcf2
pip install numpy 
