# -*- coding: utf-8 -*-
"""
"""

import os
import pandas as pd

from oemof.tabular.datapackage.building import read_elements, write_elements, \
    read_sequences, write_sequences


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

def update_field(resource, label, field, func, directory='data/elements'):
    """ Update single field value by applying func

    Parameters
    ----------
    resource: str
        Resource name.
    label: str
        Unique elment identifier.
    field: str
        Field entry to be changed.
    func: function
        Function to be applied on field entry.
    """

    element = read_elements(resource, directory=directory).loc[label, :]
    element[field] = func(element[field])

    update_element(resource, element, directory=directory)

    return None
