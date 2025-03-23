set -e

git clone https://github.com/mahmoodlab/CONCH /workspace/CONCH
cd /workspace/CONCH && git checkout 171f2be

pip install -e /workspace/CONCH
pip install huggingface_hub[cli] torch Pillow
mkdir -p /workspace/CONCH/checkpoints/conch
huggingface-cli download --local-dir /workspace/CONCH/checkpoints/conch MahmoodLab/CONCH pytorch_model.bin