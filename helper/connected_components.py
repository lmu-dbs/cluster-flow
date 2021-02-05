
def get_connected_components(graph):
    """
    returns the connected components
    """
    clusters = dict()
    cluster_counter = 0
    visited = set()
    for point in graph:
        if point in visited:
            continue
        else:
            new_cluster_index = cluster_counter
            cluster_counter += 1
            visited.add(point)
            clusters[new_cluster_index] = {point}
            remaining_points = set(graph[point])
            while len(remaining_points) > 0:
                point_i = remaining_points.pop()
                if point_i in visited:
                    continue
                visited.add(point_i)
                clusters[new_cluster_index].add(point_i)
                remaining_points.update(graph[point_i])
    return clusters
