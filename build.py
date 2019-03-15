# -*- coding: utf-8 -*-

import shutil
import zipfile
import pathlib
import os

import pandas as pd
from oemof.tabular.datapackage import building, processing

from oemof.tabular.datapackage.processing import write_elements, write_sequences

from xlrd import XLRDError


# recreate datapackages/SQ folder
pkpath = pathlib.Path('datapackages/SQ')
if pkpath.parent.is_dir():
    shutil.rmtree(pkpath.parent)
pkpath.mkdir(parents=True)

# download and unzip SQ datapackage
pkurl = 'https://github.com/ZNES-datapackages/Status-quo-2015/releases/download/v0.1-alpha/Status-quo-2015.zip'
zipfile.ZipFile(
    building.download_data(pkurl, directory=pkpath), 'r'
).extractall(pkpath)


scenarios = pd.read_excel(os.path.join('archive', 'scenarios.xls'), index_col='identifier').index.values

xls = 'archive/scenarios.xls'

for sc in scenarios:

    path = pathlib.Path(pkpath.parent, sc)
    #path.mkdir()

    processing.copy_datapackage(
        os.path.join(pkpath, 'datapackage.json'), path)

    elements_path = os.path.join(path, 'data', 'elements')
    sequences_path = os.path.join(path, 'data', 'sequences')

    try:

        timeseries = pd.read_excel(xls, sheet_name='timeseries' + '-' + sc)
        timeseries.set_index(pd.date_range('2015-01-01 00:00:00', '2015-12-31 23:00:00', freq='H'), inplace=True)
        timeseries = timeseries['Sum']

        sequence = timeseries.apply(lambda z: z if z > 0 else 0)
        sequence.name = 'BO-plus-profile'

        element = {
            'BO-plus':
            {
                'bus': 'DE-electricity',
                'capacity': 1,
                'profile': 'BO-plus-profile',
                'type': 'volatile'
            }
        }

        write_elements(
            'volatile.csv', pd.DataFrame(element).T, directory=elements_path)
        write_sequences(
            'volatile_profile.csv', sequence, directory=sequences_path)

        sequence = timeseries.apply(lambda y: y if y < 0 else 0).abs()
        sequence.name = 'BO-minus-profile'

        element = {
            'BO-minus':
            {
                'bus': 'DE-electricity',
                'amount': 1,
                'profile': 'BO-minus-profile',
                'type': 'load'
            }
        }

        write_elements(
            'load.csv', pd.DataFrame(element).T, directory=elements_path)
        write_sequences('load_profile.csv', sequence, directory=sequences_path)

    except XLRDError as e:
        pass
