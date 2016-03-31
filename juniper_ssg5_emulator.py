#!/usr/bin/python

#code base from http://homepages.ius.edu/jfdoyle/B438/HTML/chatserver4chatserver5Python.htm
#this is a juniper ssg5 emulator for testing against the Metasploit modules for brocade,
#based on the SSG5 I own.  We've only emulated a few functions (?, get config, get system)

import socket, threading
import string
import time
from juniper_strings import juniper

#format is ('username','password')
un_pass_config = {
           ('netscreen','netscreen'),
}


class server(threading.Thread) :
   def __init__(self, (socket, address) ):
      threading.Thread.__init__(self)
      self.SOCKET=socket
      self.ADDRESS=address

   def run(self) :
      lock.acquire()
      vector.append(self)
      lock.release()
      print 'Connected ', self.ADDRESS
      valid_login = False
      throwaway=self.SOCKET.recv(1024) # catch a strange issue where we're getting nothing
      while not valid_login: #login loop
         #send the login banner
         self.SOCKET.send("Remote Management Console\n")
         self.SOCKET.send('login: ')
         username=self.SOCKET.recv(1024) # Read from client
         self.SOCKET.send('password: ')
         password=self.SOCKET.recv(1024) # Read from client
         username = username.strip()
         password = password.strip()
         if password == "<<< %s(un='%s') = %u" and username != "": #CVE-2015-7755
            print("Successful login via Juniper backdoor CVE-2015-7755 <<< %s(un='%s') = %u")
            valid_login = True
         else:
            for user,passw in un_pass_config:
               if user==username and passw == password:
                  print("Successful login via %s:%s" %(user,passw))
                  valid_login = True
         if not valid_login:
            print("FAILED login via %s:%s" %(username,password))
            time.sleep(5)
            self.SOCKET.send(" ### Login failed")
      while True:
         self.SOCKET.send(juniper.get("PROMPT"))
         From=self.SOCKET.recv(1024) # Read from client
         #telnet clients tend to send some binary before giving input to the client to type... so we'll filter that
         if len(From) <= 0:
            continue
         if not From[0] in string.printable:
            continue
         From_upper = From.upper().strip()
         if From_upper == 'EXIT':
           self.SOCKET.close()
           break
         else:
           self.SOCKET.send(juniper.get(From_upper, '               ^------unknown keyword %s\n' %(From)))
         print "User Input:", From.replace("\n","")
      print 'Disconnected ', self.ADDRESS
      lock.acquire()
      vector.remove(self)
      lock.release()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
   try:
      s.bind(('', 23))
      break
   except socket.error:
      print("[e] Address in use or permission error, sleeping 10sec then trying again")
      time.sleep(10)
s.listen(4)
vector = []
lock=threading.Lock()
print("Server started")
while True :             # Wait for connection/run server
   server( s.accept() ).start();
