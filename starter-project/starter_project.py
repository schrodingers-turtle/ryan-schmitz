"""The starter project assigned to me by Ryan Schmitz.

Created and finished 4 July 2023.

Note: Some files may have been moved from /homes/anson/ to /net/cms26/cms26r0/anson/.

Add up the total energy deposit and PMT hits for each slab, and analyze the results.

TODO: Tone down the maximum length of these lines of code.
"""
import ROOT
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import linregress

# Load shared libraries (both are necessary)
ROOT.gInterpreter.ProcessLine('#include "/homes/anson/milliQanSim/include/mqROOTEvent.hh"')
ROOT.gSystem.Load('/homes/anson/milliQanSim/build/libMilliQanCore.so')

# These do not work:
# ROOT.gInterpreter.ProcessLine('#include "/net/cms17/cms17r0/schmitz/milliQanSim/include/mqROOTEvent.hh"')
# ROOT.gInterpreter.AddIncludePath('/net/cms17/cms17r0/schmitz/milliQanSim/include')
# ROOT.gInterpreter.AddIncludePath('/homes/anson/milliQanSim/include')
#
# Only the new version of the headers (e.g. mqROOTEvent.hh), i.e. the ones on GitHub and in
# /homes/anson/milliQanSim, work correctly. The old ones in /net/cms17/cms17r0/schmitz/milliQanSim
# do not. Also, I'm not able to get `AddIncludePath` to work, but `ProcessLine` works.

file = ROOT.TFile('/net/cms17/cms17r0/schmitz/slabSimMuon/withPhotons/48slab/cosmicdir1/MilliQan.root')
tree = file.Get('Events')


def read_root(save_csv=True):
    """Read data in from ROOT and save what we want to a Pandas `DataFrame`.
    
    :save: If `True`, save the `DataFrame`s to CSV files."""
    energy_df = []
    PMT_df = []

    for i, event in enumerate(tree):
        print(f"Reading event {i + 1} from the ROOT file.")

        for hit in event.ScintRHits:
            energy_df.append({'slab_number': hit.GetCopyNo(), 'energy': hit.GetEDep()})

        for hit in event.PMTHits:
            PMT_df.append({'PMT_number': hit.GetPMTNumber()})
    
    energy_df = pd.DataFrame(energy_df)
    PMT_df = pd.DataFrame(PMT_df)
    
    if save_csv:
        energy_df.to_csv('energy.csv', index=False)
        PMT_df.to_csv('PMT.csv', index=False)

    return energy_df, PMT_df


def read_csvs():
    """Just read in the data that we saved in CSV files."""
    return pd.read_csv('energy.csv'), pd.read_csv('PMT.csv')


def analyze(energy_df, PMT_df):
    """Analyze the data."""
    energy_per_slab = energy_df.groupby('slab_number').sum()
    NPE_per_PMT = PMT_df.groupby('PMT_number').size()

    # Add NPE for pairs of PMTs
    array = NPE_per_PMT.to_numpy()
    NPE_per_slab = array[::2] + array[1::2]

    results = energy_per_slab
    results['NPE'] = NPE_per_slab

    print(results)

    # Print out the slope and intercept (and their errors) of the line of best fit.
    best_fit = linregress(results.NPE, results.energy)
    print(best_fit)

    # Make a plot.

    # Divide NPE by 1000 for the plot.
    plot_df = results.copy()
    plot_df.NPE /= 1000

    # These numbers were obtained from the output of this script.
    best_fit_text = f"slope = $(1.24 \pm 0.11)$ keV per PE\nintercept = $-47$ MeV"

    ax = sns.regplot(data=plot_df, x='NPE', y='energy', marker='x',
                     label="slab data by copy #", scatter_kws={'zorder': 2},
                     line_kws={'label': best_fit_text, 'color': 'dimgray', 'zorder': 1})
    fig = ax.get_figure()
    fig.set_size_inches(5 * np.array([4, 3])/4)
    fig.set_dpi(175)
    ax.set_title(r"Total scintillator energy deposit vs. total $N_{PE}$ for each slab",
                 fontsize=10.5)
    ax.set_xlabel(r"$N_{PE}$ (in 1000s)")
    ax.set_ylabel(r"energy deposit (MeV)")

    subtitle = "milliQan"
    ax.text(0.01, 0.98, subtitle, fontsize=10.5, fontweight='bold', verticalalignment='top',
            transform=ax.transAxes)

    # Label each point on the plot.
    for slab_number, row in plot_df.iterrows():
        # text = f"{slab_number} (copy #)" if slab_number == 18 else slab_number
        text = slab_number
        xy = np.array([row.NPE, row.energy])
        ax.annotate(text, xy, xy+(3.75, 0), fontsize=8, alpha=0.8, verticalalignment='center', zorder=3)

    legend = ax.legend(loc='lower right')

    # Reverse legend order.
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='lower right', fontsize=9.5)


    fig.tight_layout()
    fig.savefig('energy_vs_NPE.png')


# Uncomment to read the ROOT file and create CSV files.
# energy_df, PMT_df = read_root(save_csv=True)

# Uncomment to read in CSV files that were saved.
energy_df, PMT_df = read_csvs()

# Analyze the data.
analyze(energy_df, PMT_df)
