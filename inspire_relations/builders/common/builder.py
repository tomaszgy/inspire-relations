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

from ..conferences.builder import conferences
from ..experiments import experiments
from ..hepnames.builder import hepnames
from ..institutions import institutions
from ..jobs import jobs
from ..journals import journals
from ..literature import literature

from inspire_relations.model.nodes import (CountryNode, ScientificRankNode,
                                           ResearchFieldNode)
from inspire_relations.model.relations import (InTheFieldOf, LocatedIn)


@conferences.element_processor('control_number')
@experiments.element_processor('control_number')
@hepnames.element_processor('control_number')
@institutions.element_processor('control_number')
@jobs.element_processor('control_number')
@journals.element_processor('control_number')
@literature.element_processor('control_number')
def recid(graph_model, element):
    graph_model.set_property_of_central_node('recid', str(element))
    graph_model.generate_and_set_central_node_uid(element)


@institutions.element_processor('address', musts=['country_code'])
@conferences.element_processor('address', musts=['country_code'])
def located_in_country(graph_model, element):
    country = CountryNode(element['country_code'])
    graph_model.add_outgoing_relation(LocatedIn, country)


@conferences.element_processor('field_categories')
@jobs.element_processor('field_categories')
@literature.element_processor('field_categories')
def in_the_field_of(graph_model, element):
    research_field = ResearchFieldNode(element['term'])
    graph_model.add_outgoing_relation(InTheFieldOf, research_field)


@jobs.element_processor('ranks')
def scientific_rank(graph_model, element):
    rank = ScientificRankNode(element)
    graph_model.add_outgoing_relation(InTheRankOf, rank)
