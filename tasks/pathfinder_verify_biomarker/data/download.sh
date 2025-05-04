#! /bin/bash

set -e

# Download large files required for the task

rm -rf TCGA_CRC/ CPTAC_CRC/

# TGCA-CRC for PathFinder
wget "https://cloud.tsinghua.edu.cn/f/a1c87bb480eb4eae9bd2/?dl=1" -O pathfinder.zip
unzip pathfinder.zip
rm pathfinder.zip

# CPTAC for PathFinder
uvx gdown --fuzzy -O pathfinder_cptac.tar.gz "https://drive.google.com/file/d/1shCsgWP4ctbcMoZ3CVelfh49AXa0RcJT/view"
tar -xvf pathfinder_cptac.tar.gz
mv prob_map CPTAC_CRC
rm pathfinder_cptac.tar.gz

