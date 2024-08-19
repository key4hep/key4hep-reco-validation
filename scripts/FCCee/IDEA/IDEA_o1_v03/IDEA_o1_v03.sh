printf "\n\nSETUP PHASE:\n"

source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh


# simulation phase
printf "\n\nSIM-DIGI-RECO PHASE:\n"

echo "Starting script..."
sed '4d;s|k4run \$SCRIPT_DIR/run_digi_reco\.py|k4run \$FCCCONFIG/share/FCC-config/FullSim/IDEA/IDEA_o1_v03/run_digi_reco.py|' $FCCCONFIG/share/FCC-config/FullSim/IDEA/IDEA_o1_v03/ctest_sim_digi_reco.sh > new_script.sh
source new_script.sh


# analyze simulation file
printf "\n\nANALYSIS PHASE:\n"

echo "Starting analysis script..."
python key4hep-reco-validation/scripts/FCCee/$GEOMETRY/$VERSION/IDEA_make_TH1.py \
       -f IDEA_sim_digi_reco.root -o IDEA_res.root
echo "Script executed successfully"


# check if reference is needed
if [ "$MAKE_REFERENCE_SAMPLE" == "yes" ]; then
    mkdir -p $WORKAREA/$REFERENCE_SAMPLE/$GEOMETRY/$VERSION
    mv IDEA_res.root $WORKAREA/$REFERENCE_SAMPLE/$GEOMETRY/$VERSION/ref_$VERSION.root
else
    # make plots
    printf "\n\nPLOT PHASE:\n"

    echo "Starting plotting script..."
    python key4hep-reco-validation/scripts/FCCee/utils/plot_histograms.py \
       -f IDEA_res.root -r $WORKAREA/$REFERENCE_SAMPLE/$GEOMETRY/$VERSION/ref_$VERSION.root \
       -o $WORKAREA/$PLOTAREA/$GEOMETRY/$VERSION --test identical
    echo "Script executed successfully"
fi

