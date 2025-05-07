#!/usr/bin/env bash
set -e

# System libraries TIAToolbox needs
apt-get update -qq && \
apt-get purge -y python3-blinker && \
apt-get install -y --no-install-recommends \
        libopenjp2-7-dev \
        openslide-tools \
        libgl1 \
        && \
apt-get clean && rm -rf /var/lib/apt/lists/*

# Install TIAToolbox
git clone https://github.com/TissueImageAnalytics/tiatoolbox /workspace/tiatoolbox
cd /workspace/tiatoolbox && git checkout 7ba7394

pip install --no-cache-dir .
