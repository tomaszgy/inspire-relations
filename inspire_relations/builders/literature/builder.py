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

from inspire_relations.graph_representation import (
    make_node,
    GraphModelBuilder
    )
from inspire_relations.model.nodes import (
    AuthorNode,
    ConferenceNode,
    LiteratureNode,
    PersonNode
    )
from inspire_relations.model.relations import (
    AUTHORED_BY,
    CONTRIBUTED_TO,
    REFERS_TO,
    WRITTEN_BY
    )
from inspire_relations.model.utils import (
    COLLECTION_TO_LABEL,
    get_recid_from_ref
    )

from inspire_relations.model_updaters import (
    add_label_to_central_node,
    add_outgoing_relation,
    set_property_of_central_node,
    set_uid
)


literature = GraphModelBuilder(central_node_type=LiteratureNode)


@literature.element_processor('control_number')
def recid(model, element):
    set_property_of_central_node(model,
                                 'recid', str(element))

    set_uid(model,
            uid=LiteratureNode.generate_uid(recid=element))


@literature.element_processor('collections')
def paper_type(model, element):
    label = COLLECTION_TO_LABEL.get(element['primary'].upper())
    if label:
        add_label_to_central_node(model, label)


@literature.element_processor('references', musts=["recid"])
def refers_to(model, element):
    refered_paper = make_node(LiteratureNode, recid=element['recid'])
    add_outgoing_relation(model,
                          REFERS_TO, refered_paper)


@literature.element_processor('publication_info', musts=['conference_record'])
def contributed_to(model, element):
    conference_recid = get_recid_from_ref(element['conference_record'])
    conference = make_node(ConferenceNode,
    recid=conference_recid)
    add_outgoing_relation(model,
                          CONTRIBUTED_TO, conference)


@literature.element_processor('authors', musts=['recid'])
def authored_by(model, element):
    person_recid = element['recid']
    affiliations_recids = [aff.get('recid')
                           for aff in element.get('affiliations', [])
                           if aff.get('recid')
                           ]
    author = make_node(AuthorNode, person_recid=person_recid,
                             affiliations=affiliations_recids)
    add_outgoing_relation(model,
                          AUTHORED_BY, author)

    person = make_node(PersonNode, recid=person_recid)
    add_outgoing_relation(model,
                          WRITTEN_BY, person)
