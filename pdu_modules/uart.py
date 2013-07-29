import serial,time,json
from HttpModule import sendData

count = 0

def convert(tmp):
	try:
		return float(tmp)
	except Exception,e:
		print e
	return 0.0

def main():
	global count
	time_seconds = 5;
	decimation = 2;
	
	ser = serial.Serial("/dev/ttyAMA0")
	ser.baudrate = 9600
	ser.open()
	
	cnt = 0
	flag = 0
	flag2 = 0
	
	watts = 0
	VA = 0
	VR =0
	PF = 0
	volt = 0
	amp = 0
	
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
			flag2=1		
		
		if c=='W' and flag==0:
			flag = 1;    
			cnt=0;              
		elif c=='V' and flag==1:
			flag= 2
			cnt=0
		elif c=='R' and flag==2:
			flag = 3
			cnt=0
		elif c=='P' and flag==3:
			flag =4
			cnt=0
		elif c=='V' and flag==4:
			flag =5;
			cnt=0;  
		elif c=='A' and flag==5:
			flag = 6;
			cnt=0;
	
		if flag==1:
			if c.isdigit() or c=='.' or c=='-':
				wattsstr += c
		elif flag==2:
			if c.isdigit() or c=='.' or c=='-':
				VAstr += c
		elif flag==3:
			if c.isdigit() or c=='.' or c=='-':
				VRstr += c 
		elif flag==4:
			if c.isdigit() or c=='.' or c=='-':
				PFstr += c;
		elif flag==5:
			if c.isdigit() or c=='.' or c=='-':
				voltstr += c;
		elif flag==6:
			if c.isdigit() or c=='.' or c=='-':
				ampstr += c;
	
		if flag2==1:
	
			if wattsstr!='':
				watts = convert(wattsstr)
			if VAstr!='':
				VA = convert(VAstr)
			if VRstr!='':
				VR = convert(VRstr)
			if PFstr!='':
				PF = convert(PFstr)
			if voltstr!='':
				volt = convert(voltstr)
			if ampstr!='':
				amp = convert(ampstr)
	
			wattsstr = ''
			VAstr= ''
			VRstr = ''
			PFstr = ''
			voltstr = ''
			ampstr = ''
			
#			print "Watts:",watts
#			print "VA:",VA
#			print "VR:",VR
#			print "PF:",PF
#			print "Volts:",volt
#			print "Amps:",amp
#			data = toJson(watts,VA,VR,PF,volt,amp)
#			print "================="
			
			data = {"watts":watts,"va":VA,"vr":VR,"pf":PF,"volt":volt,"amp":amp}
			print json.dumps(data)
			sendData(data)

		flag2=0;
		
	ser.close()
	
main()
