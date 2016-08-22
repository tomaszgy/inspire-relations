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

import pytest

from neo4j.v1 import GraphDatabase, basic_auth

from utils import (create_countries_and_continents, create_node,
                   create_relation, count_relations, flush_neo)


@pytest.fixture(scope='session')
def NeoDB():
    return GraphDatabase.driver(
        "bolt://localhost", auth=basic_auth("neo4j", "morpheus"))


def create_base_for_experiment(session):
    countries_inneoids = create_countries_and_continents(session,
                                                         {'FR': ['Europe'],
                                                          'CH': ['Europe']
                                                          })
    create_node(session, labels=['Record', 'Institution'],
                properties={'recid': '902725', 'inneoid': 'Record_902725',
                            'uuid': '243b3a19-d8eb-49ea-9b73-216cb5b70796'})
    create_relation(session, 'Record_902725', 'LOCATED_IN', 'Country_FR')
    create_relation(session, 'Record_902725', 'LOCATED_IN', 'Country_CH')

    return countries_inneoids + ['Record_902725']


@pytest.yield_fixture()
def db_before_experiment_insert(NeoDB):
    session = NeoDB.session()
    base_inneoids = create_base_for_experiment(session)

    yield {'inneoids': base_inneoids, 'rels_count': count_relations(session)}

    session.close()
    flush_neo(NeoDB)


@pytest.yield_fixture()
def db_before_experiment_update(NeoDB):
    session = NeoDB.session()
    base_inneoids = create_base_for_experiment(session)

    create_node(session, labels=['Record', 'Institution'],
                properties={'recid': '903369', 'inneoid': 'Record_903369',
                            'uuid': '0d74183d-3890-48c8-a7bb-3c9b4278947a'})
    create_relation(session, 'Record_903369', 'LOCATED_IN', 'Country_CH')
    create_node(session, labels=['Record', 'Experiment'],
                properties={
                    'uuid': '18896fa9-16ab-44b6-b0f5-75345d7143bf',
                    'inneoid': 'Record_1108541'
    }
    )
    create_relation(session, 'Record_1108541', 'AFFILIATED_WITH',
                    'Record_902725')

    yield {'inneoids': base_inneoids + ['Record_1108541', 'Record_903369'],
           'rels_count': count_relations(session)}

    session.close()
    flush_neo(NeoDB)


def create_base_for_conference(session):
    countries_inneoids = create_countries_and_continents(session,
                                                         {'FR': ['Europe']
                                                          })
    create_node(session, labels=['ResearchField'],
                properties={'name': 'Math and Math Physics',
                            'inneoid': 'ResearchField_Math and Math Physics'})
    create_node(session, labels=['ResearchField'],
                properties={'name': 'Computing',
                            'inneoid': 'ResearchField_Computing'})

    return countries_inneoids + ['ResearchField_Math and Math Physics',
                                 'ResearchField_Computing']


@pytest.yield_fixture()
def db_before_conference_insert(NeoDB):
    session = NeoDB.session()
    base_inneoids = create_base_for_conference(session)

    yield {'inneoids': base_inneoids, 'rels_count': count_relations(session)}

    session.close()
    flush_neo(NeoDB)


@pytest.yield_fixture()
def db_before_conference_update(NeoDB):
    session = NeoDB.session()
    base_inneoids = create_base_for_conference(session)
    extra_countries = create_countries_and_continents(
        session, {'CH': ['Europe']})

    create_node(session, labels=['Record', 'Conference'],
                properties={
                    'uuid': '6963fcde-5203-4cd1-9894-67c402dc5bc3',
                    'inneoid': 'Record_1245372'
    })
    create_relation(session, 'Record_1245372', 'IN_THE_FIELD_OF',
                    'ResearchField_Computing')
    create_relation(session, 'Record_1245372', 'IN_THE_FIELD_OF',
                    'ResearchField_Math and Math Physics')
    create_relation(session, 'Record_1245372', 'LOCATED_IN', 'Country_FR')
    create_node(session, ['ConferenceSeries'], {'inneoid': 'ConferenceSeries_SOS',
                                                'name': 'SOS'})
    create_relation(session, 'Record_1245372', 'IS_PART_OF_SERIES',
                    'ConferenceSeries_SOS', relation_properties={'number': '3'}
                    )

    create_node(session, ['ConferenceSeries'],
                {'inneoid': 'ConferenceSeries_ExistingOne',
                 'name': 'ExistingOne'})

    create_node(session, labels=['Record', 'Conference'],
                properties={
                    'uuid': '334e2a14-91c6-4191-8d8c-c004a1a42dfd',
                    'inneoid': 'Record_382746'
    })

    create_relation(session, 'Record_382746', 'IS_PART_OF_SERIES',
                    'ConferenceSeries_ExistingOne')

    yield {'inneoids': base_inneoids + ['Record_1245372',
                                        'ConferenceSeries_SOS',
                                        'ConferenceSeries_ExistingOne',
                                        'Record_382746'] + extra_countries,
           'rels_count': count_relations(session)}

    session.close()
    flush_neo(NeoDB)
