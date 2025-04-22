#! /bin/bash

set -e

uvx gdown "https://drive.google.com/file/d/1aaru7A8cDfyZ_d0bgErpYGh5uksHljoN/view" --fuzzy -O flowmap_datasets.zip
unzip flowmap_datasets.zip -d .
rm flowmap_datasets.zip