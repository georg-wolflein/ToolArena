#! /bin/bash

set -e

# Download large files required for the task

# Example:
# wget -O data/large_file_1.zip https://example.com/large_file_1.zip
for dataset in brca crc; do
    manifest="gdc_manifest_${dataset}.txt"
    mkdir -p ${dataset}-wsi ${dataset}-wsi.download
    uvx --from git+https://github.com/NCI-GDC/gdc-client gdc-client download --manifest $manifest --dir ${dataset}-wsi.download
    mv ${dataset}-wsi.download/*/*.svs ${dataset}-wsi
    rm -rf ${dataset}-wsi.download
done