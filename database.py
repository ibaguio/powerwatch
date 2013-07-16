import sqlite3 as lite
import flask, constants
from flask import g

app = flask.Flask(__name__)

DATABASE = constants.db_filename

"""Returns a database connection/cursor"""
def get_db():
	db = getattr(g,'_database',None)
	if db is None:
		db = g._database = lite.connect(DATABASE)
	return db

def init_db():
	print "Initializing database"
	with app.app_context():
		db = get_db()
		db.cursor().executescript(constants.db_init_script)
		db.commit()

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g,'_database',None)
	if db is not None:
		db.close()