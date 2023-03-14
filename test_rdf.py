#!/usr/bin/env python3

import ROOT

import numpy as np
import matplotlib.pyplot as plt

import yaml
import os

# Load the implementations of the utility functions
# ROOT.gSystem.Load('libedm4hepRDF.so')
# Load the declarations of the utility functions to make them available for JIT
# compilation
# ROOT.gInterpreter.LoadFile('edm4hep/utils/dataframe.h')

ROOT.EnableImplicitMT()

with open('conf.yaml', 'r') as f:
    try:
        conf = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(exc)
        exit()


def std(dist):
    return np.std(dist)


def mean(dist):
    return np.mean(dist)


def do_nothing(x):
    return x


class Validator:
    def __init__(self, conf):
        self.conf = conf
        self.groups = {}

    def check_and_parse_conf(self):
        names = self.conf.keys()
        for name in names:
            if 'template' in self.conf[name]:
                templates = self.conf[name]['template']
                if not isinstance(templates, list):
                    templates = [templates]
                templates = templates[::-1]
                for t in templates:
                    for key in self.conf[t]:
                        if key not in self.conf[name]:
                            self.conf[name][key] = self.conf[t][key]

        # Delete the templates
        names = list(self.conf.keys())
        for name in names:
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

            data = rdf.AsNumpy(varls)
            for col in data:
                data[col] = np.concatenate([np.asarray(x) for x in data[col]])

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
                    print(len(data))
                    ax.hist(func(*data.values()), bins=100, histtype='step')
                    if data_ref:
                        ax.hist(func(*data_ref.values()), bins=100, histtype='step')
                    if 'xlabel' in self.conf[name]:
                        ax.set_xlabel(self.conf[name]['xlabel'])
                    if 'ylabel' in self.conf[name]:
                        ax.set_ylabel(self.conf[name]['ylabel'])
                    fig.savefig(name)


class Reader:
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

Validator(conf).run_validation()
