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
test=[{"id":'123',"name":"pdu1","status":"online","uptime":"3 mins","consumption":"5"},{"id":'1234',"name":"pdu2","status":"online","uptime":"31 mins","consumption":"5"},{"id":'123324',"name":"pdu3","status":"dead","uptime":"321 mins","consumption":"5"}]
SECRET_WORD = "ivan_pogi"
session = {}

def isLoggedIn():
	credentials = request.cookies.get('credentials')
	return credentials == SECRET_WORD

@app.route("/logout")
def logout():
	if isLoggedIn():
		resp = make_response(render("login.jade", title="Login"))
		resp.set_cookie('credentials',"")
		resp.set_cookie('username',"")
	return render("login.jade",title="Login")

@app.route("/")
def home():
	username = request.cookies.get('username')
	if isLoggedIn():
		return render("admin.jade", title="Admin",user=username,test=test)	
	return render("login.jade",title="Login")

@app.route("/login",methods=['POST'])
def login(): #Pseudo Login
	session['username'] = request.form['username']
	session['password'] = request.form['password']
	if session['username'] == "admin" and session['password'] == "admin":
		resp = make_response(render("admin.jade", title="Admin",user=session['username'],test=test))
		resp.set_cookie('username',session['username'])
		resp.set_cookie('credentials',SECRET_WORD)
		return resp
	else:
		return render("login.jade",error="Username/Password not found",title="Login")

@app.route("/pdugraph/<pdu_id>")
def graph_data(pdu_id):
	name="PDU"+pdu_id
	data="[1,2,3,4,5,1,2,3,2,1,3,2,3,4,5]"
	return render("graph.jade",title="PDU Graph",graphdata=data,name=name)

@app.route("/dashboard")
def dashboard():
	username = request.cookies.get('username')
	if isLoggedIn():
		return render("dashboard.jade",title="Dashboard",user=username,test=test)
	return render("login.jade",title="Login")

#@app.route("/card", methods=['GET'])
#def get_card():
#	print "YouGETCARD"
#	#How many cards do I print? JSON Dapat ito no?
#	#Data in each card?
#	return render("card.jade",name="HELLO",pow="13kWorld",temp="35C",status="meh")

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
		#ss = data_.split("&")
		#for s in ss:
			#print s
		#print "POST BODY:",data_
		#print "Loading json from POST Body"
		#data = json.loads(data_)
		#print "Data load successful"
		#if not checkData(data_):
		#	raise Exception
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