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
  ##              BEGIN: Drift Chamber Histogram Definition                  ##
  ##                                                                         ## 
  #############################################################################

  dir_DCH = outputFile.mkdir("DriftChamber")

  hist_dch_hits = ROOT.TH1F("h_DriftChamber_hits",
                        "Number of hits;Hits;Counts / 0.15 meV",
                        40, 0, 200)
    
  dir_list.append(dir_DCH)
  histo_list.append([hist_dch_hits])

  #############################################################################
  ##                                                                         ##  
  ##                END: Drift Chamber Histogram Definition                  ##
  ##                                                                         ## 
  #############################################################################


  #############################################################################
  ##                                                                         ## 
  ##             BEGIN: Vertex Detector Histogram Definition                 ##
  ##                                                                         ## 
  #############################################################################

  dir_VTXD = outputFile.mkdir("VertexDetector")

  hist_vtxd_hits = ROOT.TH1F("h_VertexDetector_hits",
                        "Number of hits;Hits;Counts / 0.15 meV",
                        40, 0, 200)
    
  dir_list.append(dir_VTXD)
  histo_list.append([hist_vtxd_hits])

  #############################################################################
  ##                                                                         ##  
  ##               END: Vertex Detector Histogram Definition                 ##
  ##                                                                         ## 
  #############################################################################


  #############################################################################
  ##                                                                         ## 
  ##           BEGIN: Vertex Inner Barrel Histogram Definition               ##
  ##                                                                         ## 
  #############################################################################

  dir_VTXIB = outputFile.mkdir("VertexInnerBarrel")

  hist_vtxib_hits = ROOT.TH1F("h_VertexInnerBarrel_hits",
                        "Number of hits;Hits;Counts / 0.15 meV",
                        40, 0, 200)
    
  dir_list.append(dir_VTXIB)
  histo_list.append([hist_vtxib_hits])

  #############################################################################
  ##                                                                         ##  
  ##             END: Vertex Inner Barrel Histogram Definition               ##
  ##                                                                         ## 
  #############################################################################


  #############################################################################
  ##                                                                         ## 
  ##           BEGIN: Vertex Outer Barrel Histogram Definition               ##
  ##                                                                         ## 
  #############################################################################

  dir_VTXOB = outputFile.mkdir("VertexOuterBarrel")

  hist_vtxob_hits = ROOT.TH1F("h_VertexOuterBarrel_hits",
                        "Number of hits;Hits;Counts / 0.15 meV",
                        40, 0, 200)
    
  dir_list.append(dir_VTXOB)
  histo_list.append([hist_vtxob_hits])

  #############################################################################
  ##                                                                         ##  
  ##             END: Vertex Outer Barrel Histogram Definition               ##
  ##                                                                         ## 
  #############################################################################
  



  # Loop over dataset
  for event in podio_reader.get("events"):

    ###########################################################################
    ##                                                                       ## 
    ##                 BEGIN: Drift Chamber Event Loop                       ##
    ##                                                                       ## 
    ###########################################################################

    n_hits = 0
    for dch_hit in event.get("DCHCollection"):
      n_hits += 1
    hist_dch_hits.Fill(n_hits)

    ###########################################################################
    ##                                                                       ## 
    ##                    END: Drift Chamber Event Loop                      ##
    ##                                                                       ## 
    ###########################################################################


    ###########################################################################
    ##                                                                       ## 
    ##                BEGIN: Vertex Detector Event Loop                      ##
    ##                                                                       ## 
    ###########################################################################

    n_hits = 0
    for vtxd_hit in event.get("VTXDCollection"):
      n_hits += 1
    hist_vtxd_hits.Fill(n_hits)

    ###########################################################################
    ##                                                                       ## 
    ##                    END: Vertex Detector Event Loop                    ##
    ##                                                                       ## 
    ###########################################################################


    ###########################################################################
    ##                                                                       ## 
    ##                 BEGIN: Vertex Inner Barrel Event Loop                 ##
    ##                                                                       ## 
    ###########################################################################

    n_hits = 0
    for vtxib_hit in event.get("VTXIBCollection"):
      n_hits += 1
    hist_vtxib_hits.Fill(n_hits)

    ###########################################################################
    ##                                                                       ## 
    ##                  END: Vertex Inner Barrel Event Loop                  ##
    ##                                                                       ## 
    ###########################################################################


    ###########################################################################
    ##                                                                       ## 
    ##                 BEGIN: Vertex Outer Barrel Event Loop                 ##
    ##                                                                       ## 
    ###########################################################################

    n_hits = 0
    for vtxob_hit in event.get("VTXOBCollection"):
      n_hits += 1
    hist_vtxob_hits.Fill(n_hits)

    ###########################################################################
    ##                                                                       ## 
    ##                  END: Vertex Outer Barrel Event Loop                  ##
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
  
  