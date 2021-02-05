import numpy
from libary.result import Result
import threading
import networkx


class InterDensityConnectionFilter:
    def __init__(self):
        pass

    def get_name(self):
        return 'Filter:InterDensityConnection'

    def get_tooltip(self):
        return 'This filter is a good choice to separate points in a dense neighbourhood from points which are in a sparse one. The density esimation of the neighborhood is done by taking the distance to the k nearest neighbours into account.'

    def apply(self, input: Result, parameters: dict, old_results: list):
        input_undirected_knn_graph = input.get_undirected_knn_graph()
        input_directed_knn_graph = input.get_directed_knn_graph()
        knn_distances = input.get_resulting_knn_distances()

        parameter_p = float(parameters['parameter_p'])

        # Calculation of the sparseness estimation for each point
        if len(old_results) > 0:
            sparseness_estimation = old_results.pop().get_intermediate_result()['sparseness']
        else:
            edges = {x: set() for x in input_undirected_knn_graph.nodes()}
            for a, b in input_undirected_knn_graph.edges():
                edges[a].add(b)
                edges[b].add(a)
            sparseness_estimation = dict()
            for a in input_directed_knn_graph:
                list_of_distances = list()
                for b in input_directed_knn_graph[a]:
                    if b in edges[a]:
                        list_of_distances.append(knn_distances[(a, b)])
                if len(list_of_distances) == 0:
                    sparseness_estimation[a] = -1
                else:
                    sparseness_estimation[a] = numpy.mean(list_of_distances)

        intermediate_result = {'sparseness': sparseness_estimation}

        connected_components = networkx.algorithms.connected_components(input_undirected_knn_graph)
        parsed_component = list()
        for x in connected_components:
            parsed_component.append([a for a in x])

        worker_list = list()
        for component in parsed_component:
            if len(component) == 1:
                continue
            worker = Worker(nodes=component, parameter_p=parameter_p, input_graph=input_undirected_knn_graph, sparseness_estimation=sparseness_estimation)
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
                        intermediate_result=intermediate_result,
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
        return 'Inter-Density Connection Filter'

    def get_default_parameter(self) -> dict:
        return {'parameter_p': 3}


class Worker:
    def __init__(self, nodes, parameter_p: float, input_graph: networkx.Graph, sparseness_estimation: dict):
        self.parameter_p = parameter_p
        self.edges_to_delete = set()
        self.sparseness_estimation = sparseness_estimation
        self.input_graph = input_graph.subgraph(nodes)  # only graph of the connected component
        self.__thread = threading.Thread(target=self.__work)

    def run(self):
        self.__thread.start()

    def join(self):
        self.__thread.join()

    def __work(self):
        sparseness_differences = list()
        for a, b in self.input_graph.edges():
            sparseness_a = self.sparseness_estimation[a]
            sparseness_b = self.sparseness_estimation[b]
            sparseness_diff = abs(sparseness_a - sparseness_b)
            sparseness_differences.append((sparseness_diff, a, b))
        sparseness_diff_values = [x[0] for x in sparseness_differences]
        threshold = numpy.mean(sparseness_diff_values) + self.parameter_p * numpy.std(sparseness_diff_values)
        for diff, a, b in sparseness_differences:
            if diff >= threshold:
                self.edges_to_delete.add((a, b))
