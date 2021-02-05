from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Binary, Text
from sqlalchemy.orm import relationship, backref
from .database import BASE
#from .result import Result
import json


class Image(BASE):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)

    parameter = Column(Text)  # json encoded dict

    picture = Column(Text)

    result_id = Column(Integer, ForeignKey('result.id'))
    result = relationship('Result', back_populates='image_list', post_update=True, foreign_keys="[Image.result_id]")

    dataset_id = Column(Integer, ForeignKey('dataset.id'))
    dataset = relationship('Dataset', back_populates='image_list', post_update=True, foreign_keys="[Image.dataset_id]")

    def __init__(self, parameter, picture):
        self.parameter = json.dumps(parameter)
        self.picture = picture

    def equals(self, parameter):
        for key in parameter:
            if key not in json.loads(self.parameter):
                return False
            if json.loads(self.parameter)[key] != parameter[key]:
                return False
        return True

    def get_image(self):
        return self.picture
