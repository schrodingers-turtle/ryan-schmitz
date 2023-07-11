"""Get signal-like events from the CSV files.

Signal-like (in this script): Exactly 4 hits in a row (single module & 4
layers) and all hits < 50 NPE.

Careful - will overwrite existing output (per the behavior of
`pandas.DataFrame.to_csv`)!

TODO: There can be duplicate `eventID`s from different files. Adding
something like a file id would make it possible to distinguish the two
events.

Created 7 July 2023.
"""
from datetime import datetime
import os
import multiprocessing

import pandas as pd


def make_cuts(s):
    """Make cuts to keep only signa-like events.

    :param s: `pandas.DataFrame` in the format of a ScintRHits.csv
    (output of use_rootaway.py).
    """
    # Maximum of 50 NPE for every slab in an event.
    # Uses our new, tentative, relationship for energy deposit/NPE.
    s = make_a_cut(s, s.groupby('eventID').EDep_MeV.max() < 50 * 1.24e-3)

    # Exactly four hits total.
    s = make_a_cut(s, s.groupby('eventID').size() == 4)

    # All four layers.
    s['layerNo'] = (s.copyNo - 18) % 4
    s = make_a_cut(s, s.groupby('eventID').layerNo.nunique() == 4)

    # Only one module (all slabs in a row).
    s['moduleNo'] = (s.copyNo - 18) // 4
    s = make_a_cut(s, s.groupby('eventID').moduleNo.nunique() == 1)

    return s


def process_file(path):
    """Read and cut a file, and keep track of the total number of events.
    This function is given to `multiprocessing`."""
    print(f"Reading and cutting {path}")

    file = pd.read_csv(path)
    cut_file = make_cuts(file)
    num_events = file.eventID.nunique()

    return cut_file, num_events


def process_folder(
    folder='/net/cms26/cms26r0/anson/noPhotons',
    save='cut_ScintRHits.csv'
):
    """Load all files in the `folder`, cut them, and combine them into one
    `DataFrame`.
    
    If a file already exists at the save path (`folder` + `save`), it will be
    overwritten, per the behavior of `pandas.DataFrame.to_csv`!

    Uses `multiprocessing`.
    """
    available_cores = os.sched_getaffinity(0)
    num_cores = len(available_cores)

    print(f"Starting at: {datetime.now()}")
    print(f"{num_cores} available cores: {available_cores}")

    filepaths = [os.path.join(folder, subfolder, 'ScintRHits.csv')
                 for subfolder in next(os.walk(folder))[1]
                 if subfolder.startswith('cosmicdir')]

    with multiprocessing.Pool(num_cores) as pool:
        results = pool.map(process_file, filepaths)

    full_df = pd.concat(r[0] for r in results)
    num_events = sum(r[1] for r in results)

    if save:
        savepath = os.path.join(folder, save)
        full_df.to_csv(savepath, index=False)

    return full_df, num_events


def make_a_cut(df, eventID_bool):
    """Make a single cut.
    
    I.e., return a `DataFrame` like `df`, but only with the entries with
    `eventID`s  that correspond to `True` in the `pandas.Series`
    `eventID_bool`."""
    eventID_list = eventID_bool.index[eventID_bool] 
    return df[df.eventID.isin(eventID_list)]


df, num_events = process_folder()
print(df)
print(f"{num_events} events in total.")
