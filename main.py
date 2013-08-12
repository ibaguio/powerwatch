from flask import Flask
from flask import render_template as render
from flask import request, make_response, redirect

import database, json, math, constants

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.debug = True
database.init_db()

#for now use list as cache
pdu_ids = []
session = {}

#cache for consumption
#this is used to reduce SQL query load on server
#  KEY		VALUE
# 	id 		id of the pdu
#	rcons		running consumption
#  utime 	running uptime
#	offset 	offset of running consumption
#	last_rec time of last transmission

cache_ = {}

def isLoggedIn():
	credentials = request.cookies.get('credentials')
	return credentials == constants.SECRET_WORD

@app.route("/logout")
def logout():
	if isLoggedIn():
		resp = make_response(render("login.jade", title="Login"))
		resp.set_cookie('credentials',"")
		resp.set_cookie('username',"")
	return render("login.jade",title="Login")

@app.route("/")
def home():
	if isLoggedIn():
		return showAdmin()
	return render("login.jade",title="Login")

@app.route("/login", methods=["GET","POST"])
def login(): #Pseudo Login
	if request.method == 'GET':
		print "Redirecting to homepage"
		return redirect("/")

	session['username'] = request.form['username']
	session['password'] = request.form['password']
	if session['username'] == "admin" and session['password'] == "admin":
		resp = make_response(showAdmin())
		resp.set_cookie('username',session['username'])
		resp.set_cookie('credentials',constants.SECRET_WORD)
		return resp
	else:
		return render("login.jade",error="Username/Password not found",title="Login")

@app.route("/pdugraph/<pdu_id>")
def graph_data(pdu_id):
	import random
	username = request.cookies.get('username')
	count_ = database.query_db("SELECT count(*) FROM device_readings WHERE device_id = ?",pdu_id)[0][0]
	if count_ > 50: offset = count_ - 50
	else: offset = 0

	rows = database.query_db("SELECT watts FROM device_readings WHERE device_id = ? LIMIT ? OFFSET ?;",[pdu_id,50,offset])
	name="Watt Consumption for PDU "+pdu_id
	data= str([watt[0] for watt in rows])
	return render("graph.jade",title="PDU Graph",graphdata=data,
		user=username,
		pdu_id=pdu_id,
		name=name,isOnline=isPDUOnline(pdu_id))

@app.route("/dashboard")
def dashboard():
	username = request.cookies.get('username')
	if isLoggedIn():
		pdus = database.getPDUS()
		return render("dashboard.jade",title="Dashboard",user=username,pdus=pdus,pdu_count=len(pdus))
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
	import time
	if pdu_id not in pdu_ids:
		if checkPDU(pdu_id):
			addPDUCache(pdu_id)
		else:
			return constants.INVALID_PDU
	
	#parse data
	try:
		data_ = json.loads(request.stream.read())
		#print data_
	except Exception, e:
		print "INVALID_PARAMS"
		print e
		return constants.INVALID_PARAMS

	#save data
	data_["device_id"] = pdu_id
	if not pdu_id in cache_: 
		print "PDU ID NOT IN CACHE****"
		cache_[pdu_id] = {"offset":0, "uptime":0.0, "rcons": 0.0}
	cache_[pdu_id]["last_rec"] = time.time()	#update last recieve info
	if database.save_data(data_): return constants.REQUEST_OK
	else: return constants.REQUEST_FAILED

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
	def solveConsumption(rows, rcons=0.0):
		sum_ = rcons
		for i in range(len(rows)-1):
			sum_ += ((rows[i][0] + rows[i+1][0])/2) * (rows[i+1][1] - rows[i][1])

		kwHr = sum_ / 3600.0
		return kwHr
		#return "%s W hr"%(str(kwHr)[:kwHr.index('.')+7])

	def millsecToTime(secs):
		mins = math.ceil(secs / 60)
		if mins < 1: return "1 min"
		return str(mins).split('.')[0] + " mins"

	def solveBill(kwHr):
		php_kw_hr = 10.0
		price = str(php_kw_hr * kwHr)
		return "PhP "+(str(price)[:str(price).index('.')+3])

	#this method is not accurate, ask yourself why
	def getUptime():
		first_row = database.query_db("""SELECT time FROM device_readings WHERE 
			device_id = ? ORDER BY time ASC;""",pdu_id,True)
		last_row = database.query_db("""SELECT time FROM device_readings WHERE 
			device_id = ? ORDER BY time DESC;""",pdu_id,True)
		return last_row[0]-first_row[0]
		
	if not checkPDU(pdu_id): return constants.INVALID_PDU

	dev_name = database.query_db("""SELECT device_name from devices WHERE device_id = ?""",pdu_id,True)[0];

	if pdu_id in cache_: #pdu in cache, load only new input
		offset = cache_[pdu_id]["offset"]
		new_rows = database.query_db("""SELECT watts, time FROM device_readings WHERE
			device_id = ? ORDER BY time ASC LIMIT ?,100 ;""",[pdu_id,offset])

		cache_[pdu_id]["rcons"] += solveConsumption(new_rows)
		cache_[pdu_id]["offset"] += len(new_rows)
		#cache_[pdu_id]["utime"] += len(new_rows)

		kwHr = cache_[pdu_id]["rcons"]
		data = {'uptime':millsecToTime(getUptime()),
					'consumption':"%s W hr"%(str(kwHr)[:str(kwHr).index('.')+5]),
					'price':solveBill(kwHr),"name":dev_name}

		return json.dumps(data)
	else: #not in cache, load everything
		all_rows = database.query_db("""SELECT watts, time FROM device_readings WHERE 
			device_id = ? ORDER BY time ASC;""",pdu_id)

		#get uptime
		kwHr = solveConsumption(all_rows)
		utime = millsecToTime(getUptime())

		data = {'uptime':utime,
					'consumption':"%s W hr"%(str(kwHr)[:str(kwHr).index('.')+7]),
					'price':solveBill(kwHr),"name":dev_name}
		cache_[pdu_id] = {"rcons":kwHr,
								"offset":len(all_rows)}
		return json.dumps(data)

@app.route("/pdu/status")
def getPDUStatus():
	pdus = request.args.get("ids",'')
	if not pdus: return ""
	pdus_ = pdus.split(',')
	
	status = {}
	
	for pdu in pdus_:
		status[int(pdu)] = "Offline"
		if isPDUOnline(pdu): status[int(pdu)] = "Online"
			
	return json.dumps(status)

def isPDUOnline(pdu_id):
	import time
	try:
		time_now = time.time()
		if cache_[pdu_id]["last_rec"] + constants.TIME_THRESHOLD > time_now:
			return True
	except Exception, e:
		print "IS PDU ONLINE ERROR"
		print e

#check the database if pdu_id is valid
def checkPDU(pdu_id):
	p = database.query_db("SELECT count(*) FROM devices WHERE device_id = ?;",pdu_id)
	return len(p) == 1

#inserts the pdu_id to the cache of active pdus
def addPDUCache(pdu_id):
	if pdu_id not in pdu_ids:
		pdu_ids.append(pdu_id)

def showAdmin():
	username = request.cookies.get('username')
	pdus = database.getPDUS()
	return render("admin.jade",title="Admin", user=username, pdus=pdus, pdu_count=len(pdus))

@app.route("/show_cache")
def showCache():
	return json.dumps(cache_)

if __name__ == "__main__":
	print "Running host"
	app.run(host='0.0.0.0')