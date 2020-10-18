#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 16:42:15 2019
@author: etrhall

---

Utility to parse a directory of Humdrum **kern files and return lowest possible
timebase value for IDyOM import.

Durations that are not divisible by the default timebase of 96 divisions per
semibreve (whole note) will otherwise give an error when importing into IDyOM.

---

Usage:

$ python3 checktimebase.py <path-to-directory>

---

IDyOM timebase can be changed at:

idyom-1.6/database/data-import/kern2db.lisp

line 104: (defparameter *default-timebase* <value>)

default: <value> = 96
"""

import os
import argparse
import numpy as np


def main(args):

    durations = np.array([96])  # 96 is the default, should be returned if possible

    # Collect difference durations from files in dir
    for filename in os.listdir(args.path):

        # .krn files only
        if filename.endswith('.krn'):
            filepath = os.path.join(args.path, filename)
            f = open(filepath, 'r', encoding='utf-8', errors='ignore')
            lines = f.readlines()
            f.close()
        else:
            continue

        for ln in lines:

            # Skip comment, reference, spine, tandem interpretation or barline
            if ln[0] in ('!', '*', '='):
                continue

            # Separate concurrent voices
            voices = [i[:i.find(' ')] for i in ln.split('\t')]

            for vc in voices:

                # Skip if null
                if not vc or vc[0] == '.':
                    continue

                # Extended rhythm representation (as a rational)
                if '%' in vc:
                    # As far as I know, IDyOM doesn't actually detect rational durations of this type
                    # This just imitates IDyOM's behaviour of stopping at the % separator
                    vc = vc[:vc.find('%')]

                durstr = ''.join([i for i in vc if i.isdigit()])
                if not durstr:
                    continue
                dur = int(durstr)

                # If new, add to list
                if not dur in durations:
                    durations = np.append(durations, dur)

                # Add extensions for dotted notes
                dots = vc.count('.')
                if dots:
                    dotdurs = [dur * (2 ** (i + 1)) for i in range(dots)]
                    for i, dd in enumerate(dotdurs):
                        if not dd in durations:
                            durations = np.append(durations, dd)

    # Calculate lowest common multiple for timebase
    durations = durations[durations > 0]
    lcm = np.lcm.reduce(durations)


    print("---")
    print("Lowest Timebase:", lcm)
    print("---")

    if lcm == 96:
        print("No change needed. IDyOM default timebase.")
    else:
        print("IDyOM timebase can be changed at:")
        print("  idyom-1.6/database/data-import/kern2db.lisp")
        print("  line 104: (defparameter *default-timebase* <value>)")

    print("---")

    return lcm


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Utility to parse a directory of Humdrum **kern files and \
                     return lowest possible timebase value for IDyOM import."
    )

    parser.add_argument(
        "path",
        metavar="path",
        type=str,
        help="path to directory of .krn files"
    )

    args = parser.parse_args()

    main(args)
