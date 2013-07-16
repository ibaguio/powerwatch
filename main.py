from flask import Flask
import database

app = Flask(__name__)
app.debug = True
database.init_db()

#for now use list as cache
tmp_cache = []
INVALID_PDU = "INVALID_PDU"
INVALID_PARAMS = "INVALID_PARAMS"

@app.route("/")
def hello_world():
	return 'Hello World'

@app.route("/test")
def test():
	return 'Test'

#this is the handler that receives the request
#from the pdus. Only accepts post requests
#
#Error Codes:
#	INVALID_PDU
#	INVALID_PARAMS
@app.route("/post_info/<pdu_id>", method='POST')
def post_info(pdu_id):
	if pdu_id not in tmp_cache:
		if checkPDU(pdu_id):
			addPDUCache(pdu_id)
		else:
			return INVALID_PDU
	
	#parse data
	data = request.
	#save data


#check the database if pdu_id is valid
def checkPDU(pdu_id):
	pass

#inserts the pdu_id to the cache of active pdus
def addPDUCache(pdu_id):
	if pdu_id not in tmp_cache:
		tmp_cache.append(pdu_id)

if __name__ == "__main__":
	app.run(host='0.0.0.0')