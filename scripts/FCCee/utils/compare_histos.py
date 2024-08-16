import ROOT
import numpy as np
import argparse


def Chi2test(h1, h2, SL):
  p_val = h1.Chi2Test(h2)
  if p_val < 1-SL:
    match = False
  else:
    match = True
  print(f"P-value for histo {h1.GetName()}: {p_val} -->  match test {'passed' if match else 'failed'}")

  return match

def KStest(h1, h2, SL):
  p_val = h1.KolmogorovTest(h2)
  if p_val < 1-SL:
    match = False
  else:
    match = True
  print(f"P-value for histo {h1.GetName()}: {p_val} -->  match test {'passed' if match else 'failed'}")

  return match

def Identical(h1, h2, SL):
  if h1.GetNbinsX() != h2.GetNbinsX():
      print("Number of bins does not match.")
      return False
  
  for bin_num in range(1, h1.GetNbinsX() + 1):
      bin_edge1 = h1.GetBinLowEdge(bin_num)
      bin_edge2 = h2.GetBinLowEdge(bin_num)
      
      bin_content1 = h1.GetBinContent(bin_num)
      bin_content2 = h2.GetBinContent(bin_num)
      
      if bin_edge1 != bin_edge2:
          print(f"Bin edges do not match at bin {bin_num}: {bin_edge1} vs {bin_edge2}")
          return False
      
      if bin_content1 != bin_content2:
          print(f"Bin contents do not match at bin {bin_num}: {bin_content1} vs {bin_content2}")
          return False
      
  print(f"Histograms {h1.GetName()} match!")
  return True


tests = {
   "chi2" : Chi2test,
   "KS" : KStest,
   "identical" : Identical
}


def compare_histos(histo1, histo2, SL, test_name):
  
  if SL < 0 or SL > 1:
    print('Please select a significance level between 0 and 1!')
    return
  
  test = tests[test_name]

  match = test(histo1, histo2, SL)

  return match


if __name__ == "__main__":
  
  parser = argparse.ArgumentParser(
        description="Compare histograms in different files"
    )
  parser.add_argument('-f', "--inputFile",  type=str, 
                      help='The name of the file with new histos to check', default='ARC_analysis.root')
  parser.add_argument('-r', "--referenceFile", type=str, 
                      help='The name of the file containing reference histos', default='')
  parser.add_argument('-h', "--histo", type=str, 
                      help='The name of the histogram to check', default='')
  parser.add_argument("--SL", type=float, default=0.95, 
                      help='Significance level of the test to perform')
  dict_keys = ', '.join(tests.keys())
  parser.add_argument("--test", type=str, choices=tests.keys(), help=f"Test to check compatibility of histograms. Possible options are: {dict_keys}")
  args = parser.parse_args()


  input_file = ROOT.TFile(args.inputFile, "READ")
  ref_file = ROOT.TFile(args.refFile, "READ")
  histo1 = input_file.Get(args.histo)
  histo2 = ref_file.Get(args.histo)

  compare_histos(histo1, histo2, args.SL, args.test)