#!/bin/bash

set -e

# Create the wsis/ directory if it doesn't exist
mkdir -p wsis

# Download large files required for the task
manifest="tcga_read_gdc_manifest.2025-04-26.151110_small_batch.txt"
mkdir -p wsis.download
uvx --from git+https://github.com/NCI-GDC/gdc-client gdc-client download --manifest $manifest --dir wsis.download
mv wsis.download/*/*.svs wsis
rm -rf wsis.download