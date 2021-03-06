#!/usr/bin/env python
# Script to subset a netcdf file based on a list of 
# IDs

import argparse
from datetime import datetime
import os
import sys
import xarray as xr

def process_command_line():
    '''Parse the commandline'''
    parser = argparse.ArgumentParser(description='Script to subset a netcdf file based on a list of IDs.')
    parser.add_argument('id',
                        help='variable ID to subset on (e.g. \'hruId\')')
    parser.add_argument('ncfile',
                        help='path of netcdf file that will be subset.')
    parser.add_argument('idfile', 
                        help='path of file with list of ids.')
    parser.add_argument('ofile',
                        help='path of subsetted output file.')
    parser.add_argument('-d', '--drop', action='store_true', default=False, 
                        help=('drop the variables that are not associated with the same dimension(s) '
                              'as the ID used in subsetting'))
    args = parser.parse_args()
    return(args)


# main
if __name__ == '__main__':
    # process command line
    args = process_command_line()

    # read the IDs to subset
    with open(args.idfile) as f:
        ids = [int(x) for x in f]

    # ingest the netcdf file
    ds = xr.open_dataset(args.ncfile)

    # subset dimension
    subset_dim = list(ds[args.id].dims)

    # determine which variables do not vary along any of the subsetted dimensions
    vars_without = []
    for var in ds.variables:
        if not set(subset_dim).intersection(ds[var].dims):
            vars_without.append(var)

    # take the other variables
    vars_with = list(set(ds.variables).difference(set(vars_without)))

    # subset the netcdf file based on the hruId
    ds_with = ds[vars_with]
    ds_subset = ds_with.where(ds_with[args.id].isin(ids), drop=True)

    if not args.drop:
        # merge the with and without
        ds_subset = ds_subset.merge(ds[vars_without])

    # make sure that the subsetted types are the same as the original ones
    for var in ds_subset.variables:
        ds_subset[var] = ds_subset[var].astype(ds[var].dtype)

    # update the history attribute
    history = '{}: {}\n'.format(datetime.now().strftime('%c'), 
                                ' '.join(sys.argv))
    if 'history' in ds_subset.attrs:
        ds_subset.attrs['history'] = history + ds_subset.attrs['history']
    else:
        ds_subset.attrs['history'] = history

    # Write to file
    ds_subset.to_netcdf(args.ofile)

    # Write IDs from the ID file that were not in the NetCDF file to stdout
    missing = set(ids).difference(set(ds_subset[args.id].values))
    if missing:
        print("Missing IDs: ")
        for x in missing:
            print(x)
