'''
Discovers events generated by IDyOM where the BIOI is not equal to successive onsets.

This does not 'fix' the problem, which might stem from bad corpora or a bug in IDyOM,
but might help discover a source of model errors.

Example Usage:

- Record compositions and the respective violations:

    $ idyom/db » python checkbioi.py database.sqlite
    Composition [7 4 'deut0005'] has 1 bad BIOIs, EVENT_IDs: 34
    Composition [7 36 'deut0037'] has 1 bad BIOIs, EVENT_IDs: 73
    Composition [7 80 'deut0081'] has 1 bad BIOIs, EVENT_IDs: 18
    Composition [7 96 'deut0097'] has 1 bad BIOIs, EVENT_IDs: 14
    Composition [7 122 'deut0123'] has 1 bad BIOIs, EVENT_IDs: 22
    ...

- Print a blacklist of bad compositions:

    $ idyom/db » python checkbioi.py database.sqlite --blacklist
    deut0005
    deut0037
    deut0081
    deut0097
    deut0123
    ...

- Creating a blacklist file:

    $ idyom/db » python checkbioi.py --blacklist database.sqlite > bad_comps_blacklist.txt


Tom Kaplan
'''
import argparse
import numpy as np
import pandas as pd

from exportdb import IDyOMDatabase, DB_PATH

def main(args):
    df = IDyOMDatabase.from_sqlite(args.db_path)

    blacklist = []
    for grp_index, composition in df.groupby(['DATASET_ID', 'COMPOSITION_ID']):
        comp_ids = composition[['DATASET_ID', 'COMPOSITION_ID', 'DESCRIPTION_COMPOSITION']]
        comp_id = comp_ids.drop_duplicates().values[0]

        assert pd.Index(composition.EVENT_ID).is_monotonic, '? EVENT_ID Monotonic'
        assert pd.Index(composition.ONSET).is_monotonic, '? ONSET Monotonic'

        # BIOI not equal successive onsets?
        bioi_matches = np.where(np.diff(composition.ONSET) != composition.BIOI.values[1:])[0]
        if bioi_matches.size > 0:
            blacklist.append(comp_id[-1])
            if not args.blacklist:
                bad_comp_msg = 'Composition {} has {} bad BIOIs, EVENT_IDs: {}'
                bad_ids = [str(x) for x in composition.iloc[bioi_matches+1].EVENT_ID.values]
                print(bad_comp_msg.format(str(comp_id), len(bioi_matches), ', '.join(bad_ids)))

    if args.blacklist:
        print('\n'.join(blacklist))
    elif not blacklist:
        print('Success - no violating BIOIs!')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('db_path', type=str,
                        help='Path to IDyOM database: PATH_TO/idyom/db/{}'.format(DB_PATH))
    parser.add_argument('--blacklist', action='store_true',
                        help='Print blacklist of violating compositions, to pipe/stream to file')
    args = parser.parse_args()
    main(args)