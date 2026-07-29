#!/bin/bash

# Enable strict error tracking for production/pipeline safety
set -euo pipefail

# --- Argument Parsing ---
while [[ $# -gt 0 ]]; do
    case $1 in
        --particle)
            PARTICLE="$2"; shift 2 ;;
        --energy)
            ENERGY="$2"; shift 2 ;;
        --inputFile)
            INPUT_FILE="$2"; shift 2 ;;
        --outputFile)
            OUTPUT_FILE="$2"; shift 2 ;;
        --nEvents)
            N_EVENTS="$2"; shift 2 ;;
        --seed)
            RANDOM_SEED="$2"; shift 2 ;;
        *)
            echo "Error: Unknown option $1"
            print_usage ;;
    esac
done

# --- Setup ---
if [ -z "${KEY4HEP_STACK:-}" ]; then
    source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh
fi

source "${FCCCONFIG}/FullSim/IDEA/${VERSION}/ctest_sim_digi_reco.sh" \
    --nEvents "${N_EVENTS}" \
    --particle "${PARTICLE}" \
    --energy "${ENERGY}" \
    --outputFile "${OUTPUT_FILE}" \
    --seed "${RANDOM_SEED}"
