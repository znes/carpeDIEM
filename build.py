# -*- coding: utf-8 -*-
""" Build datapackages reflecting different subsystem configurations for
Bordelum
"""

import os
import shutil

from oemof.tabular.datapackage import building, processing
from tools import update_field, substract_bordelum_load, \
    connect_bordelum_residual

archive = 'archive'
copypath = 'datapackages'

# recreate datapackages folder
if os.path.exists(copypath):
    shutil.rmtree(copypath)

os.mkdir(copypath)

# download and move Status quo datapackage
os.mkdir(os.path.join(copypath, 'SQ'))

unzip_file = "Status-quo-2015-features-temporary-data/"
building.download_data(
    "https://github.com/ZNES-datapackages/Status-quo-2015/archive/features/"
    "temporary-data.zip",
    unzip_file=unzip_file, directory=copypath)

source = os.path.join(copypath, unzip_file, unzip_file)

for f in os.listdir(source):
    shutil.move(os.path.join(source, f), os.path.join(copypath, 'SQ'))

shutil.rmtree(os.path.join(copypath, unzip_file))

# create all showcase datapackages by copyiing and adapting Status quo
# datapackage
old_path = os.path.join(copypath, "SQ", "datapackage.json")

showcase_identifier = list("ABCDEFG")

for showcase in showcase_identifier:

    new_path = os.path.join(copypath, showcase)

    processing.copy_datapackage(old_path, new_path, subset='data')

    connect_bordelum_residual(showcase, new_path)

    if showcase in 'ABCDEF':
        substract_bordelum_load(new_path)

    if showcase == 'G':
        substract_bordelum_load(new_path, correction=2)

    if showcase in 'ABDEFG':
        update_field(
            'volatile.csv', 'DE-pv', 'capacity', lambda x: x - 2940,
            directory=os.path.join(new_path, 'data/elements'))

    if showcase == 'C':
        update_field(
            'volatile.csv', 'DE-pv', 'capacity', lambda x: x - 4269,
            directory=os.path.join(new_path, 'data/elements'))

    if showcase in 'EF':
        update_field(
            'volatile.csv', 'DE-wind-onshore', 'capacity', lambda x: x - 1000,
            directory=os.path.join(new_path, 'data/elements'))

    building.infer_metadata(
        package_name='showcase-' + showcase,
        foreign_keys={
            'bus': ['volatile', 'dispatchable',
                    'load', 'excess', 'shortage', 'ror', 'phs', 'reservoir'],
            'profile': ['load', 'volatile', 'ror', 'reservoir'],
            'from_to_bus': ['grid'],
            'chp': []
                },
        path=new_path
        )
