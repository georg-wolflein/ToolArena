#!/bin/bash

set -e

# Download large files required for the task
tail -n +2 tcga_read_gdc_manifest.2025-04-26.151110_small_batch.txt | \
while IFS=$'\t' read -r uuid filename md5 size state; do
    echo "Downloading ${filename}..."
    wget -c "https://api.gdc.cancer.gov/data/${uuid}" -O "wsis/${filename}"
done
