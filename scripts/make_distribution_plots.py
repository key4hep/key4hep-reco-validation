#!/usr/bin/env python3

import ROOT

import numpy as np
import matplotlib.pyplot as plt

import yaml
from yaml.nodes import ScalarNode
import os

from matplotlib_utils import add_table

# Load the implementations of the utility functions
# ROOT.gSystem.Load('libedm4hepRDF.so')
# Load the declarations of the utility functions to make them available for JIT
# compilation
# ROOT.gInterpreter.LoadFile('edm4hep/utils/dataframe.h')

ROOT.EnableImplicitMT()

with open('conf.yaml', 'r') as f:
    try:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    except yaml.YAMLError as exc:
        print(exc)
        exit()

def std(dist):
    return np.std(dist)

def mean(dist):
    return np.mean(dist)

def do_nothing(x):
    return x


class Reader:
    """
    Class to read the files and create the RDataFrames
    """
    def __init__(self, conf):

        self.filenames = set()

        for key, val in conf.items():
            if 'filename' in val:
                self.filenames.add(val['filename'])
            if 'reference' in val:
                self.filenames.add(val['reference'])
        print(f'List of files that will be read {self.filenames}')

    def check_filenames(self):
        for filename in self.filenames:
            if not os.path.exists(filename):
                raise FileNotFoundError

    def get_rdfs(self):
        ls = {}
        for filename in self.filenames:
            ls[filename] = ROOT.RDataFrame('events', filename)
        return ls


class Validator:
    """
    Class to run the validation
    """
    def __init__(self, conf):
        self.conf = conf
        self.groups = {}

    def check_and_parse_conf(self):
        for name in list(self.conf.keys()):
            if name.startswith('template'):
                self.conf.pop(name)

        # Validate the configuration
        required = ['var', 'filename']
        for key, values in self.conf.items():
            if not all([k in values for k in required]):
                print(f'Error parsing configuration, at least one of the fields {required} not found in the configuration for {key}: {values}')

    def run_validation(self):
        self.check_and_parse_conf()

        reader = Reader(self.conf)
        reader.check_filenames()
        rdfs = reader.get_rdfs()

        allfuncs = globals().copy()
        allfuncs.update(locals())

        for name in self.conf:
            print(f'Running validation for {name}')
            filename = self.conf[name]['filename']
            rdf = rdfs[filename]
            varls = self.conf[name]['var']
            if not isinstance(varls, list):
                varls = [varls]
            print(varls)

            if 'filter' in self.conf[name]:
                print('Filtering with', self.conf[name]['filter'])
            data = rdf.AsNumpy(varls) if 'filter' not in self.conf[name] else rdf.Filter(self.conf[name]['filter']).AsNumpy(varls)

            # for col in data:
            #     data[col] = np.concatenate([np.asarray(x) for x in data[col]])

            data_ref = None
            if 'reference' in self.conf[name]:
                data_ref = rdfs[self.conf[name]['reference']].AsNumpy(varls)
                for col in data_ref:
                    data_ref[col] = np.concatenate([np.asarray(x) for x in data_ref[col]])

            if 'function' in self.conf[name]:
                functions = self.conf[name]['function']
            else:
                functions = 'do_nothing'
            if functions in allfuncs:
                func = allfuncs.get(functions)
            else:
                func = eval(functions)
            if 'plot' in self.conf[name]:
                fig, ax = plt.subplots(1, 1, figsize=(3.72, 2.3))
                if self.conf[name]['plot'] == 'hist':
                    to_plot = func(*data.values())
                    ax.hist(to_plot, bins=100, histtype='step', density=True)
                    left = ['Mean', 'Std. Dev', 'Entries']
                    right = f'{to_plot.mean():.2f} {to_plot.std():.2f} {len(to_plot)}'
                    add_table(left, right, ax, [.45, .5, .25, .3], title='New')
                    if data_ref:
                        to_plot = func(*data_ref.values())
                        ax.hist(to_plot, bins=100, histtype='step', density=True)
                        right = f'{to_plot.mean():.2f} {to_plot.std():.2f} {len(to_plot)}'
                        add_table(left, right, ax, [.70, .5, .25, .3], title='Ref')
                    if 'xlabel' in self.conf[name]:
                        ax.set_xlabel(self.conf[name]['xlabel'])
                    if 'ylabel' in self.conf[name]:
                        ax.set_ylabel(self.conf[name]['ylabel'])
                    if 'xlim' in self.conf[name]:
                        ax.set_xlim(self.conf[name]['xlim'])
                    if 'ylim' in self.conf[name]:
                        ax.set_ylim(self.conf[name]['ylim'])

                    fig.savefig(f'{name}.png')


Validator(conf).run_validation()
