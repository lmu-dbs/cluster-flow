from libary.result import Result
import networkx


class MinPointsFilter:
    def __init__(self):
        pass

    def get_name(self):
        return 'Filter:MinPoints'

    def apply(self, input: Result, parameters: dict, old_results: list):
        input_undirected_knn_graph = input.get_undirected_knn_graph()
        parameter_threshold_min_points = float(parameters['threshold_min_points'])

        connected_components = networkx.algorithms.connected_components(input_undirected_knn_graph)
        parsed_component = list()
        for x in connected_components:
            parsed_component.append([a for a in x])

        edges_to_delete = set()
        for component in parsed_component:
            if len(component) < parameter_threshold_min_points:
                for node in component:
                    for a, b in input_undirected_knn_graph.edges(node):
                        edges_to_delete.add((a, b))

        new_undirected_graph = input_undirected_knn_graph.copy()
        for a, b in edges_to_delete:
            try:
                new_undirected_graph.remove_edge(a, b)
            except networkx.exception.NetworkXError:
                try:
                    new_undirected_graph.remove_edge(b, a)
                except:
                    pass

        result = Result(parameter=parameters,
                        intermediate_result={},
                        undirected_knn_graph=new_undirected_graph,
                        deletion_set=edges_to_delete,
                        data=input.get_resulting_data(),
                        knn_distances=input.get_resulting_knn_distances(),
                        directed_knn_graph=input.get_directed_knn_graph())
        return result

    def get_controls(self) -> list:
        controls = list()
        controls.append({'title': 'min points', 'id': 'threshold_min_points', 'type': 'int'})
        return controls

    def get_gui_name(self) -> str:
        return 'Min-Points Filter'

    def get_tooltip(self):
        return 'This filter classifies all edges as unwanted of connected components which contain less points than the parameter "min points".'

    def get_default_parameter(self) -> dict:
        return {'threshold_min_points': 2}
