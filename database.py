import sqlite3 as lite
import flask, constants
from flask import g

app = flask.Flask(__name__)

DATABASE = constants.db_filename

"""Returns a database connection/cursor"""
def get_db():
	import sys
	db = getattr(g,'_database',None)
	if db is None:
		#try:
			print "Connecting to",DATABASE
			create_db_folder()
			db = g._database = lite.connect(DATABASE)
		#except Exception, e:
		#	print e
		#	print "WILL TERMINATE"
		#	sys.exit(0)
	return db

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
		db.commit()

def save_data(data_):
	insert_sql = constants.db_insert_reading%(data_)
	print "SQL:",insert_sql
	return dbinsert(insert_sql)

def newPDU(pdu_name, ip_address, account_id = 1):
	data_ = {"pdu_name":pdu_name, "ip_address":ip_address, "account_id":account_id}
	insert_sql = constants.db_insert_pdu%(data_)
	print "SQL:",insert_sql
	return True
	return dbinsert(insert_sql)

def dbinsert(insertSQL):
	db = getattr(g,'_database',None)
	if db is None: db = get_db()
	try:
		db.cursor().executescript(insert_sql)
		return True
	except Exception, e:
		print "FAILED TO INSERT"
		print e


@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g,'_database',None)
	if db is not None:
		db.close()

"""
TODO:
	continue database storing function in main.py


"""