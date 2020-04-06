#!/usr/bin/env python3
# -*- coding: utf-8 .*-

'''
Lyssnar på MR Clock, multicast
Publicerar till MQTT
'''

import socket
import struct
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import sys

MCAST_GRP = '239.50.50.20'
MCAST_PORT = 2000
broker_address = '192.168.0.222'
base_topic = 'clees/mrclock'

def ParseMsg(msg):
    
    while len(msg) > 0:
        p2 = msg.find('\\')
        row = msg[:p2]
        print(row) 
        msg = msg[p2+2:]

def GetValue(msg,valuename):
    p1 = msg.find(valuename+'=')
    #print(p1)
    if p1 > 0:
        p1 = p1 + len(valuename) + 1
        p2 = msg.find('\\r',p1)
        return msg[p1:p2]
    else:
        return -1

def StripIp(msg):
    p2 = msg.find(',')
    return msg[:p2]

def publish_single_msg(topic, message, retain = False):
    publish.single(topic,message,hostname=broker_address, protocol=mqtt.MQTTv31, retain = retain)
		
			
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

msg = str(sock.recv(10240))
text = 'MRclock Gateway to CLEES'
print(text + '\n' + '=' * len(text) + '\n\n')

text = 'Publishing to: ' + base_topic + ' at ' + broker_address
print(text + '\n' + '-' * len(text) + '\n\n')

text = 'Listening to: ' + GetValue(msg,'name') + ' at ' + StripIp(GetValue(msg,'ip-address'))
print(text + '\n' + '-' * len(text) + '\n\n')

while True:
    msg = str(sock.recv(10240))
    print('active:' + GetValue(msg,'active') +'  clock:' + GetValue(msg,'clock') + '  speed:'+GetValue(msg,'speed') + '  text:' + GetValue(msg,'text') )
    publish_single_msg(base_topic+'/active',GetValue(msg,'active'), retain = True)
    publish_single_msg(base_topic+'/name',GetValue(msg,'name'))
    publish_single_msg(base_topic+'/clock',GetValue(msg,'clock'))
    publish_single_msg(base_topic+'/speed',GetValue(msg,'speed'))
    publish_single_msg(base_topic+'/weekday',GetValue(msg,'weekday'))
    publish_single_msg(base_topic+'/text',GetValue(msg,'text'))
        
