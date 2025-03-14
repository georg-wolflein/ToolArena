set -e

REPO_URL=https://github.com/mahmoodlab/CONCH
COMMIT=171f2be

git clone $REPO_URL /workspace/CONCH
cd /workspace/CONCH && git checkout $COMMIT

pip install -e /workspace/CONCH
pip install huggingface_hub[cli] torch Pillow
mkdir -p /workspace/CONCH/checkpoints/conch
huggingface-cli download --local-dir /workspace/CONCH/checkpoints/conch MahmoodLab/CONCH pytorch_model.bin