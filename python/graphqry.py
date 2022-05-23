"""

This program reads Archimate CSV-export files and load them into a Neo4j database

"""

import re
import sys
from os.path import join

import pandas as pd
from neo4j import GraphDatabase

DIR = r'C:\Users\XY56RE\PycharmProjects\p13596-architecture-model\other_CSV'
ELEM = r'MF_Decom_elements.csv'
PROP = r'MF_Decom_properties.csv'
REL = r'MF_Decom_relations.csv'
DB_USR = 'neo4j'
DB_PWD = 'mfdecom'  # 'test' #
URL = r'bolt://localhost:7687'  # 7687' # 11001'

i = 1


class Graphdb(object):

    def __init__(self, uri=None, auth=None, database='neo4j'):
        self._driver = GraphDatabase.driver(uri, auth=auth)
        self.database = database

    def close(self):
        self._driver.close()

    @staticmethod
    def run(tx, cmd):
        tx.run(cmd)

    # clean the database
    def clean(self, labels=None):
        cmd = ""
        if labels:
            for label in labels:
                cmd = f"MATCH (n:{label}) DETACH DELETE n;"
        else:
            cmd = "MATCH (n) DETACH DELETE n;"

        with self._driver.session(database=self.database) as session:
            result = session.write_transaction(self.run, cmd)
        return result

    def node(self, elem, attribs):
        global i
        uuid = elem['ID']
        label = elem['Type']
        attribs['Name'] = elem['Name']
        attribs['Documentation'] = re.sub(r'\s*properties={[\s\S]*};\s*', '', elem['Documentation']).replace('"', "'")
        attribs['uuid'] = uuid
        attribs['Type'] = label

        att_list = ''
        for key, value in attribs.items():
            att_list += 'n.`' + str(key) + '` = "' + str(value) + '",'
        att_list = att_list[:-1]
        if att_list == '':
            cmd = f'''
                MERGE (n:{label} {{uuid: "{uuid}" }})
            '''
        else:
            cmd = f'''
                MERGE (n:{label} {{uuid: "{uuid}" }})
                ON CREATE SET {att_list}
                ON MATCH SET {att_list}
            '''

        # print('\n', cmd)
        i += 1
        if i % 10 == 0:
            print(f"Nodes:  {i}", end='\r', flush=True)
        with self._driver.session(database=self.database) as session:
            result = session.write_transaction(self.run, cmd)
        return result

    def edge(self, rel, attribs):
        global i
        label = rel['Type']
        # get key attributes
        src = rel['Source']
        dest = rel['Target']

        attribs['Name'] = rel['Name']
        attribs['Documentation'] = re.sub(r'\s*properties={[\s\S]*};\s*', '', rel['Documentation']).replace('"', "'")
        attribs['Type'] = label

        att_list = ''
        for key, value in attribs.items():
            att_list += 'n.`' + str(key) + '` = "' + str(value) + '",'
        att_list = att_list[:-1]

        if att_list == '':
            cmd = f'''
                      MATCH (s {{uuid: "{src}" }}), (d {{uuid: "{dest}" }})
                        MERGE (s)-[n:{label}]-(d)
                      '''
        else:
            cmd = f'''
                      MATCH (s {{uuid: "{src}" }}), (d {{uuid: "{dest}" }})
                        MERGE (s)-[n:{label}]-(d)
                            ON CREATE SET {att_list}
                            ON MATCH SET {att_list}
                      '''
        # print('\n', cmd)
        i += 1
        if i % 10 == 0:
            print(f"Edges:  {i}", end='\r', flush=True)
        with self._driver.session(database=self.database) as session:
            result = session.write_transaction(self.run, cmd)
        return result


def query(self, cmd):
    with self._driver.session(database=self.database) as session:
        result = session.write_transaction(self.run, cmd)
    return result


db = Graphdb(URL, auth=(DB_USR, DB_PWD))


def add_node(row, props):
    if row['Type'] == 'ArchimateModel':
        return

    # create a element object
    elem = {
        'ID': row['ID'],
        'Type': row['Type'],
        'Name': row['Name'],
        'Documentation': row['Documentation']
    }

    # get its attributes
    pp = props.loc[props.ID == row['ID']].dropna()
    attributes = {}
    for x, y in zip(pp['Key'], pp['Value']):
        attributes[x] = y.replace('"', '\\"')

    # create or update a graph DB node
    db.node(elem, attributes)


def add_edge(row, props):
    rel = {
        'ID': row['ID'],
        'Type': row['Type'],
        'Name': row['Name'],
        'Documentation': row['Documentation'],
        'Source': row['Source'],
        'Target': row['Target']
    }

    # get its attributes
    pp = props.loc[props.ID == row['ID']].dropna()
    attributes = {}
    for x, y in zip(pp['Key'], pp['Value']):
        attributes[x] = y

    db.edge(rel, attributes)


def main():
    global i
    print('Clean DB')
    ret = db.clean()
    elems = pd.read_csv(join(DIR, ELEM), delimiter=';', quotechar='"', engine='python', encoding='Latin1').fillna('')
    props = pd.read_csv(join(DIR, PROP), delimiter=';', quotechar='"', engine='python', encoding='Latin1').fillna('')
    rels = pd.read_csv(join(DIR, REL), delimiter=';', quotechar='"', engine='python', encoding='Latin1').fillna('')

    print('Creating nodes in the database')
    i = 1
    elems.apply(lambda row: add_node(row, props), axis=1)
    print(i)
    i = 1
    print('Creating edges in the database')
    rels.apply(lambda row: add_edge(row, props), axis=1)
    print(i)


if __name__ == "__main__":
    main()
