# enable exit on error to check correct script execution from within pipeline
set -e

# setup phase
echo "SETUP PHASE:"

[ -z "${KEY4HEP_STACK}" ] && source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh


# simulation phase
echo "SIM-DIGI-RECO PHASE:"

echo "Starting script..."
bash "${FCCCONFIG}/share/FCC-config/FullSim/ALLEGRO/${VERSION}/ctest_sim_digi_reco.sh"


# analyze simulation file
echo "ANALYSIS PHASE:"

echo "Starting analysis script..."
python "${WORKAREA}/key4hep-reco-validation/scripts/FCCee/ALLEGRO/ALLEGRO_make_hists.py" \
       -f ALLEGRO_sim_digi_reco.root -o results.root
echo "Script executed successfully"
