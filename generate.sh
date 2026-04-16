#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Target paths explicitly defined for clarity
CONFIG_FILE="generator/config/eval_config.csv"
DATASET_FILE="dataset/dataset.csv"

echo "Generating configuration matrix to ${CONFIG_FILE}..."
python3 generator/gen_config.py "${CONFIG_FILE}"

echo -e "\nGenerating dataset to ${DATASET_FILE}..."
python3 generator/gen_dataset.py "${CONFIG_FILE}" "${DATASET_FILE}"

echo -e "\nGeneration pipeline complete!"
