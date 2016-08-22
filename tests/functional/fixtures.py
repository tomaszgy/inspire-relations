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


import pytest

from utils import create_record_stub


@pytest.fixture()
def basic_experiment_record():
    record = create_record_stub(
        json={
            'self': {
                '$ref': 'http://localhost:5000/api/experiments/1108541'
            },
            'control_number': '1108541',
            'affiliation_record': {
                '$ref': 'http://localhost:5000/api/institutions/902725'
            }
        },
        uuid='18896fa9-16ab-44b6-b0f5-75345d7143bf'
    )
    return record


@pytest.fixture()
def experiment_record_changed_uuid_and_exist_affiliation():
    record = create_record_stub(
        json={
            'self': {
                '$ref': 'http://localhost:5000/api/experiments/1108541'
            },
            'control_number': '1108541',
            'affiliation_record': {
                '$ref': 'http://localhost:5000/api/institutions/903369'
            }
        },
        uuid='f09c1197-f0f3-4765-a1c2-cdac0bf2e8ab'
    )
    return record


@pytest.fixture()
def experiment_record_changed_uuid_and_nonexist_affiliation():
    record = create_record_stub(
        json={
            'self': {
                '$ref': 'http://localhost:5000/api/experiments/1108541'
            },
            'control_number': '1108541',
            'affiliation_record': {
                '$ref': 'http://localhost:5000/api/institutions/90336'
            }
        },
        uuid='f09c1197-f0f3-4765-a1c2-cdac0bf2e8ab'
    )
    return record


@pytest.fixture()
def basic_conference_record():

    # TODO: conference.series assumes new structure of the schema
    # proposed in issue no. 1228 on inspire-next
    record = create_record_stub(
        json={
            'self': {
                '$ref': 'http://localhost:5000/api/conferences/1245372'
            },
            'control_number': '1245372',
            'address': [
                {
                    "original_address": "Autrans, France",
                    "country_code": "FR"
                }
            ],
            'field_categories': [
                {
                    "_term": "Math and Math Physics",
                    "term": "Math and Math Physics",
                    "scheme": "INSPIRE"
                },
                {
                    "_term": "Computing",
                    "term": "Computing",
                    "scheme": "INSPIRE"
                }
            ],
            'series': [
                {
                    'name': 'SOS',
                    'number': '3'
                }
            ]
        },
        uuid='6963fcde-5203-4cd1-9894-67c402dc5bc3'
    )
    return record


@pytest.fixture()
def conference_record_to_update():
    # TODO: conference.series assumes new structure of the schema
    # proposed in issue no. 1228 on inspire-next
    record = create_record_stub(
        json={
            'self': {
                '$ref': 'http://localhost:5000/api/conferences/1245372'
            },
            'control_number': '1245372',
            'address': [
                {
                    "original_address": "Geneve, Switzerland",
                    "country_code": "CH"
                }
            ],
            'field_categories': [
                {
                    "_term": "Astrophysics",
                    "term": "Astrophysics",
                    "scheme": "INSPIRE"
                },
                {
                    "_term": "Computing",
                    "term": "Computing",
                    "scheme": "INSPIRE"
                }
            ],
            'series': [
                {
                    'name': 'SOS',
                    'number': '4'
                },
                {
                    'name': 'ExistingOne'
                },
                {
                    'name': 'NonExistingOne',
                    'number': '1'
                }
            ]
        },
        uuid='15117ae8-498f-4612-afa7-618e19f63e87'
    )
    return record


@pytest.fixture()
def basic_institution_record():
    record = create_record_stub(
        json={
            'self': {
                '$ref': 'http://localhost:5000/api/institutions/902624'
            },
            'address': [
                {
                    "original_address": [
                        "Physikzentrum",
                        "Sommerfeldstrasse 14"
                    ],
                    "city": "Aachen",
                    "postal_code": "52056",
                    "country_code": "DE",
                    "country": "Germany"
                }
            ],
        },
        uuid='e8258342-ff8d-40d5-b1b2-c35178d4db6b'
    )
