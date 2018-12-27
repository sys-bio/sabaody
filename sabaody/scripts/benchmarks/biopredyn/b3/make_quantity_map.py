# Sabaody
# Copyright 2018 Shaik Asifullah and J Kyle Medley

from data import measured_quantity_ids

import tesbml as libsbml

from os.path import join, dirname, abspath, realpath
import argparse, csv

parser = argparse.ArgumentParser(description='Get the name of a parameter.')
parser.add_argument('chebi_table',
                    help='The chebi table tsv.')
args = parser.parse_args()

chebi_name_map = {}
with open(args.chebi_table,'r') as f:
    compounds = csv.reader(f, delimiter='\t')
    # skip first row
    for row in compounds:
        break

    for row in compounds:
        id = row[0]
        status = row[1]
        accession = row[2]
        curated = status == 'C'
        parent_id = int(row[4]) if row[4] != 'null' else None
        name = row[5] if row[5] != 'null' else None
        stars = int(row[9])
        chebi_name_map[accession] = name

reader = libsbml.SBMLReader()
doc = reader.readSBML(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b3.xml')))

model = doc.getModel()

chebi_urn_root   = r'urn:miriam:obo.chebi:CHEBI%3A'
uniprot_urn_root = r'urn:miriam:uniprot:P'

for quantity in measured_quantity_ids:
    s = model.getSpecies(quantity)
    if s is not None:
        for cvterm in (s.getCVTerm(k) for k in range(s.getNumCVTerms())):
            for uri in (cvterm.getResourceURI(j) for j in range(cvterm.getNumResources())):
                if uri.startswith(chebi_urn_root):
                    accession = uri.replace(chebi_urn_root,'CHEBI:')
                    if accession in chebi_name_map:
                        print('"{}": "{}",'.format(s.getId(), chebi_name_map[accession]))
                # if uri.startswith(uniprot_urn_root):
                #     accession = uri.replace(uniprot_urn_root,'P')
                #     if accession in chebi_name_map:
                #         print('"{}": "{}",'.format(s.getId(), chebi_name_map[accession]))
