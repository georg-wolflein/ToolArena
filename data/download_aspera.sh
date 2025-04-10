#!/bin/bash
set -e

# Download some slides from CPTAC-BRCA
# https://github.com/kirbyju/TCIA_Notebooks/blob/main/TCIA_Aspera_CLI_Downloads.ipynb
ASPERA_URL=https://faspex.cancerimagingarchive.net/aspera/faspex/public/package?context=eyJyZXNvdXJjZSI6InBhY2thZ2VzIiwidHlwZSI6ImV4dGVybmFsX2Rvd25sb2FkX3BhY2thZ2UiLCJpZCI6IjU4MyIsInBhc3Njb2RlIjoiNTc5NmFiNGY2MzA1MzBlYTE2YTA3YjQxYzM5NmYzMDgzZDcwODkxOSIsInBhY2thZ2VfaWQiOiI1ODMiLCJlbWFpbCI6ImhlbHBAY2FuY2VyaW1hZ2luZ2FyY2hpdmUubmV0In0=
SLIDES=BRCA/01BR021-76c4e1e5-d66b-43dd-bc87-e35146.svs
output_dir=$DATA_DIR/CPTAC-BRCA
for slide in $SLIDES; do
    test -f $output_dir/$slide && continue
    echo "Downloading $slide"
    ascli faspex5 packages receive --url="$ASPERA_URL" --to-folder=$output_dir $slide
done
