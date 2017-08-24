import sqlite3
import csv
import pandas as pd

OSM_PATH = "san-jose_california.osm"
sql_file = "mydb.db"
conn = sqlite3.connect(sql_file)
cursor = conn.cursor()
cursor.execute('''DROP TABLE IF EXISTS nodes;''')
cursor.execute('''DROP TABLE IF EXISTS nodes_tags;''')
cursor.execute('''DROP TABLE IF EXISTS ways;''')
cursor.execute('''DROP TABLE IF EXISTS ways_tags;''')
cursor.execute('''DROP TABLE IF EXISTS ways_nodes;''')

cursor.execute("CREATE TABLE nodes (id, lat, lon, user, uid, version, changeset, timestamp);")
cursor.execute("CREATE TABLE nodes_tags (id, key, value, type);")
cursor.execute("CREATE TABLE ways (id, user, uid, version, changeset, timestamp);")
cursor.execute("CREATE TABLE ways_tags (id, key, value, type);")
cursor.execute("CREATE TABLE ways_nodes (id, node_id,position);")
conn.commit()

with open ('nodes.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['lat'], i['lon'], i['user'].decode('UTF-8'),
    i['uid'], i['version'], i['changeset'], i['timestamp']) for i in dr]

    cursor.executemany ('''INSERT INTO nodes (id , lat ,lon ,user , 
                                                uid , version , changeset , timestamp ) 
                                                VALUES (?, ?, ?, ?, ? ,?, ? ,?);''', to_db)
conn.commit()

with open ('ways.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['user'].decode('UTF-8'),i['uid'], i['version'], i['changeset'], i['timestamp']) for i in dr]

    cursor.executemany ("INSERT INTO ways (id, user, uid , version , changeset , timestamp ) VALUES (?, ?, ? ,?, ? ,?);", to_db)
conn.commit()

with open ('nodes_tags.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['key'],i['value'].decode('UTF-8'), i['type']) for i in dr]

    cursor.executemany ("INSERT INTO nodes_tags (id,key, value, type ) VALUES (?, ?, ? ,?);", to_db)
conn.commit()

with open ('ways_tags.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['key'],i['value'].decode('UTF-8'), i['type']) for i in dr]

    cursor.executemany ("INSERT INTO ways_tags (id,key, value, type ) VALUES (?, ?, ? ,?);", to_db)
conn.commit()

with open ('ways_nodes.csv', 'rb') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['id'], i['node_id'],i['position']) for i in dr]

    cursor.executemany ("INSERT INTO ways_nodes (id,node_id,position ) VALUES (?, ?, ?);", to_db)
conn.commit()

cursor.execute('SELECT * FROM ways_nodes limit 10 offset 250')
rows = cursor.fetchall()
df_ways = pd.DataFrame(rows)
#print df_ways
#pprint.pprint(rows)
conn.close()