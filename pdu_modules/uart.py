import serial,time,json,sys,getopt
from HttpModule import sendData
from Config import *

SERVER_ADDRESS = "192.168.1.108:5000/post_info/1"

TIME_INTERVAL = 5;
DECIMATION = 2;
DEBUG = True

def convert(tmp):
	try:
		return float(tmp)
	except Exception,e:
		if DEBUG: print e
	return 0.0

#check command line if server address is given
def getServerAddress(argv):
	global SERVER_ADDRESS
	try:
		opts,args = getopt.getopt(argv,"",["server="])
	except getopt.GetoptError:
		print "uart.py --server=<ip address of server>"
		sys.exit(0)
	for opt,arg in opts:
		if opt == "--server":
			SERVER_ADDRESS = "%s/post_info/1" %(arg)

def main():
	ser = serial.Serial("/dev/ttyAMA0")
	ser.baudrate = 9600
	ser.open()

	flag = 0
	
	wattsstr =''
	VAstr= ''
	VRstr = ''
	PFstr = ''
	voltstr = ''
	ampstr = ''
	
	while True:
		c = ser.read();
		if c == 'H':

			flag=0
			watts = convert(wattsstr)
			VA = convert(VAstr)
			VR = convert(VRstr)
			PF = convert(PFstr)
			volt = convert(voltstr)
			amp = convert(ampstr)
			time_ = time.time()

			data = {"watts":watts,"va":VA,"vr":VR,"pf":PF,"volt":volt,"amp":amp,"dt":time_}
			if DEBUG: print json.dumps(data)
			sendData(data,SERVER_ADDRESS)

			wattsstr =''
			VAstr= ''
			VRstr = ''
			PFstr = ''
			voltstr = ''
			ampstr = ''
		
		if c=='W' and flag==0: flag = 1;
		elif c=='V' and flag==1: flag = 2
		elif c=='R' and flag==2: flag = 3
		elif c=='P' and flag==3: flag =4
		elif c=='V' and flag==4: flag =5;
		elif c=='A' and flag==5: flag = 6;
	
		#if char read is str/digit, append to variable
		if c.isdigit() or c=='.' or c=='-':
			if flag==1: wattsstr += c
			elif flag==2: VAstr += c
			elif flag==3: VRstr += c 
			elif flag==4: PFstr += c
			elif flag==5: voltstr += c
			elif flag==6: ampstr += c
		
	ser.close()

if __name__ == "__main__":
	getServerAddress(sys.argv[1:])
	main()