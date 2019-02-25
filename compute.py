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

    # m.write(
    #     os.path.join(base_path, 'tmp.lp'),
    #     io_options={"symbolic_solver_labels":True})

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

    return (pk, m.total_emissions())


#packages = ['2-' + i for i in list("ABCDEFG")]
packages = ["SQ"] + ['2-A']

results = os.path.expanduser('~/results')
if not os.path.exists(results):
    os.mkdir(results)

timestamp = str(datetime.now().strftime("%Y-%m-%d-%H-%M")).replace(':', '-').replace(' ', '-')
p = mp.Pool(1)

res = p.map(compute, packages)
pd.Series(dict(res)).to_csv(os.path.join(results, 'emissions' + '-' + timestamp + '.csv'))


# excess_share = (
#     excess.sum() * config["temporal-resolution"] / 1e6
# ) / supply_sum.sum(axis=1)
# excess_share.name = "excess"


# emissions
#cemissions = views.node_output_by_type(m.results, node_type=es.typemap['dispatchable'])
#emissions = emissions.loc[:, [c for c in emissions.columns.get_level_values(0) if c.tech != None]]  # filter shortage
#emissions = emissions.apply(lambda x: x * float(ef[(x.name[0].label.split('-')[1])])).T.groupby('to').sum().T.sum()
#emissions.to_csv(os.path.join(scenario_path, 'emissions.csv'))


#ef = pd.DataFrame(
#    Package('https://raw.githubusercontent.com/ZNES-datapackages/technology-cost/features/add-2015-data/datapackage.json')
#    .get_resource('carrier').read(keyed=True)).set_index(
#        ['year', 'carrier', 'parameter', 'unit']).sort_index() \
#    .loc[(2015, slice(None), 'emission-factor', 't (CO2)/MWh'), :] \
#    .reset_index().set_index('carrier')['value']
