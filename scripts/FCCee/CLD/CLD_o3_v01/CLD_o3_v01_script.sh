# enable exit on error to check correct script execution from within pipeline
set -e

# setup phase
echo "SETUP PHASE:"

[ -z "$KEY4HEP_STACK" ] && source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh


# simulation phase
echo "SIMULATION PHASE:"

cd "${CLDCONFIG}/share/CLDConfig"
echo "Starting simulation..."
ddsim --steeringFile cld_arc_steer.py \
      --compactFile "${K4GEO}/FCCee/CLD/compact/CLD_o3_v01/CLD_o3_v01.xml" \
      --enableGun --gun.distribution "cos(theta)" \
      --gun.energy "20*GeV" --gun.particle proton \
      --numberOfEvents "${NUMBER_OF_EVENTS}" \
      --outputFile "${WORKAREA}/${GEOMETRY}/${VERSION}/ARC_sim.root" \
      --random.enableEventSeed --random.seed 42 \
      --part.userParticleHandler="" > "${WORKAREA}/${GEOMETRY}/${VERSION}/ddsim_log.txt"
echo "Simulation execution finished"
cd "${WORKAREA}/${GEOMETRY}/${VERSION}"


# analyze simulation file
echo "ANALYSIS PHASE:"

echo "Starting analysis script..."
python "${WORKAREA}/key4hep-reco-validation/scripts/FCCee/CLD/CLD_o3_v01/ARC_make_hists.py" \
       -f ARC_sim.root -o results.root \
       -c "${K4GEO}/FCCee/CLD/compact/CLD_o3_v01/CLD_o3_v01.xml"
echo "Analysis execution finished"
