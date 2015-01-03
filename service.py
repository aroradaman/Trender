import os
import threading
from BaseHTTPServer import HTTPServer
import dataHandler
import httpHandler

with open('dir.txt','r') as f :
    parentDir = f.read().replace('\n','').replace('\t','').strip()

shared =['C:\python\trend\backup']
CLIENT_PORT = 5000

os.chdir(parentDir)
t1 = threading.Thread( target = dataHandler.updateData, args = () )
t2 = threading.Thread( target = dataHandler.findMusic, args = (shared,) )
t3 = threading.Thread( target = httpHandler.openHome, args = (CLIENT_PORT,) )

t1.start()
t2.start()
t3.start()

server = HTTPServer(('',CLIENT_PORT),httpHandler.handler)
server.serve_forever()