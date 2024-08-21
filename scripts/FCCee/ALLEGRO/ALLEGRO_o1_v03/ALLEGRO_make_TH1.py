import ROOT
from podio import root_io
import dd4hep as dd4hepModule
from ROOT import dd4hep

import argparse

import os
from dd4hep import Detector
import DDRec


def make_TH1_file(args):

  # create output ROOT file
  outputFile = ROOT.TFile(args.outputFile, "RECREATE")

  # set file reader
  podio_reader = root_io.Reader(args.inputFile)

  # set list of directories in ROOT file (one per subsystem to check)
  dir_list = []
  # set list of (list of) histograms created (one list per subsystem to check)
  histo_list = []

  # get detector description for cell id decoding
  #theDetector = Detector.getInstance()
  #theDetector.fromXML(os.environ["$K4GEO"]+"/FCCee/ALLEGRO/compact/ALLEGRO_o1_v03/ALLEGRO_o1_v03.xml") 
  #idposConv = DDRec.CellIDPositionConverter(theDetector)
                  



  #############################################################################
  ##                                                                         ## 
  ##                BEGIN: ECal Barrel Histogram Definition                  ##
  ##                                                                         ## 
  #############################################################################

  dir_ECalBarrel = outputFile.mkdir("ECalBarrel")

  hist_ccE = ROOT.TH1F("h_CaloCluster_E",
                       "CaloCluster Energy;Energy [MeV];Counts / 0.15 meV",
                       100, 0, 15)
  hist_ctcE = ROOT.TH1F("h_CaloTopoCluster_E",
                        "CaloTopoCluster Energy;Energy [MeV];Counts / 0.15 meV",
                        100, 0, 15)
  hist_ecal_totE = ROOT.TH1F("h_ECalBarrelModuleThetaMergedPosition_totE",
                             "ECalBarrelModuleThetaMergedPosition total Energy per evt;Energy [MeV];Counts / 0.15 meV",
                             100, 0, 15)
  hist_ecal_posX = ROOT.TH1F("h_ECalBarrelModuleThetaMergedPosition_posX",
                             "ECalBarrelModuleThetaMergedPosition position X;X [mm];Counts / 37 mm",
                             150, -2770, 2770)
  hist_ecal_posY = ROOT.TH1F("h_ECalBarrelModuleThetaMergedPosition_posY",
                             "ECalBarrelModuleThetaMergedPosition position Y;Y [mm];Counts / 37 mm",
                             150, -2770, 2770)
  hist_ecal_posZ = ROOT.TH1F("h_ECalBarrelModuleThetaMergedPosition_posZ",
                             "ECalBarrelModuleThetaMergedPosition position Z;Z [mm];Counts / 41 mm",
                             150, -3100, 3100)
  
  dir_list.append(dir_ECalBarrel)
  histo_list.append([hist_ccE, 
                     hist_ctcE,
                     hist_ecal_totE,
                     hist_ecal_posX,
                     hist_ecal_posY,
                     hist_ecal_posZ])

  #############################################################################
  ##                                                                         ##  
  ##                  END: ECal Barrel Histogram Definition                  ##
  ##                                                                         ## 
  #############################################################################
  



  # Loop over dataset
  for event in podio_reader.get("events"):


    ###########################################################################
    ##                                                                       ## 
    ##                  BEGIN: ECal Barrel Event Loop                        ##
    ##                                                                       ## 
    ###########################################################################

    for calo in event.get("CaloClusters"):
      energy =  calo.getEnergy()
      hist_ccE.Fill(energy)

    for calo in event.get("CaloTopoClusters"):
      energy =  calo.energy()
      hist_ctcE.Fill(energy)

    energy = 0
    for ecal in event.get("ECalBarrelModuleThetaMergedPositioned"):
        energy += ecal.energy()
        hist_ecal_posX.Fill(ecal.position().x)
        hist_ecal_posY.Fill(ecal.position().y)
        hist_ecal_posZ.Fill(ecal.position().z)
    hist_ecal_totE.Fill(energy)

    ###########################################################################
    ##                                                                       ## 
    ##                    END: ECal Barrel Event Loop                        ##
    ##                                                                       ## 
    ###########################################################################



  # normalize if desired
  if args.norm:
    n_evts = len(podio_reader.get("events"))
    factor = 1./n_evts
    for l in histo_list:
      for h in l:
        h.Scale(factor)

  # save to file
  for dir, h_list in zip(dir_list, histo_list):
    dir.cd()
    for h in h_list:
      h.Write()
  
  outputFile.Close()

  return
  





#########################################################################

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
        description="Process simulation"
    )
  parser.add_argument('-f', "--inputFile",  type=str, 
                      help='The name of the simulation file to be processed', default='ARC_sim.root')
  parser.add_argument('-o', "--outputFile", type=str, 
                      help='The name of the ROOT file where to save output histograms', default='ARC_analysis.root')
  parser.add_argument('--norm', action='store_true',
                      help='Normalize output histograms by number of events')
  args = parser.parse_args()
    
  make_TH1_file(args)  
  
  
  
  
  
