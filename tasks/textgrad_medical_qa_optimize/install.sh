#! /bin/bash
set -e

git clone https://github.com/zou-group/textgrad /workspace/textgrad
cd /workspace/textgrad && git checkout bf5b0c5

# Insert commands here to install dependencies and setup the environment...
pip install -e /workspace/textgrad
pip install openai pandas