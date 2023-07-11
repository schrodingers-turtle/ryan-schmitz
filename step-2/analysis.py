"""Analyze the data (after the cuts).

TODO: Forgot to turn up the `dpi` of the plot before sending it to Ryan.

Created 8 July 2023."""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

print("Finished imports.")

# plt.style.use('ggplot')

df = pd.read_csv('cut_ScintRHits.csv')
print("Read CSV.")

# Uses our tentative relationship for energy deposit/NPE.
df['EquivalentNPE'] = df.EDep_MeV / 1.24e-3

# Only plot slab hits with NPE or energy deposit not zero or negative.
positive_NPE = df.EquivalentNPE[df.EquivalentNPE > 0]

# ax = positive_NPE.hist(bins=20)
ax = sns.histplot(positive_NPE, bins=25)
print("Made histogram.")

ax.set_title("Nonzero $N_{PE}$ equivalent in individual slabs\nin non-muon-like, 4-in-a-row events", fontsize=11)
ax.set_xlabel('$N_{PE}$ equivalent from a slab')
subtitle = "milliQan"
ax.text(0.99, 0.98, subtitle, transform=ax.transAxes, fontweight='bold', fontsize=13,
        verticalalignment='top', horizontalalignment='right')
subtitle2 = "from ~111 million muon events"
ax.text(0.99, 0.86, subtitle2, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='right')
subtitle3 = (
    r"$\bullet \ N_{PE} < 50$ for all hits in each event" + '\n'
    r"$\bullet$ Exactly 4 hits in a row in each event" + '\n'
    r"$\bullet$ Ignore hits with $N_{PE} \approx 0$" + '\n'
)
ax.text(0.33, 0.76, subtitle3, transform=ax.transAxes, fontsize=7.7,
        verticalalignment='top', horizontalalignment='left')

fig = ax.get_figure()
fig.tight_layout()
fig.savefig('scratch.png')
