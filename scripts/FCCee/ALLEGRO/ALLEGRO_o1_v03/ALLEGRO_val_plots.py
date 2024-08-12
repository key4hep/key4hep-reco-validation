import ROOT
import uproot
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
from matplotlib.colors import SymLogNorm

import argparse
import numpy as np
import sys
import importlib.util
from pathlib import Path
import os


plot_params = {

  "ccE" : {
    "range" : (0, 15),
    "xlabel": 'Energy [MeV]',
    "ylabel": 'Counts / 0.15 MeV',
  },

  "ctcE" : {
    "range" : (0, 10),
    "xlabel": 'Energy [MeV]',
    "ylabel": 'Counts / 0.1 MeV',
  }

}


def make_plots(args):

  filename = os.path.splitext(os.path.basename(args.inputFile))[0] # removes path and extension
  if args.outputPath[-1] != '/':
    args.outputPath += '/'
  output_start = args.outputPath + filename 

  # read input file
  inputFile = uproot.open(args.inputFile)

  # check reference
  if len(args.referenceFile) != 0:
        # import compare_histos module from scripts directory
    current_dir = Path(__file__).resolve().parent
    target_dir = current_dir.parents[3]
    sys.path.insert(0, str(target_dir))
    module_name = "compare_histos"
    spec = importlib.util.find_spec(module_name)
    target_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(target_module)

    refFile = uproot.open(args.referenceFile)
    histograms_match = target_module.compare_histos(args.inputFile, args.referenceFile, args.SL, args.test)

    sys.path.pop(0)

  # Plot histograms
  for key in inputFile:
    histo = inputFile[key]
    edges = histo.axis().edges()
    values = histo.values()

    param = {}
    for p in plot_params:
      if p in key:
        param = plot_params[p]
        break
    if len(param) == 0:
      print(f"No plot parameters found for histogram {key}!")
      continue

    fig, ax = plt.subplots(figsize=(8,6))
    ax.hist(edges[:-1], bins=edges, weights=values, histtype='step',
             label='New hist', color='blue')
    ax.set_xlabel(param['xlabel'])
    ax.set_ylabel(param['ylabel'])
    ax.set_title(f'{histo.title}')
    ax.set_yscale('log')

    if len(args.referenceFile) != 0:
      try:
        ref_histo = refFile[key]
        ref_edges = ref_histo.axis().edges()
        ref_values = ref_histo.values()
        ax.hist(ref_edges[:-1], bins=ref_edges, weights=ref_values, histtype='step',
                label='Reference hist', color='red')
        ax.legend(loc='best')
        if not histograms_match[key.split(';')[0]]:
          fig.patch.set_facecolor('red') 
      except uproot.exceptions.KeyInFileError:
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

    if not args.no_save:
      fig.savefig(output_start+f'_{histo.name}'+'.svg', bbox_inches='tight')
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
  parser.add_argument("--SL", type=float, default=0.95, 
                      help='Significance level of the test to perform')
  parser.add_argument("--show",    action='store_true', help='Plot output histograms')
  parser.add_argument("--test", type=str, help=f"Test to check compatibility of histograms. Possible options are: chi2, KS, identical")
  #parser.add_argument("--no_norm", action='store_true', help='Do not normalize output histograms by number of events')
  
  args = parser.parse_args()
    
  make_plots(args)
  
  
  
  
  
