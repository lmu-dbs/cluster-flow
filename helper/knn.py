from sklearn.neighbors import NearestNeighbors


class KNN:
    def __init__(self, database, k):
        self.neighbourhood = NearestNeighbors(n_neighbors=k)
        self.neighbourhood.fit(database)
        self.database = database

    def get_neighbourhood_points(self, point_index):
        distances, kNN_points = self.neighbourhood.kneighbors([self.database[point_index]], return_distance=True)
        return distances[0], kNN_points[0]

    def range_query(self, point_index, range):
        return self.neighbourhood.radius_neighbors([self.database[point_index]], range, return_distance=False)[0]
