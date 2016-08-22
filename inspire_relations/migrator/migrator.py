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

from elasticsearch import Elasticsearch

from elasticsearch.helpers import scan as es_scan

import os

from constants import (JOB_RANKS, RESEARCH_FIELDS,
                       COUNTRIES, LITERATURE_LABELS)

ES = Elasticsearch()

GENERATED_FILES_DIRECTORY = os.path.join(os.path.split(os.getcwd())[0],
                                    'neo_files')


def init():
    if not os.path.exists(GENERATED_FILES_DIRECTORY):
        os.makedirs(GENERATED_FILES_DIRECTORY)


def do_both_nodes_exist(start_node, end_node,
                        start_node_domain, end_node_domain):
    if start_node in start_node_domain and end_node in end_node_domain:
        return True
    else:
        return False


def load_recids_from_file(file_name):
    file_name = os.path.join(GENERATED_FILES_DIRECTORY, file_name)
    f = open(file_name, 'r')

    # skip the first line
    f.next()
    return map(lambda s: s.replace('\n', ''), f)


def load_relations_from_file(file_name):
    file_name = os.path.join(GENERATED_FILES_DIRECTORY, file_name)
    f = open(file_name, 'r')

    # skip the first line
    f.next()
    return map(lambda y: (y[0], y[1], y[2]),
               map(
                   lambda s: s.replace('\n', '').replace("\"", "").split(','),
                   f)
        )


def save_relations_to_the_file(file_name, relations,
                               start_node_domain=[], end_node_domain=[],
                               skip_domain_checking=False):
    file_name = os.path.join(GENERATED_FILES_DIRECTORY, file_name)

    with open(file_name, 'w') as relations_file:
        relations_file.write("\"start_recid\",\"relation\",\"end_recid\"\n")
        for relation in relations:
            rel_string = '{start_n},"{rel}",{end_n}\n'.format(
                start_n=relation[0], rel=relation[1], end_n=relation[2])
            if skip_domain_checking:
                relations_file.write(rel_string)
            else:
                if do_both_nodes_exist(relation[0], relation[2],
                                       start_node_domain, end_node_domain):
                    relations_file.write(rel_string)


def save_nodes_to_the_file(file_name, recids):
    file_name = os.path.join(GENERATED_FILES_DIRECTORY, file_name)

    with open(file_name, 'w') as node_file:
        node_file.write("\"recid\"\n")
        for recid in recids:
            node_file.write(str(recid) + '\n')


def process_related_institutes(institute):
    relations = set()
    related_institutes = institute['related_institutes']
    for rel_institute in related_institutes:
        if 'relation_type' in rel_institute and 'recid' in rel_institute:
            relation_type = rel_institute['relation_type']
            start_node, end_node, relation = None, None, None

            if relation_type in ['predecessor', 'parent', 'other']:
                start_node = institute['control_number']
                end_node = str(rel_institute['recid'])
            elif rel_institue['relation_type'] == 'successor':
                start_node = str(rel_institute['recid'])
                end_node = institute['control_number']

            rels_mapping = {
                'predecessor': 'SUCCESSOR_OF',
                'parent': 'CHILD_OF',
                'other': 'RELATED_WITH',
                'successor': 'SUCCESSOR_OF'
            }
            relation = rels_mapping.get(relation_type, None)

            if start_node and relation and end_node:
                yield(start_node, relation, end_node)


def process_address(record):
    start_node = record['control_number']

    for address in record['address']:
        if "country_code" in address:
            yield (start_node, 'LOCATED_IN', address['country_code'])


def process_institutions(elastic):
    query = {
        "_source": ["control_number", "related_institutes", "address"]
        }
    institution_recids = set()
    relations = {
        'CHILD_OF': set(),
        'RELATED_WITH': set(),
        'SUCCESSOR_OF': set()
    }
    country_relations = set()
    for institution in es_scan(elastic, query, index="records-institutions",
                               doc_type="institutions"):
        institution_recids.add(institution['_source']['control_number'])
        if 'related_institutes' in institution['_source']:
            for relation in process_related_institutes(institution['_source']):
                relations[relation[1]].add(relation)

        if 'address' in institution['_source']:
            for country_relation in process_address(institution['_source']):
                country_relations.add(country_relation)

    save_nodes_to_the_file('institutions.csv', institution_recids)
    save_relations_to_the_file('institutions-countries.csv', country_relations,
                               institution_recids, COUNTRIES)

    for rel_type, rels in relations.items():
        file_name = 'institutions-' + rel_type.lower() + '-institutions.csv'
        save_relations_to_the_file(file_name, rels,
                                   institution_recids, institution_recids)


