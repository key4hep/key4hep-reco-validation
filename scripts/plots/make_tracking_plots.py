
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import uproot
import argparse

parser = argparse.ArgumentParser(description='Make plots of jet variables from the jet study root file')
parser.add_argument('root_file', help='Path to the root file')
parser.add_argument('reference_root_file', help='Path to the reference root file')
args = parser.parse_args()

upr = uproot.open('histo_muons_1GeV.root')
ref = uproot.open('histo_muons_1GeV.root')
assert all(k in ref.keys() for k in upr.keys())

i = 0
while i < len(upr.keys()):
    if 'eff_vs' in upr.keys()[i] or 'fake_vs' in upr.keys()[i] or 'dupl_vs' in upr.keys()[i]:
        passed = upr[upr.keys()[i]].to_numpy()
        total = upr[upr.keys()[i+1]].to_numpy()
        passed_ref = ref[ref.keys()[i]].to_numpy()
        total_ref = ref[ref.keys()[i+1]].to_numpy()
        bins = passed[1]
        values = np.nan_to_num((passed[0]/total[0]).astype(np.float64))
        values_ref = np.nan_to_num((passed_ref[0]/total_ref[0]).astype(np.float64))
        xlabel = '_'.join(upr.keys()[i].split('_')[:-1])
        i += 2
    else:
        xlabel = upr.keys()[i]
        values, bins = upr[upr.keys()[i]].to_numpy()
        values_ref, bins_ref = ref[ref.keys()[i]].to_numpy()
        i += 1
    central = (bins[1:] + bins[:-1])/2
    fig, ax = plt.subplots(1, 1, figsize=(3.72, 2.3))
    ax.plot(central, values, 'o', label='Current')
    ax.plot(central, values_ref, 's', label='Reference')
    ax.set_xlabel(xlabel)
    ax.legend()
    fig.savefig(f'tracking-{xlabel}.pdf')
