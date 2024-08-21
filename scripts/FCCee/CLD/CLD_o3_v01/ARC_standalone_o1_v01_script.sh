# setup phase
printf "\n\nSETUP PHASE:\n"

[ -z "$KEY4HEP_STACK" ] && source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh

echo "Downloading necessary Github repos..."
git clone https://github.com/key4hep/k4geo.git
echo "Download terminated - setup stage successful"


# simulation phase
printf "\n\nSIMULATION PHASE:\n"

cd $CLDCONFIG/share/CLDConfig
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
python $WORKAREA/key4hep-reco-validation/scripts/FCCee/$GEOMETRY/$VERSION/ARC_make_TH1.py \
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
    python $WORKAREA/key4hep-reco-validation/scripts/FCCee/utils/plot_histograms.py \
       -f ARC_res.root -r $WORKAREA/$REFERENCE_SAMPLE/$GEOMETRY/$VERSION/ref_$VERSION.root \
       -o $WORKAREA/$PLOTAREA/$GEOMETRY/$VERSION --test identical
    echo "Script executed successfully"
fi



