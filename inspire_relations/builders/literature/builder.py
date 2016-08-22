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

from inspire_relations.model_builder import GraphModelBuilder
from inspire_relations.model.graph_models import LiteratureGraphModel
from inspire_relations.model.nodes import (
    AuthorNode,
    ConferenceNode,
    LiteratureNode,
    PersonNode
    )
from inspire_relations.model.relations import (
    AuthoredBy,
    ContributedTo,
    RefersTo,
    WrittenBy,
    )
from inspire_relations.model.utils import (
    COLLECTION_TO_LABEL,
    get_recid_from_ref
    )


literature = GraphModelBuilder(model_type=LiteratureGraphModel)


@literature.element_processor('collections')
def paper_type(graph_model, element):
    label = COLLECTION_TO_LABEL.get(element['primary'].upper())
    if label:
        graph_model.add_label_to_central_node(label)


@literature.element_processor('references', musts=["recid"])
def refers_to(graph_model, element):
    refered_paper = LiteratureNode(recid=element['recid'])
    graph_model.add_outgoing_relation(RefersTo, refered_paper)


@literature.element_processor('publication_info', musts=['conference_record'])
def contributed_to(graph_model, element):
    conference_recid = get_recid_from_ref(element['conference_record'])
    conference = ConferenceNode(recid=conference_recid)
    graph_model.add_outgoing_relation(ContributedTo, conference)


@literature.element_processor('authors', musts=['recid'])
def authored_by(graph_model, element):
    person_recid = element['recid']
    affiliations_recids = [aff.get('recid')
                           for aff in element.get('affiliations', [])
                           if aff.get('recid')
                           ]
    author = AuthorNode(person_recid, affiliations=affiliations_recids)
    graph_model.add_outgoing_relation(AuthoredBy, author)

    person = PersonNode(recid=person_recid)
    graph_model.add_outgoing_relation(WrittenBy, person)
