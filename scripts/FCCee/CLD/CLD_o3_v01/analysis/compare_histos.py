import ROOT
import numpy as np
import argparse
import uproot

def compare_histos(inputFile, refFile, SL):
  
  if SL < 0 or SL > 1:
    print('Please select a significance level between 0 and 1!')
    return

  input_file = ROOT.TFile(inputFile, "READ")
  ref_file = ROOT.TFile(refFile, "READ")

  matches = {}
  ref_keys = ref_file.GetListOfKeys()
  for key in input_file.GetListOfKeys():
    for ref_key in ref_keys:
      if key.GetName() == ref_key.GetName() and \
         'TH1' in key.GetClassName() and 'TH1' in ref_key.GetClassName():
        histo1 = input_file.Get(key.GetName())
        histo2 = ref_file.Get(key.GetName())
        p_val = histo1.Chi2Test(histo2)

        if p_val < 1-SL:
          matches[key.GetName()] = False
        else:
          matches[key.GetName()] = True

        print(f"P-value for histo {key.GetName()}: {p_val} -->  match test {'passed' if matches[key.GetName()] else 'failed'}")

        break

  return matches


if __name__ == "__main__":
  
  parser = argparse.ArgumentParser(
        description="Compare histograms in different files"
    )
  parser.add_argument('-f', "--inputFile",  type=str, 
                      help='The name of the file with new histos to check', default='ARC_analysis.root')
  parser.add_argument('-r', "--referenceFile", type=str, 
                      help='The name of the file containing reference histos', default='')
  parser.add_argument("--SL", type=float, default=0.95, 
                      help='Significance level of the test to perform')
  args = parser.parse_args()

  compare_histos(args.inputFile, args.referenceFile, args.SL)