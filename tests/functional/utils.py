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

from inspire_relations import command_producers

from uuid import UUID

from neo4j.v1.session import Session


def create_record_stub(json, uuid):
    """
    Creates invenio-records Record's stub with RecordMetadata stub inside.
    """
    class RecordMetadataStub:

        def __init__(self, uuid):
            self.id = UUID(uuid)

    class RecordStub(dict):

        def __init__(self, json, uuid):
            self.model = RecordMetadataStub(uuid)
            dict.__init__(json)

    return RecordStub(json, uuid)


class NeoTester:

    def __init__(self, session):
        if isinstance(session, Session):
            self._session = session
        else:
            raise TypeError('session is not of Session type')

    def _get_all_results(self, cypher_query):
        results = self._session.run(cypher_query)
        return [r for r in results]

    def node_exists(self, labels, properties, is_exactly_same=False):
        """
        Checks whether node with given set of labels and properties exists
        and is the only one matching.
        If is_exactly_same is set, it makes sure that the found node
        doesn't have any extra labels and properties
        """
        query = 'MATCH ' + command_producers.produce_node_block(
            labels=labels, properties=properties, variable_name='node'
        ) + ' RETURN node'

        results = self._get_all_results(query)

        if len(results) == 1:
            if is_exactly_same:
                node = results[0]['node']
                are_same_labels = set(labels) == set(node.labels)

                return node.properties == properties and are_same_labels
            else:
                return True
        else:
            return False

    def relation_exists(self, start_inneoid, relation, end_inneoid,
                        relation_properties={}):
        """
        Checks whether relation of certain type between two nodes exists
        and is the only one matching.

        start_inneoid -- InspireNeoID of the start node
        end_inneoid -- InspireNeoID of the end node
        relation -- type of relation
        """
        relation_string = command_producers.produce_relation_block(
            relation_type=relation, properties=relation_properties,
            variable_name='r',
            arrow_right=True)

        query = (
            'MATCH ({{inneoid: "{start}"}}) {relation} ({{inneoid: "{end}"}})'
            'RETURN count(r) AS count'
        ).format(
            start=start_inneoid, end=end_inneoid, relation=relation_string
        )
        results = self._get_all_results(query)
        return results[0]['count'] == 1

    def relation_doesnt_exist(self, start_inneoid, relation, end_inneoid,
                              relation_properties={}):
        return not self.relation_exists(start_inneoid, relation, end_inneoid,
                                        relation_properties)

    def nodes_exist(self, inneoids):
        """
        Given list of nodes' InspireNeoIDs makes sure that the nodes exist.
        """

        node_blocks = [command_producers.produce_node_block(
            properties={'inneoid': inneoid}) for inneoid in inneoids]

        query = 'MATCH {} RETURN count(*) > 0 AS do_they_exist'.format(
            ', '.join(node_blocks)
        )

        results = self._get_all_results(query)

        return results[0]['do_they_exist']


def count_relations(session):

    query = 'MATCH () - [l] -> () RETURN count(l) as count'
    results = _get_all_results(session, query)

    return results[0]['count']


def create_node(session, labels, properties):
    session.run(command_producers.create_node(labels=labels,
                                              properties=properties))


def create_relation(session, start_inneoid, relation, end_inneoid,
                    relation_properties={}):
    """
    Creates relation between two nodes.

    session -- Neo4j's session
    start_inneoid -- InspireNeoID of the start node
    end_inneoid -- InspireNeoID of the end node
    relation -- type of relation
    relation_properties -- properties of relation
    """

    session.run(command_producers.create_relation(
        relation_type=relation, relation_properties=relation_properties,
        start_node_properties={'inneoid': start_inneoid},
        end_node_properties={'inneoid': end_inneoid}
    ))


def create_countries_and_continents(session, countries):
    """
    Creates countries and continents nodes and proper edges between them

    countries -- dictionary populated by pairs:
                    country_code : [array of names of continent(s)
                                    on which a country is located]
    """
    inneoids = []
    continents_to_create = set([continent
                                for country, continents in countries.items()
                                for continent in continents])

    for continent in continents_to_create:
        inneoid = '_'.join(['Continent', continent])
        inneoids.append(inneoid)
        create_node(session, labels=['Continent'],
                    properties={'name': continent,
                                'inneoid': inneoid
                                })

    for country, continents in countries.items():
        inneoid = '_'.join(['Country', country])
        inneoids.append(inneoid)
        create_node(session, labels=['Country'],
                    properties={'code': country,
                                'inneoid': inneoid
                                })
        for continent in continents:
            create_relation(session, '_'.join(['Country', country]),
                            'PART_OF', '_'.join(['Continent', continent]))

    return inneoids


def flush_neo(neo_driver):
    with neo_driver.session() as session:
        session.run('MATCH (m) -[l] -(n) DELETE l')
        session.run('MATCH (m) DELETE m')
