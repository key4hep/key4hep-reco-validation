printf "\n\nSETUP PHASE:\n"

echo "Downloading necessary Github repos..."
git clone https://github.com/HEP-FCC/FCC-config.git
echo "Download terminated - setup stage successful"


# simulation phase
printf "\n\nSIM-DIGI-RECO PHASE:\n"

cd FCC-config/FCCee/FullSim/ALLEGRO/ALLEGRO_o1_v03
echo "Starting script..."
./ctest_sim_digi_reco.sh
mv ALLEGRO_sim_digi_reco.root $WORKAREA/$GEOMETRY/$VERSION/
cd $WORKAREA/$GEOMETRY/$VERSION

# analyze simulation file
printf "\n\nANALYSIS PHASE:\n"

echo "Starting analysis script..."
python key4hep-reco-validation/scripts/FCCee/$GEOMETRY/$VERSION/ALLEGRO_make_file.py \
       -f ALLEGRO_sim_digi_reco.root -o ALLEGRO_res.root
echo "Script executed successfully"


# check if reference is needed
if [ "$MAKE_REFERENCE_SAMPLE" == "yes" ]; then
    mkdir -p $WORKAREA/$REFERENCE_SAMPLE/$GEOMETRY/$VERSION
    mv ALLEGRO_res.root $WORKAREA/$REFERENCE_SAMPLE/$GEOMETRY/$VERSION/ref_$VERSION.root
else
    # make plots
    printf "\n\nPLOT PHASE:\n"

    echo "Starting plotting script..."
    python key4hep-reco-validation/scripts/FCCee/$GEOMETRY/$VERSION/ALLEGRO_val_plots.py \
       -f ALLEGRO_res.root -r $WORKAREA/$REFERENCE_SAMPLE/$GEOMETRY/$VERSION/ref_$VERSION.root \
       -o $WORKAREA/$PLOTAREA/$GEOMETRY/$VERSION/plots --test identical
    echo "Script executed successfully"

    # upload them on website
    echo "Starting website script..."
    cd key4hep-reco-validation/web/python
    python3 make_web.py --dest $WORKAREA/$PLOTAREA
    echo "Script executed successfully"
fi



