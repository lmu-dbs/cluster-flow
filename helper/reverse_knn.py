from sklearn.neighbors import NearestNeighbors


class ReverseKNN:
    def __init__(self, database, k):
        knn_neighbourhood = NearestNeighbors(n_neighbors=k)
        knn_neighbourhood.fit(database)
        self.reverse_knn_neighbourhood = dict()
        for index in range(len(database)):
            point = database[index]
            distances, kNN_points = knn_neighbourhood.kneighbors([point], return_distance=True)
            kNN_points = list(kNN_points[0])
            distances = distances[0]
            if index not in kNN_points:
                kNN_points.pop()
                kNN_points.append(index)
            for kNN_point, distance in zip(kNN_points, distances):
                if kNN_point in self.reverse_knn_neighbourhood:
                    self.reverse_knn_neighbourhood[kNN_point].append((index, distance))
                else:
                    self.reverse_knn_neighbourhood[kNN_point] = [(index, distance)]

    def get_neighbourhood_points(self, point_index):
        if point_index not in self.reverse_knn_neighbourhood:
            return [0], [point_index]
        points = list()
        distances = list()
        for kNN_point, distance in self.reverse_knn_neighbourhood[point_index]:
            points.append(kNN_point)
            distances.append(distance)
        return distances, points

    def range_query(self, point_index, range):
        points = list()
        for kNN_point, distance in self.reverse_knn_neighbourhood[point_index]:
            if distance <= range:
                points.append(kNN_point)
        return points

