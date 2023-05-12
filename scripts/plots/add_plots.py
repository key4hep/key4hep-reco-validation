import glob
# Add all plots from a folder called plots to the LaTeX template
with open('template.tex', 'a') as f:
    for p in glob.glob('plots/*.pdf'):
        f.write(fr'\includegraphics[width=\textwidth]{{{p}}}' + '\n')
    f.write(r'\end{document}')
