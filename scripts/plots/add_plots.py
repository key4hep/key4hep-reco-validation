import glob
# Add all plots from a folder called plots to the LaTeX template
with open('template.tex', 'ra') as f:
    for p in glob.glob('plots/*.pdf'):
        f.write(r'\includegraphics[width=\textwidth]{' + p + '}')
    f.write(r'\end{document}')
