#! /bin/bash

set -e

# Download large files required for the task

# MSD: http://medicaldecathlon.com

mkdir -p msd

# uvx gdown "https://drive.google.com/file/d/1wEB2I6S6tQBVEPxir8cA5kFB8gTQadYY/view" --fuzzy -O msd/Task02_Heart.tar
# uvx gdown "https://drive.google.com/file/d/1RzPB1_bqzQhlWvU-YGvZzhx2omcDh38C/view" --fuzzy -O msd/Task04_Hippocampus.tar
# uvx gdown "https://drive.google.com/file/d/1Ff7c21UksxyT4JfETjaarmuKEjdqe1-a/view" --fuzzy -O msd/Task05_Prostate.tar
# uvx gdown "https://drive.google.com/file/d/1jzeNU1EKnK81PyTsrx0ujfNl-t0Jo8uE/view" --fuzzy -O msd/Task09_Spleen.tar

wget -O msd/Task02_Heart.tar "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task02_Heart.tar"
wget -O msd/Task04_Hippocampus.tar "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task04_Hippocampus.tar"
wget -O msd/Task05_Prostate.tar "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task05_Prostate.tar"
wget -O msd/Task09_Spleen.tar "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task09_Spleen.tar"

tar -xvf msd/Task02_Heart.tar -C msd
tar -xvf msd/Task04_Hippocampus.tar -C msd
tar -xvf msd/Task05_Prostate.tar -C msd
tar -xvf msd/Task09_Spleen.tar -C msd

rm msd/Task*/.*
rm msd/Task*/*/.*