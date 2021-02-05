from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Binary, Enum, Text
from sqlalchemy.orm import relationship, backref
from .database import BASE
import pickle
import json
from .filters import *
from helper.image_creator import ImageCreator
import enum


ALL_FILTERS = list()
ALL_FILTERS.append(EdgeDistanceFilter())
ALL_FILTERS.append(EdgeBetweennessFilter())
ALL_FILTERS.append(InterDensityConnectionFilter())
ALL_FILTERS.append(MinPointsFilter())
ALL_FILTERS.append(DistanceOfInboundEdgesFilter())


class FilterStatus(enum.Enum):
    RECALULATION_NEEDED = 0
    PARAMETER_CHANGED = 1
    RUNNING = 2
    READY = 3


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


class Filter(BASE):
    __tablename__ = 'filter'
    id = Column(Integer, primary_key=True)

    name = Column(String)       # name of the filter class

    parameter = Column(String)  # As json encoded dict

    expression_id = Column(Integer, ForeignKey('expressions.id'))
    expression = relationship('Expression', back_populates='filter_list')

    results = relationship('Result', back_populates='filter', foreign_keys="[Result.filter_id]")

    status = Column(Enum(FilterStatus), default=FilterStatus.RECALULATION_NEEDED)

    selected_image_parameter = Column(Text)

    __real_filter = None

    def __init__(self, name):
        self.name = name
        self.parameter = json.dumps(self.__get_filter().get_default_parameter())

    def update_parameter(self, parameters: dict):
        self.parameter = json.dumps(parameters)

    def get_decoded_parameters(self):
        return json.loads(self.parameter)

    def get_selected_image_parameter(self) -> dict or None:
        if self.selected_image_parameter is None:
            return None
        return json.loads(self.selected_image_parameter)

    def __get_filter(self):
        if self.__real_filter is None:
            for x in ALL_FILTERS:
                if x.get_name() == self.name:
                    self.__real_filter = x
                    break
        return self.__real_filter

    def get_picture(self, parameter: dict):
        self.selected_image_parameter = json.dumps(parameter)
        current_result = self.get_current_result()
        return current_result.get_picture(parameter=parameter)

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'parameter': self.get_decoded_parameters(),
                'status': self.status.value,
                'gui_name': self.__get_filter().get_gui_name(),
                'controls': self.__get_filter().get_controls(),
                'tooltip': self.__get_filter().get_tooltip(),
                'selected_image': self.get_selected_image_parameter()}

    def get_current_result(self):
        for r in self.results:
            if equal_dict(a=r.get_decoded_parameters(), b=self.get_decoded_parameters()):
                return r

    def apply(self):
        if self.get_current_result() is not None:
            return

        real_filter = self.__get_filter()
        result = real_filter.apply(input=self.expression.get_input_result(),
                                   parameters=self.get_decoded_parameters(),
                                   old_results=self.results)
        self.results.append(result)
