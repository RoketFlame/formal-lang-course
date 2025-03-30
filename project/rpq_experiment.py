import logging
import time
from collections.abc import Collection
from typing import Optional

import cfpq_data
import matplotlib.pyplot as plt
import numpy as np
from networkx import MultiDiGraph
from pandas import DataFrame
from scipy.sparse import (
    csr_matrix,
    dok_matrix,
    lil_matrix,
    csc_matrix,
)

from project.adjacency_matrix import tensor_based_rpq
from project.bfs_rpq import ms_bfs_based_rpq
from project.graph_tools import GraphData

seed = 42
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)


def get_graph_by_name(graph_name: str) -> tuple[MultiDiGraph, GraphData]:
    graph_path = cfpq_data.download(graph_name)
    graph_data = GraphData.get_graph_data_by_name(graph_name)
    return cfpq_data.graph_from_csv(graph_path), graph_data


def get_start_nodes(graph: MultiDiGraph, percent: float) -> set[int]:
    return cfpq_data.generate_multiple_source_percent(graph, percent, seed=seed)


def queries(labels: set[str]) -> list[str]:
    l1, l2, l3, l4, *_ = list(sorted(labels))
    return [
        f"({l1}|{l2})* {l3}",
        f"({l3}|{l4})+ {l1}*",
        f"{l1} {l2} {l3} ({l4}|{l1})*",
        f"{l1}+ {l2}*",
    ]


def make_groped_bar_chart_plot(
    data: DataFrame,
    title: str,
    x_labels: Collection[str],
    y_label: str,
    error: Optional[DataFrame] = None,
):
    n_groups = len(data)
    n_bars = len(data.columns)
    indices = np.arange(n_groups)

    bar_width = 0.8 / n_bars
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, col in enumerate(data.columns):
        offset = (i - (n_bars - 1) / 2) * bar_width
        values = data[col].values
        errors = None if error is None else error[col].values
        ax.bar(indices + offset, values, bar_width, yerr=errors, label=col, capsize=5)

    ax.set_xticks(indices)
    ax.set_xticklabels(x_labels, rotation=0, ha="right")
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{title}.svg")


def plot_of_grahs_data(graphs: list[str]):
    graph_names = []
    node_counts = []
    edge_counts = []
    label_counts = []

    for graph_name in graphs:
        graph, data = get_graph_by_name(graph_name)
        graph_names.append(graph_name)
        node_counts.append(data.nodes_count)
        edge_counts.append(data.edges_count)
        label_counts.append(len(data.labels))

    graph_data = {
        "nodes": node_counts,
        "edges": edge_counts,
        "labels": label_counts,
    }
    make_groped_bar_chart_plot(DataFrame(graph_data), "Graphs", graph_names, "Count")


graphs = [
    "pizza",
    "skos",
    "foaf",
    "travel",
]

plot_of_grahs_data(graphs)

matrix_types = [
    csr_matrix,
    csc_matrix,
    dok_matrix,
    lil_matrix,
]
launches = 20

raw_regex = [
    "(l1|l2)* l3",
    "(l3|l4)+ l1*",
    "l1 l2 l3 (l4|l1)*",
    "l1+ l2*",
]
rpqs = [
    tensor_based_rpq,
    ms_bfs_based_rpq,
]

persentages = [1, 2, 3, 5, 8, 12, 15, 20, 30, 40, 50, 60, 70, 80, 90]


def rpq_matrix_experiment():
    for graph_name in graphs:
        data = {}
        deviations = {}
        graph, graph_data = get_graph_by_name(graph_name)
        for matrix_type in matrix_types:
            for query in queries(graph_data.labels):
                for rpq in rpqs:
                    times = []
                    for _ in range(launches):
                        start = time.time()
                        rpq(query, graph, matrix_type=matrix_type)
                        times.append(time.time() - start)
                    average = np.mean(times)
                    deviation = np.std(times)
                    deviations.setdefault(
                        f"{matrix_type.__name__}({rpq.__name__})", []
                    ).append(deviation)
                    data.setdefault(
                        f"{matrix_type.__name__}({rpq.__name__})", []
                    ).append(average)

        make_groped_bar_chart_plot(
            DataFrame(data),
            f"RPQ {graph_name}",
            raw_regex,
            "Time",
            error=DataFrame(deviations),
        )


def rpq_start_nodes_experiment():
    for rpq in rpqs:
        for graph_name in graphs:
            data = {}
            deviations = {}
            graph, graph_data = get_graph_by_name(graph_name)
            matrix_type = csr_matrix
            for query in queries(graph_data.labels):
                for percent in persentages:
                    times = []
                    start_nodes = get_start_nodes(graph, percent)
                    for _ in range(launches):
                        start = time.time()
                        rpq(
                            query,
                            graph,
                            matrix_type=matrix_type,
                            start_nodes=start_nodes,
                            final_nodes=None,
                        )
                        times.append(time.time() - start)
                    average = np.mean(times)
                    deviation = np.std(times)
                    deviations.setdefault(f"{percent}", []).append(deviation)
                    data.setdefault(f"{percent}", []).append(average)

            make_groped_bar_chart_plot(
                DataFrame(data),
                f"RPQ {rpq.__name__} {graph_name}",
                raw_regex,
                "Time",
                error=DataFrame(deviations),
            )
