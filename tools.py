# -*- coding: utf-8 -*-
"""
"""

import os
import pandas as pd

from oemof.tabular.datapackage.building import read_elements, write_elements, \
    read_sequences, write_sequences


def update_field(resource, name, field, func, directory='data/elements'):
    """ Update single field value by applying func

    Parameters
    ----------
    resource: str
        Resource name.
    name: str
        Unique elment identifier.
    field: str
        Field entry to be changed.
    func: function
        Function to be applied on field entry.
    """

    element = read_elements(resource, directory=directory).loc[name, :]
    element[field] = func(element[field])

    update_element(resource, element, directory=directory)

    return None


def update_element(resource, element, directory="data/elements"):
    """ Update single element entry.

    Parameters
    ----------
    resource : str
        Resource name.
    element : pd.Series
        Element. Series name used as column name. (!)
        https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.update.html

    """

    elements = read_elements(resource, directory=directory)

    elements = elements.T.copy()
    elements.update(element)

    write_elements(resource, elements.T, directory=directory, replace=True)

    return None


def update_sequence(resource, sequence, directory="data/sequences"):
    """ Update single sequence

    Parameters
    ----------
    resource : str
        Resource name.
    sequence : pd.Series
        Sequence. Series name used as column name.
    """

    sequences = read_sequences(resource, directory=directory)

    sequences.update(sequence)

    write_sequences(resource, sequences, directory=directory, replace=True)

    return None


def substract_bordelum_load(basepath, archive='archive', correction=1):
    """ Substracts Bordelum load profile from German load profile

    Parameters
    ----------
    basepath : str
        Basepath of datapackage.
    correction: float
        Load profile is multiplied by correction factor. Default 1.
    archive : str
        Archive directory.

    Notes
    -----
    `Bordelum-profiles.csv` containing column `BO-load-profile` is expected to
    exist in the archive directory.
    """

    name = 'DE-load'

    elements_path = os.path.join(basepath, 'data/elements')
    sequences_path = os.path.join(basepath, 'data/sequences')

    # get German load
    load = read_elements('load.csv', directory=elements_path).loc[name, :]
    load_seq = read_sequences(
        'load_profile.csv', directory=sequences_path)[name + '-profile']

    load_diff = pd.read_csv(
        os.path.join(archive, 'Bordelum-profiles.csv'),
        index_col='timeindex'
    ) * correction

    # substract Bordelum load
    _load_seq = load_seq * load['amount'] - load_diff['BO-load-profile']

    new_load = load.copy()
    new_load['amount'] = _load_seq.sum()  # insert new amount

    new_load_seq = _load_seq / _load_seq.sum()
    new_load_seq.name = name + '-profile'

    # write German load
    update_element('load.csv', new_load, directory=elements_path)
    update_sequence('load_profile.csv', new_load_seq, directory=sequences_path)

    return None


def substract_bordelum_profile(
    base_path, element_name, field, value, profile, ressource, archive='archive'):
    """ Substract bordelum profiles from German electricity bus

    Parameters
    ----------
    basepath : str
        Basepath of datapackage.
    element_name : str
        Element to be changed.
    field : str
        Field entry to be changed.
    value : float or int
        Value of field entry for Bordelum, e.g. value of installed capacity.
    profile : str
        Name of the associated profile in `Bordelum-profiles.csv`.
    ressource: str
        E.g. `volatile`.
    """

    elements_path = os.path.join(base_path, 'data/elements')
    sequences_path = os.path.join(base_path, 'data/sequences')

    # get element
    element_old = read_elements(ressource + '.csv', directory=elements_path).\
        loc[element_name, :]

    seq_old = read_sequences(
        ressource + '_profile.csv',
        directory=sequences_path)[element_name + '-profile']

    # substract actual Bordelum sequence from actual sequence
    seq_actual = element_old[field] * seq_old - \
        (pd.read_csv(os.path.join(archive, 'Bordelum-profiles.csv'),
                index_col='timeindex'
            )[profile] * value)

    # clip negative values
    seq_actual = seq_actual.apply(lambda x: x if x > 0 else 0)

    element_new = element_old.copy()
    element_new[field] -= value

    seq_new = seq_actual / element_new[field]
    seq_new.name = element_name + '-profile'

    update_element(ressource + '.csv', element_new, directory=elements_path)
    update_sequence(ressource + '_profile.csv', seq_new, directory=sequences_path)

    return None


def connect_bordelum_residual(showcase, basepath, archive='archive'):
    """ Attach subsystem optimization results to the German electricity bus

    Parameters
    ----------
    showcase : str
        Showcase identifier.
    basepath : str
        Basepath of datapackage.
    archive : str
        Archive directory.

    """

    elements_path = os.path.join(basepath, 'data/elements')
    sequences_path = os.path.join(basepath, 'data/sequences')

    timeseries = pd.read_csv(
        os.path.join(archive, 'Bordelum-residual-load.csv'),
        index_col='timeindex'
    )[showcase]

    sequence = timeseries.apply(lambda z: z if z < 0 else 0).abs()
    sequence.name = 'BO-generation-profile'

    if sequence.sum() > 0:

        element = {
            'BO-generation':
            {
                'bus': 'DE-electricity',
                'tech': '',
                'carrier': '',
                'capacity': 1,
                'profile': 'BO-generation-profile',
                'marginal_cost': 0,
                'type': 'volatile'
            }
        }


        write_elements(
            'volatile.csv', pd.DataFrame(element).T, directory=elements_path)
        write_sequences(
            'volatile_profile.csv', sequence, directory=sequences_path)

    sequence = timeseries.apply(lambda y: y if y > 0 else 0)
    sequence.name = 'BO-load-profile'

    if sequence.sum() > 0:

        element = {
            'BO-load':
            {
                'bus': 'DE-electricity',
                'tech': 'load',
                'amount': sequence.sum(),
                'profile': 'BO-load-profile',
                'type': 'load'
            }
        }

        write_elements(
            'load.csv', pd.DataFrame(element).T, directory=elements_path)
        write_sequences(
            'load_profile.csv',
            sequence / sequence.sum(),
            directory=sequences_path
        )

    return None
