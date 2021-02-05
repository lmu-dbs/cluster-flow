from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Binary, Enum, Text
from sqlalchemy.orm import relationship, backref
from .database import BASE
import pickle
import json
from .filters import *
from helper.image_creator import ImageCreator
import numpy
from networkx import Graph


class Result(BASE):
    __tablename__ = 'result'
    id = Column(Integer, primary_key=True)

    parameter = Column(String)  # As json encoded dict

    intermediate_result = Column(Binary)

    __directed_knn_graph = Column(Binary)       # dict saved as pickle
    __undirected_knn_graph = Column(Binary)     # dict saved as pickle
    __resulting_deletion_set = Column(Binary)   # set saved as pickle
    __data = Column(Binary)                     # set saved as pickle
    __knn_distances = Column(Binary)            # set saved as pickle

    image_list = relationship('Image', back_populates='result', foreign_keys="[Image.result_id]")

    filter_id = Column(Integer, ForeignKey('filter.id'))
    filter = relationship('Filter')

    expression_id = Column(Integer, ForeignKey('expressions.id'))
    expression = relationship('Expression')

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project')

    def __init__(self, parameter: dict, intermediate_result: dict, undirected_knn_graph: Graph, deletion_set: set,
                 data: numpy.array, knn_distances: dict, directed_knn_graph: dict):
        self.parameter = json.dumps(parameter)
        self.intermediate_result = pickle.dumps(intermediate_result)
        self.__directed_knn_graph = pickle.dumps(directed_knn_graph)
        self.__undirected_knn_graph = pickle.dumps(undirected_knn_graph)
        self.__resulting_deletion_set = pickle.dumps(deletion_set)
        self.__data = pickle.dumps(data)
        self.__knn_distances = pickle.dumps(knn_distances)

    def get_resulting_knn_distances(self) -> numpy.array:
        return pickle.loads(self.__knn_distances)

    def get_intermediate_result(self) -> dict:
        return pickle.loads(self.intermediate_result)

    def get_resulting_data(self) -> numpy.array:
        return pickle.loads(self.__data)

    def get_directed_knn_graph(self) -> dict:
        return pickle.loads(self.__directed_knn_graph)

    def get_undirected_knn_graph(self) -> Graph:
        return pickle.loads(self.__undirected_knn_graph)

    def get_resulting_deletion_set(self) -> set:
        return pickle.loads(self.__resulting_deletion_set)

    def get_decoded_parameters(self) -> dict:
        return json.loads(self.parameter)

    def get_picture(self, parameter: dict):
        for image in self.image_list:
            if image.equals(parameter):
                return image
        image_creator = ImageCreator()
        new_image = image_creator.create_image(data=self.get_resulting_data(),
                                               knn_graph=self.get_undirected_knn_graph(),
                                               parameter=parameter)
        self.image_list.append(new_image)
        return new_image

