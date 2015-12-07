#!/usr/bin/env python
import socket
import threading
import sys
import dpkt
import time
import subprocess as sp
import os 

"""
this script forwards ethernet frames form received on eth0 to eth1 and visa versa
must be run as root
can be daemonized with parameter "daemon"
"""

frun = True

def passthrough(rx, tx, idf):
    while frun:
        try:
            sframe=  rx.recvfrom(65565)
            if sframe[1][2] == 0:  #not sure what this is but seems to correlate to source and destination
                eth = dpkt.ethernet.Ethernet(sframe[0])
                try:
                    #if socket.inet_ntoa(eth.ip.src) != "192.168.2.44" and socket.inet_ntoa(eth.ip.src) != "192.168.2.48": # we dont send the other route again
                    #    print sframe[1], "\t", sframe[1][4].encode('hex'), sframe[0].encode('hex')
                    tx.send(sframe[0])
                    #else: 
                    #    pass #print "*", skip forwarding of consumed entpoint frame
                except:
                    print sframe[1], "\t", sframe[1][4].encode('hex'), sframe[0].encode('hex')
                    tx.send(sframe[0]) # it was not an ip frame so we do it agian
            else: pass#print ">", # frame in send direction 
        except Exception as e:
            print e

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "daemon":
            print "start", sys.argv[0], "as daemon"
            sp.call(['python', sys.argv[0]])
        else:
            print "supports daemonized start of ethforwarding with parameter 'daemon'"
    else:
        inner = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        inner.bind(("eth1", 0))
        outer = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
        outer.bind(("eth0",0))
            
        upstream = threading.Thread(None, passthrough, None, [inner,outer,1])
        downstream = threading.Thread(None, passthrough, None, [outer,inner,2])
    
        global frun
        frun = True
        
        upstream.start()
        downstream.start()
        
        while 1:
            time.sleep(1)
            continue
            try:
                f = inner.recvfrom(65565)
                txflag = f[1][2]  # 0 is received
                eth = dpkt.ethernet.Ethernet(f[0])
                print f[1][4].encode('hex'),"\t", socket.inet_ntoa(eth.ip.src), " --> " ,  socket.inet_ntoa(eth.ip.dst), f[1], 
            except:
                print "not ip frame"
                pass
            pass
    
