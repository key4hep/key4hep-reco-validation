import ROOT
from podio import root_io
import dd4hep as dd4hepModule
from ROOT import dd4hep
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
from matplotlib.colors import SymLogNorm

import argparse
import numpy as np
import os
from dd4hep import Detector
import DDRec



def format_func(value, tick_number):
  N = int(np.round(value / np.pi * 6))
  if N == 0:
    return "0"
  elif N % 6 == 0:  
    if N == 6:
      return r"$\pi$"
    elif N == -6:
      return r"$-\pi$"
    else:
      return r"${0}\pi$".format(N // 6)
  elif N % 3 == 0:
    if N == 3:
      return r"$\pi/2$"
    elif N == -3:
      return r"$-\pi/2$"
    else:
      return r"${0}\pi/2$".format(N // 3)
  elif N % 2 == 0:
    if N == 2:
      return r"$\pi/3$"
    elif N == -2:
      return r"$-\pi/3$"
    else:
      return r"${0}\pi/3$".format(N // 2)
  else:
    if N == 1:
      return r"$\pi/6$"
    elif N == -1:
      return r"-$\pi/6$"
    else:
      return r"${0}\pi/6$".format(N)
    

def count_photons(inputFile):

  # set file reader
  podio_reader = root_io.Reader(inputFile)

  # get detector description for cell id decoding
  theDetector = Detector.getInstance()
  theDetector.fromXML("../Detector_Description/ARC/ARC_standalone_o1_v01.xml")
  idposConv = DDRec.CellIDPositionConverter(theDetector)
  n_evts = len(podio_reader.get("events"))
                  

  ########## Count Photon Hits #########################
  
  # prepare arrays for quantities of interest
  n_ph = np.zeros(n_evts)
  first_hit = np.zeros((2, n_evts))
  ph_theta = []
  ph_phi   = []
  
  # loop over dataset
  for i_evt, event in enumerate(podio_reader.get("events")):

    p = (event.get("MCParticles"))[0]
    mom = ROOT.TVector3(p.getMomentum().x, p.getMomentum().y, p.getMomentum().z)
    first_hit[0,i_evt] = mom.Theta()
    first_hit[1,i_evt] = mom.Phi()

    for i_hit, arc_hit in enumerate(event.get("ArcCollection")):
      particle =  arc_hit.getMCParticle()
      pdgID = particle.getPDG()
      if pdgID == 22 or pdgID == -22:
        n_ph[i_evt] += 1
        cellID = arc_hit.getCellID()
        x = idposConv.position(cellID) 
        ph_theta.append(x.theta())
        ph_phi.append(x.phi())

  return n_ph, first_hit, [ph_theta, ph_phi]
  

def plot_ph_count(n_ph, first_hit, ph_count, args):

  n_evt = len(n_ph)
  print("Number of evts:", n_evt)

  filename = os.path.splitext(os.path.basename(args.inputFile))[0] # removes path and extension
  if args.outputPath[-1] != '/':
    args.outputPath += '/'
  output_start = args.outputPath + filename 


  # photon count vs. theta

  fig1, ax1 = plt.subplots(figsize=(8,6))
  nbins=90
  hist, bin_edges = np.histogram(ph_count[0], bins=nbins, range=(0, np.pi))
  if not args.no_norm:
    hist = hist.astype(float)/n_evt
  ax1.bar(bin_edges[:-1], hist, width=np.diff(bin_edges),
          color='lightblue', edgecolor='black', align='edge')
  ax1.set_xlabel(r'Polar angle $\theta$')
  ax1.set_ylabel(f'Photon count / {np.pi/nbins:.2f} rad')
  ax1.set_yscale('log')
  ax1.xaxis.set_major_locator(MultipleLocator(np.pi / 6))
  ax1.xaxis.set_major_formatter(FuncFormatter(format_func))
  
  if not args.no_save:
    fig1.savefig(output_start+'_phCount_theta.png', bbox_inches='tight')
  if args.no_show:
    plt.close(fig1)


  # photon count vs. theta and phi

  fig2, ax2 = plt.subplots(figsize=(8,6))
  nbins_theta = 90
  nbins_phi = 36
  hist, x_edges, y_edges = np.histogram2d(ph_count[0], ph_count[1],
                                          bins=[nbins_theta, nbins_phi], 
                                          range=((0, np.pi), (-np.pi, np.pi)))
  vmax=1e4
  lim=1
  if not args.no_norm:
    hist = hist.astype(float)/n_evt
    vmax/=n_evt
    lim/=n_evt
  img = plt.imshow(hist.T, origin='lower', extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]],
                   aspect='auto', cmap='viridis', norm=SymLogNorm(vmin=0, vmax=vmax, linthresh=lim))
  cbar = plt.colorbar(img, ax=ax2)
  cbar.set_label(rf'Counts / {np.pi/nbins_theta:.2f} rad ($\theta$) / {2*np.pi/nbins_phi:.2f} rad ($\phi$) ')
  
  ax2.set_xlabel(r'Polar angle $\theta$')
  ax2.set_ylabel(r'Azimuthal angle $\phi$')
  ax2.set_title('Photon Count')
  ax2.xaxis.set_major_locator(MultipleLocator(np.pi / 6))
  ax2.xaxis.set_major_formatter(FuncFormatter(format_func))
  ax2.yaxis.set_major_locator(MultipleLocator(np.pi / 6))
  ax2.yaxis.set_major_formatter(FuncFormatter(format_func))

  if not args.no_save:
    fig2.savefig(output_start+'_phCount_thetaphi.png', bbox_inches='tight')
  if args.no_show:
    plt.close(fig2)

  
  # number of photons per evt

  fig3, ax3 = plt.subplots(figsize=(8,6))
  nbins=50
  ax3.hist(n_ph, bins=nbins, range=(0, 250),
           color='lightblue', edgecolor='black')
  ax3.set_xlabel('Number of photons')
  ax3.set_ylabel(f'Photon count / 5')
  ax3.set_yscale('log')
  
  if not args.no_save:
    fig3.savefig(output_start+'_phCount_Nph.png', bbox_inches='tight')
  if args.no_show:
    plt.close(fig3)

  
  # photon count vs. theta of first hit

  fig4, ax4 = plt.subplots(figsize=(8,6))
  nbins=90
  hist, bin_edges = np.histogram(first_hit[0], bins=nbins, range=(0, np.pi), weights=n_ph)
  if not args.no_norm:
    hist = hist.astype(float)/n_evt
  ax4.bar(bin_edges[:-1], hist, width=np.diff(bin_edges),
          color='lightblue', edgecolor='black', align='edge')
  ax4.set_xlabel(r'Polar angle $\theta$ of primary particle')
  ax4.set_ylabel(f'Photon count / {np.pi/nbins:.2f} rad')
  ax4.set_yscale('log')
  ax4.xaxis.set_major_locator(MultipleLocator(np.pi / 6))
  ax4.xaxis.set_major_formatter(FuncFormatter(format_func))
  
  if not args.no_save:
    fig4.savefig(output_start+'_phCount_theta_1stHit.png', bbox_inches='tight')
  if args.no_show:
    plt.close(fig4)


  # photon count vs. theta and phi of first hit

  fig5, ax5 = plt.subplots(figsize=(8,6))
  nbins_theta = 90
  nbins_phi = 36
  hist, x_edges, y_edges = np.histogram2d(first_hit[0], first_hit[1],
                                          bins=[nbins_theta, nbins_phi], 
                                          range=((0, np.pi), (-np.pi, np.pi)),
                                          weights=n_ph)
  vmax=1e4
  lim=1
  if not args.no_norm:
    hist = hist.astype(float)/n_evt
    vmax/=n_evt
    lim/=n_evt
  img = plt.imshow(hist.T, origin='lower', extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]],
                   aspect='auto', cmap='viridis', norm=SymLogNorm(vmin=0, vmax=vmax, linthresh=lim))
  cbar = plt.colorbar(img, ax=ax5)
  cbar.set_label(rf'Counts / {np.pi/nbins_theta:.2f} rad ($\theta$) / {2*np.pi/nbins_phi:.2f} rad ($\phi$) ')
  
  ax5.set_xlabel(r'Polar angle $\theta$ of primary particle')
  ax5.set_ylabel(r'Azimuthal angle $\phi$ of primary particle')
  ax5.set_title('Photon Count')
  ax5.xaxis.set_major_locator(MultipleLocator(np.pi / 6))
  ax5.xaxis.set_major_formatter(FuncFormatter(format_func))
  ax5.yaxis.set_major_locator(MultipleLocator(np.pi / 6))
  ax5.yaxis.set_major_formatter(FuncFormatter(format_func))

  if not args.no_save:
    fig5.savefig(output_start+'_phCount_thetaphi_1stHit.png', bbox_inches='tight')
  if args.no_show:
    plt.close(fig5)


  else:
    plt.show()
  

#########################################################################

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
        description="Process simulation"
    )
  parser.add_argument('-f', "--inputFile",  type=str, 
                      help='The name of the simulation file to be processed', default='arc_pi+_50GeV.root')
  parser.add_argument('-o', "--outputPath", type=str, 
                      help='The name of the directory where to save output files', default='./')
  parser.add_argument("--no_save", action='store_true', help='Do not save output arrays')
  parser.add_argument("--no_show", action='store_true', help='Do not plot output histograms')
  parser.add_argument("--no_norm", action='store_true', help='Do not normalize output histograms by number of events')
  
  args = parser.parse_args()
    
  n_ph, first_hit, ph_count = count_photons(args.inputFile)
  ph_presence = (len(ph_count[0]) != 0)
  
  if not(args.no_save and args.no_show):
    if ph_presence:
      plot_ph_count(n_ph, first_hit, ph_count, args)
  
  print(ph_presence)  
  
  
  
  
  
