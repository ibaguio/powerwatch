from flask import Flask
from flask import render_template as render
from flask import request, make_response, redirect

import database, json, math

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
		return render("admin.jade", title="Admin",user=username,pdus = database.getPDUS())	
	return render("login.jade",title="Login")

@app.route("/login", methods=["GET","POST"])
def login(): #Pseudo Login
	if request.method == 'GET':
		print "Redirecting to homepage"
		return redirect("/")

	session['username'] = request.form['username']
	session['password'] = request.form['password']
	if session['username'] == "admin" and session['password'] == "admin":
		resp = make_response(render("admin.jade", title="Admin",user=session['username'],pdus = database.getPDUS()))
		resp.set_cookie('username',session['username'])
		resp.set_cookie('credentials',SECRET_WORD)
		return resp
	else:
		return render("login.jade",error="Username/Password not found",title="Login")

@app.route("/pdugraph/<pdu_id>")
def graph_data(pdu_id):
	username = request.cookies.get('username')
	name="PDU"+pdu_id
	data="[1,2,3,4,5,1,2,3,2,1,3,2,3,4,5]"
	return render("graph.jade",title="PDU Graph",graphdata=data,user=username,name=name)

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

@app.route("/pdu/new",methods=['POST'])
def newPDU():
	#submethod that checks if a string is a valid form for ip address
	def validIPAddress(ipaddr):
		print ipaddr
		subs = ipaddr.split('.')
		for num in subs:
			try:
				num = int(num)
				if num > 255 and num < 1: raise
			except:
				return
		return len(subs) == 4

	if isLoggedIn():
		try:
			print request.form
			pdu_name = request.form['pdu_name']
			ip_address = request.form['ip_address']
			database.newPDU(pdu_name,ip_address)
		except Exception, e:
			print "Err"
			print e

		return redirect("/")
		
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
	data_["device_id"] = pdu_id
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

#returns json info about pdu's uptime and total consumption
@app.route("/pdu/info/<pdu_id>", methods=["GET"])
def getPDUInfo(pdu_id):
	#solves the estimated total consumption
	#ws
	def solveConsumption(rows):
		sum_ = 0.0
		for i in range(len(rows)-1):
			sum_ += ((rows[i][0] + rows[i+1][0])/2) * (rows[i+1][1] - rows[i][1])

		kwHr = str(sum_ / 3600.0)
		return "%s W hr"%(str(kwHr)[:kwHr.index('.')+7])

	def millsecToTime(secs):
		mins = math.ceil(secs / 60)
		if mins < 1: return "1 min"
		return str(mins).split('.')[0] + " mins"

	#get total consumption
	if not checkPDU(pdu_id): return INVALID_PDU
	all_rows = database.query_db("SELECT watts, time FROM device_readings WHERE device_id = ? ORDER BY time ASC;",pdu_id)

	#get uptime
	first_row = database.query_db("SELECT time FROM device_readings WHERE device_id = ? ORDER BY time ASC;",pdu_id,True)
	last_row = database.query_db("SELECT time FROM device_readings WHERE device_id = ? ORDER BY time DESC;",pdu_id,True)

	data = {'uptime':millsecToTime(last_row[0]-first_row[0]),'consumption':solveConsumption(all_rows),'status':"Online"}
	return json.dumps(data)

#check the database if pdu_id is valid
def checkPDU(pdu_id):
	p = database.query_db("select count(*) from devices where device_id = ?;",pdu_id)
	print "checking pdu. len: ",len(p)
	return len(p) == 1

#inserts the pdu_id to the cache of active pdus
def addPDUCache(pdu_id):
	if pdu_id not in tmp_cache:
		tmp_cache.append(pdu_id)

if __name__ == "__main__":
	print "Running host"
	app.run(host='0.0.0.0')