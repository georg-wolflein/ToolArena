#!/bin/bash
set -e

for dataset in brca crc; do
    manifest="gdc_manifest.${dataset}.txt"
    mkdir -p ${dataset} ${dataset}.download
    uvx --from git+https://github.com/NCI-GDC/gdc-client gdc-client download --manifest $manifest --dir ${dataset}.download
    mv ${dataset}.download/*/*.svs ${dataset}
    rm -rf ${dataset}.download
done
