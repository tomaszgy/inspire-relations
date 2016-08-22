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

import command_producers as commands

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan as es_scan
from functools import partial
from inspire_relations import builders

from inspire_relations.graph_representation import (
    get_central_node,
    get_node_labels,
    get_node_properties,
    get_node_uid,
    get_node_type,
    get_outgoing_relations,
    get_relation_type,
    get_start_node,
    get_end_node,
    produce_model_from_node,
    should_create_end_node_if_not_exists
)

from uuid import uuid4

import os

import csv


ES = Elasticsearch()

INDICES = [
    'records-authors',
    'records-journals',
    'records-jobs',
    'records-hep',
    'records-experiments',
    'records-conferences',
    'records-institutions'
]

INDEX_TO_BUILDER = {
    'records-authors': builders.hepnames.hepnames,
    'records-journals': builders.journals.journals,
    'records-jobs': builders.jobs.jobs,
    'records-hep': builders.literature.literature,
    'records-experiments': builders.experiments.experiments,
    'records-conferences': builders.conferences.conferences,
    'records-institutions': builders.institutions.institutions
}


def nested_setdefault(dictionary, keys, default=None):
    current_dict = dictionary
    for key in keys[:-1]:
        try:
            current_dict = current_dict.setdefault(key, dict())
        except AttributeError:
            raise TypeError(
                'Wrong internal structure. ' + '.'.join(
                    keys[:keys.index(key)]
                    ) + ' is already something else than dict.'
                )
    return current_dict.setdefault(keys[-1], default)


def make_labels_key(labels):
    return tuple(sorted(labels))


def make_properties_key(properties):
    return tuple(sorted(properties.keys()))


def move_central_node_to_proper_group(node, groups):
    labels_key = make_labels_key(get_node_labels(node))
    properties_key = make_properties_key(get_node_properties(node))

    nested_setdefault(groups,
                      [labels_key, properties_key],
                      list()).append(node)


def move_relation_to_proper_group(relation, groups):
    relation_type = get_relation_type(relation)
    start_node_type = get_node_type(get_start_node(relation))
    end_node_type = get_node_type(get_end_node(relation))

    nested_setdefault(groups,
                      [relation_type, start_node_type, end_node_type],
                      list()).append(relation)


def process_record_model(model,
                         existing_uids, nodes_to_create, relations_to_create):
    central_node = get_central_node(model)
    existing_uids.add(get_node_uid(central_node))

    move_central_node_to_proper_group(central_node, nodes_to_create)

    outgoing_relations = get_outgoing_relations(model)

    for relation in outgoing_relations:
        move_relation_to_proper_group(relation, relations_to_create)

        if should_create_end_node_if_not_exists(relation):
            end_node_model = produce_model_from_node(
                get_end_node(relation))
            process_record_model(end_node_model,
                                 existing_uids,
                                 nodes_to_create,
                                 relations_to_create)


def generate_file_name():
    return str(uuid4()) + '.csv'


def generate_csv_for_nodes(nodes_to_create, directory):
    loader_file_name = os.path.join(directory, 'loader.cypher')

    with open(loader_file_name, 'w') as loader_file:
        for labels_set, nodes_subset in nodes_to_create.items():
            for properties_set, nodes in nodes_subset.items():

                node_properties = list(properties_set) + ['uid']
                csv_file = os.path.join(directory, generate_file_name())

                nodes_to_csv(csv_file, nodes, labels_set, node_properties)

                load_command = commands.create_node_from_csv(
                    csv_file,
                    labels_set,
                    {prop:prop for prop in node_properties}
                    )

                loader_file.write(load_command)


def traverse_relations_tree(relations_to_create):
    for r_type, rs_of_rel_type in relations_to_create.items():
        for start_n_type, rs_with_start_n_type in rs_of_rel_type.items():
            for end_n_type, rs_with_end_n_type in rs_with_start_n_type.items():
                yield start_n_type, r_type, end_n_type, rs_with_end_n_type


def generate_csv_for_relations(relations_to_create, directory,
                               existining_uids):
    loader_file_name = os.path.join(directory, 'loader.cypher')
    both_edge_nodes_exist = partial(start_and_end_node_exist,
                                    existing_uids=existing_uids)

    with open(loader_file_name, 'w') as loader_file:
        for start_node_type, relation_type, end_node_type, relations \
        in traverse_relations_tree(relations_to_create):
            csv_file = os.path.join(directory, generate_file_name())

            relations_to_csv(csv_file,
                             filter(both_edge_nodes_exist, relations),
                             relation_type,
                             start_node_type,
                             end_node_type)

            load_command = commands.create_relations_from_csv(
                csv_file,
                relation_type,
                start_node_type.default_labels,
                end_node_type.default_labels
                )

            loader_file.write(load_command)


def start_and_end_node_exist(relation, existing_uids):
    start_node_uid = get_node_uid(get_start_node(relation))
    end_node_uid = get_node_uid(get_end_node(relation))

    return start_node_uid in existing_uids and end_node_uid in existing_uids


def relations_to_csv(file_name, relations, relation_type,
                     start_node_labels, end_node_labels):
    with open(file_name, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(
            ['start_node_uid', 'end_node_uid']
        )

        for relation in relations:
            start_uid = get_node_uid(get_start_node(relation))
            end_uid = get_node_uid(get_end_node(relation))

            csv_writer.writerow([start_uid, end_uid])


def nodes_to_csv(file_name, nodes, labels, properties):
    with open(file_name, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(
            ['uid'] + properties
        )

        for node in nodes:
            properties_values = map(
                lambda p: get_node_properties(node).get(p),
                properties
                )
            node_data = [get_node_uid(node)] + properties_values

            csv_writer.writerow(node_data)


if __name__ == '__main__':

    existing_uids = set()
    nodes_to_create = {}
    relations_to_create = {}

    import os
    cwd = os.path.join(os.getcwd(), 'nodd')
    cwd_rels = os.path.join(os.getcwd(), 'rels')
    # os.mkdir(cwd)
    # os.mkdir(cwd_rels)

    for index in INDICES:
        builder = INDEX_TO_BUILDER[index]
        for record in es_scan(ES,index=index, _source=builder.required_fields):
            record_model = builder.build(record['_source'])
            process_record_model(record_model,
                                 existing_uids,
                                 nodes_to_create,
                                 relations_to_create)

    generate_csv_for_nodes(nodes_to_create, cwd)
    generate_csv_for_relations(relations_to_create, cwd_rels, existing_uids)
    print len(existing_uids)