def process_experiments(elastic):
    query = {
        "_source": ["control_number"]
        }

    experiment_recids = set()
    for experiment in es_scan(elastic, query, index="records-experiments",
                               doc_type="experiments"):
        experiment_recids.add(experiment['_source']['control_number'])

    # TODO: misssing connection to Institution (data don't support it yet)
    save_nodes_to_the_file('experiments.csv', experiment_recids)


def process_job_ranks(job):
    start_node = job['control_number']
    for rank in job['ranks']:
        yield (start_node, 'IN_THE_RANK_OF', rank)


def process_field_categories(record):
    start_node = record['control_number']
    for field_category in record['field_categories']:
        yield (start_node, 'IN_THE_FIELD_OF', field_category['term'])


def process_jobs_institutions(job):
    start_node = job['control_number']
    for institution in job['institution']:
        if 'recid' in institution:
            end_node = str(institution['recid'])
            yield (start_node, 'OFFERED_BY', end_node)

def process_jobs(elastic):
    query = {
        "_source": ["control_number", "ranks", "institution.recid",
                    "field_categories"]
        }

    job_recids = set()
    rank_relations = set()
    research_field_relations = set()
    jobs_institutions_relations = set()
    known_institutions = load_recids_from_file('institutions.csv')

    for job in es_scan(elastic, query, index="records-jobs",
                               doc_type="jobs"):
        job_recids.add(job['_source']['control_number'])

        if "ranks" in job['_source']:
            for rank_relation in process_job_ranks(job['_source']):
                rank_relations.add(rank_relation)

        if "field_categories" in job['_source']:
            for field_category_relation in process_field_categories(
                job['_source']):
                research_field_relations.add(field_category_relation)

        if "institution" in job['_source']:
            for job_institution_relation in process_jobs_institutions(
                job['_source']):
                jobs_institutions_relations.add(job_institution_relation)


    save_nodes_to_the_file('jobs.csv', job_recids)

    save_relations_to_the_file('jobs-ranks.csv', rank_relations,
                                   job_recids, JOB_RANKS)
    save_relations_to_the_file('jobs-research_fields.csv',
                                   research_field_relations, job_recids,
                                   RESEARCH_FIELDS)
    save_relations_to_the_file('jobs-institutions.csv',
                                   jobs_institutions_relations,
                                   job_recids, known_institutions)

    # TODO: missing connection to Experiments (not included in the data yet)


def process_conference_series(conference):
    start_node = conference['control_number']
    for conference_series in conference['series']:
        if isinstance(conference_series, list):
            for series in conference_series:
                yield (start_node, 'IS_PART_OF_SERIES', series)
        else:
            yield (start_node, 'IS_PART_OF_SERIES', conference_series)


def process_conferences(elastic):
    query = {
        "_source": ["control_number", "address", "series", "field_categories"]
        }

    conference_recids = set()
    country_relations = set()
    research_field_relations=set()
    conference_series_names = set()
    conference_series_relations = set()

    for conference in es_scan(elastic, query, index="records-conferences",
                               doc_type="conferences"):
        conference_recids.add(conference['_source']['control_number'])

        if 'address' in conference['_source']:
            for country_relation in process_address(conference['_source']):
                country_relations.add(country_relation)

        if "field_categories" in conference['_source']:
            for field_category_relation in process_field_categories(
                conference['_source']):
                research_field_relations.add(field_category_relation)

        if "series" in conference['_source']:
            for conference_series_relation in process_conference_series(
                conference['_source']):
                conference_series_names.add(conference_series_relation[2])
                conference_series_relations.add(conference_series_relation)

    save_nodes_to_the_file('conferences.csv', conference_recids)
    # save_nodes_to_the_file('conference_series.csv', conference_series_names)
    save_relations_to_the_file('conferences-countries.csv', country_relations,
                               conference_recids, COUNTRIES)
    save_relations_to_the_file('conferences-research_fields.csv',
                               research_field_relations, conference_recids,
                               RESEARCH_FIELDS)
    # save_relations_to_the_file('conferences-conference_series.csv',
    #                            conference_series_relations, conference_recids,
    #                            conference_series_names)

    # TODO: fix ConferenceSeries (problem with names with umlauts,
    # also conference_series number is missing)


def process_publishers(journal):
    start_node = journal['control_number']
    for publisher in journal['publisher']:
        yield (start_node, 'PUBLISHED_BY', publisher)


