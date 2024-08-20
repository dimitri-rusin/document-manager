#!/usr/bin/env bash

# Exit immediately on errors, treat unset variables as an error, and fail on error in any pipeline
set -euo pipefail

# Customizing the PS4 variable to show expanded variables
export PS4='+ \e[36m${BASH_SOURCE}:${LINENO}: ${FUNCNAME[0]:+${FUNCNAME[0]}(): }$ \e[m'

# Enable debugging if the last argument is --verbose
if [[ "${@: -1}" == "--verbose" ]]; then
  set -x
  set -- "${@:1:$(($#-1))}"  # Remove the last argument (--verbose)
fi

# Initialize and update git submodules
if [ -d .git ]; then
  git submodule init
  git submodule update
fi

# Define the directory for local Miniconda installation
MINICONDA_DIR=".python/Miniconda3"

# Check if .python/venv/ exists
if [ -d ".python/venv/" ]; then
  echo ".python/venv/ exists. CLEAN first. Exiting."
  exit 1
fi

# Check if $MINICONDA_DIR exists
if [ -d "$MINICONDA_DIR" ]; then
  echo "$MINICONDA_DIR exists. CLEAN first. Exiting."
  exit 1
fi

# Clean up any previous Conda environment and build targets
rm -rf .python/venv/
rm -rf $MINICONDA_DIR

# Install Miniconda locally
curl -o /tmp/Miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-py39_24.5.0-0-Linux-x86_64.sh
bash /tmp/Miniconda3.sh -b -p $MINICONDA_DIR
rm /tmp/Miniconda3.sh

# Initialize conda in the current shell (without modifying any shell configuration files)
eval "$(.python/Miniconda3/bin/conda shell.bash hook)"

# Create and activate a new Conda environment based on .python/Miniconda3.yaml configuration
conda env create --prefix .python/venv/ --file .python/Miniconda3.yaml
conda activate .python/venv/

# Install Python dependencies from the requirements file
pip install --requirement .python/pip.txt

# conda env config vars list
# conda env update --file .python/Miniconda3.yaml --prune
