#from pysnmp.hlapi import *
from easysnmp import Session
import argparse


snmp_max_repetitions=100

def convert_mac(str):
	mac_str=""
	for i in str:
		mac_str+=hex(ord(i))
	mac_str = mac_str.replace('0x','')
	return(mac_str)


class ONT(object):
	def __init__ (self, serialNumber):
		self.serialNumber = serialNumber
	def setType(self,ontType):
		self.ontType = ontType
	def setStatus(self,status):
		if(status==1):
			self.status = "up"
		elif(status==2):
			self.status = "down"
		else:
			self.status = "invalid"

class GPON_Port(object):
	def __init__ (self, ifDescr):
		self.ifDescr=ifDescr
		self.ifAlias=""
		self.onts={}
	def setIfAlias(self,ifAlias):
		self.ifAlias=ifAlias

class OLT_Summary(object):
	def __init__ (self):
		self.oltName=""
		self.ontSN=""
		self.gpon_ports={}

	 # def addGPONPort(self,ifDescr):
		#  self.gpon_port[ifDescr] = GPON_Port(ifDescr)
		  #self.gpon_port.append()
	

parser = argparse.ArgumentParser(description='Poll parameters from OLT')
parser.add_argument('--ip',dest='ip_address',required=True,help='Hostname or IP Address')
parser.add_argument('--olt',dest='olt_name',required=True,help='Name of the OLT')
parser.add_argument('--community',dest='community',default='u2000_ro',help='SNMP read community')
#parser.add_argument('--measurement',dest='community',default='u2000_ro',help='SNMP read community')

args = parser.parse_args()

session = Session(hostname=args.ip_address, community=args.community, version=2, use_numeric=True)

olt = OLT_Summary()

gpon_port_initial_index=4194312190

oids=[]
oids.append('IF-MIB::ifDescr.' + str(gpon_port_initial_index))
oids.append('IF-MIB::ifAlias.' + str(gpon_port_initial_index))
oids.append('.1.3.6.1.4.1.2011.6.128.1.1.2.43.1.3.' + str(gpon_port_initial_index)) #ONT Serial Number
oids.append('.1.3.6.1.4.1.2011.6.128.1.1.2.45.1.4.' + str(gpon_port_initial_index)) #ONT Type
oids.append('.1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15.' + str(gpon_port_initial_index)) #ONT  Status


ont_sn_stats = session.get_bulk(oids,non_repeaters=0,max_repetitions=snmp_max_repetitions)


for item in ont_sn_stats:
    if item.oid == '.1.3.6.1.2.1.2.2.1.2':#ifDescr
        if "GPON_UNI" in item.value:
		olt.gpon_ports[item.oid_index] = GPON_Port(str(item.value))
		olt.gpon_ports[item.oid_index].ifDescr = str(item.value)
    elif item.oid == '.1.3.6.1.2.1.31.1.1.1.18':#ifAlias
        if item.oid_index  in olt.gpon_ports:
        	olt.gpon_ports[item.oid_index].setIfAlias(str(item.value))
    elif '.1.3.6.1.4.1.2011.6.128.1.1.2.43.1.3.' in item.oid:#ONT Serial Number
	oid_index = item.oid.replace('.1.3.6.1.4.1.2011.6.128.1.1.2.43.1.3.','')
        if oid_index  in olt.gpon_ports:
		ont_id = int(item.oid_index)
        	olt.gpon_ports[oid_index].onts[ont_id] = ONT(convert_mac(item.value))
    elif '.1.3.6.1.4.1.2011.6.128.1.1.2.45.1.4.' in item.oid:#ONT Serial Number
        oid_index = item.oid.replace('.1.3.6.1.4.1.2011.6.128.1.1.2.45.1.4.','')
        if oid_index  in olt.gpon_ports:
                ont_id = int(item.oid_index)
                olt.gpon_ports[oid_index].onts[ont_id].setType(str(item.value))
    elif '.1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15.' in item.oid:#ONT Serial Number
        oid_index = item.oid.replace('.1.3.6.1.4.1.2011.6.128.1.1.2.46.1.15.','')
        if oid_index  in olt.gpon_ports:
                ont_id = int(item.oid_index)
                olt.gpon_ports[oid_index].onts[ont_id].setStatus(int(item.value))



for gpon_port in olt.gpon_ports:
	for ont in olt.gpon_ports[gpon_port].onts:
		print(olt.gpon_ports[gpon_port].ifDescr + "," +  olt.gpon_ports[gpon_port].onts[ont].serialNumber+ "," +  olt.gpon_ports[gpon_port].onts[ont].ontType+"'"+olt.gpon_ports[gpon_port].onts[ont].status)

