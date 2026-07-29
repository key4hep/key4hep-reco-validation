#!/bin/bash

# Enable strict error tracking for production/pipeline safety
set -euo pipefail

# --- Setup Environment ---
if [ -z "${KEY4HEP_STACK:-}" ]; then
    source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh
fi

# Define the path to the ctest script
CTEST_SCRIPT="${WORKAREA}/FCC-config/FCCee/FullSim/ALLEGRO/${VERSION}/ctest_sim_digi_reco.sh"

# --- Forward Arguments ---
source "$CTEST_SCRIPT" "$@"
