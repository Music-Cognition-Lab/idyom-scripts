'''
Segment lisp files (exported from IDyOM's database) into individual phrases,
using the convenient ':PHRASE' tags that are exported (1/-1 are start/end),
and export as a consolidated lisp file.

NOTE: default timebase (96) and midc (60) are expected. Please adjust the script
if this is problematic. If one or more of several corpora have different values
for timebase/midc, this will require several code changes.

Example Usage:
 > segment_lisp_corpora.py w_segs 0.lisp 1.lisp 7.lisp

Tom Kaplan
'''
import argparse
import pyparsing

TIMEBASE_DEFAULT = '96'
MIDC_DEFAULT = '60'

def to_lisp(x):
    # Credit: https://stackoverflow.com/a/14059322/6334309
    return '(%s)' % ' '.join(to_lisp(y) for y in x) if isinstance(x, list) else x

def lisp_to_list(lisp_str,label=None):
    return pyparsing.nestedExpr('(', ')').parseString(lisp_str).asList()

def phrase_value(event):
    for tag, val in event:
        if tag == ':PHRASE':
            return val

def onset_value_ind(event):
    for i, e in enumerate(event):
        tag, val = e
        if tag == ':ONSET':
            return val, i

def main(args):

    # This will collect all phrases within the specified corpora
    phrases = []

    for lisp_file in args.files:
        fname = lisp_file.name
        print('Parsing {}'.format(fname))
        contents = lisp_file.read()
        # This takes time, but gives us a convenient representation
        data = lisp_to_list(contents, label='PHRASE')

        # Collection
        col_name = '_'.join(data[0][0:3])
        print('Segmenting {}'.format(col_name))

        if data[0][1] != TIMEBASE_DEFAULT:
            err = "Variable timebase ({}, not default {}) not supported!"
            raise NotImplementedError(err.format(data[0][1], TIMEBASE_DEFAULT))
        if data[0][2] != MIDC_DEFAULT:
            err = "Variable midc ({}, not default {}) not supported!"
            raise NotImplementedError(err.format(data[0][2], MIDC_DEFAULT))

        n_mels = len(data[0])

        # Each melody
        for i in range(3, n_mels):
            mel_name = data[0][i][0].replace('"', '')
            n_events = len(data[0][i])

            # Ensure we don't trail events into next melody
            curr_phrase = []
            n_segs = 0

            # Each event
            onset_offset = 0
            for j in range(1, n_events):
                event = data[0][i][j]
                # Use :PHRASE to check boundaries of segment
                val = phrase_value(event)
                # Adjust :ONSET to start from 0 within segment
                ons, ons_ind = onset_value_ind(event)

                # Build phrase
                if val == '-1':
                    # End of phrase, reset
                    event[ons_ind][1] = str(int(event[ons_ind][1])-onset_offset)
                    curr_phrase.append(event)
                    ext = '_{}'.format(n_segs)
                    phrases.append([mel_name+ext]+curr_phrase[:])
                    n_segs += 1
                    curr_phrase = []
                elif val == '1':
                    # Start of phrase, reset
                    onset_offset = int(ons)
                    event[ons_ind][1] = '0'
                    curr_phrase = [event]
                elif val == '0' and len(curr_phrase) > 0:
                    # Only add to phrase if we explicitly know a phrase
                    # has started (i.e. previous conditional)
                    event[ons_ind][1] = str(int(event[ons_ind][1])-onset_offset)
                    curr_phrase.append(event)

    new_data = [[args.newname, TIMEBASE_DEFAULT, MIDC_DEFAULT, phrases]]
    out_path = '{}.lisp'.format(args.newname)
    print('Writing to {}: {}'.format(len(phrases), out_path))
    with open(out_path, 'w') as outfile:
        outfile.write(to_lisp(new_data))

    import pdb; pdb.set_trace()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('newname', type=str)
    parser.add_argument('files', type=argparse.FileType('r'), nargs='+')
    args = parser.parse_args()
    main(args)