def process_journals(elastic):
    query = {
        "_source": ["control_number", "publisher", "relation"]
        }

    journals_recids = set()
    publisher_names = set()
    publisher_relations = set()

    for journal in es_scan(elastic, query, index="records-journals",
                               doc_type="journals"):
        journals_recids.add(journal['_source']['control_number'])

        if "relation" in journal['_source']:
            pass
        if "publisher" in journal['_source']:
            for publisher_relation in process_publishers(journal['_source']):
                publisher_names.add(publisher_relation[2])
                publisher_relations.add(publisher_relation)

    save_nodes_to_the_file('journals.csv', journals_recids)
    save_nodes_to_the_file('publishers.csv', publisher_names)
    save_relations_to_the_file('journals-publishers.csv', publisher_relations,
                               journals_recids, publisher_names)


def process_persons(elastic):
    query = {
        "_source": ["control_number", "phd_advisors"]
    }

    persons_recids = set()

    for person in es_scan(elastic, query, index="records-authors",
                          doc_type="authors"):
        persons_recids.add(person['_source']['control_number'])

        if "positions" in person['_source']:
            # TODO: implement it (connection to Jobs)
            pass

    save_nodes_to_the_file('persons.csv', persons_recids)

    # TODO: missing connection to PhAdvisors and degrees


def create_author_inneoid(person_recid, institutions_recids):
    institution_string = '#'.join(
        map(str, sorted(institutions_recids, lambda x,y: cmp(int(x), int(y)))
            )
        )

    return 'Author_{person_recid}_{institutions_recids_string}'.format(
        person_recid=person_recid,
        institutions_recids_string=institution_string
    )


def process_references(paper):
    start_node = paper['control_number']
    for reference in paper['references']:
        if 'recid' in reference:
            yield (start_node, 'REFERS_TO', str(reference['recid']))


def extract_author(author):
    person_recid = str(author['recid'])
    affiliations_recids = []

    if 'affiliations' in author:
        affiliations_recids = set(
            [str(aff['recid']) for aff in author['affiliations']
             if 'recid' in aff]
            )
    author_inneoid = create_author_inneoid(person_recid,
                                           affiliations_recids)

    return author_inneoid, person_recid, affiliations_recids


def process_literature(elastic):
    query = {
        "_source": ["control_number", "references.recid",
                    "authors.recid", "authors.affiliations.recid",
                    "collections"]
    }

    literature_recids = set()
    literature_to_remove = set()
    literature_labels = {
        "Published": set(),
        "arXiv": set(),
        "ConferencePaper": set(),
        "Thesis": set(),
        "Review": set(),
        "Lectures": set(),
        "Note": set(),
        "Proceedings": set(),
        "Introductory": set(),
        "Book": set(),
        "BookChapter": set(),
        "Report": set()
    }

    #literature_recids = set(load_recids_from_file('literature.csv'))
    institutions_recids = set(load_recids_from_file('institutions.csv'))
    persons_recids = set(load_recids_from_file('persons.csv'))

    print 'Read!'

    authors_inneoids = set()
    reference_relations = set()
    paper_to_author_relations = set()
    paper_to_person_relations = set()
    authors_to_persons_relations = set()
    authors_to_institutions_relations = set()

    it = 0
    sum = 0
    for paper in es_scan(elastic, query, index="hep_v1",
                          doc_type="record"):
        if it == 10000:
            print str(sum) + ' papers processed.'
            sum += 10000
            it = 0
        else:
            it = it + 1

        paper_recid = paper['_source']['control_number']
        if it % 4 == 0: # save only 1/4 of papers
            literature_recids.add(paper_recid)
            if "collections" in paper['_source']:
                paper_collections = set(
                    map(lambda x: x['primary'],
                        filter(
                            lambda x: x.get('primary') in LITERATURE_LABELS,
                            paper['_source']['collections']))
                )
                for doc_type in paper_collections:
                    literature_labels[doc_type].add(paper_recid)
            if "references" in paper['_source']:
                for reference_relation in process_references(paper['_source']):
                    reference_relations.add(reference_relation)

            if "authors" in paper["_source"]:
                for author in paper['_source']['authors']:
                    if 'recid' in author:
                        author_inneoid, person_recid, affiliations = extract_author(author)
                        if person_recid in persons_recids:
                            paper_to_person_relations.add(
                                (paper_recid, 'WRITTEN_BY_PERSON', person_recid)
                            )
                            authors_inneoids.add(author_inneoid)
                            paper_to_author_relations.add(
                                (paper_recid, 'WRITTEN_BY', author_inneoid)
                                )
                            authors_to_persons_relations.add(
                                (author_inneoid, 'REPRESENTS', person_recid)
                            )
                            existing_affiliations = filter(
                                lambda aff: aff in institutions_recids,
                                affiliations)
                            for existsing_aff in existing_affiliations:
                                authors_to_institutions_relations.add(
                                    (author_inneoid, 'AFFILIATED_WITH',
                                    existsing_aff)
                                    )

            #TODO: missing connection to ResearchField

            #TODO: missing link to Conferences
        else:
            literature_to_remove.add(paper['_id'])




    print 'Saving'
    save_nodes_to_the_file('literature.csv', literature_recids)
    for label, lit_recids in literature_labels.items():
        save_nodes_to_the_file(
            'literature_{label}.csv'.format(label=label), lit_recids
        )
    save_nodes_to_the_file('literature_to_remove.csv', literature_to_remove)
    save_relations_to_the_file('literature-refers_to-literature.csv',
                                reference_relations, literature_recids,
                                literature_recids)
    save_relations_to_the_file('literature-written_by_person-persons.csv',
                               paper_to_person_relations,
                               skip_domain_checking=True)
    save_nodes_to_the_file('authors.csv', authors_inneoids)
    save_relations_to_the_file('literature-written_by-authors.csv',
                               paper_to_author_relations,
                               skip_domain_checking=True)
    save_relations_to_the_file('authors-represents-persons.csv',
                               authors_to_persons_relations,
                               skip_domain_checking=True)
    save_relations_to_the_file('authors-affiliated_with-institutions.csv',
                               authors_to_institutions_relations,
                               skip_domain_checking=True)

