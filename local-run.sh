#!/usr/bin/env bash
set -e

# Define detectors to validate
DETECTORS=(
"IDEA_o1_v03"
"ALLEGRO_o1_v03"
)

# Define particle mappings: full_name -> short_code
declare -A PARTICLES=(
["electron"]="e"
["muon"]="mu"
)

for DET in "${DETECTORS[@]}"; do
    DET_FAMILY="${DET%%_*}"
    CONFIG_PATH="config/${DET_FAMILY}/${DET}/config.yaml"
    PLOT_INPUTS=()

    echo "================================================================================"
    echo " Processing Detector: ${DET}"
    echo "================================================================================"

    for PARTICLE in "${!PARTICLES[@]}"; do
        SHORT_NAME="${PARTICLES[$PARTICLE]}"

        INPUT_FILE="data/${DET_FAMILY}/${DET}/${DET_FAMILY}_${SHORT_NAME}_particleGun_digi.root"
        OUTPUT_FILE="output/${DET_FAMILY}/${DET}/${DET_FAMILY}_${SHORT_NAME}_particleGun_hist.root"

        echo "==> Running histogram extraction for ${DET} (${PARTICLE})..."
        python3 "scripts/detectors/${DET_FAMILY}/${DET}/hist.py" \
            --input "${INPUT_FILE}" \
            --output "${OUTPUT_FILE}" \
            --particle-prefix "${PARTICLE}" \
            --config "${CONFIG_PATH}"

        PLOT_INPUTS+=("${PARTICLE}=${OUTPUT_FILE}")
    done

    echo "==> Rendering plots for ${DET}..."
    python3 scripts/detectors/k4_reco_val_utils/plotting.py \
        --inputs "${PLOT_INPUTS[@]}" \
        --style-config config/plotting.yaml \
        --detector-config "${CONFIG_PATH}" \
        --output-dir "plots/${DET_FAMILY}/${DET}"
done

echo "==> Local validation run completed successfully."
