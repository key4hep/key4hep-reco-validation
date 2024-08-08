import ROOT
from podio import root_io
import dd4hep as dd4hepModule
from ROOT import dd4hep
import argparse
import numpy as np
import os
from dd4hep import Detector
import DDRec

def find_directory_upwards(start_dir, target_dir_name):
    """
    Recursively searches upwards from the start directory for a directory with the specified name.

    :param start_dir: The starting directory path.
    :param target_dir_name: The name of the directory to search for.
    :return: The path to the found directory or None if not found.
    """
    current_dir = os.path.abspath(start_dir)
    
    while True:
        # Check if the target directory exists in the current directory
        if target_dir_name in os.listdir(current_dir):
            possible_match = os.path.join(current_dir, target_dir_name)
            if os.path.isdir(possible_match):
                return possible_match
        
        # Move up one level in the directory tree
        parent_dir = os.path.dirname(current_dir)
        
        # If we have reached the root directory and haven't found the directory, return None
        if current_dir == parent_dir:
            return None
        
        current_dir = parent_dir


def make_photon_file(args):
  
  # create output ROOT file
  outputFile = ROOT.TFile(args.outputFile, "RECREATE")

  # set file reader
  podio_reader = root_io.Reader(args.inputFile)

  # get detector description for cell id decoding
  k4geo = find_directory_upwards('./', 'k4geo')
  theDetector = Detector.getInstance()
  theDetector.fromXML(k4geo+"/test/compact/ARC_standalone_o1_v01.xml")
  idposConv = DDRec.CellIDPositionConverter(theDetector)
                  

  ########## Count Photon Hits #########################

  hist_nPh = ROOT.TH1F("h_nPh", "Total number of photon counts per event",
                       50, 0, 250)
  hist_theta = ROOT.TH1F("h_theta", "Number of photons counts per event vs. theta",
                         90, 0, np.pi)
  hist_theta_1stHit = ROOT.TH1F("h_theta_1stHit", "Number of photons counts per event vs. theta of incoming particle",
                                90, 0, np.pi)
  
  # loop over dataset
  for event in podio_reader.get("events"):

    n_ph = 0

    p = (event.get("MCParticles"))[0]
    mom = ROOT.TVector3(p.getMomentum().x, p.getMomentum().y, p.getMomentum().z)
    theta_1stHit = mom.Theta()

    for arc_hit in event.get("ArcCollection"):
      particle =  arc_hit.getMCParticle()
      pdgID = particle.getPDG()
      if pdgID == 22 or pdgID == -22:
        n_ph += 1
        cellID = arc_hit.getCellID()
        x = idposConv.position(cellID) 
        theta = x.theta()

        hist_theta.Fill(theta)

    hist_nPh.Fill(n_ph)
    hist_theta_1stHit.Fill(theta_1stHit, n_ph)

  if not args.no_norm:
    factor = 1./hist_nPh.GetEntries()
    hist_nPh.Scale(factor)
    hist_theta.Scale(factor)
    hist_theta_1stHit.Scale(factor)

  hist_nPh.Write()
  hist_theta.Write()
  hist_theta_1stHit.Write()

  # check for photon presence
  photon_presence = True
  if hist_theta.GetEntries() == 0:
    photon_presence = False
  
  outputFile.Close()

  return photon_presence
  

#########################################################################

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
        description="Process simulation"
    )
  parser.add_argument('-f', "--inputFile",  type=str, 
                      help='The name of the simulation file to be processed', default='ARC_sim.root')
  parser.add_argument('-o', "--outputFile", type=str, 
                      help='The name of the ROOT file where to save output histograms', default='ARC_analysis.root')
  parser.add_argument('--no_norm', action='store_true',
                      help='Do not normalize output histograms by number of events')
  args = parser.parse_args()
    
  ph_presence = make_photon_file(args)
  print(ph_presence)  
  
  
  
  
  