if __name__ == '__main__':
    init()
    # process_institutions(ES)
    # process_experiments(ES)
    # process_jobs(ES)
    # process_conferences(ES)
    # process_journals(ES)
    # process_persons(ES)
    # process_literature(ES)

    # rels = load_relations_from_file('literature-written_by-authors.csv')
    # represents = load_relations_from_file('authors-represents-persons.csv')
    # affiliated = load_relations_from_file('authors-affiliated_with-institutions.csv')

    #literature = set(load_recids_from_file('literature_little.csv'))
    #big_literature = set(load_recids_from_file('literature.csv'))


    #lit_ids_to_remove = set(load_recids_from_file('literature_to_remove.csv'))
    actions_iterator = (
        {
            '_op_type': 'delete',
            '_index': 'hep_v1',
            '_type': 'record',
            '_id': str(int(id)),
            }
        for id in lit_ids_to_remove
    )

    from elasticsearch.helpers import bulk
    #bulk(ES, actions_iterator)



    #save_nodes_to_the_file('literature_to_remove.csv', lit_ids_to_remove)
    # references_to_save = set()
    # print 'Doing staff'
    # with open(
    #     os.path.join(GENERATED_FILES_DIRECTORY,
    #                  'literature-refers_to-literature.csv'), 'r') as ref_file:
    #     ref_file.next()
    #     for line in ref_file:
    #         rel_elements = line.replace('\n', '').replace("\"", "").split(',')
    #         if rel_elements[0] in literature and rel_elements[2] in literature:
    #             references_to_save.add((rel_elements[0],
    #                                     rel_elements[1], rel_elements[2]))
    #
    #
    # save_relations_to_the_file('literature-refers_to-literature_little.csv',
    #                            references_to_save, skip_domain_checking=True)
    # rels_to_save = {
    #             r for r in rels if r[0] in literature
    # }
    # authors_to_save = set(map(lambda x: x[2], rels_to_save))
    # represents_to_save = filter(lambda r: r[0] in authors_to_save, represents)
    # affiliated_to_save = filter(lambda r: r[0] in authors_to_save, affiliated)
    #
    # save_nodes_to_the_file('authors_little.csv', authors_to_save)
    # save_relations_to_the_file('literature-written_by-authors_little.csv',
    #                            rels_to_save, skip_domain_checking=True)
    # save_relations_to_the_file('authors-represents-persons_little.csv',
    #                            represents_to_save, skip_domain_checking=True)
    # save_relations_to_the_file('authors-affiliated_with-institutions_little.csv',
    #                            affiliated_to_save, skip_domain_checking=True)

    #literature_to_save = list(literature)[::4]
    #save_nodes_to_the_file('literature_little.csv', literature_to_save)

    print 'Done!'
