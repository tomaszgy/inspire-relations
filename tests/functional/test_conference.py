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

from fixtures import (basic_conference_record, conference_record_to_update)

from utils import count_relations, NeoTester


def test_conference_record_insert(basic_conference_record,
                                  db_before_conference_insert,
                                  NeoDB):
    graph_manager.insert_record(basic_conference_record)
    session = NeoDB.session()
    that = NeoTester(session)

    assert that.node_exists(['Record', 'Conference'], {
        'uuid': '6963fcde-5203-4cd1-9894-67c402dc5bc3',
        'inneoid': 'Record_1245372'
    },
        is_exactly_same=True)

    assert that.relation_exists('Record_1245372', 'IN_THE_FIELD_OF',
                                'ResearchField_Computing')
    assert that.relation_exists('Record_1245372', 'IN_THE_FIELD_OF',
                                'ResearchField_Math and Math Physics')

    assert that.relation_exists('Record_1245372', 'LOCATED_IN', 'Country_FR')

    assert that.node_exists(['ConferenceSeries'], {
        'inneoid': 'ConferenceSeries_SOS',
        'name': 'SOS'
    },
        is_exactly_same=True)

    assert that.relation_exists('Record_1245372', 'IS_PART_OF_SERIES',
                                'ConferenceSeries_SOS',
                                relation_properties={
                                    'number': '3'
                                }
                                )

    # have the nodes and relations
    # that were present before insert been changed?
    assert that.nodes_exist(
        db_before_conference_insert['inneoids'])
    assert count_relations(session) == db_before_conference_insert[
        'rels_count'] + 4

    session.close()


def test_conference_record_update(conference_record_to_update,
                                  db_before_conference_update,
                                  NeoDB):

    graph_manager.update_record(conference_record_to_update)
    session = NeoDB.session()
    that = NeoTester(session)

    # make sure record's node has been updated
    assert that.node_exists(['Record', 'Conference'], {
        'uuid': '15117ae8-498f-4612-afa7-618e19f63e87',
        'inneoid': 'Record_1245372'
    },
        is_exactly_same=True)

    assert that.relation_exists('Record_1245372', 'LOCATED_IN', 'Country_CH')
    assert that.relation_doesnt_exist('Record_1245372', 'LOCATED_IN',
                                      'Country_FR')
    assert that.relation_exists('Record_1245372', 'IS_PART_OF_SERIES',
                                'ConferenceSeries_SOS',
                                relation_properties={
                                    'number': '4'
                                }
                                )
    assert that.relation_exists('Record_1245372', 'IS_PART_OF_SERIES',
                                'ConferenceSeries_ExistingOne')
    assert that.node_exists(['ConferenceSeries'], {
        'inneoid': 'ConferenceSeries_NonExistingOne',
        'name': 'NonExistingOne'},
        is_exactly_same=True)
    assert that.relation_exists('Record_1245372', 'IS_PART_OF_SERIES',
                                'ConferenceSeries_NonExistingOne',
                                relation_properties={
                                    'number': '1'
                                })

    assert that.relation_exists('Record_1245372', 'IN_THE_FIELD_OF',
                                'ResearchField_Computing')
    assert that.relation_exists('Record_1245372', 'IN_THE_FIELD_OF',
                                'ResearchField_Astrophysics')
    assert that.relation_doesnt_exist('Record_1245372', 'IN_THE_FIELD_OF',
                                      'ResearchField_Math and Math Physics')

    # have the nodes and relations
    # that were present before insert been changed?
    assert that.nodes_exist(
        db_before_conference_update['inneoids'])
    assert count_relations(session) == db_before_conference_update[
        'rels_count'] + 2

    session.close()
