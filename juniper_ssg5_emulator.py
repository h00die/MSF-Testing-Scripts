#!/usr/bin/python

#code base from http://homepages.ius.edu/jfdoyle/B438/HTML/chatserver4chatserver5Python.htm
#this is a juniper ssg5 emulator for testing against the Metasploit modules for brocade,
#based on the SSG5 I own.  We've only emulated a few functions (?, get config, get system)

import socket, threading
import string
import time

#prompts
PROMPT = "ssg5-serial->  "

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
         self.SOCKET.send(PROMPT)
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
         elif From_upper == 'GET CONFIG':
            #we want to build our username list part dynamically for the config file to make sure its configurable
            unlist = []
            for cred in un_pass_config:
               un,p = cred
               unlist.append('set user "%s" uid 1' %(un))
               unlist.append('set user "%s" type auth' %(un))
               unlist.append('set user "%s" hash-password "02b0jt2gZGipCiIEgl4eainqZIKzjSNQYLIwE="' %(un)) #not sure how hash is generated, so thsi is just a fake one i made
               unlist.append('set user "%s" "enable"' %(un))
            unlist = "\n".join(unlist)
            self.SOCKET.send("""Total Config size 3679:
unset key protection enable
set clock timezone 0
set vrouter trust-vr sharable
set vrouter "untrust-vr"
exit
set vrouter "trust-vr"
unset auto-route-export
exit
set alg appleichat enable
unset alg appleichat re-assembly enable
set alg sctp enable
set auth-server "Local" id 0
set auth-server "Local" server-name "Local"
set auth default auth server "Local"
set auth radius accounting port 1646
set admin name "netscreen"
set admin password "nKVUM2rwMUzPcrkG5sWIHdCtqkAibn"
set admin auth web timeout 10
set admin auth dial-in timeout 3
set admin auth server "Local"
set admin format dos
set zone "Trust" vrouter "trust-vr"
set zone "Untrust" vrouter "trust-vr"
set zone "DMZ" vrouter "trust-vr"
set zone "VLAN" vrouter "trust-vr"
set zone "Untrust-Tun" vrouter "trust-vr"
set zone "Trust" tcp-rst 
set zone "Untrust" block 
unset zone "Untrust" tcp-rst 
set zone "MGT" block 
unset zone "V1-Trust" tcp-rst 
unset zone "V1-Untrust" tcp-rst 
set zone "DMZ" tcp-rst 
unset zone "V1-DMZ" tcp-rst 
unset zone "VLAN" tcp-rst 
set zone "Untrust" screen tear-drop
set zone "Untrust" screen syn-flood
set zone "Untrust" screen ping-death
set zone "Untrust" screen ip-filter-src
set zone "Untrust" screen land
set zone "V1-Untrust" screen tear-drop
set zone "V1-Untrust" screen syn-flood
set zone "V1-Untrust" screen ping-death
set zone "V1-Untrust" screen ip-filter-src
set zone "V1-Untrust" screen land
set interface "ethernet0/0" zone "Untrust"
set interface "ethernet0/1" zone "DMZ"
set interface "bgroup0" zone "Trust"
set interface bgroup0 port ethernet0/2
set interface bgroup0 port ethernet0/3
set interface bgroup0 port ethernet0/4
set interface bgroup0 port ethernet0/5
set interface bgroup0 port ethernet0/6
unset interface vlan1 ip
set interface bgroup0 ip 192.168.1.1/24
set interface bgroup0 nat
unset interface vlan1 bypass-others-ipsec
unset interface vlan1 bypass-non-ip
set interface bgroup0 ip manageable
set interface ethernet0/0 dhcp client enable
set interface ethernet0/0 dhcp client settings autoconfig
set interface "serial0/0" modem settings "USR" init "AT&F"
set interface "serial0/0" modem settings "USR" active
set interface "serial0/0" modem speed 115200
set interface "serial0/0" modem retry 3
set interface "serial0/0" modem interval 10
set interface "serial0/0" modem idle-time 10
set ip tftp retry 30
set ip tftp timeout 30
set flow tcp-mss
unset flow no-tcp-seq-check
set flow tcp-syn-check
unset flow tcp-syn-bit-check
set flow reverse-route clear-text prefer
set flow reverse-route tunnel always
set pki authority default scep mode "auto"
set pki x509 default cert-path partial
%s
set crypto-policy
exit
set ike respond-bad-spi 1
set ike ikev2 ike-sa-soft-lifetime 60
unset ike ikeid-enumeration
unset ike dos-protection
unset ipsec access-session enable
set ipsec access-session maximum 5000
set ipsec access-session upper-threshold 0
set ipsec access-session lower-threshold 0
set ipsec access-session dead-p2-sa-timeout 0
unset ipsec access-session log-error
unset ipsec access-session info-exch-connected
unset ipsec access-session use-error-log
set url protocol websense
exit
set policy id 1 from "Trust" to "Untrust"  "Any" "Any" "ANY" permit 
set policy id 1
exit
set nsmgmt bulkcli reboot-timeout 60
set ssh version v2
set config lock timeout 5
unset license-key auto-update
set telnet client enable
set snmp port listen 161
set snmp port trap 162
set snmpv3 local-engine id "0162122013002408"
set vrouter "untrust-vr"
exit
set vrouter "trust-vr"
unset add-default-route
exit
set vrouter "untrust-vr"
exit
set vrouter "trust-vr"
exit
""" %(unlist))
         elif From_upper == '?':
            self.SOCKET.send("""clear                clear dynamic system info
delete               delete persistent info in flash
exec                 exec system commands
exit                 exit command console
get                  get system information
mtrace               multicast traceroute from source to destination
ping                 ping other host
reset                reset system
save                 save command
set                  configure system parameters
telnet               Telnet other hostname
trace-route          trace route
unset                unconfigure system parameters
""")
         elif From_upper == 'GET SYSTEM':
            self.SOCKET.send("""Product Name: SSG5-Serial
Serial Number: 0000000000000008, Control Number: 00000000
Hardware Version: 0710(0)-(00), FPGA checksum: 00000000, VLAN1 IP (0.0.0.0)
Flash Type: Samsung
Software Version: 6.3.0r19.0, Type: Firewall+VPN
Feature: AV-K
BOOT Loader Version: 1.3.2
Compiled by build_master at: Sun Apr 19 21:42:28 PDT 2015
Base Mac: 0000.0000.a3c0
File Name: ssg5ssg20.6.3.0r19.0, Checksum: 8c102d42
, Total Memory: 128MB

Date 03/28/2016 19:51:01, Daylight Saving Time enabled
The Network Time Protocol is Disabled
Up 0 hours 26 minutes 29 seconds Since 28Mar2016:19:24:32
Total Device Resets: 2, Last Device Reset at: 03/27/2016 19:17:05

System in NAT/route mode.

Use interface IP, Config Port: 80
Manager IP enforced: False
Manager IPs: 0
             
Address                                  Mask                                     Vsys                
---------------------------------------- ---------------------------------------- --------------------
User Name: netscreen

Interface serial0/0:
  description serial0/0
  number 21, if_info 1848, if_index 0
  link down, phy-link down, admin status up
  status change:0
  vsys Root, zone Null, vr untrust-vr
  admin mtu 0, operating mtu 1500, default mtu 1500
  *ip 0.0.0.0/0   mac 0000.0000.a300
  bandwidth: physical 92kbps, configured egress [gbw 0kbps mbw 0kbps]
             configured ingress mbw 0kbps, current bw 0kbps
             total allocated gbw 0kbps
Interface ethernet0/0:
  description ethernet0/0
  number 0, if_info 0, if_index 0, mode route
  link down, phy-link down, admin status up
  status change:0
  vsys Root, zone Untrust, vr trust-vr
  dhcp client enabled
  PPPoE disabled
  admin mtu 0, operating mtu 1500, default mtu 1500
  *ip 0.0.0.0/0   mac 0000.0000.a301
  *manage ip 0.0.0.0, mac 0000.0000.a301
  bandwidth: physical 0kbps, configured egress [gbw 0kbps mbw 0kbps]
             configured ingress mbw 0kbps, current bw 0kbps
             total allocated gbw 0kbps
Interface ethernet0/1:
  description ethernet0/1
  number 5, if_info 440, if_index 0, mode nat
  link down, phy-link down, admin status up
  status change:0
  vsys Root, zone DMZ, vr trust-vr
  dhcp client disabled
  PPPoE disabled
  admin mtu 0, operating mtu 1500, default mtu 1500
  *ip 0.0.0.0/0   mac 0000.0000.a302
  *manage ip 0.0.0.0, mac 0000.0000.a302
  bandwidth: physical 0kbps, configured egress [gbw 0kbps mbw 0kbps]
             configured ingress mbw 0kbps, current bw 0kbps
             total allocated gbw 0kbps
Interface ethernet0/2:
  description ethernet0/2
  number 6, if_info 528, if_index 0
  link down, phy-link down
  status change:0
  member of bgroup0
  vsys Root, zone Null, vr untrust-vr
  *ip 0.0.0.0/0   mac 0000.0000.a303
Interface ethernet0/3:
  description ethernet0/3
  number 7, if_info 616, if_index 0
  link up, phy-link up/full-duplex
  status change:1, last change:03/28/2016 19:24:34
  member of bgroup0
  vsys Root, zone Null, vr untrust-vr
  *ip 0.0.0.0/0   mac 0000.0000.a304
Interface ethernet0/4:
  description ethernet0/4
  number 8, if_info 704, if_index 0
  link down, phy-link down
  status change:0
  member of bgroup0
  vsys Root, zone Null, vr untrust-vr
  *ip 0.0.0.0/0   mac 0000.0000.a305
Interface ethernet0/5:
  description ethernet0/5
  number 9, if_info 792, if_index 0
  link down, phy-link down
  status change:0
  member of bgroup0
  vsys Root, zone Null, vr untrust-vr
  *ip 0.0.0.0/0   mac 0000.0000.a306
Interface ethernet0/6:
  description ethernet0/6
  number 10, if_info 880, if_index 0
  link down, phy-link down
  status change:0
  member of bgroup0
  vsys Root, zone Null, vr untrust-vr
  *ip 0.0.0.0/0   mac 0000.0000.a307
Interface bgroup0:
  description bgroup0
  number 11, if_info 968, if_index 0, mode nat
  link up, phy-link up/full-duplex, admin status up
  status change:1, last change:03/28/2016 19:24:34
  vsys Root, zone Trust, vr trust-vr
  dhcp client disabled
  PPPoE disabled
  admin mtu 0, operating mtu 1500, default mtu 1500
  *ip 192.168.1.1/24   mac 0000.0000.a308
  *manage ip 192.168.1.1, mac 0000.0000.a308
  route-deny disable
  bandwidth: physical 100000kbps, configured egress [gbw 0kbps mbw 0kbps]
             configured ingress mbw 0kbps, current bw 0kbps
             total allocated gbw 0kbps
Interface bgroup1:
  description bgroup1
  number 12, if_info 1056, if_index 0
  link down, phy-link down, admin status up
  status change:0
  vsys Root, zone Null, vr untrust-vr
  admin mtu 0, operating mtu 1500, default mtu 1500
  *ip 0.0.0.0/0   mac 0000.0000.a309
  bandwidth: physical 0kbps, configured egress [gbw 0kbps mbw 0kbps]
             configured ingress mbw 0kbps, current bw 0kbps
             total allocated gbw 0kbps
Interface bgroup2:
  description bgroup2
  number 13, if_info 1144, if_index 0
  link down, phy-link down, admin status up
  status change:0
  vsys Root, zone Null, vr untrust-vr
  admin mtu 0, operating mtu 1500, default mtu 1500
  *ip 0.0.0.0/0   mac 0000.0000.a30a
  bandwidth: physical 0kbps, configured egress [gbw 0kbps mbw 0kbps]
             configured ingress mbw 0kbps, current bw 0kbps
             total allocated gbw 0kbps
Interface bgroup3:
  description bgroup3
  number 14, if_info 1232, if_index 0
  link down, phy-link down, admin status up
  status change:0
  vsys Root, zone Null, vr untrust-vr
  admin mtu 0, operating mtu 1500, default mtu 1500
  *ip 0.0.0.0/0   mac 0000.0000.a30b
  bandwidth: physical 0kbps, configured egress [gbw 0kbps mbw 0kbps]
             configured ingress mbw 0kbps, current bw 0kbps
             total allocated gbw 0kbps
""")
         else:
            #this is a cheap forgery. if the command is known but incomplete it will say so. however, for brevity...
            self.SOCKET.send('               ^------unknown keyword %s\n' %(From))
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
