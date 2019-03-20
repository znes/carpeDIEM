# -*- coding: utf-8 -*-
""" """

import shutil
import zipfile
import os

import pandas as pd
from oemof.tabular.datapackage import building, processing
from oemof.tabular.datapackage.building import \
    write_elements, write_sequences

from xlrd import XLRDError

# path handling
dpkg = './datapackages'
base = os.path.join(dpkg, 'SQ')

if os.path.exists(dpkg):
    shutil.rmtree(dpkg)

os.mkdir(dpkg)

# unzip reference datapackage
zipfile.ZipFile(
    building.download_data(
        'https://github.com/ZNES-datapackages/Status-quo-2015/releases/'
        'download/v0.1-beta/Status-quo-2015.zip',
        directory=dpkg), 'r').extractall(base)

# load archived data
xls = './archive/data.xls'
datapackages = pd.read_excel(
    xls, sheet_name='scenarios', index_col='identifier')

storages = pd.read_excel(xls, sheet_name='storages', index_col='name')

# based on data.xls the reference datapackage is copied for each scenario
# and updated
for pk in datapackages.index:

    # declare paths
    path = os.path.join(dpkg, pk)
    epath = os.path.join(path, 'data', 'elements')
    spath = os.path.join(path, 'data', 'sequences')

    # copy datapackage
    processing.copy_datapackage(os.path.join(base, 'datapackage.json'), path)

    # try add storages
    try:

        building.write_elements(
            'battery.csv',
            storages.loc[[pk], :].rename(index={pk: pk + '-battery'}),
            directory=os.path.join(epath)
        )

        print('Added storage in datapackage %s.' % pk)

    except KeyError as e:
        pass

    # try fetch timeseries data
    try:

        # TODO: parse dates from xls file
        timesteps = pd.date_range(
            '2015-01-01 00:00:00', '2015-12-31 23:00:00', freq='H')

        ts = pd.read_excel(
                xls, sheet_name='timeseries' + '-' + pk
            ).set_index(timesteps)['net_balance']

        df = pd.read_excel(
            xls, sheet_name='r_timeseries_components').set_index('name')

        element = df.loc[['TS-pos-residual'], :]

        write_elements(
            'volatile.csv', element, directory=epath)

        write_sequences(
            'volatile_profile.csv',
            ts.apply(lambda x: x if x > 0 else 0).rename(element.profile[0]),
            directory=spath)

        element = df.loc[['TS-neg-residual'], :]

        write_elements('load.csv', element, directory=epath)

        write_sequences(
            'load_profile.csv',
            ts.apply(lambda x: x if x < 0 else 0).rename(element.profile[0]),
            directory=spath)

    except XLRDError as e:
        print('Warning: No timeseries data found for package %s.' % pk)
        pass

    # update metadata
    building.infer_metadata(
        package_name=pk,
        foreign_keys={
            'bus': ['volatile', 'dispatchable', 'battery',
                    'load', 'excess', 'shortage', 'ror', 'phs', 'reservoir'],
            'profile': ['load', 'volatile', 'ror', 'reservoir'],
            'from_to_bus': ['grid'],
            'chp': []
                },
        path=path
        )
