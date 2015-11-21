'''
Created on 26.11.2013

@author: Jan
'''
import threading
import socket

Port = 3333

def scan():
    # create udp socket
    # brodcast any interface port 3333
    # recvfrom() give back list of tubles
    pass

def scanAnswerServiceThrFu():
    # create udp socket
    # bind to broadcasts on port 3333
    # recvfrom ->  respond: __name__ip, tcp_port 
    pass
    
    
def recvThrFu(conn_sock):
    #args[0] = conn_sock
    print "ready to receive"
    global fRecvRunning
    while fRecvRunning:
        res = conn_sock.recv(1024)
        print res
        if len(res) == 0:
            print "closing connection"
            sc.shutdown(socket.SHUT_WR)
            fRecvRunning = False
            break
    print "stopped receving"
    
def server(s):
    s.bind(('',Port))
    print "listening"
    s.listen(1)
    sc, addr = s.accept()
    print "accepted", addr
    return sc

def client(s):
    s.connect(('127.0.0.1',Port)) # 255.255.255.255
    return s


s = socket.socket()
try:
        sc = server(s)
except Exception as e:
        #print e
        print "try client"
        try:
                sc = client(s)
        except:
                raise

global fRecvRunning
fRecvRunning = True
recvTh = threading.Thread(target=recvThrFu, args=[sc])

recvTh.start()
print "type what you want hit Enter to send and ctr+c to stop"
rawin = raw_input()
while len(rawin) != 0:
    sc.send(rawin)        
    rawin = ''
    rawin = raw_input()
    if fRecvRunning == False:
        print"receving not running anymore"
        break
    if len(rawin) == 0:
        print"stopping connection"
        sc.shutdown(socket.SHUT_WR)
sc.close()
recvTh.join()
print "end"

