#! /bin/bash

set -e

# Download large files required for the task

# Example:
# wget -O data/large_file_1.zip https://example.com/large_file_1.zip
dataset="crc-wsi"
manifest="gdc_manifest_crc.txt"
mkdir -p ${dataset} ${dataset}.download
uvx --from git+https://github.com/NCI-GDC/gdc-client gdc-client download --manifest $manifest --dir ${dataset}.download
mv ${dataset}.download/*/*.svs ${dataset}
rm -rf ${dataset}.download