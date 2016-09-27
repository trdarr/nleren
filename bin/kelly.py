#!/usr/bin/env python3.5

import psycopg2
from bs4 import BeautifulSoup


def entries():
  with open('./data/kelly.xml') as kelly_file:
    soup = BeautifulSoup(kelly_file, 'xml')

  for entry in soup.find_all('LexicalEntry'):
    xs = ('cefr', 'example', 'grammar', 'id', 'pos', 'gf')
    zs = (getattr(y, 'string') for y in (getattr(entry, x) for x in xs))
    yield tuple(zs)

sql = '''
  INSERT INTO words (cefr, example, grammar, "order", pos, word)
  VALUES (%s, %s, %s, %s, %s, %s)
  ON CONFLICT DO NOTHING
'''

with psycopg2.connect(host='postgres', user='postgres') as connection:
  for entry in entries():
    with connection.cursor() as cursor:
      cursor.execute(sql, entry)
