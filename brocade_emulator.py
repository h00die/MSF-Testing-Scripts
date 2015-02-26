#!/usr/bin/python

#code base from http://homepages.ius.edu/jfdoyle/B438/HTML/chatserver4chatserver5Python.htm
#this is a brocade emulator for testing against the Metasploit moduels for brocade, 
#based on the switch I own.  We've only emulated a few functions (?, show config, enable) and kept some
#features out like tab complete, ? on commands, just o keep this code fairly simple.
#we've also forged in a 'switchversion' command, which will dynamically switch from 7.2 emulation to 7.4 emulation.

import socket, threading
import string
import time

#prompts
PROMPT = "brocade> "
ENABLED_PROMPT = "brocade# "

#format is ('username','password'):privilege
un_pass_config = {
           ('username','password'):'',
           ('ttrogdon','ttrogdon'):5,
           ('dmudd', 'crazypassword'):4
}
un_pass_running_config = {
           ('TopDogUser','mystery'):''
}

class server(threading.Thread) :
   def __init__(self, (socket, address) ):
      threading.Thread.__init__(self)
      self.SOCKET=socket
      self.ADDRESS=address
      self.enabled = False
      self.version = "7.2"

   def run(self) :
      lock.acquire()
      vector.append(self)
      lock.release()
      print 'Connected ', self.ADDRESS
      #send the consent banner
      self.SOCKET.send("""Warning Notification!!!
This system is to be used by authorized users only for the purpose of
conducting official company work. Any activities conducted on this system may
be monitored and/or recorded and there is no expectation of privacy while
using this system. All possible abuse and criminal activity may be handed
over to the proper law enforcement officials for investigation and
prosecution. Use of this system implies consent to all of the conditions
stated within this Warning Notification.""")
      while True :
         self.SOCKET.send('\n' + ENABLED_PROMPT) if self.enabled else self.SOCKET.send('\n' + PROMPT)
         From=self.SOCKET.recv(1024) # Read from client
         #telnet clients tend to send some binary before giving input to the client to type... so we'll filter that
         if len(From) <= 0:
            continue
         if not From[0] in string.printable:
            continue
         From_upper = From.upper().strip()
         if From_upper == 'QUIT' or From_upper == 'LOGOUT':
            self.SOCKET.close()
            break
         elif From_upper == 'EXIT':
            if self.enabled:
                self.enabled = False
            else:
                self.SOCKET.close()
                break
         elif From_upper == 'SWITCHVERSION':
            self.version = "7.4" if self.version == "7.2" else "7.2"
            print("Version is now set to: %s" %(self.version))
         elif From_upper == 'SHOW CONFIG' or From_upper == 'SHOW RUNNING-CONFIG':
            #we want to build our username list part dynamically for the config file to make sure its configurable
            unlist = []
            credToUse = un_pass_config if From_upper == 'SHOW CONFIG' else un_pass_running_config
            for cred in credToUse:
                un,p = cred
                if credToUse[cred]: #we have a permission to add
                    unlist.append("username %s privilege %s password ....." %(un,credToUse[cred]))
                else:
                    unlist.append("username %s password ....." %(un))
            unlist = "\n".join(unlist)
            if self.version == "7.2":
               self.SOCKET.send("""!
Startup-config data location is flash memory
!
Startup configuration:
!
ver 07.2.02fT7e1
!
module 1 fwsl00m-24-port-copper-base-module
!
tftp disable
!
!
!
vlan 1 name DEFAULT-VLAN by port
!
vlan 100 by port
!
!
!
!
system-max hw-ip-route-tcam 64
!
!
!
aaa authentication web-server default local
aaa authentication login default local
boot sys fl sec
console timeout 10
enable super-user-password .....
hostname brocade
ip dhcp-server enable
!
ip dhcp-server pool bro
 dns-server 192.168.50.1
 domain-name groupbro
 lease 1 0 0
 network 192.168.50.0 255.255.255.0
!
ip route 0.0.0.0 0.0.0.0 10.210.10.65
!
no ip source-route
logging facility local4
no logging buffered debugging
logging console
no telnet server
telnet server enable vlan 1
%s
password-change any
cdp run
fdp run
snmp-server community ..... ro 15
clock summer-time
clock timezone us Eastern
no web-management hp-top-tools
no web-management http
banner motd ^C
**********************************************^C
**********************************************^C
WARNING .... WARNING .... WARNING^C
You have entered into a restricted site.^C
This system is to be accessed only by^C
specifically authorized personnel. Any^C
unauthorized access or use of this system^C
is strictly prohibited and constitutes a^C
violation of federal, state criminal, and^C
of the United States Code and applicable^C
international laws.  Violators will be^C
prosecuted to the fullest extent of the law.^C
logged and/or monitored without further^C
notice, and these logs may be used as^C
evidence in court.^C
**********************************************^C
^C
!
no port bootp
!
!
access-list 15 permit host 10.1.2.32
access-list 15 deny any log
!
!
!
!
ip ssh  idle-time 10
!
!
end
""" %(unlist))
            elif self.version == "7.4":
               self.SOCKET.send("""!
Startup-config data location is flash memory
!
Startup configuration:
!
ver 07.4.00bT311
!
stack unit 1
module 1 icx6450-24-port-management-module
module 2 icx6450-sfp-plus-4port-40g-module
!
!
!
!
vlan 1 name DEFAULT-VLAN by port
!
vlan 901 name Test by port
tagged ethe 1/1/1 to 1/1/12
untagged ethe 1/1/12 to 1/1/24
!
!
!
!
!
!
!
!
aaa authentication enable default local
aaa authentication login default local
console timeout 10
enable super-user-password .....
enable aaa console
hostname bro-switch
ip address 10.1.2.1 255.255.255.224
no ip dhcp-client enable
%s
no snmp-server

no snmp-server community public ro

no web-management http
banner exec ^C
Warning Notification!!!^C
This system is to be used by authorized users only for the purpose of^C
conducting official company work. Any activities conducted on this system may^C
be monitored and/or recorded and there is no expectation of privacy while^C
using this system. All possible abuse and criminal activity may be handed^C
over to the proper law enforcement officials for investigation and^C
prosecution. Use of this system implies consent to all of the conditions^C
stated within this Warning Notification.^C
^C
!
banner motd require-enter-key
banner motd ^C
Warning Notification!!!^C
This system is to be used by authorized users only for the purpose of^C
conducting official company work. Any activities conducted on this system may^C
be monitored and/or recorded and there is no expectation of privacy while^C
using this system. All possible abuse and criminal activity may be handed^C
over to the proper law enforcement officials for investigation and^C
prosecution. Use of this system implies consent to all of the conditions^C
stated within this Warning Notification.^C
^C
!
banner incoming ^C
Warning Notification!!!^C
This system is to be used by authorized users only for the purpose of^C
conducting official company work. Any activities conducted on this system may^C
be monitored and/or recorded and there is no expectation of privacy while^C
using this system. All possible abuse and criminal activity may be handed^C
over to the proper law enforcement officials for investigation and^C
prosecution. Use of this system implies consent to all of the conditions^C
stated within this Warning Notification.^C
^C
!
ssh access-group 10
interface ethernet 1/1/1
speed-duplex 1000-full-master
!
interface ethernet 1/1/2
speed-duplex 1000-full-master
!
interface ethernet 1/1/4
speed-duplex 1000-full-master
!
!
access-list 10 permit 10.1.2.1 0.0.0.24
access-list 10 deny any log
!
!
!
!
ip ssh timeout 30
ip ssh idle-time 10
!
!
end
""" %(unlist))
         elif From_upper == 'ENABLE':
            self.SOCKET.send("Username: ")
            un = self.SOCKET.recv(1024)
            if un.upper() == "LOGOUT": break
            print("    Username: %s" %(un.strip()))
            self.SOCKET.send("Password: ")
            pas = self.SOCKET.recv(1024)
            if pas.upper() == "LOGOUT": break
            print("    Password: %s" %(pas.strip()))
            if (un.strip(),pas.strip()) in un_pass_config or (un.strip(),pas.strip()) in un_pass_running_config:
               self.enabled = True
            else:
               self.SOCKET.send("Error - incorrect password.")
         elif From_upper == '?':
               self.SOCKET.send("""  enable            Enter Privileged mode
  ping              Ping IP node
  show              Display system information
  stop-traceroute   Stop current TraceRoute
  traceroute        TraceRoute to IP Node""")
         elif From_upper == 'SHOW VERSION':
               if self.version == "7.2":
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
               elif self.version == "7.4":
                  self.SOCKET.send("""  Copyright (c) 1996-2012 Brocade Communications Systems, Inc. All rights reserved.
    UNIT 1: compiled on Oct 3 2012 at 08:42:29 labeled as ICX64S07400b
                (10371776 bytes) from Primary ICX64S07400b.bin
        SW: Version 07.4.00bT311
  Boot-Monitor Image size = 776680, Version:07.4.01T310 (kxz07401)
  HW: Stackable ICX6450-24
==========================================================================
UNIT 1: SL 1: ICX6450-24 24-port Management Module
         Serial #: BAA1111A11A
         License: BASE_SOFT_PACKAGE (LID: aaaAAAAaAAa)
         P-ENGINE 0: type DEF0, rev 01
==========================================================================
UNIT 1: SL 2: ICX6450-SFP-Plus 4port 40G Module
==========================================================================
  800 MHz ARM processor ARMv5TE, 400 MHz bus
  65536 KB flash memory
  512 MB DRAM
STACKID 1 system uptime is 78 days 2 hours 54 minutes 7 seconds
The system : started=cold start 
""")
         else:
               self.SOCKET.send('Invalid input -> %s\nType ? for a list' %(From))
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
        print("[e] Address in use, sleeping 30sec then trying again")
        time.sleep(30)
s.listen(4)
vector = []
lock=threading.Lock()
print("Server started")
while True :             # Wait for connection/run server
   server( s.accept() ).start(); 
