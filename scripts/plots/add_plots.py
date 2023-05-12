# Add all plots from a folder called plots to the LaTeX template
import glob
with open('template.tex', 'a') as f:
    plots = glob.glob('plots/*.pdf')
    jet_plots = []
    tracking_plots = []
    for p in list(plots):
        if p.startswith('jet-'):
            jet_plots.append(p)
            plots.remove(p)
        if p.startswith('tracking-'):
            tracking_plots.append(p)
            plots.remove(p)
    for p in sorted(glob.glob('plots/*.pdf')):
        f.write(fr'\includegraphics[width=\textwidth]{{{p}}}' + '\n')

    if tracking_plots:
        f.write(r'\newpage\section{Tracking plots}' + '\n')
    for p in tracking_plots:
        f.write(fr'\includegraphics[width=0.8\textwidth]{{{p}}}' + '\n')

    if jet_plots:
        f.write(r'\newpage\section{Jet plots}' + '\n')
    for p in jet_plots:
        f.write(fr'\includegraphics[width=0.8\textwidth]{{{p}}}' + '\n')

    f.write(r'\end{document}')
