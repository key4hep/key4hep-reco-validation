printf "\n\nSETUP PHASE:\n"

[ -z "$KEY4HEP_STACK" ] && source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh


# simulation phase
printf "\n\nSIM-DIGI-RECO PHASE:\n"

echo "Starting script..."
source $FCCCONFIG/share/FCC-config/FullSim/ALLEGRO/ALLEGRO_o1_v03/ctest_sim_digi_reco.sh


# analyze simulation file
printf "\n\nANALYSIS PHASE:\n"

echo "Starting analysis script..."
python $WORKAREA/key4hep-reco-validation/scripts/FCCee/$GEOMETRY/$VERSION/ALLEGRO_make_TH1.py \
       -f ALLEGRO_sim_digi_reco.root -o results.root
echo "Script executed successfully"



