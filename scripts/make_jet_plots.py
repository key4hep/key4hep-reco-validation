# Make plots of jet variables from the jet study root file
import numpy as np
import matplotlib.pyplot as plt
import uproot
import argparse
from matplotlib_utils import add_table

label_map = {'recoJetE': 'Reconstructed Jet Energy [GeV]',
             'recoJetPx': 'Reconstructed Jet $P_x$ [GeV]',
             'recoJetPy': 'Reconstructed Jet $P_y$ [GeV]',
             'recoJetPz': 'Reconstructed Jet $P_z$ [GeV]',
             'genJetE': 'MC Jet Energy [GeV]',
             'genJetPx': 'MC Jet $P_x$ [GeV]',
             'genJetPy': 'MC Jet $P_y$ [GeV]',
             'genJetPz': 'MC Jet $P_z$ [GeV]',
             'E_totPFO': 'Total PFO Energy [GeV]',
             'E_trueInv': 'MC Invisible Energy [GeV]',
             'E_trueVis': 'MC Visible Energy [GeV]',
             'Px_totPFO': 'Total PFO $P_x$ [GeV]',
             'Py_totPFO': 'Total PFO $P_y$ [GeV]',
             'Pz_totPFO': 'Total PFO $P_z$ [GeV]',
             'Px_trueInv': 'MC Invisible $P_x$ [GeV]',
             'Py_trueInv': 'MC Invisible $P_y$ [GeV]',
             'Pz_trueInv': 'MC Invisible $P_z$ [GeV]',
             'Px_trueVis': 'MC Visible $P_x$ [GeV]',
             'Py_trueVis': 'MC Visible $P_y$ [GeV]',
             'Pz_trueVis': 'MC Visible $P_z$ [GeV]',
             'd1_mcE': 'Daughter 1 MC Energy [GeV]',
             'd2_mcE': 'Daughter 2 MC Energy [GeV]',
             'd1_mcPDGID': 'Daughter 1 MC PDGID',
             'd2_mcPDGID': 'Daughter 2 MC PDGID',
             'd1_mcPx': 'Daughter 1 MC $P_x$ [GeV]',
             'd2_mcPx': 'Daughter 2 MC $P_x$ [GeV]',
             'd1_mcPy': 'Daughter 1 MC $P_y$ [GeV]',
             'd2_mcPy': 'Daughter 2 MC $P_y$ [GeV]',
             'd1_mcPz': 'Daughter 1 MC $P_z$ [GeV]',
             'd2_mcPz': 'Daughter 2 MC $P_z$ [GeV]',
             'd1_mcE': 'Daughter 1 MC Energy [GeV]',
             'd2_mcE': 'Daughter 2 MC Energy [GeV]',
             }

# Number of sigmas away from the mean to make the plot red
threshold = 3

# x, y, width, height
table_dimensions_left = [0.5, 0.7, 0.25, 0.2]
table_dimensions_right = [0.75, 0.7, 0.25, 0.2]

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
        if 'pdg' in k.lower():
            bins = 'auto'
        elif k == 'E_trueInv':
            bins = [-.5, .5]
        else:
            bins = np.linspace(min(dist_current.min(), dist_reference.min()), max(dist_current.max(), dist_reference.max()), 15)
        _, bins, _ = ax.hist(dist_current, bins=bins, histtype='step', label='Current', density=True)
        ax.hist(dist_reference, bins=bins, histtype='step', label='Reference', density=True)

        left = ['Mean', 'Std. Dev.', 'Entries']
        right_current_values = [dist_current.mean(), dist_current.std(), len(dist_current)]
        right_current_labels = [f'{right_current_values[0]:.2f}', f'{right_current_values[1]:.2f}', f'{right_current_values[2]}']
        add_table(left, right_current_labels, ax, table_dimensions_left, title='Current')
        right_reference_values = [dist_reference.mean(), dist_reference.std(), len(dist_reference)]
        right_reference_labels = [f'{right_reference_values[0]:.2f}', f'{right_reference_values[1]:.2f}', f'{right_reference_values[2]}']
        add_table(left, right_reference_labels, ax, table_dimensions_right, title='Reference')

        # If the mean is more than threshold sigma away from the reference, make the plot red
        if abs(right_current_values[0] - right_reference_values[0]) > threshold*(right_reference_values[1] / np.sqrt(len(dist_reference))):
            fig.patch.set_facecolor('red')

        ax.legend()
        ax.set_ylabel('Entries [a.u.]')
        ax.set_xlabel(label_map[k])
        ax.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1]*1.2)
        fig.savefig(f'jet-{k}.png')
        ax.clear()
        fig.patch.set_facecolor('white')

        # if k == 'genJetE':
        #     print(dist_current, dist_reference)
        #     print(right_current_values, right_reference_values)
        #     print(abs(right_current_values[0] - right_reference_values[0]), threshold*(right_reference_values[1] / np.sqrt(len(dist_reference))))

    for gen, reco in [['genJetE', 'recoJetE'], ['genJetPx', 'recoJetPx'], ['genJetPy', 'recoJetPy'], ['genJetPz', 'recoJetPz']]:
        dist_current = np.concatenate(arrays[0][gen])-np.concatenate(arrays[0][reco])
        # Remove any array that doesn't have both the generated and reconstructed
        for i in range(len(arrays[1][gen])):
            if len(arrays[1][gen][i]) and len(arrays[1][gen][i]) != len(arrays[1][reco][i]):
                arrays[1][gen][i] = np.array([])
                arrays[1][reco][i] = np.array([])
        dist_reference = np.concatenate(arrays[1][gen])-np.concatenate(arrays[1][reco])
        _, bins, _ = ax.hist(dist_current, bins=20, histtype='step', label='Current', density=True)
        ax.hist(dist_reference, bins=bins, histtype='step', label='Reference', density=True)
        left = ['Mean', 'Std. Dev.', 'Entries']
        right_current_values = [dist_current.mean(), dist_current.std(), len(dist_current)]
        right_current_labels = [f'{right_current_values[0]:.2f}', f'{right_current_values[1]:.2f}', f'{right_current_values[2]}']
        add_table(left, right_current_labels, ax, table_dimensions_left, title='Current')
        right_reference_values = [dist_reference.mean(), dist_reference.std(), len(dist_reference)]
        right_reference_labels = [f'{right_reference_values[0]:.2f}', f'{right_reference_values[1]:.2f}', f'{right_reference_values[2]}']
        add_table(left, right_reference_labels, ax, table_dimensions_right, title='Reference')

        # If the mean is more than threshold sigma away from the reference, make the plot red
        if abs(right_current_values[0] - right_reference_values[0]) > threshold*(right_reference_values[1] / np.sqrt(len(dist_reference))):
            fig.patch.set_facecolor('red')

        ax.legend()
        ax.set_xlabel(f'{label_map[gen]} - {label_map[reco]}')
        ax.set_ylabel('Entries [a.u.]')
        ax.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1]*1.2)
        fig.savefig(f'jet-{gen}-{reco}.png')
        ax.clear()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make plots of jet variables from the jet study root file')
    parser.add_argument('root_file', help='Path to the root file')
    parser.add_argument('reference_root_file', help='Path to the reference root file')
    args = parser.parse_args()
    make_jet_plots(args.root_file, args.reference_root_file)
