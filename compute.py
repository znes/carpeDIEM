"""
--solver
--clean results-folder
--cpu-cores
--debug lp file
--scenarios list
"""

import os
import json

import oemof.outputlib as outputlib
import multiprocessing as mp

from oemof.tabular import facades
from datetime import datetime
from oemof.tabular.datapackage import processing
from oemof.solph import EnergySystem, Model, Bus
from oemof.tabular.tools import postprocessing as pp

import pyomo.core as po
import pandas as pd


def compute(pk):

    base_path = os.path.join(
        results, pk + '-' + timestamp)
    input_path = os.path.join('datapackages', pk)
    output_path = os.path.join(base_path, 'output')

    os.mkdir(base_path)
    os.mkdir(output_path)

    processing.copy_datapackage(
        os.path.join(input_path, 'datapackage.json'),
        os.path.join(base_path, 'input'))

    es = EnergySystem.from_datapackage(
        os.path.join(input_path, 'datapackage.json'),
        attributemap={},
        typemap=facades.TYPEMAP,
    )

    m = Model(es)

    flows = {}
    for (i, o) in m.flows:
        if hasattr(m.flows[i, o], 'emission_factor'):
            flows[(i, o)] = m.flows[i, o]

    # emissions by country
    for node in es.nodes:
        if isinstance(node, Bus):
            expr = sum(
                m.flow[inflow, outflow, t] * m.timeincrement[t] *
                flows[inflow, outflow].emission_factor
                for (inflow, outflow) in flows
                for t in m.TIMESTEPS if outflow.label == node.label)
            setattr(
                m, node.label.split('-')[0] + '_emissions',
                po.Expression(expr=expr)
            )

    m.total_emissions =  po.Expression(
        expr=sum(m.flow[inflow, outflow, t] * m.timeincrement[t] *
                 flows[inflow, outflow].emission_factor
                 for (inflow, outflow) in flows
                 for t in m.TIMESTEPS))

    m.receive_duals()

    m.solve('gurobi')

    m.results = m.results()

    pp.write_results(m, output_path, scalars=False, types=[
        "dispatchable", "volatile", "storage", "reservoir"])

    modelstats = outputlib.processing.meta_results(m)
    modelstats.pop("solver")
    modelstats["problem"].pop("Sense")
    modelstats["total-emissions"] = m.total_emissions()

    # store emissions by country
    for node in es.nodes:
        if isinstance(node, Bus):
            name = node.label.split('-')[0] + '_emissions'
            modelstats[name] = getattr(m, name)()

    with open(os.path.join(base_path, "modelstats.json"), "w") as outfile:
        json.dump(modelstats, outfile, indent=4)

    supply_sum = (
        pp.supply_results(
            results=m.results,
            es=m.es,
            bus=[b.label for b in es.nodes if isinstance(b, Bus)],
            types=[
                "dispatchable",
                "volatile",
                "reservoir",
            ],
        )
        .sum()
        .reset_index()
    )

    supply_sum['from'] = supply_sum['from'].apply(lambda i: '-'.join(i.label.split("-")[1:3:]))
    supply_sum = supply_sum.groupby(['from', 'to', 'type']).sum().reset_index()

    supply_sum.drop("type", axis=1, inplace=True)
    supply_sum = (
        supply_sum.set_index(["from", "to"]).unstack("from")
        / 1e6
    )
    supply_sum.columns = supply_sum.columns.droplevel(0)

    summary = supply_sum
    summary.to_csv(os.path.join(base_path, 'summary.csv'))

    return (pk, modelstats['objective'], m.total_emissions())


packages = ['2' + i for i in list("ABCDEFG")] + ['SQ'] + ['3B', '3C', '3D', '3F'] + ['4B', '4C']

results = os.path.expanduser('~/results')
if not os.path.exists(results):
    os.mkdir(results)

timestamp = str(datetime.now().strftime("%Y-%m-%d-%H-%M")).replace(':', '-').replace(' ', '-')
p = mp.Pool(7)

container = p.map(compute, packages)
pd.DataFrame(
    container, columns=['datapackage', 'objective', 'emissions']
).to_csv(os.path.join(results, 'summary' + '-' + timestamp + '.csv'), index=False)
