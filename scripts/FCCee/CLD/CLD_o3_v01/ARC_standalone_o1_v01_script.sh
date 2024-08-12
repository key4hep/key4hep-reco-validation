# setup phase
printf "\n\nSETUP PHASE:\n"

echo "Sourcing key4hep..."
source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh
echo "Sourcing executed successfully"

echo "Downloading necessary Github repos..."
git clone https://github.com/key4hep/CLDConfig.git
git clone https://github.com/key4hep/k4geo.git
echo "Download terminated - setup stage successful"


# simulation phase
printf "\n\nSIMULATION PHASE:\n"

cd CLDConfig/CLDConfig
echo "Starting simulation..."
ddsim --steeringFile cld_arc_steer.py \
      --compactFile ../../k4geo/test/compact/ARC_standalone_o1_v01.xml \
      --enableGun --gun.distribution "cos(theta)" \
      --gun.energy "20*GeV" --gun.particle proton \
      --numberOfEvents $NUMBER_OF_EVENTS \
      --outputFile $WORKAREA/$GEOMETRY/$VERSION/ARC_sim.root \
      --random.enableEventSeed --random.seed 42 \
      --part.userParticleHandler='' > $WORKAREA/$GEOMETRY/$VERSION/ddsim_log.txt
echo "Simulation ended successfully"
cd $WORKAREA/$GEOMETRY/$VERSION


# analyze simulation file
printf "\n\nANALYSIS PHASE:\n"

echo "Starting analysis script..."
python key4hep-reco-validation/scripts/FCCee/$GEOMETRY/$VERSION/ARC_make_file.py \
       -f ARC_sim.root -o ARC_res.root
echo "Script executed successfully"


# check if reference is needed
if [ "$MAKE_REFERENCE_SAMPLE" == "yes" ]; then
    mkdir -p $WORKAREA/$REFERENCE_SAMPLE/$GEOMETRY/$VERSION
    mv ARC_res.root $WORKAREA/$REFERENCE_SAMPLE/$GEOMETRY/$VERSION/ref_$VERSION.root
else
    # make plots
    printf "\n\nPLOT PHASE:\n"

    echo "Starting plotting script..."
    python key4hep-reco-validation/scripts/FCCee/$GEOMETRY/$VERSION/ARC_val_plots.py \
       -f ARC_res.root -r $WORKAREA/$REFERENCE_SAMPLE/$GEOMETRY/$VERSION/ref_$VERSION.root \
       -o $WORKAREA/$PLOTAREA/$GEOMETRY/$VERSION/plots --test identical
    echo "Script executed successfully"

    # upload them on website
    echo "Starting website script..."
    cd key4hep-reco-validation/web/python
    python3 make_web.py --dest $WORKAREA/$PLOTAREA
    echo "Script executed successfully"
fi



