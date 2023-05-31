# Make plots of jet variables from the jet study root file
import numpy as np
import matplotlib.pyplot as plt
import uproot
import argparse
from matplotlib_utils import add_table

label_map = {'recoJetE': 'Reconstructed Jet Energy',
             'recoJetPx': 'Reconstructed Jet $P_x$',
             'recoJetPy': 'Reconstructed Jet $P_y$',
             'recoJetPz': 'Reconstructed Jet $P_z$',
             'genJetE': 'Generated Jet Energy',
             'genJetPx': 'Generated Jet $P_x$',
             'genJetPy': 'Generated Jet $P_y$',
             'genJetPz': 'Generated Jet $P_z$',
             'E_totPFO': 'Total PFO Energy',
             'E_trueInv': 'True Invisible Energy',
             'E_trueVis': 'True Visible Energy',
             'Px_totPFO': 'Total PFO $P_x$',
             'Py_totPFO': 'Total PFO $P_y$',
             'Pz_totPFO': 'Total PFO $P_z$',
             'Px_trueInv': 'True Invisible $P_x$',
             'Py_trueInv': 'True Invisible $P_y$',
             'Pz_trueInv': 'True Invisible $P_z$',
             'Px_trueVis': 'True Visible $P_x$',
             'Py_trueVis': 'True Visible $P_y$',
             'd1_mcE': 'Daughter 1 MC Energy',
             'd2_mcE': 'Daughter 2 MC Energy',
             'd1_mcPDGID': 'Daughter 1 MC PDGID',
             'd2_mcPDGID': 'Daughter 2 MC PDGID',
             'd1_mcPx': 'Daughter 1 MC $P_x$',
             'd2_mcPx': 'Daughter 2 MC $P_x$',
             'd1_mcPy': 'Daughter 1 MC $P_y$',
             'd2_mcPy': 'Daughter 2 MC $P_y$',
             'd1_mcPz': 'Daughter 1 MC $P_z$',
             'd2_mcPz': 'Daughter 2 MC $P_z$',
             'd1_mcE': 'Daughter 1 MC Energy',
             'd2_mcE': 'Daughter 2 MC Energy',
             }

# Number of sigmas away from the mean to make the plot red
threshold = 3


def make_jet_plots(root_file, reference_root_file):
    upr = uproot.open(root_file)['showerData;1']
    ref = uproot.open(reference_root_file)['showerData;1']
    arrays = [upr.arrays(upr.keys(), library='np'), ref.arrays(ref.keys(), library='np')]
    assert all(k in ref.keys() for k in upr.keys())

    fig, ax = plt.subplots(1, 1, figsize=(3.72, 2.3))

    for k in arrays[0].keys():
        if arrays[0][k].dtype != object:
            dist_current = arrays[0][k]
            dist_reference = arrays[1][k]
        else:
            dist_current = np.concatenate(arrays[0][k])
            dist_reference = np.concatenate(arrays[1][k])
        _, bins, _ = ax.hist(dist_current, bins=15, histtype='step', label='Current')
        ax.hist(dist_reference, bins=bins, histtype='step', label='Reference')

        left = ['Mean', 'Std. Dev.', 'Entries']
        right_current_values = [dist_current.mean(), dist_current.std(), len(dist_current)]
        right_current_labels = [f'{right_current_values[0]:.2f}', f'{right_current_values[1]:.2f}', f'{right_current_values[2]}']
        add_table(left, right_current_labels, ax, [0.6, 0.4, 0.2, 0.2])
        right_reference_values = [dist_reference.mean(), dist_reference.std(), len(dist_reference)]
        right_reference_labels = [f'{right_reference_values[0]:.2f}', f'{right_reference_values[1]:.2f}', f'{right_reference_values[2]}']
        add_table(left, right_reference, ax, [0.8, 0.4, 0.2, 0.2])

        # If the mean is more than threshold sigma away from the reference, make the plot red
        if abs(right_current_values[0] - right_reference_values[0]) > threshold*(right_reference_values[1] / np.sqrt(len(dist_reference))):
            fig.patch.set_facecolor('red')

        ax.legend()
        ax.set_ylabel('Entries')
        ax.set_xlabel(label_map[k])
        fig.savefig(f'jet-{k}.png')
        ax.clear()

    for gen, reco in [['genJetE', 'recoJetE'], ['genJetPx', 'recoJetPx'], ['genJetPy', 'recoJetPy'], ['genJetPz', 'recoJetPz']]:
        _, bins, _ = ax.hist(np.concatenate(arrays[0][gen])-np.concatenate(arrays[0][reco]),
                             bins=20, histtype='step', label='Current')
        ax.hist(np.concatenate(arrays[1][gen])-np.concatenate(arrays[1][reco]),
                bins=bins, histtype='step', label='Reference')
        ax.legend()
        ax.set_xlabel(f'{label_map[gen]} - {label_map[reco]}')
        ax.set_ylabel('Entries')
        fig.savefig(f'jet-{gen}-{reco}.png')
        ax.clear()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make plots of jet variables from the jet study root file')
    parser.add_argument('root_file', help='Path to the root file')
    parser.add_argument('reference_root_file', help='Path to the reference root file')
    args = parser.parse_args()
    make_jet_plots(args.root_file, args.reference_root_file)
