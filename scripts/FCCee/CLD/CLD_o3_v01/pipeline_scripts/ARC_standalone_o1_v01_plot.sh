# make plots
echo "Sourcing key4hep..."
source /cvmfs/sw.hsf.org/key4hep/setup.sh
echo "Sourcing executed successfully"

echo "Starting analysis and plot script..."
python key4hep-reco-validation/scripts/FCCee/$GEOMETRY/$VERSION/analysis/ARC_val_plots.py \
       -f ARC_sim.root --no_show \
       -o $WORKAREA/$PLOTAREA/$GEOMETRY/$VERSION/plots
echo "Script executed successfully"

# upload them on website
echo "Starting website script..."
cd key4hep-reco-validation/web/python
python3 make_web.py --dest $WORKAREA/$PLOTAREA
echo "Script executed successfully"