# Run all the plotting scripts and move the output to the correct folder
# Expects the current plots to be in the current directory while the reference
# plots are in the directory passed with --reference

import argparse
import importlib
import os
import shutil
import logging

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('plots', nargs='+')
arg_parser.add_argument('--reference', required=True)
arg_parser.add_argument('--output', required=True)
arg_parser.add_argument('--debug', action='store_true')
args = arg_parser.parse_args()

modules = {'jets': 'make_jet_plots',
           'hists': 'make_distribution_hists',
           }
filenames = {'jets': 'jet_study.root',
             'hists': 'histograms.root',
             }

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

to_run = []
for k, module in modules.items():
    if k in args.plots:
        imported = importlib.import_module(module)
        to_run.append({'name': k, 'function': imported.main})
        if args.debug:
            logging.debug(f'Will run "{k}" with "{module}"')
        args.plots.remove(k)
print(f'The following arguments were not recognized: {args.plots}')


for run in to_run:
    try:
        logging.debug(f'Running "{run["name"]}" with file "{filenames[run["name"]]}"')
        run['function'](filenames[run['name']], os.path.join(args.reference, filenames[run['name']]))
        # Move all png files to the corresponding folder
        os.makedirs(os.path.join(args.output, run['name'], 'plots'), exist_ok=True)
        for f in os.listdir('.'):
            if f.endswith('.svg'):
                shutil.move(f, os.path.join(args.output, run['name'], 'plots', f))

    except Exception as e:
        print('Failed to run:', run['name'], e)
