# -*- coding: utf-8 -*-
""" Build datapackages reflecting different subsystem configurations for
Bordelum
"""

import os
import shutil

from oemof.tabular.datapackage import building, processing
from tools import substract_bordelum_profile, connect_bordelum_residual

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

    new_path = os.path.abspath(os.path.join(copypath, showcase))

    processing.copy_datapackage(old_path, new_path, subset='data')

    connect_bordelum_residual(showcase, new_path)

    if showcase in 'ABCDEF':
        substract_bordelum_profile(
            new_path, 'DE-load', 'amount', 974, 'BO-load-profile', 'load')

    if showcase == 'G':
        substract_bordelum_profile(
            new_path, 'DE-load', 'amount', 974 * 2, 'BO-load-profile', 'load')

    if showcase in 'ABDEFG':
        substract_bordelum_profile(
            new_path, 'DE-pv', 'capacity', 2.94, 'BO-pv-profile', 'volatile')

    if showcase == 'C':
        substract_bordelum_profile(
            new_path, 'DE-pv', 'capacity', 4.269, 'BO-pv-profile', 'volatile')

    if showcase in 'EF':
        substract_bordelum_profile(
            new_path, 'DE-wind-onshore', 'capacity', 1,
            'BO-wind-onshore-profile', 'volatile')

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
