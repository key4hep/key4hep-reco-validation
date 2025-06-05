import argparse
import ROOT
from podio import root_io



def make_TH1_file(args):

    # create output ROOT file
    outputFile = ROOT.TFile(args.outputFile, "RECREATE")

    # set file reader
    podio_reader = root_io.Reader(args.inputFile)

    # set list of directories in ROOT file (one per subsystem to check)
    dir_list = []
    # set list of (list of) histograms created (one list per subsystem to check)
    histo_list = []

    ############      BEGIN: Drift Chamber Histogram Definition      ############

    dir_DCH = outputFile.mkdir("DriftChamber")

    hist_dch_hits = ROOT.TH1F(
        "h_DriftChamber_hits", "Number of hits;Hits;Counts / 5 hits", 40, 0, 200
    )

    dir_list.append(dir_DCH)
    histo_list.append([hist_dch_hits])

    #############      END: Drift Chamber Histogram Definition      #############

    #########     BEGIN: Vertex Barrel Histogram Definition      ##########

    dir_VTXB = outputFile.mkdir("VertexBarrel")

    hist_vtxb_hits = ROOT.TH1F(
        "h_VertexBarrel_hits", "Number of hits;Hits;Counts / 5 hits", 40, 0, 200
    )

    dir_list.append(dir_VTXB)
    histo_list.append([hist_vtxb_hits])

    # #######     END: Vertex Barrel Histogram Definition      ##########

    # ######     BEGIN: Vertex Endcap Histogram Definition      #########

    dir_VTXE = outputFile.mkdir("VertexEndcap")

    hist_vtxe_hits = ROOT.TH1F(
        "h_VertexEndcap_hits", "Number of hits;Hits;Counts / 5 hits", 40, 0, 200
    )

    dir_list.append(dir_VTXE)
    histo_list.append([hist_vtxe_hits])

    # ########     END: Vertex Endcap Histogram Definition      #########

    # ###########      BEGIN: Muon System Histogram Definition      ###########

    dir_MUS = outputFile.mkdir("MuonSystem")

    hist_mus_hits = ROOT.TH1F(
        "h_MuonSystem_hits", "Number of hits;Hits;Counts / 5 hits", 40, 0, 200
    )

    dir_list.append(dir_MUS)
    histo_list.append([hist_mus_hits])

    # ##########      END: Muon System Histogram Definition      ##############

    # ###########      BEGIN: LumiCal Histogram Definition      ###############

    dir_LC = outputFile.mkdir("LumiCal")

    hist_lc_hits = ROOT.TH1F(
        "h_LumiCal_hits", "Number of hits;Hits;Counts / 5 hits", 40, 0, 200
    )

    dir_list.append(dir_LC)
    histo_list.append([hist_lc_hits])

    # ###########      END: LumiCal Histogram Definition      ##############

    # Loop over dataset
    for event in podio_reader.get("events"):

        # ###########      BEGIN: Drift Chamber Event Loop      ##############

        n_hits = 0
        for dch_hit in event.get("DCHCollection"):
            n_hits += 1
        hist_dch_hits.Fill(n_hits)

        # #############      END: Drift Chamber Event Loop      ###############

        # #########      BEGIN: Vertex Barrel Event Loop      ###########

        n_hits = 0
        for vtxb_hit in event.get("VertexBarrelCollection"):
            n_hits += 1
        hist_vtxb_hits.Fill(n_hits)

        # ##########      END: Vertex Barrel Event Loop      ############

        # #########      BEGIN: Vertex Endcap Event Loop      ###########

        n_hits = 0
        for vtxe_hit in event.get("VertexEndcapCollection"):
            n_hits += 1
        hist_vtxe_hits.Fill(n_hits)

        # ##########      END: Vertex Endcap Event Loop      ############

        # #############      BEGIN: Muon System Event Loop      ###############

        n_hits = 0
        for mus_hit in event.get("MuonSystemCollection"):
            n_hits += 1
        hist_mus_hits.Fill(n_hits)

        # ##############      END: Muon System Event Loop      ################

        # ###############      BEGIN: LumiCal Event Loop      #################

        n_hits = 0
        for lc_hit in event.get("LumiCalCollection"):
            n_hits += 1
        hist_lc_hits.Fill(n_hits)

        # ################      END: LumiCal Event Loop      ##################

    # normalize if desired
    if args.norm:
        n_evts = len(podio_reader.get("events"))
        factor = 1.0 / n_evts
        for l in histo_list:
            for h in l:
                h.Scale(factor)

    # save to file
    for directory, h_list in zip(dir_list, histo_list):
        directory.cd()
        for h in h_list:
            h.Write()

    outputFile.Close()

    return


#########################################################################
def main():
    '''
    Setting things in motion.
    '''

    parser = argparse.ArgumentParser(description="Process simulation")
    parser.add_argument(
        "-f",
        "--inputFile",
        type=str,
        help="The name of the simulation file to be processed",
        default="IDEA_sim_digi_reco.root",
    )
    parser.add_argument(
        "-o",
        "--outputFile",
        type=str,
        help="The name of the ROOT file where to save output histograms",
        default="results.root",
    )
    parser.add_argument(
        "--norm",
        action="store_true",
        help="Normalize output histograms by number of events",
    )
    args = parser.parse_args()

    make_TH1_file(args)


if __name__ == "__main__":
    main()
