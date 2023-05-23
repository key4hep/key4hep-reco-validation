import os
import base64
from jinja2 import Template

# Define the path to the folder containing the PNG images
IMAGES_FOLDER = 'plots'

# Define the path to the output HTML file
OUTPUT_FILE = 'index.html'

def write_plots(folder):
    # Generate a list of the PNG images in the folder
    png_files = [filename for filename in os.listdir(os.path.join(folder, IMAGES_FOLDER)) if filename.endswith('.png')]

    # Generate a base64-encoded data URI for each image
    image_data = {}
    for filename in png_files:
        with open(os.path.join(folder, IMAGES_FOLDER, filename), 'rb') as f:
            png_data = f.read()
        base64_data = base64.b64encode(png_data).decode()
        image_data[filename] = f'data:image/png;base64,{base64_data}'

    # Generate the HTML markup using a Jinja2 template
    template = Template('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PNG plots</title>
    </head>
    <body>
    {% for filename in png_files %}
        <img src="{{ image_data[filename] }}" />
    {% endfor %}
    </body>
    </html>
    ''')
    html = template.render(png_files=png_files, image_data=image_data)

    # Write the HTML to the output file
    with open(os.path.join(folder, OUTPUT_FILE), 'w') as f:
        f.write(html)

for folder in os.listdir('.'):
    if os.path.isdir(folder):
        write_plots(folder)
