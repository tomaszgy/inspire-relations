# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, print_function

import pytest

from inspire_relations import graph_manager

from fixtures import (basic_experiment_record,
                      experiment_record_changed_uuid_and_exist_affiliation,
                      experiment_record_changed_uuid_and_nonexist_affiliation
                      )

from utils import count_relations, NeoTester


def test_experiment_record_insert(basic_experiment_record,
                                  db_before_experiment_insert, NeoDB):

    graph_manager.insert_record(basic_experiment_record)

    session = NeoDB.session()
    that = NeoTester(session)
    assert that.node_exists(['Record', 'Experiment'],
                            {
                                'uuid': '18896fa9-16ab-44b6-b0f5-75345d7143bf',
                                'inneoid': 'Record_1108541'
    },
        is_exactly_same=True)
    assert that.relation_exists('Record_1108541', 'AFFILIATED_WITH',
                                'Record_902725')

    # have the nodes and relations present before insert been changed?
    assert that.nodes_exist(db_before_experiment_insert['inneoids'])
    assert count_relations(session) == db_before_experiment_insert[
        'rels_count'] + 1

    session.close()


def test_experiment_update_changed_uuid_and_existing_affiliation(
        experiment_record_changed_uuid_and_exist_affiliation, NeoDB,
        db_before_experiment_update):

    graph_manager.update_record(
        experiment_record_changed_uuid_and_exist_affiliation)

    session = NeoDB.session()
    that = NeoTester(session)

    # check if uuid in record's node has been updated
    assert that.node_exists(['Record', 'Experiment'],
                            {
                                'uuid': 'f09c1197-f0f3-4765-a1c2-cdac0bf2e8ab',
                                'inneoid': 'Record_1108541'
    },
        is_exactly_same=True)

    # check if record's affiliation has been correctly updated
    assert that.relation_doesnt_exist('Record_1108541', 'AFFILIATED_WITH',
                                      'Record_902725')

    assert that.relation_exists('Record_1108541', 'AFFILIATED_WITH',
                                'Record_1108541')

    # have the nodes and relations present before insert been changed?
    assert that.nodes_exist(db_before_experiment_insert['inneoids'])
    assert count_relations(session) == db_before_experiment_insert[
        'rels_count']


def test_experiment_update_changed_uuid_and_nonexisting_affiliation(
        experiment_record_changed_uuid_and_nonexist_affiliation, NeoDB,
        db_before_experiment_update):

    graph_manager.update_record(
        experiment_record_changed_uuid_and_nonexist_affiliation)

    session = NeoDB.session()
    that = NeoTester(session)

    # check if uuid in record's node has been updated
    assert that.node_exists(['Record', 'Experiment'],
                            {
                                'uuid': 'f09c1197-f0f3-4765-a1c2-cdac0bf2e8ab',
                                'inneoid': 'Record_1108541'
    },
        is_exactly_same=True)

    # check if record's affiliation has been correctly updated
    assert that.relation_doesnt_exist('Record_1108541', 'AFFILIATED_WITH',
                                      'Record_902725')

    assert that.relation_doesnt_exist(['Record'], {'inneoid': 'Record_90336'})

    # have the nodes and relations present before insert been changed?
    assert that.nodes_exist(db_before_experiment_insert['inneoids'])
    assert count_relations(session) == db_before_experiment_insert[
        'rels_count'] - 1


# TODO: test for records deletion
