#!/usr/bin/python

#code base from http://homepages.ius.edu/jfdoyle/B438/HTML/chatserver4chatserver5Python.htm
#this is a brocade emulator for testing against the Metasploit moduels for brocade, 
#based on the switch I own.  We've only emulated a few functions (?, show config, enable) and kept some
#features out like tab complete, ? on commands, just o keep this code fairly simple.

import socket, threading
import string

#prompts
PROMPT = "brocade> "
ENABLED_PROMPT = "brocade# "

class server(threading.Thread) :
   def __init__(self, (socket, address) ):
      threading.Thread.__init__(self)
      self.SOCKET=socket
      self.ADDRESS=address
      self.enabled = False

   def run(self) :
      lock.acquire()
      vector.append(self)
      lock.release()
      print 'Connected ', self.ADDRESS
      while True :
         self.SOCKET.send('\n' + ENABLED_PROMPT) if self.enabled else self.SOCKET.send('\n' + PROMPT)
         From=self.SOCKET.recv(1024) # Read from client
         #telnet clients tend to send some binary before giving input to the client to type... so we'll filter that
         if not From[0] in string.printable:
            continue
         From_upper = From.upper().strip()
         if From_upper == 'QUIT':
            self.SOCKET.close()
            break
         elif From_upper == '?':
               self.SOCKET.send("""  enable            Enter Privileged mode
  ping              Ping IP node
  show              Display system information
  stop-traceroute   Stop current TraceRoute
  traceroute        TraceRoute to IP Node""")
         elif From_upper == 'SHOW VERSION':
               self.SOCKET.send("""  Copyright (c) 1996-2010 Brocade Communications Systems, Inc.
    UNIT 1: compiled on Feb 16 2012 at 20:20:31 labeled as FGSL07202f
                (3172304 bytes) from Secondary FGSL07202f.bin
        SW: Version 07.2.02fT7e1
  Boot-Monitor Image size = 416213, Version:05.0.00T7e5 (Fev2)
  HW: Stackable FWS624
==========================================================================
UNIT 1: SL 1: FastIron WS 624 24-port Management Module
         Serial  #: AN11111111
         License: FWS_BASE_L3_SOFT_PACKAGE   (LID: aaAAAAAAAA)
         P-ENGINE  0: type D814, rev 01
==========================================================================
  400 MHz Power PC processor 8248 (version 130/2014) 66 MHz bus
  512 KB boot flash memory
30720 KB code flash memory
  256 MB DRAM
STACKID 1  system uptime is 2 days 4 hours 25 minutes 10 seconds
The system : started=warm start  reloaded=by "reload"
""")
         else:
               self.SOCKET.send('Invalid input -> %s\nType ? for a list' %(From))
         print(From)
         #if not From : break
         #for s in vector :
         #      if s != self :
         #         s.SOCKET.send(From)
         #self.SOCKET.close()
      print 'Disconnected ', self.ADDRESS
      lock.acquire()
      vector.remove(self)
      lock.release()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 23))
s.listen(4)
vector = []
lock=threading.Lock()

while True :             # Wait for connection/run server
   server( s.accept() ).start(); 
