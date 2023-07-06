# Make the actual web pages for the validation website by filling the templates
# and adding index.html files to the directories

import os
import argparse
import jinja2
import datetime
from collections import defaultdict
import base64
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

metadata = {}
if os.path.exists('metadata.yaml'):
    with open('metadata.yaml') as f:
        metadata = yaml.load(f, Loader=yaml.FullLoader)
if 'key4hep-spack' in metadata:
    metadata['key4hep-spack'] = [metadata['key4hep-spack'], f"https://github.com/key4hep/key4hep-spack/commit/{metadata['key4hep-spack']}"]
if 'spack' in metadata:
    metadata['spack'] = [metadata['spack'], f"https://github.com/spack/spack/commit/{metadata['spack']}"]
for k, v in metadata.items():
    if isinstance(v, str) or len(v) == 1:
        metadata[k] = [v, None]
print(metadata)


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
    svg_files = [os.path.join(folder, 'plots', filename) for filename in os.listdir(os.path.join(folder, 'plots')) if filename.endswith('.svg')]

    # Generate the HTML markup using a Jinja2 template
    template = jinja2.Template('''
    {% for filename in svg_files %}
        <img src="{{ filename }}" />
    {% endfor %}
    ''')
    html = template.render(svg_files=svg_files)

    return html

parser = argparse.ArgumentParser(description='Make the web pages for the validation website')
parser.add_argument('--dest', required=True, help='Destination directory for the web pages', default='.')

args = parser.parse_args()

# Top level folders, maybe different types of validation
top_folders = [folder for folder in os.listdir(args.dest) if os.path.isdir(os.path.join(args.dest, folder))]
top_folders.remove('static')
# latest_modified_date = [get_latest_modified_date(os.path.join(args.dest, folder)) for folder in top_folders]
latest_modified_date = [get_latest_modified_date(os.path.join(args.dest, folder)) for folder in top_folders]
env = jinja2.Environment(loader=jinja2.FileSystemLoader('../templates'))
template = env.get_template('main_index.html')
with open(os.path.join(args.dest, 'index.html'), 'w') as f:
    f.write(template.render(folders=zip(top_folders, latest_modified_date)))

# Now let's put an index.html file in each of the subdirectories and the plot folders
for folder in top_folders:
    print(folder)
    plot_folders = [plot_folder for plot_folder in os.listdir(os.path.join(args.dest, folder)) if os.path.isdir(os.path.join(args.dest, folder, plot_folder))]
    plot_category_names = [FOLDER_NAMES[x] for x in plot_folders]
    template = env.get_template('section_index.html')
    with open(os.path.join(args.dest, folder, 'index.html'), 'w') as f:
        f.write(template.render(plot_sections=zip(plot_folders, plot_category_names), table=metadata))

    for plot_folder in plot_folders:
        template = env.get_template('plot_index.html')
        content = write_plots(os.path.join(args.dest, folder, plot_folder))

        with open(os.path.join(args.dest, folder, plot_folder, 'index.html'), 'w') as f:
            f.write(template.render(content=content))


