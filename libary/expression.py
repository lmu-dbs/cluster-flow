from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Table, Binary, Enum, Text
from sqlalchemy.orm import relationship, backref
from .database import BASE
import enum
import pickle
from helper.image_creator import ImageCreator
from .filter import FilterStatus
import json
from .result import Result
from networkx import Graph


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


class Expression(BASE):
    __tablename__ = 'expressions'
    id = Column(Integer, primary_key=True)

    required_filter = Column(Integer, default=1)

    parent_expression_id = Column(Integer, ForeignKey('expressions.id'))
    parent_expression = relationship('Expression', foreign_keys="[Expression.parent_expression_id]", uselist=False)

    child_expression_id = Column(Integer, ForeignKey('expressions.id'))
    child_expression = relationship('Expression', foreign_keys="[Expression.child_expression_id]", uselist=False, post_update=True)

    filter_list = relationship('Filter', back_populates='expression')

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates='expression_list')

    results = relationship('Result', back_populates='expression', foreign_keys="[Result.expression_id]")

    selected_image_parameter = Column(Text)

    status = Column(Enum(FilterStatus), default=FilterStatus.RECALULATION_NEEDED)

    def __init__(self):
        pass

    def set_selected_image_parameter(self, parameters: dict) -> None:
        self.selected_image_parameter = json.dumps(parameters)

    def get_selected_image_parameter(self) -> dict or None:
        if self.selected_image_parameter is None:
            return None
        return json.loads(self.selected_image_parameter)

    def get_current_result(self):
        if len(self.filter_list) == 1:
            return self.filter_list[0].get_current_result()
        for r in self.results:
            if equal_dict(a=r.get_decoded_parameters(), b={'required_filter': self.required_filter}):
                return r

    def get_picture(self, parameter: dict):
        current_result = self.get_current_result()
        return current_result.get_picture(parameter=parameter)

    def to_dict(self):
        return {'id': self.id,
                'required_filter': self.required_filter,
                'filters': [x.to_dict() for x in self.filter_list],
                'status': self.status.value,
                'selected_image': self.get_selected_image_parameter()
        }

    def get_input_result(self):
        if self.parent_expression is None:
            return self.project.get_current_result()
        return self.parent_expression.get_current_result()

    def new_calculation_required(self, database):
        self.results.clear()

        self.status = FilterStatus.RECALULATION_NEEDED
        for x in self.filter_list:
            x.results.clear()
            x.status = FilterStatus.RECALULATION_NEEDED
        if self.child_expression is not None:
            self.child_expression.new_calculation_required(database)

    def apply(self):
        input = self.get_input_result()

        if len(self.filter_list) == 1:
            return

        for filter in self.filter_list:
            if filter.status != FilterStatus.READY:
                raise ValueError('Not all filters are ready')

        deletion_sets = dict()
        for x in self.filter_list:
            unwanted_edges = x.get_current_result().get_resulting_deletion_set()
            for edge in unwanted_edges:
                if edge in deletion_sets:
                    deletion_sets[edge] += 1
                else:
                    deletion_sets[edge] = 1

        result_deletion_set = set()

        for edge in deletion_sets:
            if deletion_sets[edge] >= self.required_filter:
                result_deletion_set.add(edge)

        new_undirected_knn_graph = input.get_undirected_knn_graph().copy()
        for a, b in result_deletion_set:
            new_undirected_knn_graph.remove_edge(a, b)

        result = Result(parameter={'required_filter': self.required_filter},
                        intermediate_result={},
                        undirected_knn_graph=new_undirected_knn_graph,
                        deletion_set=result_deletion_set,
                        data=input.get_resulting_data(),
                        knn_distances=input.get_resulting_knn_distances(),
                        directed_knn_graph=input.get_directed_knn_graph())
        self.results.append(result)

