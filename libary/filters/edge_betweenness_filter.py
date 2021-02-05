from libary.result import Result
import networkx
import threading


class EdgeBetweennessFilter:
    def __init__(self):
        pass

    def get_name(self):
        return 'Filter:EdgeBetweeness'

    def apply(self, input: Result, parameters: dict, old_results: list):
        input_undirected_knn_graph = input.get_undirected_knn_graph()

        parameter_p = float(parameters['parameter_p'])
        iterations = int(parameters['iterations'])

        ########################################################
        deletion_set_before_start = None
        start_iteration = None
        for old_result in old_results:
            if old_result.get_decoded_parameters()['parameter_p'] == parameter_p:       # p has to be the same
                old_intermediate_result = old_result.get_intermediate_result()
                key = max([x for x in old_intermediate_result.keys() if x < iterations])
                if start_iteration is None or key > start_iteration:
                    start_iteration = key
                    deletion_set_before_start = old_intermediate_result[key]

        new_undirected_graph = input_undirected_knn_graph.copy()

        if deletion_set_before_start is None:
            start_iteration = 1
        else:
            for a, b in deletion_set_before_start:
                new_undirected_graph.remove_edge(a, b)

        ######################################################### new application
        intermediate_result = dict()
        total_deleted_edges = set()
        for i in range(start_iteration, iterations+1):
            connected_components = networkx.algorithms.connected_components(new_undirected_graph)
            parsed_component = list()
            for x in connected_components:
                parsed_component.append([a for a in x])

            worker_list = list()
            for component in parsed_component:
                if len(component) == 1:
                    continue
                worker = Worker(nodes=component, parameter_p=parameter_p, input_graph=new_undirected_graph)
                worker_list.append(worker)
                worker.run()

            deleted_edges = set()
            for worker in worker_list:
                worker.join()
                for a, b in worker.edges_to_delete:
                    try:
                        new_undirected_graph.remove_edge(a, b)
                        deleted_edges.add((int(a), int(b)))
                    except:
                        try:
                            new_undirected_graph.remove_edge(b, a)
                            deleted_edges.add((int(b), int(a)))
                        except:
                            continue
            intermediate_result[i] = list(deleted_edges)
            total_deleted_edges = total_deleted_edges.union(deleted_edges)

        result = Result(parameter=parameters,
                        intermediate_result=intermediate_result,
                        undirected_knn_graph=new_undirected_graph,
                        deletion_set=total_deleted_edges,
                        data=input.get_resulting_data(),
                        knn_distances=input.get_resulting_knn_distances(),
                        directed_knn_graph=input.get_directed_knn_graph())
        return result

    def get_controls(self) -> list:
        controls = list()
        controls.append({'title': 'iterations', 'id': 'iterations', 'type': 'int'})
        controls.append({'title': 'p', 'id': 'parameter_p', 'type': 'float'})
        return controls

    def get_gui_name(self) -> str:
        return 'Edge-Betweenness Filter'

    def get_tooltip(self):
        return 'This filter is a good choice to identify bridges between clusters. It works on the basis of the edge-betweenness concept of the Girvan-Newman algorithm.'

    def get_default_parameter(self) -> dict:
        return {'iterations': 1, 'parameter_p': 0.0075}


class Worker:
    def __init__(self, nodes, parameter_p: float, input_graph: networkx.Graph):
        self.parameter_p = parameter_p
        self.edges_to_delete = set()
        self.input_graph = networkx.Graph(input_graph.subgraph(nodes))  # only graph of the connected component
        self.__thread = threading.Thread(target=self.__work)

    def run(self):
        self.__thread.start()

    def join(self):
        self.__thread.join()

    def __work(self):
        edge_betweenness = networkx.edge_betweenness_centrality(self.input_graph, weight='weight')
        edge_betweenness = [x for x in edge_betweenness.items()]
        edge_betweenness = sorted(edge_betweenness, key=lambda x: x[1], reverse=True)
        for k, v in edge_betweenness[:max(int(self.parameter_p * self.input_graph.number_of_edges()), 1)]:
            self.edges_to_delete.add((k[0], k[1]))
            self.input_graph.remove_edge(k[0], k[1])
