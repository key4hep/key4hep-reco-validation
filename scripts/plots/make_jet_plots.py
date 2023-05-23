# Make plots of jet variables from the jet study root file
import numpy as np
import matplotlib.pyplot as plt
import uproot
import argparse

parser = argparse.ArgumentParser(description='Make plots of jet variables from the jet study root file')
parser.add_argument('root_file', help='Path to the root file')
parser.add_argument('reference_root_file', help='Path to the reference root file')
args = parser.parse_args()

upr = uproot.open(args.root_file)['showerData;1']
ref = uproot.open(args.reference_root_file)['showerData;1']
arrays = [upr.arrays(upr.keys(), library='np'), ref.arrays(ref.keys(), library='np')]
assert all(k in ref.keys() for k in upr.keys())

for k in arrays[0].keys():
    fig, ax = plt.subplots(1, 1, figsize=(3.72, 2.3))
    if arrays[0][k].dtype != object:
        _, bins, _ = ax.hist(arrays[0][k], bins=15, histtype='step', label='Current')
        ax.hist(arrays[1][k], bins=bins, histtype='step', label='Reference')
    else:
        _, bins, _ = ax.hist(np.concatenate(arrays[0][k]), bins=15, histtype='step', label='Current')
        ax.hist(np.concatenate(arrays[1][k]), bins=bins, histtype='step', label='Reference')
    ax.legend()
    ax.set_ylabel('Entries')
    ax.set_xlabel(k)
    fig.savefig(f'jet-{k}.png')

for gen, reco in [['genJetE', 'recoJetE'], ['genJetPx', 'recoJetPx'], ['genJetPy', 'recoJetPy'], ['genJetPz', 'recoJetPz']]:
    fig, ax = plt.subplots(1, 1, figsize=(3.72, 2.3))
    _, bins, _ = ax.hist(np.concatenate(arrays[0][gen])-np.concatenate(arrays[0][reco]),
            bins=20, histtype='step', label='Current')
    ax.hist(np.concatenate(arrays[1][gen])-np.concatenate(arrays[1][reco]),
            bins=bins, histtype='step', label='Reference')
    ax.legend()
    ax.set_xlabel(f'{gen} - {reco}')
    ax.set_ylabel('Entries')
    fig.savefig(f'jet-{gen}-{reco}.png')