import numpy
from helper.knn import KNN


class RockPreclustering:
    def __init__(self):
        pass

    @staticmethod
    def apply(input_data, parameters: dict):
        parameter_iterations = int(parameters['iterations'])
        parameter_k = int(parameters['k'])

        new_positions = input_data

        for iteration in range(0, parameter_iterations):
            kNN = KNN(database=input_data, k=parameter_k)
            new_positions = list()
            for point_index in range(len(input_data)):
                _, neighbors = kNN.get_neighbourhood_points(point_index=point_index)
                new_position = RockPreclustering.__calculate_new_pos(points=neighbors, input_data=input_data)
                new_positions.append(new_position)
            new_positions = numpy.array(new_positions)

        return new_positions

    @staticmethod
    def __calculate_new_pos(points, input_data):
        mean = numpy.zeros(shape=input_data[0].shape)
        for k in points:
            mean += input_data[k]
        return mean / len(points)
