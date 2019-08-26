#!/usr/bin/env python
# Script to add an gruId from an attribute file to another file
# IDs

import argparse
from datetime import datetime
import os
import sys
import xarray as xr


def process_command_line():
    '''Parse the commandline'''
    parser = argparse.ArgumentParser(
        description=('Script to add a gruId from a SUMMA attributes to another file. '
                     'The assumption is that the file to which the gruId is added has the '
                     'same ordering along the gru dimension as the attribute file.'))
    parser.add_argument('input_file',
                        help='path of netcdf file to which gruId will added.')
    parser.add_argument('gruId_file',
                        help='path of netcdf file from which the gruId will be taken.')
    parser.add_argument('output_file',
                        help='path of output netcdf file.')
    args = parser.parse_args()
    return(args)


# main
if __name__ == '__main__':
    # process command line
    args = process_command_line()

    # open files
    ds=xr.open_dataset(args.input_file)
    ds_attr=xr.open_dataset(args.gruId_file)

    # add gruId
    ds['gruId']=ds_attr['gruId']

    # update the history attribute
    history = '{}: {}\n'.format(datetime.now().strftime('%c'),
                                ' '.join(sys.argv))
    if 'history' in ds.attrs:
        ds.attrs['history'] = history + ds.attrs['history']
    else:
        ds.attrs['history'] = history

    # Write to file
    ds.to_netcdf(args.output_file)
