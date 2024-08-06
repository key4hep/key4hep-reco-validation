# simulation phase
echo "Sourcing key4hep..."
source /cvmfs/sw.hsf.org/key4hep/setup.sh
echo "Sourcing executed successfully"

cd CLDConfig/CLDConfig
echo "Starting simulation..."
ddsim --steeringFile cld_arc_steer.py \
      --enableGun --gun.distribution "cos(theta)" \
      --gun.energy "20*GeV" --gun.particle proton \
      --numberOfEvents $NUMBER_OF_EVENTS \
      --outputFile $WORKAREA/$GEOMETRY/$VERSION/ARC_sim.root \
      --random.enableEventSeed --random.seed 42
echo "Simulation ended successfully"
cd $WORKAREA/$GEOMETRY/$VERSION