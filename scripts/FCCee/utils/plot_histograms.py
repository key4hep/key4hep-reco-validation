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

  n_bins = h.GetNbinsX()
  bin_edges = np.array([h.GetBinLowEdge(i+1) for i in range(n_bins+1)])
  bin_contents = np.array([h.GetBinContent(i+1) for i in range(n_bins)])

  # plot new validation hist
  fig, ax = plt.subplots(figsize=(8,6))
  ax.bar(bin_edges[:-1], bin_contents, width=np.diff(bin_edges), align="edge",
         label='Current', edgecolor='orange', color='white', ecolor='orange')
  ax.set_xlabel(h.GetXaxis().GetTitle())
  ax.set_ylabel(h.GetYaxis().GetTitle())
  ax.set_title(h.GetTitle())

  # if check with reference value
  if h_ref is not None:
    # if reference histo is found in the correct place
    if h_ref:
      n_bins = h.GetNbinsX()
      ref_edges = np.array([h_ref.GetBinLowEdge(i+1) for i in range(n_bins+1)])
      ref_contents = np.array([h_ref.GetBinContent(i+1) for i in range(n_bins)])
      ax.bar(ref_edges[:-1], ref_contents, width=np.diff(ref_edges), align="edge",
              label='Reference', edgecolor='skyblue', color='white', alpha=0.7)
      ax.legend(loc='best')
      if not match:
        fig.patch.set_facecolor('red') 
    # if reference histo is not present
    else:
        fig.patch.set_facecolor('yellow')
        plt.text(
          0.95, 0.05,  
          "WARNING: Reference histogram not found",  
          fontsize=12, 
          color='black',  
          ha='right',  # Horizontal alignment: right
          va='bottom',  # Vertical alignment: bottom
          transform=plt.gca().transAxes  # Use the Axes coordinates (relative coordinates)
        )

  return fig


def make_plots(args):

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

      fig = plot_histo(histo, histo_ref, match)

      if not args.no_save:
        fig.savefig(save_dir+f'/{h_name}'+'.svg', bbox_inches='tight')
      if not args.show:
        plt.close(fig)

  if args.show:
    plt.show()
  

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
  
  