from flask import Flask
from flask import render_template as render
from flask import request

import database, json

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.debug = True
database.init_db()

#for now use list as cache
tmp_cache = []
INVALID_PDU = "INVALID_PDU"
INVALID_PARAMS = "INVALID_PARAMS"
REQUEST_OK = "OK"
REQUEST_FAILED = "NOT"
session = {}

@app.route("/")
def home():
	return render("login.jade",title="Login")

@app.route("/login",methods=['POST'])
def login(): #Pseudo Login
	session['username'] = request.form['username']
	session['password'] = request.form['password']
	if session['username'] == "admin" and session['password'] == "admin":
		return render("dashboard.jade", title="Dashboard",user=session['username'])
	else:
		return render("login.jade",error="Username/Password not found")

@app.route("/card", methods=['GET'])
def get_card():
	print "YouGETCARD"
	#How many cards do I print? JSON Dapat ito no?
	#Data in each card?
	return render("card.jade",name="HELLO",pow="13kWorld",temp="35C",status="meh")

#this is the handler that receives the request
#from the pdus. Only accepts post requests
#
#Error Codes:
#	INVALID_PDU
#	INVALID_PARAMS
@app.route("/post_info/<pdu_id>", methods=['POST'])
def post_info(pdu_id):
	if pdu_id not in tmp_cache:
		if checkPDU(pdu_id):
			addPDUCache(pdu_id)
		else:
			return INVALID_PDU
	
	#parse data
	try:
		json_data = request.stream.read()
		ss = json_data.split("&")
		for s in ss:
			print s
		#print "POST BODY:",json_data
		#print "Loading json from POST Body"
		#data = json.loads(json_data)
		#print "Data load successful"
		#if not checkData(json_data):
		#	raise Exception
	except Exception, e:
		print "INVALID_PARAMS"
		print e
		return INVALID_PARAMS

	#save data
	if saveData(json_data): return REQUEST_OK
	else: return REQUEST_FAILED

def saveData(data_):
	return True

#check the dictionary if it has the valid 
def checkData(data_):
	import collections

	print "checking if data has valid values"
	keys_tocheck = ["watts","va","vr","pf","volts","amps"]
	valid = collections.Counter(keys_tocheck) == collections.Counter(data_.keys())
	print "VALID?",valid

	return valid

#check the database if pdu_id is valid
def checkPDU(pdu_id):
	return True

#inserts the pdu_id to the cache of active pdus
def addPDUCache(pdu_id):
	if pdu_id not in tmp_cache:
		tmp_cache.append(pdu_id)

if __name__ == "__main__":
	print "Running host"
	app.run(host='0.0.0.0')