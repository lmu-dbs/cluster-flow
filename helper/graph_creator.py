from helper.knn import KNN
from collections import namedtuple
import networkx as nx


InitialKnnGraph = namedtuple('InitialKnnGraph', 'directed_knn_graph undirected_knn_graph distances')


def generate_initial_knn_graph(data, parameters: dict) -> InitialKnnGraph:
    directed_knn_graph, distances = __create_directed_knn_graph(database=data, k=int(parameters['k']))
    if parameters['graph-type'] == 'MkNN-Graph':
        undirected_knn_graph = __create_mutual_knn_graph(graph_directed=directed_knn_graph, distances=distances)
    elif parameters['graph-type'] == 'sym kNN-Graph':
        undirected_knn_graph = __create_symmetric_knn_graph(graph_directed=directed_knn_graph, distances=distances)
    else:
        raise AttributeError(parameters['graph-type'])
    return InitialKnnGraph(directed_knn_graph, undirected_knn_graph, distances)


def __create_directed_knn_graph(database, k: int):
    """
    returns an undirected kNN-Graph for the given dataset
    """
    neighbourhood = KNN(k=k, database=database)
    distances_cache = dict()
    graph_directed = dict()
    for index in range(len(database)):
        distances, points = neighbourhood.get_neighbourhood_points(point_index=index)
        graph_directed[index] = set()
        knn_counter = 0
        for p, d in zip(points, distances):
            distances_cache[(index, p)] = d
            distances_cache[(p, index)] = d
            graph_directed[index].add(p)
            knn_counter += 1
    return graph_directed, distances_cache


def __create_symmetric_knn_graph(graph_directed: dict, distances: dict) -> nx.Graph:
    symmetric_knn_graph = nx.Graph()
    for a in graph_directed:
        symmetric_knn_graph.add_node(a)
        for b in graph_directed[a]:
            if a == b:
                continue
            symmetric_knn_graph.add_edge(a, b, weight=distances[(a, b)])
    return symmetric_knn_graph


def __create_mutual_knn_graph(graph_directed: dict, distances: dict) -> nx.Graph:
    mutual_knn_graph = nx.Graph()
    for a in graph_directed:
        mutual_knn_graph.add_node(a)
        for b in graph_directed[a]:
            if a == b:
                continue
            if a in graph_directed[b]:
                mutual_knn_graph.add_edge(a, b, weight=distances[(a, b)])
    return mutual_knn_graph
