import argparse
import numpy as np
import matplotlib.pyplot as plt
import uproot
from matplotlib_utils import add_table

# Number of sigmas away from the mean to make the plot red
threshold = 3

# x, y, width, height
table_dimensions_left = [0.5, 0.7, 0.25, 0.2]
table_dimensions_right = [0.75, 0.7, 0.25, 0.2]


def main(root_file, reference_root_file):
    upr = uproot.open(root_file)
    ref = uproot.open(reference_root_file)
    assert all(k in ref.keys() for k in upr.keys())

    fig, ax = plt.subplots(1, 1, figsize=(3.72, 2.3))

    for k in upr.keys():
        try:
            upr[k].classname
        except AttributeError:
            print(f'Skipping {k}, no classname found in the current sample')
            continue
        if upr[k].classname != 'TTree':
            print(f'Skipping {k}, not a TTree')
            continue

        try:
            arrays_current = upr[k].arrays(library='np')
        except AttributeError:
            print(f'Skipping {k}, no arrays found in the current sample')
            continue
        try:
            arrays_reference = ref[k].arrays(library='np')
        except AttributeError:
            print(f'Skipping {k}, no arrays found in the reference sample')
            continue
        for name in arrays_current.keys():
            print(f'{name}: {arrays_current[name].dtype}')

            dist_current = arrays_current[name]
            dist_reference = arrays_reference[name]
            if dist_current.dtype == object:
                dist_current = np.concatenate(dist_current)
                dist_reference = np.concatenate(dist_reference)
            if not dist_current.size:
                continue

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
            ax.set_xlabel(name)
            ax.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1]*1.2)
            fig.savefig(f'hist-{name}.svg')
            ax.clear()
            fig.patch.set_facecolor('white')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make plots of jet variables from the jet study root file')
    parser.add_argument('root_file', help='Path to the root file')
    parser.add_argument('reference_root_file', help='Path to the reference root file')
    args = parser.parse_args()
    main(args.root_file, args.reference_root_file)
