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

from __future__ import absolute_import, print_function

from inspire_relations.exceptions import MissingNodeUid

from inspire_relations.graph_representation import GraphModel, Node

from inspire_relations.model.labels import NodeLabels

from inspire_relations.model.relations import (
    AffiliatedWith,
    At,
    InTheRankOf,
    Represents
    )

UID_BASIC_SEPARATOR = '|^|'
UID_SECONDARY_SEPARATOR = '|/|'


def add_default_labels(*labels):
    def class_decorator(cls):
        cls.DEFAULT_LABELS = cls.DEFAULT_LABELS | set(labels)
        return cls
    return class_decorator


@add_default_labels(NodeLabels.Record)
class RecordNode(Node):

    def __init__(self, labels=None, properties=None, recid=None):
        super(RecordNode, self).__init__(labels, properties)
        if recid:
            self.gen_and_set_uid(recid)


    @staticmethod
    def generate_uid(recid):
        return 'Record' + UID_BASIC_SEPARATOR + str(recid)


@add_default_labels(NodeLabels.Author)
class AuthorNode(Node):

    def __init__(self, person_recid, affiliations=[]):
        super(AuthorNode, self).__init__()
        self.gen_and_set_uid(person_recid, affiliations)

    @staticmethod
    def generate_uid(person_recid, affiliations=[]):
        sorted_affiliations = map(str, sorted(map(int, affiliations)))
        affiliations_string = UID_SECONDARY_SEPARATOR.join(sorted_affiliations)
        return 'Author' + UID_BASIC_SEPARATOR + str(person_recid) + \
        UID_BASIC_SEPARATOR + affiliations_string

    def get_graph_model(self):
        try:
            uid = self.uid
        except MissingNodeUid:
            raise MissingNodeUid(
                'Cannot return graph model. Node UID is missing')

        _, person_recid, affiliations_string = uid.split(UID_BASIC_SEPARATOR)
        affiliations_recids = affiliations_string.split(UID_SECONDARY_SEPARATOR)

        graph_model = GraphModel(central_node=self)
        person = PersonNode(recid=person_recid)
        graph_model.add_outgoing_relation(Represents, person)

        for affiliation_recid in affiliations_recids:
            institution = InstitutionNode(recid=affiliation_recid)
            graph_model.add_outgoing_relation(AffiliatedWith, institution)

        return graph_model


@add_default_labels(NodeLabels.PreviousJobPosition)
class PreviousJobPositionNode(Node):

    def __init__(self, rank, institution_recid, start_date, end_date):
        super(PreviousJobPositionNode, self).__init__(properties={
            'start_date': start_date,
            'end_date': end_date
        })
        self.gen_and_set_uid(rank, institution_recid, start_date, end_date)

    @staticmethod
    def generate_uid(rank, institution_recid, start_date, end_date):
        uid_elements = ['PreviousJobPosition'] + map(str,
                                                     [rank, institution_recid,
                                                      start_date, end_date]
                                                     )
        return UID_BASIC_SEPARATOR.join(uid_elements)

    def get_graph_model(self):
        try:
            uid = self.uid
        except MissingNodeUid:
            raise MissingNodeUid(
                'Cannot return graph model. Node UID is missing')

        _, rank_name, institution_recid, _, _ = uid.split(
            UID_BASIC_SEPARATOR
            )

        graph_model = GraphModel(central_node=self)

        rank = ScientificRankNode(rank_name)
        institution = InstitutionNode(recid=institution_recid)

        graph_model.add_outgoing_relation(InTheRankOf, rank)
        graph_model.add_outgoing_relation(At, institution)

        return graph_model


@add_default_labels(NodeLabels.CurrentJobPosition)
class CurrentJobPositionNode(Node):

    def __init__(self, rank, institution_recid, start_date):
        super(CurrentJobPositionNode, self).__init__(properties={
            'start_date': start_date,
            'end_date': end_date
        })
        self.gen_and_set_uid(rank, institution_recid, start_date)

    @staticmethod
    def generate_uid(rank, institution_recid, start_date):
        uid_elements = ['CurrentJobPosition'] + map(str,
                                                     [rank, institution_recid,
                                                      start_date]
                                                     )
        return UID_BASIC_SEPARATOR.join(uid_elements)

    def get_graph_model(self):
        try:
            uid = self.uid
        except MissingNodeUid:
            raise MissingNodeUid(
                'Cannot return graph model. Node UID is missing')

        _, rank_name, institution_recid, _ = uid.split(
            UID_BASIC_SEPARATOR
            )

        graph_model = GraphModel(central_node=self)

        rank = ScientificRankNode(rank_name)
        institution = InstitutionNode(recid=institution_recid)

        graph_model.add_outgoing_relation(InTheRankOf, rank)
        graph_model.add_outgoing_relation(At, institution)

        return graph_model


@add_default_labels(NodeLabels.Conference)
class ConferenceNode(RecordNode):
    pass


@add_default_labels(NodeLabels.Continent)
class ContinentNode(Node):

    def __init__(self, continent_name):
        super(ContinentNode, self).__init__(
            properties={'name': continent_name})
        self.gen_and_set_uid(continent_name)

    @staticmethod
    def generate_uid(continent_name):
        return 'Continent' + UID_BASIC_SEPARATOR + continent_name


@add_default_labels(NodeLabels.Country)
class CountryNode(Node):

    def __init__(self, country_code):
        super(CountryNode, self).__init__(
            properties={'country_code': country_code})
        self.gen_and_set_uid(country_code)

    @staticmethod
    def generate_uid(country_code):
        return 'Country' + UID_BASIC_SEPARATOR + country_code


@add_default_labels(NodeLabels.Experiment)
class ExperimentNode(RecordNode):
    pass


@add_default_labels(NodeLabels.Institution)
class InstitutionNode(RecordNode):
    pass


@add_default_labels(NodeLabels.Journal)
class JournalNode(RecordNode):
    pass


@add_default_labels(NodeLabels.Job)
class JobNode(RecordNode):
    pass


@add_default_labels(NodeLabels.Literature)
class LiteratureNode(RecordNode):
    pass


@add_default_labels(NodeLabels.Person)
class PersonNode(RecordNode):
    pass


@add_default_labels(NodeLabels.Publisher)
class PublisherNode(Node):

    def __init__(self, publisher_name):
        super(PublisherNode, self).__init__(
            properties={'name': publisher_name})
        self.gen_and_set_uid(publisher_name)

    @staticmethod
    def generate_uid(publisher_name):
        return 'Publisher' + UID_BASIC_SEPARATOR + publisher_name


@add_default_labels(NodeLabels.ResearchField)
class ResearchFieldNode(Node):

    def __init__(self, field_name):
        super(ResearchFieldNode, self).__init__(
            properties={'name': field_name})
        self.gen_and_set_uid(field_name)

    @staticmethod
    def generate_uid(field_name):
        return 'ResearchField' + UID_BASIC_SEPARATOR + field_name


@add_default_labels(NodeLabels.ScientificRank)
class ScientificRankNode(Node):

    def __init__(self, rank_name):
        super(ScientificRankNode, self).__init__(
            properties={'name': rank_name})
        self.gen_and_set_uid(rank_name)

    @staticmethod
    def generate_uid(rank_name):
        return 'ScientificRank' + UID_BASIC_SEPARATOR + rank_name
