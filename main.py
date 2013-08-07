from flask import Flask
from flask import render_template as render
from flask import request, make_response

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

SECRET_WORD = "ivan_pogi"
session = {}

def isLoggedIn():
	credentials = request.cookies.get('credentials')
	return credentials == SECRET_WORD

@app.route("/")
def home():
	username = request.cookies.get('username')
	if isLoggedIn():
		return render("dashboard.jade", title="Dashboard",user=session['username'])	
	return render("login.jade",title="Login")

@app.route("/login",methods=['POST'])
def login(): #Pseudo Login
	session['username'] = request.form['username']
	session['password'] = request.form['password']
	if session['username'] == "admin" and session['password'] == "admin":
		resp = make_response(render("dashboard.jade", title="Dashboard",user=session['username']))
		resp.set_cookie('username',session['username'])
		resp.set_cookie('credentials',SECRET_WORD)
		return resp
	else:
		return "WRONG PASSWORD"

@app.route("/card")
def test():
	return render("card.jade",name="TEST",pow="42",temp="25")

@app.route("/pdu/new",methods=['POST'])
def newPDU():
	if isLoggedIn():
		return request.form
	return notLoggedIn()

def notLoggedIn():
	return "Unauthorized access. Please Login"

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
		data_ = json.loads(request.stream.read())
		print data_
	except Exception, e:
		print "INVALID_PARAMS"
		print e
		return INVALID_PARAMS

	#save data
	if database.save_data(data_): return REQUEST_OK
	else: return REQUEST_FAILED

#check the dictionary if it has the valid 
def checkData(data_):
	import collections

	#print "checking if data has valid values"
	keys_tocheck = ["watts","va","vr","pf","volts","amps","dt"]
	valid = collections.Counter(keys_tocheck) == collections.Counter(data_.keys())
	#print "VALID?",valid

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