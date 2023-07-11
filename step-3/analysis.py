"""Analyze the data (after the cuts).

This is a modified copy of step-2/analysis.py.

Caution:
 - Event counts in plot text labels need to be updated by hand.
 - Check all plot and text contents before uncommenting and using
 alternative plot styles.

Comment out the call to `make_plot_data` to speed things up (useful for making
small changes to the plot style, etc. and seeing the results fast.)

TODO: ARK about 4 themes (maybe experiment by giving Ryan transparent version,
 and also ask him)
TODO: Ask Ryan about negative energy deposits and resulting negative NPE
 ratios.
TODO: Also ask Ryan, and think about:
 - Replacing "muon" with the Greek letter mu
 - Bin sizes

TODO: Possible things to update:
 - Different plot colors

Created 8 July 2023."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

print("Finished imports.")

# plt.style.use('ggplot')


def make_plot_data(s):
    """Do the analysis and make the data for the plots.

    This only takes 10 seconds or so, but it's nice to not have to wait that
    long every time a change to a plot is made.

    :param s: `DataFrame` in the format of cut_ScintRHits.csv.
    """

    # Only one module (all slabs in a row).
    # This really cuts down the number of events, so that the "statistics are poor."
    # s['moduleNo'] = (s.copyNo - 18) // 4
    # s = make_a_cut(s, s.groupby('uniqueEventID').moduleNo.nunique() == 1)

    # Calibrate the hit times
    # (relative to a particle at light speed coming from the IP).
    # The measured distance of the length of the detector (from Ryan) is
    # 3.4 meters, or 11.3 light-nanoseconds.
    s['relativeHitTime_ns'] = s.hitTime_ns - s.layerNo * (11.3 / 3)

    event = s.groupby('uniqueEventID')

    NPE_ratio = event.EDep_MeV.max() / event.EDep_MeV.min()

    # Calculate delta_t_max as described in the TDR.
    max_time_hit = s.iloc[event.relativeHitTime_ns.idxmax()].set_index('uniqueEventID')
    min_time_hit = s.iloc[event.relativeHitTime_ns.idxmin()].set_index('uniqueEventID')
    delta_t_max = (
        max_time_hit.relativeHitTime_ns - min_time_hit.relativeHitTime_ns
    ) * np.sign(max_time_hit.layerNo - min_time_hit.layerNo)

    # An alternative method for calculating time differences between hits.
    # layers = [s[s.layerNo == i].set_index('uniqueEventID') for i in (0, 1, 2, 3)]
    # t0, t1, t2, t3 = (layer.relativeHitTime_ns for layer in layers)

    # # Make the NPE/energy deposit ratio cut.
    # # NPE_ratio_per_event = g.EDep_MeV.max() / g.EDep_MeV.min()  TODO
    # s_without_timing_cut = make_a_cut(s, NPE_ratio < 10)
    #
    # # Make the timing cut.
    # # delta_t_max = g.relativeHitTime_ns.max() - g.relativeHitTime_ns.min()  TODO
    # s_without_ratio_cut = make_a_cut(s, (-15 < delta_t_max) & (delta_t_max < 45))

    # TODO: save CSVs

    return NPE_ratio, delta_t_max


def plot_NPE(s):
    """Plot the distribution of NPE in individual slabs, as in step 2, but with
    the new, less restrictive cut."""
    # Uses our tentative relationship for energy deposit/NPE.
    s['equivalentNPE'] = s.EDep_MeV / 1.24e-3

    # Mini-cut for plot slab hits with NPE or energy deposit not zero or negative.
    s = s[s.equivalentNPE > 0]

    print(f"{s.uniqueEventID.nunique()} events and {len(s)} hits in the nonzero NPE plot.")

    # Make the plot.

    fig, ax = histogram_with_error_bars(s.equivalentNPE,
                                        bin_size=1/2,
                                        min=0,
                                        max=50,
                                        color='tab:red')

    ax.set_title("Nonzero $N_{PE}$ equivalent in individual slabs\nin non-muon-like, 1-per-layer events", fontsize=10.5)
    ax.set_xlabel('$N_{PE}$ equivalent')
    subtitle = "milliQan"
    ax.text(0.99, 0.98, subtitle, transform=ax.transAxes, fontweight='bold', fontsize=13,
            verticalalignment='top', horizontalalignment='right')

    subtitle2 = r"$\approx 23000$ of $10^9$ simulated muon events"

    # Same size subtitles. (Check subtitle content before using.)
    # subtitle3 = (
    #      subtitle2 + '\n'
    #     r"$N_{PE} < 50$ for all hits in each event $\bullet$" + '\n'
    #     r"Exactly 4 hits in a row in each event $\bullet$" + '\n'
    #     r"Ignore hits with $N_{PE} \approx 0$ $\bullet$" + '\n'
    # )
    # ax.text(0.99, 0.86, subtitle3, transform=ax.transAxes, fontsize=7.7,
    #         verticalalignment='top', horizontalalignment='right')
    # ax.legend(loc=(0.765, 0.45), fontsize=9)

    # Big subtitle 2.
    ax.text(0.99, 0.86, subtitle2, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right')
    subtitle3 = (
        r"($23000 \times 4 \approx 93000$ hits)" + '\n'
        r"$N_{PE} < 50$ for all hits in each event $\bullet$" + '\n'
        r"Exactly 1 hit per layer in each event $\bullet$" + '\n'
        r"Ignoring hits with $N_{PE} \approx 0$ $\bullet$" + '\n'
    )
    ax.text(0.99, 0.76, subtitle3, transform=ax.transAxes, fontsize=7.7,
            verticalalignment='top', horizontalalignment='right')
    # Legend position for subtitle 2 + shorter subtitle 3.
    ax.legend(loc=(0.77, 0.32), fontsize=9)

    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig('scratch-NPE.png')


def plot_delta_t_max(NPE_ratio, delta_t_max):
    """Make a histogram of delta_t_max after all other cuts (except 4-in-a-row
    and veto cuts.)"""
    # Cut for NPE (or energy deposit) max/min < 10.
    good_NPE_ratio_eventIDs = NPE_ratio.index[NPE_ratio < 10]
    cut_delta_t_max = delta_t_max[good_NPE_ratio_eventIDs]

    print(f"{len(cut_delta_t_max)} events in the delta_t_max plot.")

    fig, ax = histogram_with_error_bars(cut_delta_t_max,
                                        bin_size=2,
                                        min=-50,
                                        max=50,
                                        color='tab:orange')

    ax.set_title(r"$\Delta t_{max}$ of signal-like cosmic muon events", fontsize=11)
    ax.set_xlabel(r"$\Delta t_{max}$ (ns)")
    subtitle = "milliQan"
    ax.text(0.98, 0.98, subtitle, transform=ax.transAxes, fontweight='bold', fontsize=13,
            verticalalignment='top', horizontalalignment='right')

    # Alternative style
    # subtitle2 = "from ~1 billion muon events"
    # ax.text(0.99, 0.87, subtitle2, transform=ax.transAxes, fontsize=9.5,
    #         verticalalignment='top', horizontalalignment='right')
    # subtitle3 = (
    #      "Only including events with:\n"
    #     r"$N_{PE} < 50$ for all hits $\bullet$" + '\n'
    #     r"Exactly 1 hit per layer $\bullet$" + '\n'
    #     r"$N_{PE}$ max/min < 10 $\bullet$" + '\n'
    # )

    # Alternative style
    # ax.text(0.99, 0.77, subtitle3, transform=ax.transAxes, fontsize=7.7,
    #         verticalalignment='top', horizontalalignment='right')
    # subtitle2 = "1733 of $10^9$ simulated events with"
    # ax.text(0.99, 0.86, subtitle2, transform=ax.transAxes, fontsize=9.1,
    #         verticalalignment='top', horizontalalignment='right')

    subtitle3 = (
        r"$\approx 14000$ of $10^9$ events with" + '\n'  # TODO: "simulated"?
        r"$N_{PE} < 50$ for all hits $\bullet$" + '\n'
        r"Exactly 1 hit per layer $\bullet$" + '\n'
        r"$N_{PE}$ max/min$< 10$ $\bullet$" + '\n'
    )
    ax.text(0.97, 0.86, subtitle3, transform=ax.transAxes, fontsize=7.7,
            verticalalignment='top', horizontalalignment='right')
    ax.legend(loc=(0.765, 0.45), fontsize=9)

    fig.tight_layout()
    fig.savefig('scratch-delta.png')


def plot_NPE_ratio(NPE_ratio, delta_t_max):
    """Make a histogram of the NPE_ratio after all other cuts (except
    4-in-a-row and veto cuts)."""
    # Cut for -15 ns < delta_t_max < 45 ns.
    good_delta_t_max_eventIDs = delta_t_max.index[(-15 < delta_t_max) & (delta_t_max < 45)]
    cut_NPE_ratio = NPE_ratio[good_delta_t_max_eventIDs]

    print(f"{len(cut_NPE_ratio)} events in the NPE ratio plot.")

    fig, ax = histogram_with_error_bars(cut_NPE_ratio,
                                        bin_size=1/2,
                                        min=0,
                                        max=45,
                                        color='tab:green')  # TODO: Decide whether to show negative values.

    ax.set_title("$N_{PE}$ max/min of signal-like cosmic muon events", fontsize=10.4)
    ax.set_xlabel(r"$N_{PE}$ equivalent max/min")
    subtitle = "milliQan"
    ax.text(0.99, 0.98, subtitle, transform=ax.transAxes, fontweight='bold', fontsize=13,
            verticalalignment='top', horizontalalignment='right')

    # subtitle2 = "$39000$ of $10^9$ events with"
    # ax.text(0.99, 0.86, subtitle2, transform=ax.transAxes, fontsize=9.5,
    #         verticalalignment='top', horizontalalignment='right')
    # Old legend location that goes with this subtitle.
    # ax.legend(loc=(0.77, 0.39), fontsize=9)

    subtitle3 = (
        r"$\approx 12000$ of $10^9$ events with" + '\n'
        r"$N_{PE} < 50$ for all hits $\bullet$" + '\n'
        r"Exactly 1 hit per layer $\bullet$" + '\n'
        r"$-15$ ns$< \Delta t_{max} < 45$ ns $\bullet$" + '\n'
    )
    ax.text(0.99, 0.86, subtitle3, transform=ax.transAxes, fontsize=7.7,
            verticalalignment='top', horizontalalignment='right')

    ax.legend(loc=(0.765, 0.45), fontsize=9)

    # Alternative style of subtitle 3 - with a bbox around it
    # subtitle3 = (  # TODO
    #     "$35000$ of $10^9$ events with\n"
    #     r"$\bullet$ $N_{PE} < 50$ for all hits" + '\n'
    #     r"$\bullet$ Exactly 1 hit per layer" + '\n'
    #     r"$\bullet$ $-15$ ns$< \Delta t_{max} < 45$ ns"
    # )
    # # ax.text(0.96, 0.83, subtitle3, transform=ax.transAxes, fontsize=7.7,
    # #         verticalalignment='top', horizontalalignment='right',
    # #         bbox={'edgecolor': 'lightgray', 'facecolor': 'none', 'boxstyle': 'round'})
    # ax.text(0.53, 0.5, subtitle3, transform=ax.transAxes, fontsize=7.7,
    #         verticalalignment='center', horizontalalignment='left',
    #         bbox={'edgecolor': 'lightgray', 'facecolor': 'none', 'boxstyle': 'round'})
    # ax.legend(loc=(0.77, 0.68), fontsize=9)


    fig.tight_layout()
    fig.savefig('scratch-ratio.png')


def histogram_with_error_bars(x, bin_size, min, max, color='tab:purple'):
    """TODO"""
    bins = np.arange(min, max + bin_size, bin_size)

    fig, ax = plt.subplots(figsize=(4, 3), dpi=200)

    x = x[(min < x) & (x < max)]
    sns.histplot(x=x, bins=bins, ax=ax, edgecolor=None, color=color)
    print("Made histogram.")

    error_bar_type = 'notCRC'
    histogram_counts, _ = np.histogram(x, bins)
    histogram_error = 2*np.sqrt(histogram_counts)  # x2 sigma; TODO decide on this permanently

    # Add error bars (lines) on top of the seaborn histogram.
    if error_bar_type == 'CRC':
        bin_midpoints = (bins[:-1] + bins[1:])/2
        ax.errorbar(bin_midpoints, histogram_counts, yerr=histogram_error,
                    fmt='none', color='tab:red', alpha=0.7)

    else:
        # Add error bars (transparent bars) on top of the seaborn histogram.
        # The first four lines allow the error to be the same shape as the
        # `bins` (the values of the entries appended to the errors do not
        # affect the final output).
        std_top = histogram_counts + histogram_error
        std_bottom = histogram_counts - histogram_error
        std_top = np.append(std_top, 0)
        std_bottom = np.append(std_bottom, 0)
        ax.fill_between(bins,
                        std_bottom,
                        std_top,
                        # facecolor='none',
                        facecolor='tab:gray',
                        edgecolor='black',
                        linewidth=0,
                        step='post',
                        alpha=0.35,
                        hatch='/////',
                        label='2$\sigma$')

    ax.set_xlim(min, max)
    ax.set_ylim(0, ax.get_ylim()[1])

    ax.legend(loc=(0.77, 0.39), fontsize=9)

    return fig, ax


def read_csv_series(*args, **kwargs):
    """Utility for reading `pandas.DataFrame.Series` that were saved to CSV
    files via `to_csv` (without any other arguments).

    The standard `pandas.read_csv` returns a `DataFrame` instead of a
    `Series`. This function also works for turning any CSV files with two
    columns into a `Series`."""
    df = pd.read_csv(*args, **kwargs)
    series = df.set_index(df.columns[0])[df.columns[1]]
    return series


s = pd.read_csv('cut_ScintRHits_v2.csv')

# Uncomment to write plot data to files.
NPE_ratio, delta_t_max = make_plot_data(s)
pd.DataFrame({'NPE_ratio': NPE_ratio}).to_csv('NPE_ratio.csv')
pd.DataFrame({'delta_t_max': delta_t_max}).to_csv('delta_t_max.csv')
print(f"Wrote plot data to files.")

# Load plot data from files.
NPE_ratio = read_csv_series('NPE_ratio.csv')
delta_t_max = read_csv_series('delta_t_max.csv')

plot_NPE(s)
plot_delta_t_max(NPE_ratio, delta_t_max)
plot_NPE_ratio(NPE_ratio, delta_t_max)
