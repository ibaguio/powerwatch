import sqlite3 as lite
import flask, constants
from flask import g

app = flask.Flask(__name__)

DATABASE = constants.db_filename

"""Returns a database connection/cursor"""
def get_db():
	db = getattr(g,'_database',None)
	if db is None:
		print "Connecting to",DATABASE
		create_db_folder()
		db = g._database = lite.connect(DATABASE)
	return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#creates the 'database' folder
def create_db_folder():
	import os
	src = os.path.dirname(__file__) + os.sep + constants.db_folder
	if not os.path.exists(src):
		os.makedirs(src)

def init_db():
	print "Initializing database"
	with app.app_context():
		db = get_db()
		db.cursor().executescript(constants.db_init_script)
		try:
			db.cursor().executescript(constants.db_test_accounts)
		except:
			pass
		db.commit()

def save_data(data_):
	insert_sql = constants.db_insert_reading%(data_)
	print "SQL:",insert_sql
	return dbinsert(insert_sql)

def newPDU(pdu_name, ip_address, account_id = 1):
	data_ = {"pdu_name":pdu_name, "ip_address":ip_address, "account_id":account_id}
	insert_sql = constants.db_insert_pdu%(data_)
	print "SQL:",insert_sql
	return dbinsert(insert_sql)

def dbinsert(insertSQL):
	db = getattr(g,'_database',None)
	if db is None: db = get_db()
	try:
		db.cursor().executescript(insertSQL)
		db.commit()
		return True
	except Exception, e:
		print "FAILED TO INSERT"
		print e

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g,'_database',None)
	if db is not None:
		db.close()

#gets all the list of PDUS
def getPDUS():
	select_sql = """SELECT * FROM devices;""";
	pdus = query_db(select_sql)
	print pdus
	return pdus

"""
TODO:
	continue database storing function in main.py
"""