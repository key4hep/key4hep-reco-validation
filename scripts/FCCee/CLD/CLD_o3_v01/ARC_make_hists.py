import os
import sys
import argparse
import ROOT
from podio import root_io
import numpy as np
from dd4hep import Detector
import DDRec


def make_hists_file(args):

    # create output ROOT file
    outputFile = ROOT.TFile(args.outputFile, "UPDATE")

    # set file reader
    podio_reader = root_io.Reader(args.inputFile)

    # get detector description for cell id decoding
    theDetector = Detector.getInstance()
    theDetector.fromXML(args.compactFile)
    idposConv = DDRec.CellIDPositionConverter(theDetector)

    # set list of directories in ROOT file (one per subsystem to check)
    dir_list = []
    # set list of (list of) histograms created (one list per subsystem to check)
    histo_list = []

    # ########      BEGIN: ARC standalone Histogram Definition      ###########

    dir_ARC = outputFile.mkdir("ARC_standalone")

    hist_ARC_nPh = ROOT.TH1F(
        "h_ARC_nPh",
        "Total number of photon counts per event;Number of Photons;"
        "Photon count / 5",
        50,
        0,
        250,
    )
    hist_ARC_theta = ROOT.TH1F(
        "h_ARC_theta",
        "Photons counts vs. #theta;Polar angle #theta;Photon count / 35 mrad",
        90,
        0,
        np.pi,
    )
    hist_ARC_1stHit = ROOT.TH1F(
        "h_ARC_1stHit",
        "Photons counts vs. #theta of incoming particle;Polar angle #theta;Photon count / 35 mrad",
        90,
        0,
        np.pi,
    )

    dir_list.append(dir_ARC)
    histo_list.append([hist_ARC_nPh, hist_ARC_theta, hist_ARC_1stHit])

    # ##########      END: ARC standalone Histogram Definition      ###########

    # loop over dataset
    for event in podio_reader.get("events"):

        # ###########      BEGIN: ARC standalone Event Loop      ##############

        n_ph = 0

        p = (event.get("MCParticles"))[0]
        mom = ROOT.TVector3(p.getMomentum().x,
                            p.getMomentum().y,
                            p.getMomentum().z)
        theta_1stHit = mom.Theta()

        for arc_hit in event.get("ArcCollection"):
            particle = arc_hit.getMCParticle()
            pdgID = particle.getPDG()
            if pdgID in (22, -22):
                n_ph += 1
                # cellID = arc_hit.getCellID()
                # print(f'cellID: {cellID}')

                # hist_ARC_theta.Fill(idposConv.position(cellID).theta())

        hist_ARC_nPh.Fill(n_ph)
        hist_ARC_1stHit.Fill(theta_1stHit, n_ph)

        # ############      END: ARC standalone Event Loop      ###############

    if args.norm:
        n_evts = len(podio_reader.get("events"))
        factor = 1.0 / n_evts
        for l in histo_list:
            for h in l:
                h.Scale(factor)

    # save to file
    for dir, h_list in zip(dir_list, histo_list):
        dir.cd()
        for h in h_list:
            h.Write()

    outputFile.Close()


# #############################################################################
def main():
    '''
    Setting things in motion
    '''
    parser = argparse.ArgumentParser(description="Process simulation")
    parser.add_argument(
        "-f",
        "--inputFile",
        type=str,
        default="ARC_sim.root",
        help="The name of the simulation file to be processed"
    )
    parser.add_argument(
        "-o",
        "--outputFile",
        type=str,
        default="results.root",
        help="The name of the ROOT file where to save output histograms"
    )
    parser.add_argument(
        "-c",
        "--compactFile",
        type=str,
        default=None,
        help="Compact file describing the sub-detector",
    )
    parser.add_argument(
        "--norm",
        action="store_true",
        help="Normalize output histograms by number of events",
    )
    args = parser.parse_args()

    if args.compactFile is None:
        print('ERROR: Compact file not provided!')
        print('       Aborting...')
        sys.exit(1)

    ph_presence = make_hists_file(args)
    print(ph_presence)


if __name__ == "__main__":
    main()
