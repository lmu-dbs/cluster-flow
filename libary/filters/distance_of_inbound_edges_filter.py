import numpy
from libary.result import Result
import threading
import networkx


class DistanceOfInboundEdgesFilter:
    def __init__(self):
        pass

    def get_name(self):
        return 'Filter:DistanceOfInboundEdges'

    def get_tooltip(self):
        return 'This filter classifies all incoming edges to a node as unwanted which have a higher distance than a threshold.'

    def get_default_parameter(self) -> dict:
        return {'parameter_p': 3}

    def apply(self, input: Result, parameters: dict, old_results: list):
        input_undirected_knn_graph = input.get_undirected_knn_graph()
        input_directed_knn_graph = input.get_directed_knn_graph()
        knn_distances = input.get_resulting_knn_distances()
        rknn = {idx: list(idx2 for idx2, i in input_directed_knn_graph.items() if idx2 != idx and idx in i)
                for idx, j in input_directed_knn_graph.items()}

        parameter_p = float(parameters['parameter_p'])

        unwanted_edges = set()

        if len(old_results) > 0:
            total_considered_edges = old_results.pop().get_intermediate_result()['considered_edges']
        else:
            total_considered_edges = dict()
            edges = set(x for x in input_undirected_knn_graph.edges())
            for a in input_directed_knn_graph:
                considered_edges = dict()
                for b in rknn[a]:
                    if a == b:
                        continue
                    if (a, b) in edges or (b, a) in edges:
                        considered_edges[(a, b)] = knn_distances[(a, b)]
                total_considered_edges[a] = considered_edges

        for node in total_considered_edges:
            values = [x for x in total_considered_edges[node].values()]
            threshold = numpy.mean(values) + parameter_p * numpy.std(values)

            for edge in total_considered_edges[node]:
                if total_considered_edges[node][edge] > threshold:
                    unwanted_edges.add(edge)

        new_undirected_graph = input_undirected_knn_graph.copy()
        for edge in unwanted_edges:
            try:
                new_undirected_graph.remove_edge(*edge)
            except:
                pass

        intermediate_result = {'considered_edges': total_considered_edges}

        result = Result(parameter=parameters,
                        intermediate_result=intermediate_result,
                        undirected_knn_graph=new_undirected_graph,
                        deletion_set=unwanted_edges,
                        data=input.get_resulting_data(),
                        knn_distances=input.get_resulting_knn_distances(),
                        directed_knn_graph=input.get_directed_knn_graph())
        return result

    def get_controls(self) -> list:
        controls = list()
        controls.append({'title': 'p', 'id': 'parameter_p', 'type': 'float'})
        return controls

    def get_gui_name(self) -> str:
        return 'Distance of Incoming Edges Filter'
