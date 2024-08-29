import ROOT
import matplotlib.pyplot as plt

import argparse
import importlib.util
import numpy as np
import os
from pathlib import Path


def get_current_path():
    current_dir = ROOT.gDirectory  # Get the current directory
    dir_name = current_dir.GetPath()  # Get the full path of the current directory
    file_name, *path_parts = dir_name.split(":")
    
    # Join the parts to get the relative path
    relative_path = "/".join(path_parts)
    
    return relative_path[1:]
  


def recursive_search(target_dir, dict):
    target_dir.cd()
    for key in target_dir.GetListOfKeys():
        if "TH1" in key.GetClassName():
            h = key.GetName()
            path = get_current_path()
            if path in dict:
              dict[path].append(h)
            else:
               dict[path] = [h]
        elif key.GetClassName() == "TDirectoryFile":
            new_dir = target_dir.Get(key.GetName())
            recursive_search(new_dir, dict)
            target_dir.cd()


def plot_histo(h, h_ref, match):

  c1 = ROOT.TCanvas("c1", "Canvas", 800, 600)
  pad = c1.GetPad(0)

  # Set different colors for each histogram
  h.SetLineColor(ROOT.kBlue)

  # Draw the first histogram
  h.Draw()

  # Create a legend
  legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9) # this is the position of the legend (I usualy do trial and error to place it properly)
  legend.AddEntry(h, "Current", "l")

  # if check with reference value
  if h_ref is not None:
    # if reference histo is found in the correct place
    if h_ref:
      h_ref.SetLineColor(ROOT.kRed)
      h_ref.Draw("SAME")
      legend.AddEntry(h_ref, "Reference", "l")
      if not match:
        c1.SetFillColor(ROOT.kRed) 
        pad.SetFillColor(0)
    # if reference histo is not present
    else:
        c1.SetFillColor(ROOT.kYellow) 
        pad.SetFillColor(0)
        # Create a TLatex object for the text
        warning = ROOT.TLatex()
        warning.SetNDC()  # Use Normalized Device Coordinates (0 to 1)
        warning.SetTextSize(0.04)  # Text size
        warning.SetTextAlign(33)   # Align bottom-right corner
        warning.DrawLatex(0.95, 0.05, "WARNING: Reference histogram not found")

  
  # Update the canvas to display the plots
  legend.Draw()
  c1.Update()
  
  return c1


def make_plots(args):

  if not args.show:
    ROOT.gROOT.SetBatch(True)

  # read input file
  inputFile = ROOT.TFile(args.inputFile, "READ")
  # create dict with file structure
  file_struct = {}
  recursive_search(inputFile, file_struct)

  # check reference
  check_ref = Path(args.referenceFile).is_file() 
  if check_ref:
    refFile = ROOT.TFile(args.referenceFile, "READ")
    comparison_module = importlib.import_module("compare_histos")

  # Plot histograms
  # loop over all directories inside file
  for dir in file_struct:
    print(dir)
    if dir != '':
      inputDir = inputFile.Get(dir)
      if check_ref:
        refDir = refFile.Get(dir)
    else:
      inputDir = inputFile
      if check_ref:
        refDir = refFile
      

    #check output directory
    save_dir = os.path.join(args.outputPath, dir, 'plots')
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    # loop over all histos inside directory
    for h_name in file_struct[dir]:
      
      histo = inputDir.Get(h_name)
      histo_ref = None
      match = False
      if check_ref:
        if refDir:
          histo_ref = refDir.Get(h_name)
        else:
          histo_ref = refDir
        if histo_ref:
          match = comparison_module.compare_histos(histo, histo_ref, args.SL, args.test)

      c = plot_histo(histo, histo_ref, match)

      if not args.no_save:
        c.SaveAs(save_dir+f'/{h_name}'+'.svg')
  

#########################################################################

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
        description="Process simulation"
    )
  parser.add_argument('-f', "--inputFile",  type=str, 
                      help='The name of the simulation file to be processed', default='ARC_analysis.root')
  parser.add_argument('-o', "--outputPath", type=str, 
                      help='The name of the directory where to save output files', default='./')
  parser.add_argument('-r', "--referenceFile", type=str, 
                      help='The name of the file containing reference histos', default='')
  parser.add_argument("--no_save", action='store_true', help='Do not save output arrays')
  parser.add_argument("--show",    action='store_true', help='Plot output histograms')
  parser.add_argument("--test", type=str, help=f"Test to check compatibility of histograms. Possible options are: chi2, KS, identical")
  parser.add_argument("--SL", type=float, default=0.95, 
                      help='Significance level of the test to perform')
  
  args = parser.parse_args()
    
  make_plots(args)
  
  