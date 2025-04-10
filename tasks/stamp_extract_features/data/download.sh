#!/bin/bash
set -e

for manifest in gdc_manifest.brca.txt gdc_manifest.crc.txt; do
    uvx --from git+https://github.com/NCI-GDC/gdc-client gdc-client download --manifest $manifest
    mv */*.svs .
    rm -rf */logs
done
