# -*- coding: utf-8 -*-
""" Build datapackages reflecting different subsystem configurations for
Bordelum
"""

import os
import shutil

import pandas as pd

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

showcase_identifier = ["2-" + i for i in list("ABCDEFG")]
showcase_identifier += ['3-A', '3-B', '3-C', '3-D']

for showcase in showcase_identifier:

    new_path = os.path.abspath(os.path.join(copypath, showcase))

    processing.copy_datapackage(old_path, new_path, subset='data')

    if '2' in showcase:
        connect_bordelum_residual(showcase.split('-')[1], new_path)

    if showcase in ['2-A', '2-B', '2-C', '2-D', '2-E', '2-F']:
        substract_bordelum_profile(
            new_path, 'DE-load', 'amount', 974, 'BO-load-profile', 'load')

    if showcase == '2-G':
        substract_bordelum_profile(
            new_path, 'DE-load', 'amount', 974 * 2, 'BO-load-profile', 'load')

    if showcase in ['2-A', '2-B', '2-D', '2-E', '2-F', '2-G']:
        substract_bordelum_profile(
            new_path, 'DE-pv', 'capacity', 2.94, 'BO-pv-profile', 'volatile')

    if showcase == '2-C':
        substract_bordelum_profile(
            new_path, 'DE-pv', 'capacity', 4.269, 'BO-pv-profile', 'volatile')

    if showcase in ['2-E', '2-F']:
        substract_bordelum_profile(
            new_path, 'DE-wind-onshore', 'capacity', 1,
            'BO-wind-onshore-profile', 'volatile')

    if showcase == '3-B':

        element = {
            'bus': 'DE-electricity',
            'capacity': 0.18,
            'carrier': 'electricity',
            'efficiency': 0.95,
            'loss': 0.0,
            'marginal_cost': 1e-7,
            'storage_capacity': 0.3492,
            'storage_capacity_inital': 0,
            'tech': 'battery',
            'type': 'storage'
        }

        building.write_elements(
            os.path.join(new_path, 'data', 'elements', 'battery.csv'),
            pd.DataFrame(element, index=['DE-battery'])
        )

    if showcase == '3-C':

        element = {
            'bus': 'DE-electricity',
            'capacity': 0.865,
            'carrier': 'electricity',
            'efficiency': 0.95,
            'loss': 0.0,
            'marginal_cost': 1e-7,
            'storage_capacity': 1.6781,
            'storage_capacity_inital': 0,
            'tech': 'battery',
            'type': 'storage'
        }

        building.write_elements(
            os.path.join(new_path, 'data', 'elements', 'battery.csv'),
            pd.DataFrame(element, index=['DE-battery'])
        )

    if showcase == '3-D':

        element = {
            'bus': 'DE-electricity',
            'capacity': 1,
            'carrier': 'electricity',
            'efficiency': 0.85,
            'loss': 0.0,
            'marginal_cost': 1e-7,
            'storage_capacity': 2.263,
            'storage_capacity_inital': 0,
            'tech': 'battery',
            'type': 'storage'
        }

        building.write_elements(
            os.path.join(new_path, 'data', 'elements', 'battery.csv'),
            pd.DataFrame(element, index=['DE-battery'])
        )

    if showcase == '3-F':

        element = {
            'bus': 'DE-electricity',
            'capacity': 1,
            'carrier': 'electricity',
            'efficiency': 0.92,
            'loss': 0.0,
            'marginal_cost': 1e-7,
            'storage_capacity': 0.56,
            'storage_capacity_inital': 0,
            'tech': 'battery',
            'type': 'storage'
        }

        building.write_elements(
            os.path.join(new_path, 'data', 'elements', 'battery.csv'),
            pd.DataFrame(element, index=['DE-battery'])
        )

    building.infer_metadata(
        package_name='showcase-' + showcase,
        foreign_keys={
            'bus': ['volatile', 'dispatchable', 'battery',
                    'load', 'excess', 'shortage', 'ror', 'phs', 'reservoir'],
            'profile': ['load', 'volatile', 'ror', 'reservoir'],
            'from_to_bus': ['grid'],
            'chp': []
                },
        path=new_path
        )
