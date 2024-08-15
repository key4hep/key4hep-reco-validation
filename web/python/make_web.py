# Make the actual web pages for the validation website by filling the templates
# and adding index.html files to the directories

import os
import argparse
import jinja2
import datetime
from collections import defaultdict
import yaml

class TranslationDict(defaultdict):
    def __missing__(self, key):
        return key

SECTION_NAMES = TranslationDict()
SECTION_NAMES['sim_reco'] = 'Simulation and Reconstruction'

FOLDER_NAMES = TranslationDict()
for k, v in {'track_validation': 'Track Validation',
             'jets': 'Jet Validation',
             'distributions': 'Distributions',}.items():
    FOLDER_NAMES[k] = v

def get_metadata(folder_path):
    metadata = {}
    file = os.path.join(folder_path, 'metadata.yaml')
    if os.path.exists(file):
        with open(file) as f:
            metadata = yaml.load(f, Loader=yaml.FullLoader)
    if 'key4hep-spack' in metadata:
        metadata['key4hep-spack'] = [metadata['key4hep-spack'], f"https://github.com/key4hep/key4hep-spack/commit/{metadata['key4hep-spack']}"]
    if 'spack' in metadata:
        metadata['spack'] = [metadata['spack'], f"https://github.com/spack/spack/commit/{metadata['spack']}"]
    for k, v in metadata.items():
        if isinstance(v, str) or len(v) == 1:
            metadata[k] = [v, None]
    print(metadata)
    return metadata


def get_latest_modified_date(folder_path):
    latest_modified_date = None

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            modified_date = os.path.getmtime(file_path)

            if latest_modified_date is None or modified_date > latest_modified_date:
                latest_modified_date = modified_date

    if latest_modified_date is None:
        latest_modified_date = 0
    latest_modified_date = datetime.datetime.fromtimestamp(int(latest_modified_date))
    return latest_modified_date

def write_plots(folder):
    # Generate a list of the PNG images in the folder
    svg_files = [os.path.join('plots', filename) for filename in os.listdir(os.path.join(folder, 'plots')) if filename.endswith('.svg')]
    print(svg_files)

    # Generate the HTML markup using a Jinja2 template
    template = jinja2.Template('''
    {% for filename in svg_files %} <img src="{{ filename }}" class="plot-container"/>
    {% endfor %}
    ''')
    html = template.render(svg_files=svg_files)

    return html

parser = argparse.ArgumentParser(description='Make the web pages for the validation website')
parser.add_argument('--dest', required=True, help='Destination directory for the web pages', default='.')

args = parser.parse_args()

# detector folders
detector_folders = [folder for folder in os.listdir(args.dest) if os.path.isdir(os.path.join(args.dest, folder))]
detector_folders.remove('static')
# latest_modified_date = [get_latest_modified_date(os.path.join(args.dest, folder)) for folder in top_folders]
version_folders = []
latest_modified_date = []
for folder in detector_folders:
    print(folder)
    versions = [version_folder for version_folder in os.listdir(os.path.join(args.dest, folder)) if os.path.isdir(os.path.join(args.dest, folder, version_folder))]
    version_folders.append(versions)
    dates = [get_latest_modified_date(os.path.join(args.dest, folder, version)) for version in versions]
    latest_modified_date.append(dates)
version_date = [[(v, d) for v, d in zip(version, date)] for version, date in zip(version_folders, latest_modified_date)]

env = jinja2.Environment(loader=jinja2.FileSystemLoader('../templates'))
template = env.get_template('main_index.html')
with open(os.path.join(args.dest, 'index.html'), 'w') as f:
    f.write(template.render(folders=zip(detector_folders, version_date)))

# Now let's put an index.html file in each of the subdirectories and the plot folders
for i_folder, folder in enumerate(detector_folders):
    print("Detector:", folder)
    for version in version_folders[i_folder]:
        print("Version:", version)
        metadata = get_metadata(os.path.join(args.dest, folder, version))
        subsystem_folders = [subsyst for subsyst in os.listdir(os.path.join(args.dest, folder, version)) if os.path.isdir(os.path.join(args.dest, folder, version, subsyst))]
        plot_category_names = [FOLDER_NAMES[x] for x in subsystem_folders]
    
        template = env.get_template('version_index.html')
        with open(os.path.join(args.dest, folder, version, 'index.html'), 'w') as f:
            f.write(template.render(subsystems=zip(subsystem_folders, plot_category_names), table=metadata, version=version, detector_list=zip(detector_folders, version_folders)))

        for subsystem in subsystem_folders:
            print("Subsystem:", subsystem)
            print("Full path:", os.path.join(args.dest, folder, version, subsystem))
            template = env.get_template('plot_index.html')
            content = write_plots(os.path.join(args.dest, folder, version, subsystem))

            with open(os.path.join(args.dest, folder, version, subsystem, 'index.html'), 'w') as f:
                f.write(template.render(content=content, subsystems=subsystem_folders, version=version, subsystem=subsystem, detector_list=zip(detector_folders, version_folders)))