import argparse
import importlib
import os
import shutil

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('plots', nargs='+')
arg_parser.add_argument('--reference', required=True)
arg_parser.add_argument('--output', required=True)
args = arg_parser.parse_args()

to_run = []

modules = {'jets': 'make_jet_plots',
           'hists': 'make_distribution_hists',
           }
filenames = {'jets': 'jet_study.root',
             'hists': 'histograms.root',
             }

for k, module in modules.items():
    if k in args.plots:
        imported = importlib.import_module(module)
        to_run.append({'name': k, 'function': imported.main})

for run in to_run:
    try:
        run['function'](filenames[run['name']], os.path.join(args.reference, filenames[run['name']]))
        # Move all png files to the corresponding folder
        os.makedirs(os.path.join(args.output, run['name'], 'plots'), exist_ok=True)
        for f in os.listdir('.'):
            if f.endswith('.png'):
                shutil.move(f, os.path.join(args.output, run['name'], 'plots', f))

    except Exception as e:
        print('Failed to run', run['name'], e)
