# Add all plots from a folder called plots to the LaTeX template
import glob
with open('template.tex', 'a') as f:
    for p in sorted(glob.glob('plots/*.pdf')):
        f.write(fr'\includegraphics[width=\textwidth]{{{p}}}' + '\n')
    f.write(r'\end{document}')
