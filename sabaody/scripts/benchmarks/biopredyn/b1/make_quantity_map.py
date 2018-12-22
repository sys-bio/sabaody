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
doc = reader.readSBML(abspath(join(dirname(realpath(__file__)), '..','..','..','..','..','sbml','b1-fixed.xml')))

model = doc.getModel()

chebi_root = 'http://identifiers.org/obo.chebi/'

for quantity in measured_quantity_ids:
    s = model.getSpecies(quantity)
    if s is not None:
        for cvterm in (s.getCVTerm(k) for k in range(s.getNumCVTerms())):
            for uri in (cvterm.getResourceURI(j) for j in range(cvterm.getNumResources())):
                if uri.startswith(chebi_root):
                    accession = uri.replace(chebi_root,'')
                    if accession in chebi_name_map:
                        print('"{}": "{}",'.format(s.getId(), chebi_name_map[accession]))

print('"r_1166": "Glucose uptake",')
print('"r_1697": "Carbon dioxide exchange",')
print('"r_1762": "Ethanol exchange",')
print('"r_1106": "Acetate exchange",')
print('"r_1172": "Glycerol exchange",')
print('"r_2079": "Trehalose exchange",')
