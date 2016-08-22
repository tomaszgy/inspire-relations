# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


from graph_representation import GraphModel, GraphModelType, Node

from utils import extract_element


class GraphModelBuilder:

    def __init__(self, model_type=GraphModelType,
                 element_types=None, graph_updaters=None):
        self._model_type = model_type
        self._element_types = (element_types
                               if element_types is not None else {})
        self._graph_updaters = (graph_updaters
                                if graph_updaters is not None else {})

    def element_processor(self, field, musts=[]):
        def decorator(processor):
            self._graph_updaters[processor.func_name] = processor
            self._element_types[processor.func_name] = (field, musts)
            return processor
        return decorator

    def update_graph_model(self, graph_model, element_type, element):
        self._graph_updaters[element_type](graph_model, element)

    def build(self, record):
        graph_model = GraphModel(
            central_node_type=self._model_type.central_node_type)

        for element_type, element_definition in self._element_types.items():
            elements = extract_element(record, element_definition[0],
                                       element_definition[1])
            for element in elements:
                self.update_graph_model(graph_model, element_type, element)

        return graph_model
