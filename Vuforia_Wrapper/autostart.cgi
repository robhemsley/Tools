#!/bin/env python2.4
import os

# Test if the process is already running
running = False
try:
    # Try to read pid file
    pid = open('/home/robhemsley/webapps/ar/pid').read()
    # Check if this process is up
    lines = os.popen('ps -p %s' % pid).readlines()
    if len(lines) > 1:
        running = True
    else:
        # Delete pid file
        os.remove('/home/robhemsley/webapps/ar/pid')
except IOError:
    pass

print "Content-type: text/html\r\n"
if running:
    print """<html><head><META HTTP-EQUIV="Refresh" CONTENT="2; URL=."></head><body>
    Site is starting ...<a href=".">click here<a></body></html>"""
else:
    print """<html><head><META HTTP-EQUIV="Refresh" CONTENT="2; URL=."></head><body>
    Restarting site ...<a href=".">click here<a></body></html>"""
    os.setpgid(os.getpid(), 0)

    pid = os.fork()
    if pid == 0:
        os.execl('/usr/local/bin/python2.7', '/usr/local/bin/python2.7', '/home/robhemsley/webapps/ar/site_server.py')
    else:
        open('/home/robhemsley/webapps/ar/pid', 'w').write(str(pid))
        
