"""Use rootaway to convert all ROOT files in
/net/cms17/cms17r0/schmitz/slabSimMuon/noPhotons/slab48/
to CSV files.

The `output_folder` must exist.

Caution:
Any existing subfolders in the `output_folder` will be skipped and not
modified.
(This is useful for starting the script up again after it was stopped in the
middle of running.)

TODO: Sort the order of input/output directories (to make it even easier to
stop while the script is running and pick it up later.)

TODO: Sign off on multiprocessing!

Created 7ish July 2023.
Last modified 7 July 2023.
"""
import os
import multiprocessing
import subprocess
import warnings

input_folder = '/net/cms17/cms17r0/schmitz/slabSimMuon/noPhotons/48slab/'
output_folder = '/net/cms26/cms26r0/anson/noPhotons/'


def convert_file(subfolder):
    """TODO"""
    this_input_file = os.path.join(input_folder, subfolder, 'MilliQan.root')
    this_output_folder = os.path.join(output_folder, subfolder)

    if os.path.exists(this_output_folder):
        warnings.warn(f"\n@@@@@ Not writing to the existing directory @@@@@\n{this_output_folder}\n")
        return

    print(f"Converting {this_input_file} to {this_output_folder}")
    print(subprocess.run(f"""root -q '/homes/anson/rootaway/rootaway.C("{this_input_file}", "{this_output_folder}")'""", shell=True))


if not os.path.exists(output_folder):
    raise ValueError(f"Sorry, but this script requires the output folder to exist. The output folder given was: {output_folder}")

# Ensure that we are using ROOT (this is Ryan's ROOT installation).
# TODO: try removing brackets
subprocess.run(['source /net/cms17/cms17r0/schmitz/root6/install/bin/thisroot.sh'], shell=True)

subfolders = next(os.walk(input_folder))[1]
num_available_cores = len(os.sched_getaffinity(0))

with multiprocessing.Pool(num_available_cores) as pool:
    pool.map(convert_file, subfolders)
 