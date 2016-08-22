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

from inspire_relations.exceptions import (
    CannotCompare,
    MissingNodeUid,
    NodeUidAlreadySet
    )

import json


class Node(object):

    DEFAULT_LABELS = set([])

    def __init__(self, labels=None, properties=None, uid=None):
        self._uid = uid
        self.properties = properties if properties is not None else {}
        self.labels = (
            (labels if labels is not None else set()) | self.DEFAULT_LABELS
            )

    @property
    def uid(self):
        if self._uid:
            return self._uid
        else:
            raise MissingNodeUid()

    @uid.setter
    def uid(self, value):
        if self._uid is None:
            self._uid = value
        else:
            raise NodeUidAlreadySet()

    @staticmethod
    def generate_uid(*args, **kwargs):
        raise NotImplementedError()

    def gen_and_set_uid(self, *args, **kwargs):
        self.uid = self.generate_uid(*args, **kwargs)

    def get_graph_model(self):
        return GraphModel(central_node=self)

    def __hash__(self):
        if not hasattr(self, '_hash_value'):
            try:
                uid = self.uid
            except MissingNodeUid:
                raise TypeError('Node is unhashable: missing UID.')
            self._hash_value = hash(self.uid)
        return self._hash_value

    def __eq__(self, other):
        return self.uid == other.uid and \
        self.properties == other.properties and \
        self.labels == other.labels

    def __repr__(self):
        try:
            uid = str(self.uid)
            data_repr = [str(self.labels), str(self.properties),
                         '\'' + uid + '\'']
        except MissingNodeUid:
            data_repr = [str(self.labels), str(self.properties)]
        return 'Node(' + ', '.join(data_repr) + ')'


class Relation(object):

    def __init__(self, start_node, end_node,
                 type='RELATED_TO',properties=None):
        self.type = type
        self.start_node = start_node
        self.end_node = end_node
        self.properties = properties if properties is not None else {}

    def __hash__(self):
        if not hasattr(self, '_hash_value'):
            self._hash_value = hash(
                (self.start_node.uid,
                 self.type,
                 self.end_node.uid,
                 json.dumps(self.properties, sort_keys=True))
            )
        return self._hash_value

    def __eq__(self, other):
        try:
            self_start_uid = self.start_node.uid
            self_end_uid = self.end_node.uid
            other_start_uid = other.start_node.uid
            other_end_uid = other.end_node.uid
        except MissingNodeUid:
            raise CannotCompare('One of the relations\' nodes'
                                'does not have UID.')

        return self.type == other.type and \
        self_start_uid == other_start_uid and \
        self_end_uid == other_end_uid and \
        self.properties == other.properties


    def __str__(self):
        return '({start_node}) - [:{type}] -> ({end_node})'.format(
            start_node=self.start_node.uid,
            type=self.type, end_node=self.end_node.uid
        )


class GraphModelType(object):
    central_node_type = Node


class GraphModel(object):

    def __init__(self, central_node=None, central_node_type=Node):
        if central_node:
            self.central_node = central_node
        else:
            self.central_node = central_node_type()
        self.ingoing_relations = []
        self.outgoing_relations = []

    def add_label_to_central_node(self, label):
        self.central_node.labels.add(label)

    def remove_label_from_central_node(self, label):
        self.central_node.labels.remove(label)

    def set_property_of_central_node(self, name, value):
        self.central_node.properties[name] = value

    def remove_property_from_central_node(self, name):
        if self.central_node.properties.get(name):
            del self.central_node.properties[name]

    def generate_and_set_central_node_uid(self, *args, **kwargs):
        self.central_node.gen_and_set_uid(*args, **kwargs)

    def add_ingoing_relation(self, relation_type, start_node, properties=None):
        if properties is None: properties = {}
        self.ingoing_relations.append(
            relation_type(start_node, self.central_node, properties))

    def add_outgoing_relation(self, relation_type, end_node, properties=None):
        if properties is None: properties = {}
        self.outgoing_relations.append(
            relation_type(self.central_node, end_node, properties))

    def __eq__(self, other):

        try:
            are_central_nodes_same = self.central_node == other.central_node

            are_ingoing_relations_same = \
            set(self.ingoing_relations) == set(other.ingoing_relations)

            are_outgoing_relations_same =
            set(self.outgoing_relations) == set(other.outgoing_relations)

        except MissingNodeUid:
            raise CannotCompare('Some nodes of models don\'t have UIDs.)

        return are_central_nodes_same and are_ingoing_relations_same and \
        are outgoing_relations_same
