#!/usr/bin/env python3.5

import csv

import psycopg2


connection = psycopg2.connect(host='postgres', user='postgres')

def read_kelly_words(nouns_only=False):
  sql = 'SELECT word, word_id FROM words'
  if nouns_only:
    sql += " WHERE pos LIKE 'noun%'"

  with connection.cursor() as cursor:
    cursor.execute(sql)
    connection.commit()
    return dict(cursor)

def read_pairs(file_path):
  with open(file_path, newline='') as tsv_file:
    return list(csv.reader(tsv_file, delimiter='\t'))

sql = '''
  INSERT INTO translations (word_id, translation, source)
  VALUES (%s, %s, %s)
'''

kelly_nouns = read_kelly_words(nouns_only=True)
for swedish, english in read_pairs('./data/wikipedia.tsv'):
  swedish, _, _ = swedish.lower().partition('(')
  if swedish in kelly_nouns:
    english, _, _ = english.lower().partition('(')
    with connection.cursor() as cursor:
      cursor.execute(sql, (kelly_nouns[swedish], english, 'Wikipedia'))
connection.commit()

kelly_words = read_kelly_words()
for swedish, english in read_pairs('./data/wiktionary.tsv'):
  swedish, _, _ = swedish.lower().partition('(')
  if swedish in kelly_words:
    english, _, _ = english.lower().partition('(')
    with connection.cursor() as cursor:
      cursor.execute(sql, (kelly_words[swedish], english, 'Wiktionary'))
connection.commit()

kelly_words = read_kelly_words()
for swedish, english in read_pairs('./data/omegawiki.tsv'):
  swedish, _, _ = swedish.lower().partition('(')
  if swedish in kelly_words:
    for english in english.split(' ; '):
      english, _, _ = english.lower().partition('(')
      with connection.cursor() as cursor:
        cursor.execute(sql, (kelly_words[swedish], english, 'OmegaWiki'))
connection.commit()
