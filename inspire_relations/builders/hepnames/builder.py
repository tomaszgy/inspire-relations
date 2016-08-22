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
from inspire_relations.model.graph_models import PersonGraphModel
from inspire_relations.model.nodes import (
    CurrentJobPositionNode,
    PreviousJobPositionNode
    )
from inspire_relations.model.relations import HiredAs, SupervisedBy
from inspire_relations.model.utils import get_recid_from_ref


hepnames = GraphModelBuilder(model_type=PersonGraphModel)


@hepnames.element_processor('advisors', musts=['record'])
def gained_a_degree(graph_model, element):
    supervisor_recid = get_recid_from_ref(element['record'])
    supervisor = PersonNode(recid=supervisor_recid)

    degree_type = element.get('degree_type')
    rel_properties = {'degree_type': degree_type} if degree_type else {}

    graph_model.add_outgoing_relation(SupervisedBy, supervisor, rel_properties)


@hepnames.element_processor('positions', musts=['institution'])
def hired_as(graph_model, element):
    institution_data = element['institution']

    if 'recid' in institution_data:
        institution_recid = institution_data['recid']
        rank_name = element.get('rank')
        start_date = element.get('start_date')

        if element.get('current', ''):
            job_position = CurrentJobPositionNode(rank_name,
                                                  institution_recid,
                                                  start_date)
        else:
            end_date = element.get('end_date')
            job_position = PreviousJobPositionNode(rank_name,
                                                   institution_recid,
                                                   start_date,
                                                   end_date
                                                   )

        graph_model.add_outgoing_relation(HiredAs, job_position)
