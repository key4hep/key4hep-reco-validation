# Make plots of jet variables from the jet study root file

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import uproot

upr = uproot.open('JetStudy_WW1000_11814_CLIC_o3_v14_CT_PandoraPFOs_testnew.root')['showerData;1']
ref = uproot.open('JetStudy_WW1000_11814_CLIC_o3_v14_CT_PandoraPFOs_testnew.root')['showerData;1']
arrays = [upr.arrays(upr.keys(), library='np'), ref.arrays(ref.keys(), library='np')]
assert all(k in ref.keys() for k in upr.keys())

for k in arrays[0].keys():
    fig, ax = plt.subplots(1, 1, figsize=(3.72, 2.3))
    if arrays[0][k].dtype != object:
        _, bins, _ = ax.hist(arrays[0][k], bins=100, label='Current')
        ax.hist(arrays[1][k], bins=bins, label='Reference')
    else:
        _, bins, _ = ax.hist(np.concatenate(arrays[0][k]), bins=100, label='Current')
        ax.hist(np.concatenate(arrays[1][k]), bins=bins, label='Reference')
    ax.legend()
    ax.set_ylabel('Entries')
    ax.set_xlabel(k)
    fig.savefig(f'jet-{k}.pdf')

for gen, reco in [['genJetE', 'recoJetE'], ['genJetPx', 'recoJetPx'], ['genJetPy', 'recoJetPy'], ['genJetPz', 'recoJetPz']]:
    fig, ax = plt.subplots(1, 1, figsize=(3.72, 2.3))
    ax.hist(np.concatenate(arrays[0][gen])-np.concatenate(arrays[0][reco]),
            bins=20, histtype='step', label='Current')
    ax.hist(np.concatenate(arrays[1][gen])-np.concatenate(arrays[1][reco]),
            bins=20, histtype='step', label='Reference')
    ax.legend()
    ax.set_xlabel(f'{gen} - {reco}')
    ax.set_ylabel('Entries')
    fig.savefig(f'jet-{gen}-{reco}.pdf')
