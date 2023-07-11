"""Get signal-like events from the CSV files.

This is version 1, used for the plots shown in the Monday 10 July group
meeting. It does NOT aggregate energy deposits (EDep_MeV) or hit times
(hitTime_ns) per slab per event.

Similar to step-2/cuts.py, but modified for the next steps, of course.

Signal-like (in this script): Exactly 1 hit per layer and all hits < 50 NPE.

Careful - will overwrite existing output (per the behavior of
`pandas.DataFrame.to_csv`)!

Created 8 July 2023.
Last modified 9 July 2023.
"""
from datetime import datetime
import os
import multiprocessing

import numpy as np
import pandas as pd


def make_cuts(s):
    """Make cuts to keep only signa-like events.

    :param s: `pandas.DataFrame` in the format of a ScintRHits.csv
    (output of use_rootaway.py).
    """
    s['equivalentNPE'] = s.EDep_MeV / 1.24e-3

    # Ignore all hits with NPE ~ 0.
    # (This was the first major update to this cuts file, done 9 July 2023. The
    # second major update is the new file.)
    np.random.seed(0)
    random_NPE_limit = np.random.rand(len(s))
    s = s[s.equivalentNPE > random_NPE_limit]

    # Maximum of 50 NPE for every slab in an event.
    # Uses our new, tentative, relationship for energy deposit/NPE.
    s = cut_by_event(s, s.groupby('eventID').equivalentNPE.max() < 50)

    # Exactly four hits total.
    s = cut_by_event(s, s.groupby('eventID').size() == 4)

    # All four layers.
    s['layerNo'] = (s.copyNo - 18) % 4
    s = cut_by_event(s, s.groupby('eventID').layerNo.nunique() == 4)

    return s


def process_file(path):
    """Read and cut a file, and keep track of the total number of events.
    This function is given to `multiprocessing`."""
    print(f"Reading and cutting {path}")

    file = pd.read_csv(path)
    num_events_before_cuts = file.eventID.nunique()
    cut_file = make_cuts(file)

    return cut_file, num_events_before_cuts


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

    # Create a `uniqueEventID` to differentiate between equal `eventID`s from
    # different files.
    dfs = []
    for i, r in enumerate(results):
        df = r[0]
        df.insert(0, 'uniqueEventID', int(1e9*i) + df.eventID)
        df.drop(columns='eventID', inplace=True)
        dfs.append(df)

    full_df = pd.concat(dfs)
    num_events_before_cuts = sum(r[1] for r in results)

    if save:
        savepath = os.path.join(folder, save)
        full_df.to_csv(savepath, index=False)
        print(f"Saved cut results to {savepath}")
    
    print(f"Ending at: {datetime.now()}")

    return full_df, num_events_before_cuts


def cut_by_event(df, eventID_bool):
    """Make a single cut.
    
    I.e., return a `DataFrame` like `df`, but only with the entries with
    `eventID`s  that correspond to `True` in the `pandas.Series`
    `eventID_bool`."""
    eventID_list = eventID_bool.index[eventID_bool] 
    return df[df.eventID.isin(eventID_list)]


if __name__ == '__main__':
    df, num_events_before_cuts = process_folder()
    print(df)
    print(f"{num_events_before_cuts} events in total before any cuts.")
