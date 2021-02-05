from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Text, Binary, Enum
from sqlalchemy.orm import relationship, backref
from .database import BASE
from .filter import Filter, FilterStatus
import json
import pickle
from helper.image_creator import ImageCreator
from .image import Image

def equal_dict(a: dict, b: dict):
    for i in a:
        if i not in b:
            return False
    for i in b:
        if i not in a:
            return False
        if a[i] != b[i]:
            return False
    return True


class Project(BASE):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    dataset_id = Column(Integer, ForeignKey('dataset.id'))
    dataset = relationship('Dataset')

    preclustering_rock_parameters = Column(Text)
    preclustering_rock_data = Column(Binary)
    preclustering_rock_status = Column(Enum(FilterStatus), default=FilterStatus.READY)
    preclustering_rock_image_parameters = Column(Text)
    preclustering_rock_image_id = Column(Integer, ForeignKey('images.id'))
    preclustering_rock_image = relationship('Image', foreign_keys="[Project.preclustering_rock_image_id]")

    expression_list = relationship('Expression', back_populates="project")

    parameter_dataset_image_id = Column(Integer, ForeignKey('images.id'))
    parameter_dataset_image = relationship('Image', foreign_keys="[Project.parameter_dataset_image_id]")

    knn_graph_selected_image_parameter = Column(Text)

    knn_graph_generation_status = Column(Enum(FilterStatus), default=FilterStatus.RECALULATION_NEEDED)

    results = relationship('Result', back_populates='project', foreign_keys="[Result.project_id]")

    __knn_graph_generation_parameters = Column(Text)  # dict saved as json

    def __init__(self, name, dataset):
        self.name = name
        self.dataset = dataset

    def set_knn_graph_selected_image_parameter(self, parameters: dict) -> None:
        self.knn_graph_selected_image_parameter = json.dumps(parameters)

    def get_knn_graph_selected_image_parameter(self) -> dict or None:
        if self.knn_graph_selected_image_parameter is None:
            return None
        return json.loads(self.knn_graph_selected_image_parameter)

    def get_rock_selected_image_parameter(self) -> dict or None:
        if self.preclustering_rock_image_parameters is None:
            return None
        return json.loads(self.preclustering_rock_image_parameters)

    def get_current_result(self):
        for r in self.results:
            if equal_dict(a=r.get_decoded_parameters(), b=self.get_knn_graph_generation_parameters()):
                return r

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'dataset': self.dataset.to_dict(),
                'expressions': [x.to_dict() for x in self.expression_list],
                'parameter_dataset_image': self.parameter_dataset_image_id,
                'knn_graph_generation': {
                    'parameter': self.get_knn_graph_generation_parameters(),
                    'selected_image': self.get_knn_graph_selected_image_parameter(),
                    'status': self.knn_graph_generation_status.value,
                    'tooltip': 'Generation of the kNN graph which is used for the following clustering. Parameter k determines the number of neighbours which are considered.'
                },
                'rock': {
                    'parameter': self.get_rock_parameters(),
                    'selected_image': self.get_rock_selected_image_parameter(),
                    'status': self.preclustering_rock_status.value,
                    'tooltip': 'Rock can be used to precluster the dataset. The points roam to themself by moving to the average position of their kNN neighbours. (If not used, simply skip calculation or set iterations and k to 0)'
                }
        }

    def get_rock_parameters(self) -> dict or None:
        if self.preclustering_rock_parameters is None:
            return {'k': 0, 'iterations': 0}
        return json.loads(self.preclustering_rock_parameters)

    def get_knn_graph_generation_parameters(self) -> dict or None:
        if self.__knn_graph_generation_parameters is None:
            return {'k': 10, 'graph-type': 'sym kNN-Graph'}
        return json.loads(self.__knn_graph_generation_parameters)

    def set_knn_graph_generation_parameters(self, parameters: dict) -> None:
        self.__knn_graph_generation_parameters = json.dumps(parameters)

    def get_picture(self, parameter: dict):
        self.set_knn_graph_selected_image_parameter(parameters=parameter)
        current_result = self.get_current_result()
        return current_result.get_picture(parameter=parameter)
