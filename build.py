# -*- coding: utf-8 -*-
""" """

import shutil
import zipfile
import os

import pandas as pd
from oemof.tabular.datapackage import building, processing
from oemof.tabular.datapackage.processing import \
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
        'download/v0.1-alpha/Status-quo-2015.zip',
        directory=dpkg), 'r').extractall(base)

# load archived data
xls = './archive/data.xls'
datapackages = pd.read_excel(xls, index_col='identifier')

for pk in datapackages.index:

    # declare paths
    path = os.path.join(dpkg, pk)
    epath = os.path.join(path, 'data', 'elements')
    spath = os.path.join(path, 'data', 'sequences')

    # copy datapackage
    processing.copy_datapackage(os.path.join(base, 'datapackage.json'), path)

    # fetch timeseries data
    try:

        # TODO: parse dates from xls file
        timesteps = pd.date_range('2015-01-01 00:00:00', '2015-12-31 23:00:00', freq='H')

        ts = pd.read_excel(
                xls, sheet_name='timeseries' + '-' + pk
            ).set_index(timesteps)['Sum']

        positive = ts.apply(lambda x: x if x > 0 else 0)
        positive.name = 'BO-plus-profile'

        negative = ts.apply(lambda x: x if x < 0 else 0).abs()
        negative.name = 'BO-minus-profile'

        # positive values represent a net generation for the macro-system
        header = ['bus', 'capacity', 'profile', 'type']
        data = ['DE-electricity', 1, 'BO-plus-profile', 'volatile']

        element = pd.DataFrame({
            'BO-plus': dict(zip(header, data))
        }).T

        write_elements('volatile.csv', element, directory=epath)
        write_sequences('volatile_profile.csv', positive, directory=spath)

        # negative values represent a net demand for the macro-system
        header = ['bus', 'amount', 'profile', 'type']
        data = ['DE-electricity', 1, 'BO-minus-profile', 'load']

        element = pd.DataFrame({
            'BO-minus': dict(zip(header, data))
        }).T

        write_elements('load.csv', element, directory=epath)
        write_sequences('load_profile.csv', negative, directory=spath)

    except XLRDError as e:
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
