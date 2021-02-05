import numpy
import networkx
import threading
from libary.result import Result

class EdgeDistanceFilter:
    def __init__(self):
        pass

    def get_name(self):
        return 'Filter:EdgeDistance'

    def apply(self, input, parameters: dict, old_results: list):
        parameter_p = float(parameters['parameter_p'])
        knn_distances = input.get_resulting_knn_distances()
        input_undirected_knn_graph = input.get_undirected_knn_graph()

        connected_components = networkx.algorithms.connected_components(input_undirected_knn_graph)
        parsed_component = list()
        for x in connected_components:
            parsed_component.append([a for a in x])

        worker_list = list()
        for component in parsed_component:
            if len(component) == 1:
                continue
            worker = Worker(nodes=component, parameter_p=parameter_p, distances=knn_distances, input_graph=input_undirected_knn_graph)
            worker_list.append(worker)
            worker.run()

        new_undirected_graph = input.get_undirected_knn_graph().copy()
        deleted_edges = set()
        for worker in worker_list:
            worker.join()
            for a, b in worker.edges_to_delete:
                new_undirected_graph.remove_edge(a, b)
                deleted_edges.add((a, b))

        result = Result(parameter=parameters,
                        intermediate_result={},
                        undirected_knn_graph=new_undirected_graph,
                        deletion_set=deleted_edges,
                        data=input.get_resulting_data(),
                        knn_distances=input.get_resulting_knn_distances(),
                        directed_knn_graph=input.get_directed_knn_graph())
        return result

    def get_controls(self) -> list:
        controls = list()
        controls.append({'title': 'p', 'id': 'parameter_p', 'type': 'float'})
        return controls

    def get_gui_name(self) -> str:
        return 'Edge-Distance Filter'

    def get_tooltip(self):
        return 'Classifies edges which are longer than a threshold as unwanted. This filter is a good choice to be applied frist.'

    def get_default_parameter(self) -> dict:
        return {'parameter_p': 3}


class Worker:
    def __init__(self, nodes, distances, parameter_p: float, input_graph: networkx.Graph):
        self.nodes = nodes
        self.distances = distances
        self.parameter_p = parameter_p
        self.edges_to_delete = set()
        self.input_graph = input_graph
        self.__thread = threading.Thread(target=self.__work)

    def run(self):
        self.__thread.start()

    def join(self):
        self.__thread.join()

    def __work(self):
        local_distances = dict()
        for node in self.nodes:
            for (a, b) in self.input_graph.edges(node):
                if (b, a) in local_distances:
                    continue
                local_distances[(a, b)] = self.distances[(a, b)]
        distance_values = list(local_distances.values())
        threshold = numpy.mean([distance_values]) + self.parameter_p * numpy.std([distance_values])
        self.edges_to_delete = {x for x in local_distances if local_distances[x] > threshold}
