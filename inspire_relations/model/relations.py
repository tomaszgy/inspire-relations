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

from inspire_relations.graph_representation import Relation

from inspire_relations.model.labels import RelationLabels


class AffiliatedWith(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(AffiliatedWith, self).__init__(start_node, end_node,
                                             RelationLabels.AFFILIATED_WITH,
                                             properties)


class AuthoredBy(Relation):
    def __init__(self, start_node, end_node, properties=None):
        super(AuthoredBy, self).__init__(start_node, end_node,
                                         RelationLabels.AUTHORED_BY,
                                         properties)


class At(Relation):
    def __init__(self, start_node, end_node, properties=None):
        super(At, self).__init__(start_node, end_node,
                                 RelationLabels.AT,
                                 properties)


class ContributedTo(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(ContributedTo, self).__init__(start_node, end_node,
                                            RelationLabels.CONTRIBUTED_TO,
                                            properties)


class HiredAs(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(HiredAs, self).__init__(start_node, end_node,
                                            RelationLabels.HIRED_AS,
                                            properties)


class InTheFieldOf(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(InTheFieldOf, self).__init__(start_node, end_node,
                                           RelationLabels.IN_THE_FIELD_OF,
                                           properties)


class InTheRankOf(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(InTheRankOf, self).__init__(start_node, end_node,
                                          RelationLabels.IN_THE_RANK_OF,
                                          properties)


class IsAboutExperiment(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(IsAboutExperiment, self).__init__(start_node, end_node,
                                        RelationLabels.IS_ABOUT_EXPERIMENT,
                                        properties)


class LocatedIn(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(LocatedIn, self).__init__(start_node, end_node,
                                        RelationLabels.LOCATED_IN,
                                        properties)


class OfferedBy(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(OfferedBy, self).__init__(start_node, end_node,
                                        RelationLabels.OFFERED_BY,
                                        properties)


class PublishedBy(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(PublishedBy, self).__init__(start_node, end_node,
                                          RelationLabels.PUBLISHED_BY,
                                          properties)


class RefersTo(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(RefersTo, self).__init__(start_node, end_node,
                                           RelationLabels.REFERS_TO,
                                           properties)


class Represents(Relation):

    def __init__(self, start_node, end_node, properties=None):
        super(Represents, self).__init__(start_node, end_node,
                                         RelationLabels.REPRESENTS,
                                         properties)


class SupervisedBy(Relation):

        def __init__(self, start_node, end_node, properties=None):
            super(SupervisedBy, self).__init__(start_node, end_node,
                                               RelationLabels.SUPERVISED_BY,
                                               properties)


class WrittenBy(Relation):

        def __init__(self, start_node, end_node, properties=None):
            super(WrittenBy, self).__init__(start_node, end_node,
                                               RelationLabels.WRITTEN_BY,
                                               properties)
