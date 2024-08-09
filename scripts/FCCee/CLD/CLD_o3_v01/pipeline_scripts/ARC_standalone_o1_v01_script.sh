# setup phase
echo "SETUP PHASE:"

echo "Sourcing key4hep..."
source /cvmfs/sw.hsf.org/key4hep/setup.sh
echo "Sourcing executed successfully"

echo "Downloading necessary Github repos..."
git clone https://github.com/key4hep/CLDConfig.git
git clone https://github.com/key4hep/k4geo.git
echo "Download terminated - setup stage successful"


# simulation phase
echo "SIMULATION PHASE"

cd CLDConfig/CLDConfig
echo "Starting simulation..."
ddsim --steeringFile cld_arc_steer.py \
      --enableGun --gun.distribution "cos(theta)" \
      --gun.energy "20*GeV" --gun.particle proton \
      --numberOfEvents $NUMBER_OF_EVENTS \
      --outputFile $WORKAREA/$GEOMETRY/$VERSION/ARC_sim.root \
      --random.enableEventSeed --random.seed 42 \
      --part.userParticleHandler=''
echo "Simulation ended successfully"
cd $WORKAREA/$GEOMETRY/$VERSION


# analyze simulation file
echo "ANALYSIS PHASE"

echo "Starting analysis script..."
python key4hep-reco-validation/scripts/FCCee/$GEOMETRY/$VERSION/analysis/ARC_make_file.py \
       -f ARC_sim.root -o ARC_res.root
echo "Script executed successfully"


# check if reference is needed
if [ "$MAKE_REFERENCE_SAMPLE" == "yes" ]; then
    mkdir -p $WORKAREA/$GEOMETRY/$VERSION/$REFERENCE_SAMPLE
    mv ARC_res.root $WORKAREA/$GEOMETRY/$VERSION/$REFERENCE_SAMPLE/ref_$VERSION.root
else
    # make plots
    echo "PLOT PHASE"

    echo "Starting plotting script..."
    python key4hep-reco-validation/scripts/FCCee/$GEOMETRY/$VERSION/analysis/ARC_val_plots.py \
       -f ARC_res.root -r $REFERENCE_SAMPLE/ref_$VERSION.root \
       -o $WORKAREA/$PLOTAREA/$GEOMETRY/$VERSION/plots
    echo "Script executed successfully"

    # upload them on website
    echo "Starting website script..."
    cd key4hep-reco-validation/web/python
    python3 make_web.py --dest $WORKAREA/$PLOTAREA
    echo "Script executed successfully"
fi



