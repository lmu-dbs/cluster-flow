from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Binary
from .database import BASE
from sqlalchemy.orm import relationship, backref
import pickle
import numpy
from helper.image_creator import ImageCreator
from .image import Image


class Dataset(BASE):
    __tablename__ = 'dataset'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    _data = Column(Binary)

    number_of_rows = Column(Integer)
    number_of_dimensions = Column(Integer)

    image_list = relationship('Image', back_populates='dataset')

    def __init__(self, name: str, data: numpy.array, number_of_rows: int, number_of_dimensions: int):
        self.name = name
        self.number_of_rows = number_of_rows
        self.number_of_dimensions = number_of_dimensions
        self._data = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)

    def get_data(self) -> numpy.array:
        return pickle.loads(self._data)

    data = property(fget=get_data)

    def get_picture(self, parameter: dict):
        for image in self.image_list:
            if image.equals(parameter):
                return image
        image_creator = ImageCreator()
        new_image = image_creator.create_image(data=self.get_data(), knn_graph=None, parameter=parameter)
        return new_image

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'number_of_rows': self.number_of_rows,
                'number_of_dimensions': self.number_of_dimensions}
