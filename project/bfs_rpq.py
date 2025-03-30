import functools
import operator
from itertools import product
from typing import Optional, TypeVar, Union, cast

from networkx import MultiDiGraph
from scipy.sparse import csr_matrix, vstack, csc_matrix, lil_matrix, dok_matrix

from project.adjacency_matrix import AdjacencyMatrixFA
from project.finite_automaton import graph_to_nfa, regex_to_dfa

MatrixType = TypeVar(
    "MatrixType", bound=Union[csr_matrix, csc_matrix, dok_matrix, lil_matrix]
)


def ms_bfs_based_rpq(
    regex: str,
    graph: MultiDiGraph,
    start_nodes: Optional[set[int]] = None,
    final_nodes: Optional[set[int]] = None,
    matrix_type: Optional[type[MatrixType]] = None,
) -> set[tuple[int, int]]:
    matrix_type = cast(type[MatrixType], matrix_type or csr_matrix)
    start_nodes = start_nodes or set(graph.nodes)
    final_nodes = final_nodes or set(graph.nodes)
    dfa = AdjacencyMatrixFA(regex_to_dfa(regex), matrix_type)
    nfa = AdjacencyMatrixFA(graph_to_nfa(graph, start_nodes, final_nodes), matrix_type)

    symbols = dfa.matrices.keys() & nfa.matrices.keys()
    permutation_matrices = {s: dfa.matrices[s].transpose() for s in symbols}

    start_states = tuple(product(dfa.start_states, nfa.start_states))

    k = dfa.states_count
    m = nfa.states_count

    def init_matrix(dfa_idx, nfa_idx):
        matrix = matrix_type((k, m), dtype=bool)
        matrix[dfa_idx, nfa_idx] = True
        return matrix

    matrices = [init_matrix(dfa_idx, nfa_idx) for dfa_idx, nfa_idx in start_states]
    front = vstack(matrices, "csr", dtype=bool)
    visited = front

    while front.nnz > 0:
        next_front = []
        for symbol in symbols:
            symbols_front = front @ nfa.matrices[symbol]
            next_front.append(
                vstack(
                    [
                        permutation_matrices[symbol]
                        @ symbols_front[k * i : k * (i + 1)]
                        for i in range(len(start_states))
                    ]
                )
            )

        front = functools.reduce(operator.add, next_front, front) > visited
        visited = visited + front

    nfa_states = {i: state for i, state in enumerate(nfa.states)}
    res: set[tuple[int, int]] = set()
    for i, nfa_start_idx in enumerate(nfa.start_states):
        for final_dfa_state in dfa.final_states:
            reached = visited[k * i : k * (i + 1)].getrow(final_dfa_state).indices
            res.update(
                (
                    (nfa_states[nfa_start_idx], nfa_states[dfa_st_idx])
                    for dfa_st_idx in reached
                    if dfa_st_idx in nfa.final_states
                )
            )

    return res
